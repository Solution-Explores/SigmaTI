"""Coleta assíncrona limitada; sem dependência de banco ou framework."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import partial
import random
import time
import threading

from . import probe


@dataclass
class SchedulerMetrics:
    started: int = 0
    completed: int = 0
    missed: int = 0
    missed_clock: int = 0
    missed_overlap: int = 0
    missed_capacity: int = 0
    capacity_deferrals: int = 0
    timeouts: int = 0
    errors: int = 0
    active: int = 0
    peak_active: int = 0
    max_lag_seconds: float = 0.0
    probe_finished: int = 0
    probe_seconds_total: float = 0.0
    max_probe_seconds: float = 0.0
    write_finished: int = 0
    write_seconds_total: float = 0.0
    max_write_seconds: float = 0.0


class Scheduler:
    """Sem fila de sondas: reserva no máximo concurrency trabalhos por vez.

    Timeout lógico não mata thread Python. A vaga permanece ocupada até a
    função retornar; resultado tardio é descartado e não dispara nova medição.
    Assim um DNS travado não multiplica threads nem tarefas pendentes.
    """
    def __init__(self, repository, *, concurrency=32, refresh=1.0,
                 allowed_networks=probe.DEFAULT_ALLOWED_NETWORKS, probe_fn=None,
                 lease=None, seed=None):
        if not 1 <= concurrency <= 128 or not 0.05 <= refresh <= 60:
            raise ValueError("limites inválidos")
        self.repository, self.concurrency, self.refresh = repository, concurrency, refresh
        self.allowed_networks = tuple(allowed_networks)
        self.probe_fn = probe_fn or probe.probe_service
        self.lease = lease
        self.random = random.Random(seed)
        self.metrics = SchedulerMetrics()
        self._stop = asyncio.Event()
        self._task = None
        self._refresh_task = None
        self._jobs = {}
        self._workers = set()
        self._writes = set()
        self._pending_batch = []
        self._batch_task = None
        self._due = {}
        self._capacity_deferred = set()
        self._executor = ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix="sigma-probe")
        # Não disputar as poucas threads padrão do event loop com auth/SSE/inventário.
        # Reserva até 12 persistências para o pool PostgreSQL padrão de 15 conexões.
        self._repository_executor = ThreadPoolExecutor(max_workers=min(concurrency, 12),
                                                       thread_name_prefix="sigma-persist")
        self.leader = False

    def status(self):
        return dict(asdict(self.metrics), leader=self.leader, queued=0,
                    pending_writes=len(self._writes))

    def start(self):
        if self._task is not None:
            raise RuntimeError("scheduler já iniciado")
        self._task = asyncio.create_task(self.run())

    async def stop(self):
        self._stop.set()
        if self._task is not None:
            await self._task
        for task in self._jobs.values():
            task.cancel()
        await asyncio.gather(*self._jobs.values(), return_exceptions=True)
        self._jobs.clear()
        if self._writes:
            await asyncio.gather(*list(self._writes), return_exceptions=True)
        if self._batch_task is not None:
            await self._batch_task
        if self._refresh_task is not None:
            await self._refresh_task
            self._refresh_task = None
        self.metrics.active = 0
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._repository_executor.shutdown(wait=False, cancel_futures=True)
        if self.lease is not None:
            await asyncio.to_thread(self.lease.release)
        self.leader = False

    def _worker_done(self, future, *, started):
        self._workers.discard(future)
        elapsed = time.monotonic() - started
        self.metrics.probe_finished += 1
        self.metrics.probe_seconds_total += elapsed
        self.metrics.max_probe_seconds = max(self.metrics.max_probe_seconds, elapsed)
        if not future.cancelled():
            # Consumir exceções tardias sem log automático de texto da rede.
            future.exception()

    def _write_done(self, future, *, started):
        self._writes.discard(future)
        elapsed = time.monotonic() - started
        self.metrics.write_finished += 1
        self.metrics.write_seconds_total += elapsed
        self.metrics.max_write_seconds = max(self.metrics.max_write_seconds, elapsed)
        if not future.cancelled():
            future.exception()

    async def _flush_batch(self):
        loop = asyncio.get_running_loop()
        # Coalesce as conclusões já prontas sem acrescentar prazo artificial.
        # Novas chegadas se agrupam naturalmente enquanto o commit está em curso.
        await asyncio.sleep(0)
        while self._pending_batch:
            batch = self._pending_batch[:32]
            del self._pending_batch[:32]
            try:
                results = await loop.run_in_executor(self._repository_executor,
                    self.repository.record_measurements, [row for _, row in batch])
                if len(results) != len(batch):
                    raise RuntimeError('resultado de lote inválido')
            except Exception as exc:
                for future, _ in batch:
                    if not future.done():
                        future.set_exception(exc)
            else:
                for (future, _), result in zip(batch, results):
                    if not future.done():
                        future.set_result(result)

    def _submit_write(self, target, available, latency):
        loop = asyncio.get_running_loop()
        if callable(getattr(self.repository, 'record_measurements', None)):
            future = loop.create_future()
            self._pending_batch.append((future, dict(target_id=target['id'], success=available,
                latency_ms=latency, ts=datetime.now(timezone.utc), detector_kind=target['detector'])))
            if self._batch_task is None or self._batch_task.done():
                self._batch_task = asyncio.create_task(self._flush_batch())
            return future
        return loop.run_in_executor(self._repository_executor, partial(
            self.repository.record_measurement, target['id'], available, latency,
            ts=datetime.now(timezone.utc), detector_kind=target['detector']))

    async def _collect(self, target):
        timeout = target["timeout_s"]
        loop = asyncio.get_running_loop()
        validated = threading.Event()
        def execute():
            ip = probe.resolve_target(target["host"], self.allowed_networks)
            validated.set()
            return self.probe_fn(target["host"], target["porta"], target["kind"],
                timeout=timeout, resolved_ip=ip, allowed_networks=self.allowed_networks)
        probe_started = time.monotonic()
        future = loop.run_in_executor(self._executor, execute)
        self._workers.add(future)
        future.add_done_callback(partial(self._worker_done, started=probe_started))
        timed_out = False
        try:
            try:
                result = await asyncio.wait_for(asyncio.shield(future), timeout)
            except TimeoutError:
                timed_out = True
                self.metrics.timeouts += 1
                if not validated.is_set():
                    # DNS ainda sem decisão de política: não inventar disponibilidade.
                    self.metrics.missed += 1
                    self.metrics.errors += 1
                    return
                result = probe.ProbeResult(status="down")
            except probe.TargetNotAllowed:
                # Uma política recusada não é diagnóstico de indisponibilidade.
                self.metrics.missed += 1
                self.metrics.errors += 1
                return
            if self.lease is not None and not self.leader:
                self.metrics.missed += 1
                return
            available = result.status != "down" and (target["kind"] == "tcp" or
                result.http_status is not None and 200 <= result.http_status < 500)
            write_started = time.monotonic()
            write = self._submit_write(target, available, result.latency_ms)
            self._writes.add(write)
            write.add_done_callback(partial(self._write_done, started=write_started))
            await asyncio.shield(write)
            self.metrics.completed += 1
        except asyncio.CancelledError:
            raise
        except Exception:
            # Nunca registrar hostname, saída da sonda, credenciais ou texto de exceção.
            self.metrics.errors += 1
            self.metrics.missed += 1
        finally:
            if timed_out and not asyncio.current_task().cancelling():
                try:
                    await asyncio.shield(future)
                except (Exception, asyncio.CancelledError):
                    pass

    async def _load_targets(self):
        try:
            leader = self.lease is None or await asyncio.to_thread(self.lease.acquire)
            targets = await asyncio.to_thread(self.repository.collection_targets) if leader else []
            return leader, targets
        except Exception:
            self.metrics.errors += 1
            return False, []

    async def run(self):
        targets = []
        refresh_at = 0.0
        try:
            while not self._stop.is_set():
                now = time.monotonic()
                for identifier, task in list(self._jobs.items()):
                    if task.done():
                        if not task.cancelled():
                            task.result()
                        del self._jobs[identifier]
                self.metrics.active = len(self._jobs)
                # Atualização de inventário/liderança nunca bloqueia o relógio de coleta.
                if self._refresh_task is not None and self._refresh_task.done():
                    self.leader, targets = self._refresh_task.result()
                    self._refresh_task = None
                    refresh_at = now + self.refresh
                    # Sem liderança, targets fica vazio. Manter trabalhos em andamento
                    # reservados até terminarem evita acumular writes em cada failover.
                    identifiers = {t["id"] for t in targets}
                    self._due = {key: value for key, value in self._due.items() if key in identifiers}
                    self._capacity_deferred.intersection_update(identifiers)
                    for target in targets:
                        self._due.setdefault(target["id"], now + self.random.uniform(0, target["intervalo_s"]))
                if now >= refresh_at and self._refresh_task is None:
                    self._refresh_task = asyncio.create_task(self._load_targets())
                now = time.monotonic()
                # Mais antigo primeiro evita que a ordem do cadastro provoque fome.
                for target in sorted(targets, key=lambda t: self._due[t["id"]]):
                    identifier = target["id"]
                    due = self._due[identifier]
                    if now < due:
                        continue
                    interval = target["intervalo_s"]
                    self.metrics.max_lag_seconds = max(self.metrics.max_lag_seconds, now - due)
                    # Descartar atrasos; nunca enfileirar ciclos de recuperação.
                    skipped = int((now - due) // interval)
                    self.metrics.missed += skipped
                    if skipped:
                        self._due[identifier] = due + skipped * interval
                        if identifier in self._capacity_deferred:
                            self.metrics.missed_capacity += skipped
                        else:
                            self.metrics.missed_clock += skipped
                    if identifier in self._jobs:
                        self.metrics.missed += 1
                        self.metrics.missed_overlap += 1
                        self._due[identifier] = now + interval * self.random.uniform(0.9, 1.1)
                        self._capacity_deferred.discard(identifier)
                        continue
                    if len(self._jobs) >= self.concurrency or len(self._workers) >= self.concurrency:
                        # Manter apenas a próxima oportunidade no calendário.
                        # Não submeter/enfileirar sonda nem descartar um período
                        # inteiro por uma indisponibilidade momentânea de vaga.
                        self._capacity_deferred.add(identifier)
                        self.metrics.capacity_deferrals += 1
                        continue
                    self._due[identifier] = now + interval * self.random.uniform(0.9, 1.1)
                    self._capacity_deferred.discard(identifier)
                    self._jobs[identifier] = asyncio.create_task(self._collect(target))
                    self.metrics.started += 1
                    self.metrics.active = len(self._jobs)
                    self.metrics.peak_active = max(self.metrics.peak_active, len(self._jobs))
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=0.01)
                except TimeoutError:
                    pass
        finally:
            self.leader = False
