# api_errors.py

- PublicError · class · L28-L29 — class PublicError(BaseModel)
- public_error · function · L32-L34 — def public_error(status: int, headers: dict | None = None) -> JSONResponse
- log_failure · function · L37-L43 — def log_failure(scope: Scope, category: str, status: int, exception: str) -> None
- validation_error · function · L46-L48 — async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse
- http_error · function · L51-L60 — async def http_error(request: Request, exc: HTTPException) -> JSONResponse
- PublicErrorBoundary · class · L63-L89 — class PublicErrorBoundary
- __init__ · method · L66-L67 — def __init__(self, app: ASGIApp)
- __call__ · method · L69-L89 — async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None
- track_start · function · L76-L80 — async def track_start(message: Message) -> None
- RestrictedCORSMiddleware · class · L92-L116 — class RestrictedCORSMiddleware(CORSMiddleware)
- __call__ · method · L93-L107 — async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None
- preflight_response · method · L109-L116 — def preflight_response(self, request_headers: Headers) -> Response
- configure_public_errors · function · L119-L130 — def configure_public_errors(app: FastAPI, origins: tuple[str, ...]) -> None
