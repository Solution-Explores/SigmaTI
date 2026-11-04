"""Custo da trilha de auditoria (#46): cache do estado verificado sem perder a recusa após adulteração."""
import os
import time

import pytest

from sigma_eng import audit_chain
from sigma_eng.audit_chain import AuditChain, GENESIS

CHAVE = b"chave-de-teste-incremental"


@pytest.fixture(autouse=True)
def cache_limpo():
    audit_chain._ESTADOS.clear()
    yield
    audit_chain._ESTADOS.clear()


def _cadeia(caminho, **kwargs):
    kwargs.setdefault("chave", CHAVE)
    return AuditChain(caminho, **kwargs)


def _povoar(caminho, n):
    cadeia = _cadeia(caminho)
    for i in range(n):
        cadeia.registrar("teste", "evento", f"r{i}")
    return cadeia


def _conta_assinaturas(monkeypatch):
    chamadas = []
    original = AuditChain._assinar

    def contar(chave, corpo):
        chamadas.append(corpo.get("seq"))
        return original(chave, corpo)

    monkeypatch.setattr(AuditChain, "_assinar", staticmethod(contar))
    return chamadas


def test_instancia_nova_nao_recalcula_o_historico(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 50)
    chamadas = _conta_assinaturas(monkeypatch)
    entrada = _cadeia(caminho).registrar("login", "auth.login")  # uma instância por login
    assert entrada["seq"] == 50
    assert chamadas == [50]  # só a assinatura da entrada nova, nenhuma das 50 anteriores
    assert _cadeia(caminho).verificar() == (True, None)


def test_estado_vale_entre_instancias_e_depois_da_janela_de_escrita_recente(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 20)
    # Como se a última escrita fosse antiga: o timestamp do arquivo passa a valer sem reler os bytes.
    monkeypatch.setattr(audit_chain, "_agora_ns", lambda: time.time_ns() + 10 * audit_chain.JANELA_TIMESTAMP_NS)
    _cadeia(caminho).registrar("a", "b")
    chamadas = _conta_assinaturas(monkeypatch)
    assert len(_cadeia(caminho)) == 21
    assert _cadeia(caminho).ancora()["entradas"] == 21
    assert chamadas == []


def _adulterar_mantendo_tamanho_e_timestamp(caminho):
    antes = caminho.stat()
    dados = caminho.read_bytes()
    assert b'"r3"' in dados
    caminho.write_bytes(dados.replace(b'"r3"', b'"x3"', 1))  # mesmo tamanho, entrada 3 alterada
    os.utime(caminho, ns=(antes.st_atime_ns, antes.st_mtime_ns))
    return antes


def test_adulteracao_logo_apos_a_escrita_com_timestamp_restaurado_bloqueia_a_gravacao(tmp_path, monkeypatch):
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 10)
    antes = _adulterar_mantendo_tamanho_e_timestamp(caminho)
    # Escrita recente (dentro da janela): o timestamp não vale e os bytes são reconferidos.
    monkeypatch.setattr(audit_chain, "_agora_ns", lambda: antes.st_mtime_ns + 1_000_000)
    with pytest.raises(ValueError, match="gravação recusada"):
        cadeia.registrar("a", "b")
    assert _cadeia(caminho).verificar() == (False, 3)


def test_limite_documentado_timestamp_restaurado_depois_da_janela_so_a_verificacao_completa_pega(tmp_path, monkeypatch):
    """Fora da janela e antes da reconferência periódica, o registrar confia no timestamp.

    verificar() e resumo() (API e job diário) percorrem tudo e acusam a adulteração; e a
    reconferência dos bytes a cada REVALIDAR_CONTEUDO_SEGUNDOS fecha a brecha para o registrar.
    """
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 10)
    cadeia.registrar("a", "b")
    antes = _adulterar_mantendo_tamanho_e_timestamp(caminho)
    monkeypatch.setattr(audit_chain, "_agora_ns", lambda: antes.st_mtime_ns + 10 * audit_chain.JANELA_TIMESTAMP_NS)
    cadeia.registrar("a", "passou")  # a brecha: ainda confia no estado em memória
    assert _cadeia(caminho).verificar()[0] is False  # mas a verificação completa a acusa
    monkeypatch.setattr(audit_chain, "REVALIDAR_CONTEUDO_SEGUNDOS", 0)
    with pytest.raises(ValueError, match="gravação recusada"):
        cadeia.registrar("a", "bloqueada")


def test_adulteracao_com_reconferencia_obrigatoria_tambem_bloqueia(tmp_path, monkeypatch):
    """Sem a janela de escrita recente, o que vale é a reconferência periódica dos bytes."""
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 10)
    cadeia.registrar("a", "b")
    monkeypatch.setattr(audit_chain, "REVALIDAR_CONTEUDO_SEGUNDOS", 0)
    antes = caminho.stat()
    caminho.write_bytes(caminho.read_bytes().replace(b'"r5"', b'"y5"', 1))
    os.utime(caminho, ns=(antes.st_atime_ns, antes.st_mtime_ns))
    with pytest.raises(ValueError, match="gravação recusada"):
        cadeia.registrar("a", "b")


