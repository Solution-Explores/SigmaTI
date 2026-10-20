import asyncio
from types import SimpleNamespace

from fastapi import HTTPException

from routers import events


def test_stream_stops_on_session_revocation_and_releases_capacity(monkeypatch):
    async def scenario():
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(event_streams=1)))
        async def connected():
            return False
        request.is_disconnected = connected
        class Store:
            def stream_events(self, after, limit):
                return []
        calls = []
        def authorize(*args):
            calls.append(1)
            if len(calls) > 1:
                raise HTTPException(401)
        monkeypatch.setattr(events, "obter_usuario_atual", authorize)
        frames = events.event_frames(request, Store(), 0, "Bearer synthetic")
        assert await anext(frames) == ': heartbeat\n\n'
        assert 'session.closed' in await anext(frames)
        try:
            await anext(frames)
            assert False
        except StopAsyncIteration:
            pass
        assert request.app.state.event_streams == 0
    asyncio.run(scenario())


def test_stream_rechecks_auth_between_events_after_consumer_pause(monkeypatch):
    async def scenario():
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(event_streams=1)))
        async def connected():
            return False
        request.is_disconnected = connected
        class Store:
            def stream_events(self, after, limit):
                return [{"id":1},{"id":2}]
        revoked = False
        def authorize(*args):
            if revoked:
                raise HTTPException(401)
        monkeypatch.setattr(events,"obter_usuario_atual",authorize)
        frames = events.event_frames(request,Store(),0,"Bearer synthetic")
        assert 'id: 1' in await anext(frames)
        revoked = True
        assert 'session.closed' in await anext(frames)
        await frames.aclose()
        assert request.app.state.event_streams == 0
    asyncio.run(scenario())


def test_stream_hides_database_error_and_releases_capacity(monkeypatch):
    from persistence.database import PersistenceUnavailable
    async def scenario():
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(event_streams=1)))
        async def connected():
            return False
        request.is_disconnected = connected
        class Store:
            def stream_events(self, after, limit):
                raise PersistenceUnavailable("private database details")
        monkeypatch.setattr(events,"obter_usuario_atual",lambda *args: None)
        frames = events.event_frames(request,Store(),0,"Bearer synthetic")
        frame = await anext(frames)
        assert 'stream.error' in frame and 'private' not in frame
        await frames.aclose()
        assert request.app.state.event_streams == 0
    asyncio.run(scenario())
