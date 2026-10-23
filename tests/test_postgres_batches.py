"""Lotes preservam os contratos transacionais da ingestão individual."""
from datetime import datetime, timezone, timedelta
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from persistence.operational import PostgresOperationalStore
from sigma_eng.state import StateConflict


def samples(store, count=4, success=True):
    return [dict(target_id=store.create_target('synthetic-batch', '127.0.0.1', 1234)['id'],
        success=success, latency_ms=1 if success else None, detector_kind='ewma',
        ts=datetime.now(timezone.utc), identifier=str(uuid.uuid4())) for _ in range(count)]


def test_batch_retries_do_not_duplicate_aggregates_or_detector(pg):
    store = PostgresOperationalStore(pg.engine)
    rows = samples(store)
    assert all(r['inserted'] for r in store.record_measurements(rows))
    assert all(not r['inserted'] for r in store.record_measurements(rows))
    for row in rows:
        assert len(store.measurements(row['target_id'])) == 1
        assert store.aggregates(row['target_id'], 'minute')[0]['total'] == 1
        assert store.get('detectors', row['target_id'])['versao'] == 1
    rows[0]['latency_ms'] = 2
    with pytest.raises(StateConflict):
        store.record_measurements(rows)


def test_batch_incidents_and_samples_rollback_together(pg, monkeypatch):
    store = PostgresOperationalStore(pg.engine)
    rows = samples(store, success=False)
    original = store._event
    def fail(*args, **kwargs):
        raise RuntimeError('synthetic')
    monkeypatch.setattr(store, '_event', fail)
    with pytest.raises(RuntimeError):
        store.record_measurements(rows)
    assert all(not store.measurements(r['target_id']) for r in rows)
    monkeypatch.setattr(store, '_event', original)
    first = store.record_measurements(rows)
    assert all(r['incident'] for r in first)
    retry = store.record_measurements(rows)
    assert [r['incident']['id'] for r in retry] == [r['incident']['id'] for r in first]


def test_batch_and_individual_detector_state_match(pg):
    store = PostgresOperationalStore(pg.engine)
    left, right = samples(store, 2)
    for kind in ('ewma', 'mad'):
        for latency in [10] * 8 + [900] * 6:
            left.update(identifier=str(uuid.uuid4()), detector_kind=kind, latency_ms=latency)
            right.update(identifier=str(uuid.uuid4()), detector_kind=kind, latency_ms=latency)
            store.record_measurements([left])
            store.record_measurement(**right)
            assert store.get('detectors', left['target_id']) == store.get('detectors', right['target_id'])
    active = store.incidents(True)
    assert sorted(i['tipo'] for i in active if i['alvo_id'] == left['target_id']) == sorted(
        i['tipo'] for i in active if i['alvo_id'] == right['target_id'])


def test_batch_rejects_unbounded_or_repeated_targets(pg):
    store = PostgresOperationalStore(pg.engine)
    row = samples(store, 1)[0]
    for batch in ([], [row] * 33, [row, dict(row, identifier=str(uuid.uuid4()))]):
        with pytest.raises(ValueError):
            store.record_measurements(batch)
    assert not store.measurements(row['target_id'])


def test_retry_batch_conflict_rolls_back_new_sample(pg):
    store = PostgresOperationalStore(pg.engine)
    existing, new = samples(store, 2)
    store.record_measurements([existing])
    invalid = dict(existing, latency_ms=99)
    with pytest.raises(StateConflict):
        store.record_measurements([new, invalid])
    assert not store.measurements(new['target_id'])
    assert store.aggregates(existing['target_id'], 'minute')[0]['total'] == 1


def test_overlapping_batches_preserve_detector_versions(pg):
    store = PostgresOperationalStore(pg.engine)
    rows = samples(store, 8)
    batches = [[dict(row, identifier=str(uuid.uuid4())) for row in (rows if i % 2 else rows[::-1])]
               for i in range(4)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(store.record_measurements, batches))
    assert all(all(r['inserted'] for r in result) for result in results)
    for row in rows:
        assert len(store.measurements(row['target_id'])) == 4
        assert store.aggregates(row['target_id'], 'minute')[0]['total'] == 4
        assert store.get('detectors', row['target_id'])['versao'] == 4


def test_mixed_results_numeric_types_and_months(pg):
    store = PostgresOperationalStore(pg.engine)
    rows = samples(store, 3)
    rows[0].update(success=False, latency_ms=None, ts=rows[0]['ts']-timedelta(days=40))
    rows[1]['latency_ms'] = 2.5
    rows[2]['latency_ms'] = 0
    results = store.record_measurements(rows)
    assert results[0]['incident']['tipo'] == 'availability'
    assert results[1]['incident'] is None
    for row in rows:
        saved = store.measurements(row['target_id'])[0]
        aggregate = store.aggregates(row['target_id'], 'minute')[0]
        assert saved['sucesso'] == row['success']
        assert aggregate['total'] == 1
        assert aggregate['latencia_n'] == int(row['latency_ms'] is not None)
