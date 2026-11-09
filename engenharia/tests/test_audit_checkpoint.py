"""Ponto de verificação assinado (#46, opção D): a partida fria não refaz o HMAC do histórico.

O ponto é só otimização. Toda dúvida (ausente, forjado, chave desconhecida, bytes diferentes,
arquivo menor) cai na verificação completa, que mantém a recusa de gravação após adulteração.
"""
import json

import pytest

from sigma_eng import audit_chain
from sigma_eng.audit_chain import AuditChain

CHAVE = b"chave-de-teste-checkpoint"
INTERVALO = 5


@pytest.fixture(autouse=True)
def ambiente(monkeypatch):
    audit_chain._ESTADOS.clear()
    monkeypatch.setattr(audit_chain, "CHECKPOINT_INTERVALO", INTERVALO)
    yield
    audit_chain._ESTADOS.clear()


def _cadeia(caminho, **kwargs):
    kwargs.setdefault("chave", CHAVE)
    return AuditChain(caminho, **kwargs)


def _povoar(caminho, n, **kwargs):
    cadeia = _cadeia(caminho, **kwargs)
    for i in range(n):
        cadeia.registrar("teste", "evento", f"r{i}")
    return cadeia


def _ponto(caminho):
    return caminho.with_name(caminho.name + audit_chain.CHECKPOINT_SUFIXO)


def _partida_fria():
    audit_chain._ESTADOS.clear()


def _conta_assinaturas(monkeypatch):
    chamadas = []
    original = AuditChain._assinar

    def contar(chave, corpo):
        chamadas.append(corpo.get("seq"))
        return original(chave, corpo)

    monkeypatch.setattr(AuditChain, "_assinar", staticmethod(contar))
    return chamadas


def test_ponto_e_gravado_a_cada_intervalo(tmp_path):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    cp = json.loads(_ponto(caminho).read_text(encoding="utf-8"))
    assert cp["contagem"] == 10  # gravado ao chegar em 5 e em 10
    assert cp["assinatura"] and cp["v"] == 1


def test_partida_fria_com_ponto_nao_refaz_o_hmac_do_historico(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    _partida_fria()
    chamadas = _conta_assinaturas(monkeypatch)
    entrada = _cadeia(caminho).registrar("login", "auth.login")
    assert entrada["seq"] == 12
    assert chamadas == [10, 11, 12]  # só o trecho depois do ponto e a entrada nova
    _partida_fria()
    assert _cadeia(caminho).verificar() == (True, None)


def test_sem_ponto_a_partida_fria_verifica_tudo(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    _ponto(caminho).unlink()
    _partida_fria()
    chamadas = _conta_assinaturas(monkeypatch)
    assert _cadeia(caminho).registrar("login", "auth.login")["seq"] == 12
    assert chamadas == list(range(13))


def test_adulterar_o_historico_invalida_o_ponto_e_bloqueia_a_gravacao(tmp_path):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    dados = caminho.read_bytes()
    assert b'"r3"' in dados
    caminho.write_bytes(dados.replace(b'"r3"', b'"x3"', 1))  # mesmo tamanho, entrada 3 alterada
    _partida_fria()
    with pytest.raises(ValueError):
        _cadeia(caminho).registrar("login", "auth.login")
    assert _cadeia(caminho).verificar() == (False, 3)


def test_ponto_forjado_sem_a_chave_e_ignorado(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    cp = json.loads(_ponto(caminho).read_text(encoding="utf-8"))
    cp["contagem"] = 11  # muda o conteúdo mantendo a assinatura antiga
    _ponto(caminho).write_text(json.dumps(cp), encoding="utf-8")
    _partida_fria()
    chamadas = _conta_assinaturas(monkeypatch)
    assert _cadeia(caminho).registrar("login", "auth.login")["seq"] == 12
    assert chamadas == list(range(13))  # caiu na verificação completa


def test_ponto_assinado_com_outra_chave_nao_vale(tmp_path):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    _partida_fria()
    with pytest.raises(ValueError):  # outra chave: a trilha inteira é inválida para ela
        _cadeia(caminho, chave=b"outra-chave").registrar("login", "auth.login")


def test_sem_chave_nao_grava_ponto(tmp_path):
    caminho = tmp_path / "a.jsonl"
    cadeia = AuditChain(caminho)  # SHA-256 simples: não há como autenticar o ponto
    for i in range(12):
        cadeia.registrar("teste", "evento", f"r{i}")
    assert not _ponto(caminho).exists()


def test_ponto_maior_que_o_arquivo_e_ignorado(tmp_path):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    linhas = caminho.read_bytes().splitlines(keepends=True)
    caminho.write_bytes(b"".join(linhas[:6]))  # prefixo válido, menor que o ponto (contagem 10)
    _partida_fria()
    assert _cadeia(caminho).registrar("login", "auth.login")["seq"] == 6


def test_ponto_antigo_com_acrescimo_valido_e_aceito_e_so_o_acrescimo_e_verificado(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    antigo = _ponto(caminho).read_bytes()  # contagem 10
    cadeia = _cadeia(caminho)
    for i in range(20):
        cadeia.registrar("teste", "evento", f"s{i}")
    _ponto(caminho).write_bytes(antigo)  # volta para o ponto antigo (válido, só mais curto)
    _partida_fria()
    chamadas = _conta_assinaturas(monkeypatch)
    assert _cadeia(caminho).registrar("login", "auth.login")["seq"] == 32
    assert min(chamadas) == 10
    _partida_fria()
    assert _cadeia(caminho).verificar() == (True, None)


def test_acrescimo_invalido_depois_do_ponto_e_recusado(tmp_path):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    with caminho.open("ab") as fh:
        fh.write(b'{"seq":12,"anterior":"x","hash":"y"}\n')
    _partida_fria()
    with pytest.raises(ValueError):
        _cadeia(caminho).registrar("login", "auth.login")


def test_ponto_corrompido_e_ignorado(tmp_path):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    _ponto(caminho).write_bytes(b"\xff\xfe nao e json")
    _partida_fria()
    assert _cadeia(caminho).registrar("login", "auth.login")["seq"] == 12


def test_rotacao_de_chave_o_ponto_segue_a_chave_ativa(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    a, b = b"chave-a", b"chave-b"
    cadeia = AuditChain(caminho, chaves={"k1": a}, chave_ativa="k1")
    for i in range(8):
        cadeia.registrar("teste", "evento", f"r{i}")
    cadeia.rotacionar("k2", b, "adm")
    for i in range(8):
        cadeia.registrar("teste", "evento", f"t{i}")
    assert json.loads(_ponto(caminho).read_text(encoding="utf-8"))["kid"] == "k2"
    _partida_fria()
    chamadas = _conta_assinaturas(monkeypatch)
    nova = AuditChain(caminho, chaves={"k1": a, "k2": b}, chave_ativa="k2")
    assert nova.registrar("login", "auth.login")["seq"] == 17
    assert len(chamadas) < 17  # não refez o histórico inteiro
    # sem a chave k2 configurada o ponto não é aceito: verificação completa (e aqui, trilha inválida)
    _partida_fria()
    with pytest.raises(ValueError):
        AuditChain(caminho, chaves={"k1": a}, chave_ativa="k1").registrar("x", "y")


def test_verificar_completo_continua_percorrendo_tudo_com_ponto(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 12)
    chamadas = _conta_assinaturas(monkeypatch)
    assert _cadeia(caminho).verificar() == (True, None)
    assert chamadas == list(range(12))
