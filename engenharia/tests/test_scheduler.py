import asyncio
import threading
import time

import pytest

from sigma_eng.probe import ProbeResult, TargetNotAllowed
from sigma_eng.scheduler import Scheduler


def target(identifier="one", **kwargs):
    return dict(id=identifier, host="127.0.0.1", porta=80, kind="tcp",
                intervalo_s=0.1, timeout_s=0.05, detector="ewma", **kwargs)


class Store:
    def __init__(self, count=1):
        self.targets = [target(str(i)) for i in range(count)]
        self.results = []

    def collection_targets(self):
        return self.targets

    def record_measurement(self, *args, **kwargs):
        self.results.append((args, kwargs))


def test_timeout_holds_slot_and_discards_late_success():
    async def scenario():
        release = threading.Event()
        store = Store(20)
        calls = []
        def blocked(*args, **kwargs):
            calls.append(1)
            release.wait(3)
            return ProbeResult(status="up", latency_ms=1)
        scheduler = Scheduler(store, concurrency=2, refresh=0.05, probe_fn=blocked, seed=1)
        scheduler.start()
        try:
            await asyncio.sleep(0.35)
            assert len(calls) == 2
            assert scheduler.metrics.timeouts == 2
            assert scheduler.metrics.missed > 0
            assert scheduler.metrics.peak_active <= 2
            assert len(store.results) == 2
            assert all(not args[1] for args, _ in store.results)
        finally:
            await scheduler.stop()
            release.set()
        await asyncio.sleep(0.05)
        assert len(store.results) == 2
    asyncio.run(scenario())


def test_policy_denial_does_not_open_availability_incident():
    async def scenario():
        store = Store()
        def denied(*args, **kwargs):
            raise TargetNotAllowed()
        scheduler = Scheduler(store, refresh=0.05, probe_fn=denied, seed=1)
        scheduler.start()
        await asyncio.sleep(0.2)
        await scheduler.stop()
        assert scheduler.metrics.errors > 0
        assert not store.results
    asyncio.run(scenario())


def test_saturated_scheduler_has_no_backlog_or_per_target_overlap():
    async def scenario():
        store = Store(200)
        calls = []
        lock = threading.Lock()
        def slow(host, port, kind, **kwargs):
            with lock:
                calls.append(time.monotonic())
            time.sleep(0.03)
            return ProbeResult(status="up", latency_ms=30)
        scheduler = Scheduler(store, concurrency=4, refresh=0.05, probe_fn=slow, seed=2)
        scheduler.start()
        await asyncio.sleep(0.4)
        await scheduler.stop()
        assert scheduler.status()["queued"] == 0
        assert scheduler.metrics.peak_active <= 4
        assert scheduler.metrics.missed > 0
        assert scheduler.metrics.max_lag_seconds < 0.3
    asyncio.run(scenario())


def test_slow_inventory_refresh_does_not_block_probe_clock():
    async def scenario():
        class SlowStore(Store):
            def collection_targets(self):
                time.sleep(0.15)
                return self.targets
        store = SlowStore()
        scheduler = Scheduler(store, refresh=0.05,
            probe_fn=lambda *a, **k: ProbeResult(status="up",latency_ms=1), seed=1)
        scheduler.start()
        await asyncio.sleep(0.8)
        await scheduler.stop()
        assert len(store.results) >= 4
        assert scheduler.metrics.max_lag_seconds < 0.1
        assert scheduler.metrics.missed == 0
    asyncio.run(scenario())


def test_dns_timeout_before_policy_does_not_create_false_incident(monkeypatch):
    from sigma_eng import probe
    async def scenario():
        store = Store()
        release = threading.Event()
        def blocked_resolution(*args, **kwargs):
            release.wait(3)
            raise TargetNotAllowed()
        monkeypatch.setattr(probe, "resolve_target", blocked_resolution)
        scheduler = Scheduler(store, concurrency=1, refresh=0.05, seed=1)
        scheduler.start()
        try:
            await asyncio.sleep(0.25)
            assert scheduler.metrics.timeouts == 1
            assert not store.results
        finally:
            await scheduler.stop()
            release.set()
        await asyncio.sleep(0.03)
    asyncio.run(scenario())


def test_persistence_failure_is_visible_as_lost_sample():
    async def scenario():
        class BrokenStore(Store):
            def record_measurement(self,*args,**kwargs):
                raise RuntimeError("synthetic database error")
        scheduler=Scheduler(BrokenStore(), refresh=0.05,
            probe_fn=lambda *a,**k: ProbeResult(status="up",latency_ms=1),seed=1)
        scheduler.start()
        await asyncio.sleep(0.2)
        await scheduler.stop()
        assert scheduler.metrics.errors > 0
        assert scheduler.metrics.missed == scheduler.metrics.errors
        assert scheduler.metrics.completed == 0
    asyncio.run(scenario())


def test_shutdown_finishes_started_write_before_releasing_leadership():
    async def scenario():
        writing, release, committed = threading.Event(), threading.Event(), threading.Event()
        class SlowStore(Store):
            def record_measurement(self,*args,**kwargs):
                writing.set()
                release.wait(3)
                committed.set()
        class Lease:
            released=False
            def acquire(self):
                return True
            def release(self):
                assert committed.is_set()
                self.released=True
        lease=Lease()
        store=SlowStore()
        store.targets[0]["timeout_s"]=1
        scheduler=Scheduler(store,concurrency=1,refresh=0.05,lease=lease,seed=1,
            probe_fn=lambda *a,**k: ProbeResult(status="up",latency_ms=1))
        scheduler.random.uniform=lambda low,high: low
        scheduler.start()
        for _ in range(500):
            if writing.is_set():
                break
            await asyncio.sleep(0.01)
        assert writing.is_set(), scheduler.status()
        stopping=asyncio.create_task(scheduler.stop())
        try:
            await asyncio.sleep(0.05)
            assert not stopping.done() and not lease.released
        finally:
            release.set()
            await stopping
        assert lease.released
    asyncio.run(scenario())


@pytest.mark.parametrize("status,expected", [(503,False),(200,True),(None,False)])
def test_http_health_distinguishes_error_from_security_finding(status,expected):
    async def scenario():
        store=Store()
        store.targets[0].update(kind="http",timeout_s=1)
        scheduler=Scheduler(store,refresh=0.05,seed=1,
            probe_fn=lambda *a,**k: ProbeResult(status="degraded",latency_ms=1,http_status=status))
        try:
            # Classificação de uma coleta, sem depender da fase do relógio periódico.
            await scheduler._collect(store.targets[0])
        finally:
            await scheduler.stop()
        assert store.results and store.results[0][0][1] is expected, scheduler.status()
    asyncio.run(scenario())
