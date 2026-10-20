"""Regressões de escritores independentes e leitores duradouros."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sigma_eng.audit_chain import AuditChain
from sigma_eng.api import create_router


def test_preloaded_writers_continue_current_chain(tmp_path):
    path = tmp_path / "audit.jsonl"
    a, b = AuditChain(path, chave=b"test"), AuditChain(path, chave=b"test")
    a.registrar("a", "login")
    b.registrar("b", "logout")
    assert a.resumo() == {"integra": True, "primeira_invalida": None, "entradas": 2}


def test_independent_processes_share_chain(tmp_path):
    path = tmp_path / "audit.jsonl"
    script = """
import sys
from sigma_eng.audit_chain import AuditChain
c = AuditChain(sys.argv[1], chave=b'test')
for i in range(25): c.registrar(sys.argv[2], 'event', detalhes={'i': i})
"""
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    processes = [subprocess.Popen([sys.executable, "-c", script, str(path), str(i)], env=env)
                 for i in range(4)]
    try:
        for process in processes:
            assert process.wait(timeout=30) == 0
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
            process.wait()
    audit = AuditChain(path, chave=b"test")
    assert audit.resumo() == {"integra": True, "primeira_invalida": None, "entradas": 100}
    assert len({(row['ator'], row['detalhes']['i']) for row in audit.entradas}) == 100


def test_endpoint_reads_new_events_and_tampering(tmp_path):
    path = tmp_path / "audit.jsonl"
    app = FastAPI()
    app.include_router(create_router(lambda role: lambda: None, auditoria=AuditChain(path)))
    writer = AuditChain(path)
    with TestClient(app) as client:
        writer.registrar("synthetic", "auth.login.success")
        assert client.get('/api/eng/auditoria/verificar').json() == {
            'integra': True, 'primeira_invalida': None, 'entradas': 1}
        rows = path.read_text(encoding='utf-8').splitlines()
        row = json.loads(rows[0]); row['ator'] = 'changed'
        path.write_text(json.dumps(row) + '\n', encoding='utf-8')
        assert client.get('/api/eng/auditoria/verificar').json() == {
            'integra': False, 'primeira_invalida': 0, 'entradas': 1}


def test_corruption_refuses_append_and_releases_lock(tmp_path):
    path = tmp_path / 'audit.jsonl'
    audit = AuditChain(path)
    path.write_text('{broken\n', encoding='utf-8')
    with pytest.raises(ValueError, match='inválida'):
        audit.registrar('a', 'event')
    assert path.read_text(encoding='utf-8') == '{broken\n'
    path.write_text('', encoding='utf-8')
    AuditChain(path).registrar('b', 'repaired')
    assert audit.verificar() == (True, None)


def test_busy_file_times_out_without_writing_and_can_retry(tmp_path, monkeypatch):
    from sigma_eng import audit_chain
    path = tmp_path / 'audit.jsonl'
    first, second = AuditChain(path), AuditChain(path)
    monkeypatch.setattr(audit_chain, 'LOCK_TIMEOUT_SECONDS', 0)
    with first._coordenar():
        with pytest.raises(TimeoutError, match='ocupada'):
            second.registrar('test', 'blocked')
        assert not path.exists()
    second.registrar('test', 'retry')
    assert first.resumo() == {'integra': True, 'primeira_invalida': None, 'entradas': 1}


def test_complete_last_record_without_newline_is_not_concatenated(tmp_path):
    path = tmp_path / 'audit.jsonl'
    audit = AuditChain(path)
    audit.registrar('test', 'first')
    path.write_bytes(path.read_bytes().rstrip(b'\r\n'))
    audit.registrar('test', 'second')
    assert audit.resumo() == {'integra': True, 'primeira_invalida': None, 'entradas': 2}


def test_non_ascii_hash_is_invalid_instead_of_crashing(tmp_path):
    path = tmp_path / 'audit.jsonl'
    audit = AuditChain(path)
    row = audit.registrar('test', 'first')
    row['hash'] = '\u2603'
    path.write_text(json.dumps(row) + '\n', encoding='utf-8')
    assert audit.verificar() == (False, 0)
