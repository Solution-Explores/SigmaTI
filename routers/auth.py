"""Roteador de autenticação (login/logout/me) com JWT de sessão (RF07)."""

import os
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from auth import (
    JWT_EXPIRATION_SECONDS,
    Usuario,
    criar_token_sessao,
    obter_auditor,
    obter_usuario_atual,
    rate_limiter,
    usuario_repo,
    verificar_senha,
)

router = APIRouter(prefix="/api/auth", tags=["autenticacao"])


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: str
    papel: str


class LogoutOut(BaseModel):
    status: str
    mensagem: str


class UsuarioMeOut(BaseModel):
    usuario: str
    papel: str


@router.post("/login", response_model=LoginOut)
def login(dados: LoginIn, request: Request) -> dict:
    ip_origem = request.client.host if request.client else "unknown"
    chave_bloqueio = f"{ip_origem}:{dados.username}"
    auditor = obter_auditor()

    # 1. Verifica se a conta/IP está temporariamente bloqueada por excesso de falhas
    if rate_limiter.esta_bloqueado(chave_bloqueio):
        if auditor is not None:
            auditor.registrar(
                ator=dados.username,
                acao="auth.login.blocked_attempt",
                recurso="session",
                detalhes={"ip": ip_origem, "motivo": "lockout_ativo"},
            )
        raise HTTPException(
            status_code=429,
            detail="Limite de requisições excedido.",
        )

    # 2. Busca o usuário no repositório
    usuario = usuario_repo.obter_por_username(dados.username)
    if not usuario or not usuario.ativo or not verificar_senha(dados.password, usuario.senha_hash):
        falhas, bloqueou_agora = rate_limiter.registrar_falha(chave_bloqueio)
        if auditor is not None:
            auditor.registrar(
                ator=dados.username,
                acao="auth.login.failed" if not bloqueou_agora else "auth.login.locked",
                recurso="session",
                detalhes={"ip": ip_origem, "tentativa": falhas},
            )
        raise HTTPException(
            status_code=401,
            detail="Autenticação necessária.",
        )

    # 3. Credenciais válidas: limpa histórico de falhas e registra sucesso na AuditChain
    rate_limiter.limpar(chave_bloqueio)
    if auditor is not None:
        auditor.registrar(
            ator=usuario.username,
            acao="auth.login.success",
            recurso="session",
            detalhes={"papel": usuario.papel, "ip": ip_origem},
        )

    # 4. Emite JWT de sessão com prazo de expiração (nunca devolve chaves permanentes do servidor)
    token = criar_token_sessao(
        usuario=usuario.username,
        papel=usuario.papel,
        expira_em_segundos=JWT_EXPIRATION_SECONDS,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_SECONDS,
        "usuario": usuario.username,
        "papel": usuario.papel,
    }


@router.post("/logout", response_model=LogoutOut)
def logout(usuario: Usuario = Depends(obter_usuario_atual)) -> dict:
    auditor = obter_auditor()
    if auditor is not None:
        auditor.registrar(
            ator=usuario.username,
            acao="auth.logout",
            recurso="session",
            detalhes={"papel": usuario.papel},
        )
    return {
        "status": "sucesso",
        "mensagem": "Logout efetuado com sucesso.",
    }


@router.get("/me", response_model=UsuarioMeOut)
def me(usuario: Usuario = Depends(obter_usuario_atual)) -> dict:
    return {
        "usuario": usuario.username,
        "papel": usuario.papel,
    }