def test_remover_ou_reordenar_entradas_bloqueia_a_gravacao(tmp_path):
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 6)
    linhas = caminho.read_bytes().splitlines(keepends=True)
    caminho.write_bytes(b"".join([linhas[0], linhas[2], linhas[1], *linhas[3:]]))
    with pytest.raises(ValueError):
        cadeia.registrar("a", "b")
    caminho.write_bytes(b"".join(linhas[:2] + linhas[3:]))  # removeu a de índice 2
    with pytest.raises(ValueError):
        _cadeia(caminho).registrar("a", "b")


def test_outra_instancia_anexando_continua_a_cadeia(tmp_path):
    caminho = tmp_path / "a.jsonl"
    primeira = _povoar(caminho, 5)
    for _ in range(3):
        _cadeia(caminho).registrar("outro", "processo")
    entrada = primeira.registrar("eu", "depois")
    assert entrada["seq"] == 8
    assert primeira.verificar() == (True, None)
    assert [e["seq"] for e in _cadeia(caminho).entradas] == list(range(9))


def test_acrescimo_invalido_por_fora_e_recusado(tmp_path):
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 4)
    with caminho.open("ab") as fh:
        fh.write(b'{"seq":4,"anterior":"errado","hash":"x"}\n')
    with pytest.raises(ValueError):
        cadeia.registrar("a", "b")


def test_outra_chave_nao_aproveita_o_estado_alheio(tmp_path):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 3)
    with pytest.raises(ValueError):
        AuditChain(caminho, chave=b"outra-chave").registrar("a", "b")
    assert _cadeia(caminho).registrar("a", "b")["seq"] == 3


def test_arquivo_trocado_por_outro_e_reverificado(tmp_path):
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 5)
    outro = tmp_path / "b.jsonl"
    _povoar(outro, 2)
    os.replace(outro, caminho)  # outro arquivo no mesmo caminho
    entrada = cadeia.registrar("a", "b")
    assert entrada["seq"] == 2 and cadeia.verificar() == (True, None)


def test_encolher_para_um_prefixo_valido_segue_o_comportamento_anterior(tmp_path):
    """A cadeia sozinha não vê remoção do fim; quem vê é a âncora externa (ver audit_anchor)."""
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 6)
    linhas = caminho.read_bytes().splitlines(keepends=True)
    caminho.write_bytes(b"".join(linhas[:3]))
    assert cadeia.registrar("a", "b")["seq"] == 3
    assert cadeia.verificar() == (True, None)


def test_arquivo_sem_quebra_de_linha_final_continua_valido(tmp_path):
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 3)
    caminho.write_bytes(caminho.read_bytes().rstrip(b"\n"))
    assert cadeia.registrar("a", "b")["seq"] == 3
    assert _cadeia(caminho).verificar() == (True, None)
    assert _cadeia(caminho).registrar("a", "c")["seq"] == 4


def test_ancora_e_len_continuam_lendo_trilha_adulterada(tmp_path):
    caminho = tmp_path / "a.jsonl"
    _povoar(caminho, 4)
    caminho.write_bytes(caminho.read_bytes().replace(b'"r1"', b'"z1"', 1))
    cadeia = _cadeia(caminho)
    assert len(cadeia) == 4
    ancora = cadeia.ancora()
    assert ancora["entradas"] == 4 and ancora["ultimo_hash"] != GENESIS
    assert cadeia.resumo() == {"integra": False, "primeira_invalida": 1, "entradas": 4}


def test_ancora_traz_o_kid_da_ultima_entrada_depois_da_rotacao(tmp_path):
    caminho = tmp_path / "a.jsonl"
    cadeia = AuditChain(caminho, chaves={"k1": b"um"}, chave_ativa="k1")
    cadeia.registrar("a", "b")
    cadeia.rotacionar("k2", b"dois", "admin")
    cadeia.registrar("a", "c")
    outra = AuditChain(caminho, chaves={"k1": b"um", "k2": b"dois"}, chave_ativa="k2")
    assert outra.ancora()["kid"] == "k2" and outra.ancora()["entradas"] == 3
    assert outra.verificar() == (True, None)


def test_trilha_em_memoria_nao_muda(tmp_path):
    cadeia = AuditChain(chave=CHAVE)
    cadeia.registrar("a", "b")
    cadeia.registrar("a", "c")
    assert cadeia.verificar() == (True, None) and len(cadeia) == 2
    cadeia._entradas[0]["ator"] = "x"
    with pytest.raises(ValueError):
        cadeia.registrar("a", "d")


def test_resumo_e_verificar_sao_completos_mesmo_com_estado_em_cache(tmp_path):
    caminho = tmp_path / "a.jsonl"
    cadeia = _povoar(caminho, 5)
    cadeia.registrar("a", "b")
    time.sleep(0.01)
    caminho.write_bytes(caminho.read_bytes().replace(b'"r2"', b'"w2"', 1))
    assert cadeia.verificar() == (False, 2)
    assert cadeia.resumo()["integra"] is False
