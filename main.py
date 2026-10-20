import asyncio
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import re
from time import monotonic
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, Field
import httpx2 as httpx

from config import load_settings
from api_errors import PublicError, configure_public_errors
from auth import Usuario, configure_auth, exige_papel, usuario_repo

settings = load_settings()
configure_auth(settings.jwt_secret)
from routers.auth import router as auth_router

logger = logging.getLogger(__name__)
IA_TIMEOUT_SECONDS = 14.0
IA_UNAVAILABLE = "Diagnóstico de IA indisponível no momento. Tente novamente mais tarde."
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def create_provider_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=httpx.Timeout(IA_TIMEOUT_SECONDS))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Um pool por aplicação, criado no event loop e fechado no desligamento.
    async with create_provider_client() as client:
        app.state.provider_client = client
        yield


async def get_provider_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.provider_client


app = FastAPI(
    title="SIGMA - Mini MVP Integrado",
    lifespan=lifespan,
    responses={status: {"model": PublicError} for status in (403, 422, 500)},
)
configure_public_errors(app, settings.cors_origins)

from persistence.database import PersistenceUnavailable
from fastapi.responses import JSONResponse


@app.exception_handler(PersistenceUnavailable)
async def persistence_error(request: Request, exc: PersistenceUnavailable):
    return JSONResponse(status_code=503, content={"detail": "Serviço temporariamente indisponível."})

# Registro de roteadores da aplicação
app.include_router(auth_router)

from persistence.operational import PostgresOperationalStore
from routers.operational import router as operational_router
app.state.operational_store = (PostgresOperationalStore(usuario_repo.backend.engine)
                               if usuario_repo.backend is not None else None)
app.include_router(operational_router)

from sigma_eng.api import create_router
from sigma_eng.audit_chain import AuditChain

# O pacote não escolhe o local dos dados da aplicação hospedeira.
# Preservar o caminho da trilha de engenharia existente no checkout.
_audit_key = os.getenv("SIGMA_AUDIT_KEY")
engineering_audit = AuditChain(
    os.getenv("SIGMA_AUDIT_PATH", str(Path(__file__).resolve().parent / "engenharia" / "resultados" / "audit.jsonl")),
    chave=_audit_key.encode() if _audit_key else None,
)
app.include_router(create_router(exige_papel, auditoria=engineering_audit))
# --------------------------------------------------

class AlertaRede(BaseModel):
    equipamento: str
    ip_origem: str
    descricao_erro: str

from sanitizer import (
    SanitizationError,
    SanitizationResidualError,
    anonimizar_dados,
    categorizar_equipamento,
    sanitizar_texto,
)

async def consultar_ia(client: httpx.AsyncClient, headers: dict, payload: dict) -> str:
    inicio = monotonic()
    status_http = None
    try:
        # O timeout HTTP é por etapa/inatividade. Este prazo limita a espera total,
        # inclusive quando o provedor envia dados lentamente sem ficar inativo.
        async with asyncio.timeout(IA_TIMEOUT_SECONDS):
            resposta_api = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            status_http = resposta_api.status_code
            resposta_api.raise_for_status()
            dados_resposta = resposta_api.json()
            diagnostico = dados_resposta["choices"][0]["message"]["content"]
            if not isinstance(diagnostico, str) or not diagnostico.strip():
                raise ValueError("Invalid provider diagnosis")
            return diagnostico
    except (TimeoutError, httpx.TimeoutException) as error:
        categoria = "timeout"
        classe = type(error).__name__
    except httpx.HTTPStatusError as error:
        categoria = "http"
        classe = type(error).__name__
    except httpx.RequestError as error:
        categoria = "transport"
        classe = type(error).__name__
    except (ValueError, KeyError, IndexError, TypeError) as error:
        categoria = "invalid_response"
        classe = type(error).__name__
    except Exception as error:
        # Não captura CancelledError: o cancelamento externo deve se propagar.
        categoria = "unexpected"
        classe = type(error).__name__

    # Não registrar str(error), traceback, headers, payload ou corpo da resposta:
    # estes podem conter chave, dados do incidente ou texto arbitrário do provedor.
    logger.warning(
        "Falha na IA category=%s exception=%s status=%s duration_ms=%.0f",
        categoria, classe, status_http, (monotonic() - inicio) * 1000,
    )
    return IA_UNAVAILABLE


