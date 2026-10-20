"""Política HTTP pública: origens explícitas e erros sem dados da requisição."""

import logging
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send


logger = logging.getLogger(__name__)
MESSAGES = {
    400: "Requisição inválida.",
    401: "Autenticação necessária.",
    403: "Requisição não permitida.",
    404: "Recurso não encontrado.",
    405: "Método não permitido.",
    422: "Dados da requisição inválidos.",
    429: "Limite de requisições excedido.",
}


class PublicError(BaseModel):
    detail: str


def public_error(status: int, headers: dict | None = None) -> JSONResponse:
    message = "Erro interno do servidor." if status >= 500 else MESSAGES.get(status, MESSAGES[400])
    return JSONResponse({"detail": message}, status_code=status, headers=headers)


def log_failure(scope: Scope, category: str, status: int, exception: str) -> None:
    started = scope.get("state", {}).get("public_error_started", monotonic())
    # Nunca incluir str(exc), traceback, path/query, Origin, corpo ou headers.
    logger.warning(
        "Falha da API category=%s exception=%s status=%s duration_ms=%.0f",
        category, exception, status, (monotonic() - started) * 1000,
    )


async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    log_failure(request.scope, "validation", 422, type(exc).__name__)
    return public_error(422)


async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
    log_failure(request.scope, "http", exc.status_code, type(exc).__name__)
    # Preservar somente métodos HTTP conhecidos no Allow do erro 405 do roteador.
    # Outros headers arbitrários da exceção podem refletir dados internos.
    headers = None
    if exc.status_code == 405 and exc.headers:
        methods = [method.strip() for method in exc.headers.get("Allow", "").split(",")]
        if methods and all(method in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"} for method in methods):
            headers = {"Allow": ", ".join(methods)}
    return public_error(exc.status_code, headers)


class PublicErrorBoundary:
    """Captura falhas antes dos headers, dentro do CORS para também cobrir o 500."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        scope.setdefault("state", {})["public_error_started"] = monotonic()
        started = False

        async def track_start(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.app(scope, receive, track_start)
        except Exception as exc:
            log_failure(scope, "internal", 500, type(exc).__name__)
            if started:
                # Não é possível substituir uma resposta já iniciada.
                raise
            await public_error(500)(scope, receive, send)


class RestrictedCORSMiddleware(CORSMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            origins = headers.getlist("origin")
            preflight = scope["method"] == "OPTIONS" and "access-control-request-method" in headers
            # Ausência de Origin é permitida para clientes de serviço. Origin vazio,
            # null, duplicado ou diferente da lista é recusado, sem executar a rota.
            if origins and (len(origins) != 1 or not self.is_allowed_origin(origins[0])):
                if len(origins) == 1 and preflight:
                    await super().__call__(scope, receive, send)
                    return
                log_failure(scope, "origin", 403, "OriginRejected")
                await public_error(403, {"Vary": "Origin"})(scope, receive, send)
                return
        await super().__call__(scope, receive, send)

    def preflight_response(self, request_headers: Headers) -> Response:
        response = super().preflight_response(request_headers)
        if response.status_code != 400:
            return response
        logger.warning("Falha da API category=cors exception=PreflightRejected status=400")
        headers = {key: value for key, value in response.headers.items()
                   if key.lower() not in {"content-type", "content-length"}}
        return public_error(400, headers)


def configure_public_errors(app: FastAPI, origins: tuple[str, ...]) -> None:
    app.add_exception_handler(RequestValidationError, validation_error)
    app.add_exception_handler(HTTPException, http_error)
    app.add_middleware(PublicErrorBoundary)
    # O último middleware adicionado é o mais externo entre os middlewares do app.
    app.add_middleware(
        RestrictedCORSMiddleware,
        allow_origins=list(origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type", "Authorization", "Last-Event-ID"],
    )
