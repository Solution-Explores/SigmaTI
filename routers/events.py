"""SSE persistente, autenticado por cabeçalho e sem tokens na URL."""
import asyncio
import json

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from auth import obter_usuario_atual
from persistence.database import PersistenceUnavailable
from .operational import Reader, repository

router = APIRouter(prefix="/api/eng", tags=["eventos"])
POLL_SECONDS = 0.2
MAX_STREAMS = 32


async def event_frames(request, store, cursor, authorization):
    try:
        while not await request.is_disconnected():
            try:
                await asyncio.to_thread(obter_usuario_atual, request, authorization)
                events = await asyncio.to_thread(store.stream_events, cursor, 100)
            except HTTPException:
                yield 'event: session.closed\ndata: {}\n\n'
                return
            except PersistenceUnavailable:
                yield 'event: stream.error\ndata: {"code":"unavailable"}\n\n'
                return
            if events:
                for event in events:
                    # Revalidar também após backpressure de um consumidor lento.
                    try:
                        await asyncio.to_thread(obter_usuario_atual, request, authorization)
                    except HTTPException:
                        yield 'event: session.closed\ndata: {}\n\n'
                        return
                    except PersistenceUnavailable:
                        yield 'event: stream.error\ndata: {"code":"unavailable"}\n\n'
                        return
                    cursor = event["id"]
                    yield f'id: {cursor}\nevent: incidente\ndata: {json.dumps(event, separators=(",", ":"))}\n\n'
            else:
                yield ': heartbeat\n\n'
            await asyncio.sleep(POLL_SECONDS)
    finally:
        request.app.state.event_streams -= 1


@router.get("/eventos")
async def events(request: Request, user: Reader,
                 last_event_id: str | None = Header(default=None, max_length=19)):
    if request.query_params:
        raise HTTPException(422, "Use Authorization e Last-Event-ID nos cabeçalhos.")
    if last_event_id is None:
        cursor = 0
    elif not last_event_id.isascii() or not last_event_id.isdecimal() or not 0 <= int(last_event_id) < 2**63:
        raise HTTPException(422, "Cursor inválido.")
    else:
        cursor = int(last_event_id)
    store = repository(request)
    # Consultar antes dos headers: falha inicial do banco conserva resposta HTTP 503.
    await asyncio.to_thread(store.stream_events, cursor, 1)
    if getattr(request.app.state, "event_streams", 0) >= MAX_STREAMS:
        raise HTTPException(503, "Limite de conexões atingido.")
    request.app.state.event_streams = getattr(request.app.state, "event_streams", 0) + 1
    return StreamingResponse(event_frames(request, store, cursor, request.headers.get("authorization")),
        media_type="text/event-stream", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})