@app.post("/api/alertas")
async def receber_alerta(
    alerta: AlertaRede,
    client: Annotated[httpx.AsyncClient, Depends(get_provider_client)],
    usuario: Annotated[Usuario, Depends(exige_papel("suporte_n1"))],
):
    # 1. Aplica a anonimização irreversível e fail-closed (Conformidade com a LGPD - RF05)
    equipamento_categorizado = categorizar_equipamento(alerta.equipamento)
    erro_anonimizado = anonimizar_dados(alerta.descricao_erro)
    
    prompt_enviado = f"Equipamento: {equipamento_categorizado} | Erro: {erro_anonimizado}. Forneça um diagnóstico de rede curto e direto."
    
    # 2. Chamada ao OpenRouter com chave e modelo definidos no ambiente.
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": "És um engenheiro de redes sénior de um hospital oncológico. Responde de forma técnica e concisa."},
            {"role": "user", "content": prompt_enviado}
        ]
    }
    
    diagnostico_ia = await consultar_ia(client, headers, payload)
    
    # 3. Retorno para o Frontend (O bloco que devolve a resposta)
    return {
        "status": "Incidente Registrado",
        "dados_enviados_nuvem": prompt_enviado,
        "diagnostico_ia": diagnostico_ia
    }


# =====================================================================
# Rotas da Matriz de Permissões RBAC (README / stack-de-tecnologia.md)
# =====================================================================

@app.get("/api/status")
async def obter_status(usuario: Annotated[Usuario, Depends(exige_papel("suporte_n1"))]):
    """Ver alertas e status da rede (Suporte N1, Analista de Redes, Gestor de TI)."""
    return {"status": "operacional", "perfil": usuario.papel}


@app.get("/api/alertas")
async def listar_alertas(usuario: Annotated[Usuario, Depends(exige_papel("suporte_n1"))]):
    """Ver alertas e status da rede (Suporte N1, Analista de Redes, Gestor de TI)."""
    return {"alertas": []}


@app.get("/api/pacotes")
async def ver_pacotes(usuario: Annotated[Usuario, Depends(exige_papel("analista_redes"))]):
    """Ver histórico e detalhes de pacotes (Analista de Redes, Gestor de TI)."""
    return {"pacotes": []}


@app.get("/api/incidentes")
def listar_incidentes(usuario: Annotated[Usuario, Depends(exige_papel("analista_redes"))]):
    """Ver histórico e incidentes (Analista de Redes, Gestor de TI)."""
    return {"incidentes": app.state.operational_store.incidents() if app.state.operational_store else []}


@app.get("/api/relatorios")
async def relatorios_gerenciais(usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))]):
    """Ver relatórios gerenciais (Exclusivo Gestor de TI)."""
    return {"relatorios": []}


@app.get("/api/usuarios")
def listar_usuarios(usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))]):
    """Gerenciar usuários (Exclusivo Gestor de TI)."""
    return {"usuarios": usuario_repo.listar()}


class NovoUsuarioIn(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)
    papel: Literal["suporte_n1", "analista_redes", "gestor_ti"]


@app.post("/api/usuarios")
def criar_usuario(
    dados: NovoUsuarioIn,
    usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))],
):
    """Criar novo usuário no sistema (Exclusivo Gestor de TI)."""
    novo = usuario_repo.adicionar_usuario(dados.username, dados.password, dados.papel)
    return {"username": novo.username, "papel": novo.papel, "status": "criado"}


@app.post("/api/chaves/rotacao")
async def rotacionar_chaves(usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))]):
    """Gerenciar chaves e rotação de credenciais (Exclusivo Gestor de TI)."""
    return {"status": "chaves_rotacionadas"}


@app.get("/api/n8n/acesso")
async def acessar_n8n(usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))]):
    """Acesso ao n8n via VLAN de gerência / VPN restrita (Exclusivo Gestor de TI)."""
    return {"status": "autorizado_vlan_gerencia", "url": "http://n8n-internal.hospital:5678"}
