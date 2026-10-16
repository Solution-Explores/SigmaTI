import asyncio
from contextlib import asynccontextmanager
import logging
import re
from time import monotonic
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel
import httpx2 as httpx

from config import load_settings
from api_errors import PublicError, configure_public_errors

settings = load_settings()

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
# --------------------------------------------------

class AlertaRede(BaseModel):
    equipamento: str
    ip_origem: str
    descricao_erro: str

def anonimizar_dados(texto: str) -> str:
    texto_limpo = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_MASCARADO]', texto)
    texto_limpo = texto_limpo.replace("dr.joao", "[USUARIO_MEDICO]")
    return texto_limpo

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
):
    # 1. Aplica a anonimização irreversível (Conformidade com a LGPD)
    erro_anonimizado = anonimizar_dados(alerta.descricao_erro)
    
    prompt_enviado = f"Equipamento: {alerta.equipamento} | Erro: {erro_anonimizado}. Forneça um diagnóstico de rede curto e direto."
    
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
