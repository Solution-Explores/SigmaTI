import socket
import threading

import pytest

from sigma_eng import probe
from sigma_eng.stats import percentile, summary


def test_percentile_interpolacao():
    assert percentile([1, 2, 3, 4], 50) == 2.5
    assert percentile([10], 99) == 10
    assert percentile(range(101), 95) == 95


def test_percentile_erros():
    with pytest.raises(ValueError):
        percentile([], 50)
    with pytest.raises(ValueError):
        percentile([1], 101)


def test_summary_vazio():
    assert summary([]) == {"n": 0}


def _servidor(resposta: bytes | None):
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)

    def loop():
        while True:
            try:
                conn, _ = srv.accept()
            except OSError:
                return
            if resposta is not None:
                conn.recv(1024)
                conn.sendall(resposta)
            conn.close()

    threading.Thread(target=loop, daemon=True).start()
    return srv, srv.getsockname()[1]


def test_probe_tcp_up():
    srv, port = _servidor(None)
    try:
        r = probe.probe_service("127.0.0.1", port, "tcp")
        assert r.status == "up" and r.latency_ms is not None
    finally:
        srv.close()


def test_probe_porta_fechada_down():
    srv, port = _servidor(None)
    srv.close()
    r = probe.probe_service("127.0.0.1", port, "tcp", timeout=0.5)
    assert r.status == "down" and r.findings[0]["code"] == "unreachable"


def test_probe_http_500_degradado():
    srv, port = _servidor(b"HTTP/1.0 503 Service Unavailable\r\n\r\n")
    try:
        r = probe.probe_service("127.0.0.1", port, "http")
        assert r.http_status == 503 and r.status == "degraded"
        assert any(f["code"] == "http_error" for f in r.findings)
    finally:
        srv.close()


def test_probe_http_200_com_csp_up():
    srv, port = _servidor(b"HTTP/1.0 200 OK\r\nContent-Security-Policy: default-src 'self'\r\n\r\nok")
    try:
        assert probe.probe_service("127.0.0.1", port, "http").status == "up"
    finally:
        srv.close()


def test_probe_validacao():
    with pytest.raises(ValueError):
        probe.probe_service("127.0.0.1", 80, "ftp")
    with pytest.raises(ValueError):
        probe.probe_service("127.0.0.1", 70000, "tcp")


def test_probe_many_perda_e_jitter():
    srv, port = _servidor(None)
    try:
        s = probe.probe_many("127.0.0.1", port, "tcp", count=10)
        assert s.samples == 10 and s.failures == 0 and s.loss_pct == 0
        assert s.latency["n"] == 10 and s.jitter_ms >= 0
    finally:
        srv.close()
    morto = probe.probe_many("127.0.0.1", port, "tcp", count=3, timeout=0.3)
    assert morto.loss_pct == 100 and morto.latency == {"n": 0}


def test_alvo_permitido():
    assert probe.is_target_allowed("127.0.0.1")
    assert probe.is_target_allowed("192.168.1.10", ["192.168.0.0/16"])
    assert not probe.is_target_allowed("8.8.8.8")
    assert not probe.is_target_allowed("host-que-nao-existe.invalid")
    assert not probe.is_target_allowed("127.0.0.1", ["10.0.0.0/8"])
