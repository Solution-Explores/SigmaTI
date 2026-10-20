"""Regressão #14: DNS controlado nunca altera o destino da conexão."""
import socket

import pytest

from sigma_eng import probe


def answer(ip):
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    return (family, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (ip, 0))


class Wire:
    def __init__(self):
        self.request = b""
        self.closed = False
        self.response = b"HTTP/1.0 200 OK\r\nContent-Security-Policy: default-src 'none'\r\nStrict-Transport-Security: max-age=1\r\n\r\n"

    def sendall(self, data):
        self.request += data

    def settimeout(self, value):
        pass

    def recv(self, size):
        data, self.response = self.response, b""
        return data

    def getpeercert(self, binary_form=False):
        return b""

    def close(self):
        self.closed = True


@pytest.mark.parametrize("kind", ["tcp", "http", "https"])
def test_alternating_dns_never_connects_to_second_answer(monkeypatch, kind):
    resolutions, connections, wires, sni = [], [], [], []

    def dns(*args, **kwargs):
        resolutions.append(args[0])
        return [answer("127.0.0.1" if len(resolutions) == 1 else "8.8.8.8")]

    def connect(address, **kwargs):
        connections.append(address)
        wire = Wire()
        wires.append(wire)
        return wire

    class TLS:
        def __init__(self, *args):
            pass

        def wrap_socket(self, sock, *, server_hostname):
            sni.append(server_hostname)
            return sock

    monkeypatch.setattr(socket, "getaddrinfo", dns)
    monkeypatch.setattr(probe.ssl, "SSLContext", TLS)
    stats = probe.probe_many("servico.hospital.test", 8443, kind, count=3, connector=connect)
    assert stats.failures == 0
    assert resolutions == ["servico.hospital.test"]
    assert connections == [("127.0.0.1", 8443)] * 3
    assert all(w.closed for w in wires)
    if kind != "tcp":
        assert all(b"Host: servico.hospital.test:8443\r\n" in w.request for w in wires)
    assert sni == (["servico.hospital.test"] * 3 if kind == "https" else [])
    # Uma operação posterior com resposta externa é recusada antes de conectar.
    with pytest.raises(probe.TargetNotAllowed):
        probe.probe_many("servico.hospital.test", 8443, kind, connector=connect)
    assert len(connections) == 3


@pytest.mark.parametrize("addresses", [["127.0.0.1", "8.8.8.8"], [], ["::ffff:8.8.8.8"]])
def test_mixed_empty_and_mapped_public_answers_fail_closed(monkeypatch, addresses):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [answer(ip) for ip in addresses])
    def forbidden(*args, **kwargs):
        pytest.fail("destino recusado chegou ao conector")
    with pytest.raises(probe.TargetNotAllowed):
        probe.probe_service("hospital.test", 80, "http", connector=forbidden)


@pytest.mark.parametrize("host", ["hospital.test\r\nX-Test: yes", "http://hospital.test", "hospital.test/path", "nome com espaco", "::1%1"])
def test_invalid_authority_rejected_without_network(monkeypatch, host):
    def forbidden(*args, **kwargs):
        pytest.fail("entrada inválida chegou à rede")
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    with pytest.raises(probe.TargetNotAllowed):
        probe.probe_service(host, 80, "http", connector=forbidden)


@pytest.mark.parametrize("ip, family, expected", [
    ("127.0.0.1", socket.AF_INET, ("127.0.0.1", 8080)),
    ("::1", socket.AF_INET6, ("::1", 8080, 0, 0)),
])
def test_numeric_socket_path_has_no_second_resolver(monkeypatch, ip, family, expected):
    wire = Wire()
    connected = []
    def forbidden(*args, **kwargs):
        pytest.fail("socket numérico consultou DNS")
    def factory(actual_family, kind):
        assert (actual_family, kind) == (family, socket.SOCK_STREAM)
        wire.connect = connected.append
        return wire
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket, "socket", factory)
    assert probe.probe_service(ip, 8080, "http").status == "up"
    assert connected == [expected]
    authority = "[::1]" if family == socket.AF_INET6 else ip
    assert f"Host: {authority}:8080\r\n".encode() in wire.request


def test_dns_failure_is_policy_failure(monkeypatch):
    def failed(*args, **kwargs):
        raise socket.gaierror("private resolver detail")
    monkeypatch.setattr(socket, "getaddrinfo", failed)
    assert not probe.is_target_allowed("hospital.test")
    with pytest.raises(probe.TargetNotAllowed, match="alvo"):
        probe.probe_many("hospital.test", 80)


def test_real_http_uses_pinned_ip_and_does_not_follow_redirect(monkeypatch):
    import threading
    requests, errors, resolutions = [], [], []
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        server.settimeout(3)
        port = server.getsockname()[1]
        def serve():
            try:
                with server.accept()[0] as connection:
                    connection.settimeout(3)
                    requests.append(connection.recv(4096))
                    connection.sendall(b"HTTP/1.0 302 Found\r\nLocation: http://8.8.8.8/\r\n\r\n")
            except Exception as exc:
                errors.append(exc)
        worker = threading.Thread(target=serve)
        worker.start()
        def dns(*args, **kwargs):
            resolutions.append(args[0])
            return [answer("127.0.0.1" if len(resolutions) == 1 else "8.8.8.8")]
        monkeypatch.setattr(socket, "getaddrinfo", dns)
        try:
            result = probe.probe_service("hospital.test", port, "http", timeout=2)
        finally:
            worker.join(timeout=4)
        assert not worker.is_alive() and not errors
    assert result.http_status == 302
    assert resolutions == ["hospital.test"]
    assert f"Host: hospital.test:{port}\r\n".encode() in requests[0]
