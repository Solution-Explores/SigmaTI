"""Issue #13: rotação de chave com key id, âncora externa e verificação agendada."""
import json
from datetime import datetime, timezone

import pytest
from sigma_eng.audit_anchor import (
    AncoraArquivo,
    AncoraWebhook,
    ResultadoVerificacao,
    executar_verificacao,
    verificar_contra_ancora,
)
from sigma_eng.audit_chain import AuditChain, chaves_do_ambiente


def _cadeia(tmp_path, **kw):
    return AuditChain(tmp_path / "audit.jsonl", **kw)


def _preencher(chain, n=3):
    for i in range(n):
        chain.registrar("op", "acao", detalhes={"i": i})


# --- Âncora: remoção total do arquivo ---------------------------------------

def test_remocao_total_do_arquivo_e_detectada_pela_ancora(tmp_path):
    chain = _cadeia(tmp_path, chave=b"k")
    _preencher(chain)
    ancora = AncoraArquivo(tmp_path / "ancora" / "ancoras.jsonl")
    ancora.publicar(chain.ancora())
    (tmp_path / "audit.jsonl").unlink()
    recomecada = _cadeia(tmp_path, chave=b"k")
    recomecada.registrar("atacante", "inicio")
    assert recomecada.verificar() == (True, None)  # sozinha, a cadeia nova parece íntegra
    ok, motivo = verificar_contra_ancora(recomecada, ancora.ultima())
    assert ok is False and motivo == "cadeia_menor_que_ancora"


def test_truncamento_da_cauda_e_detectado(tmp_path):
    chain = _cadeia(tmp_path, chave=b"k")
    _preencher(chain, 4)
    ancora = chain.ancora()
    linhas = (tmp_path / "audit.jsonl").read_bytes().splitlines(keepends=True)
    (tmp_path / "audit.jsonl").write_bytes(b"".join(linhas[:2]))
    ok, motivo = verificar_contra_ancora(_cadeia(tmp_path, chave=b"k"), ancora)
    assert ok is False and motivo == "cadeia_menor_que_ancora"


def test_reescrita_com_mesma_quantidade_e_detectada(tmp_path):
    chain = _cadeia(tmp_path)  # sem chave: o atacante refaz todos os hashes
    _preencher(chain, 3)
    ancora = chain.ancora()
    (tmp_path / "audit.jsonl").unlink()
    forjada = _cadeia(tmp_path)
    _preencher(forjada, 3)
    assert forjada.verificar() == (True, None)
    assert verificar_contra_ancora(forjada, ancora) == (False, "hash_diferente_da_ancora")


def test_cadeia_maior_que_a_ancora_continua_valida(tmp_path):
    chain = _cadeia(tmp_path, chave=b"k")
    _preencher(chain, 2)
    ancora = chain.ancora()
    _preencher(chain, 2)
    assert verificar_contra_ancora(chain, ancora) == (True, None)


def test_sem_ancora_previa_nao_bloqueia_primeira_execucao(tmp_path):
    assert verificar_contra_ancora(_cadeia(tmp_path), None) == (True, None)


def test_ancora_de_cadeia_vazia_e_aceita(tmp_path):
    chain = _cadeia(tmp_path)
    ancora = chain.ancora()
    assert ancora["entradas"] == 0
    assert verificar_contra_ancora(chain, ancora) == (True, None)


def test_ancora_nao_contem_dados_pessoais(tmp_path):
    chain = _cadeia(tmp_path)
    chain.registrar("maria.analista", "login", detalhes={"ip": "10.0.0.5"})
    texto = json.dumps(chain.ancora())
    assert "maria" not in texto and "10.0.0.5" not in texto
    assert set(chain.ancora()) == {"entradas", "ultimo_hash", "ts", "kid"}


# --- Rotação de chave -------------------------------------------------------

def test_rotacao_preserva_historico_verificavel(tmp_path):
    chain = _cadeia(tmp_path, chaves={"k1": b"chave-antiga"}, chave_ativa="k1")
    _preencher(chain, 2)
    chain.rotacionar("k2", b"chave-nova", ator="gestor")
    _preencher(chain, 2)
    # Nova instância com as duas chaves verifica o segmento antigo e o novo.
    outra = _cadeia(tmp_path, chaves={"k1": b"chave-antiga", "k2": b"chave-nova"}, chave_ativa="k2")
    assert outra.verificar() == (True, None)
    assert [e.get("kid") for e in outra.entradas] == ["k1", "k1", "k1", "k2", "k2"]
    assert outra.entradas[2]["acao"] == "audit.key_rotated"


def test_sem_a_chave_antiga_o_segmento_antigo_nao_verifica(tmp_path):
    chain = _cadeia(tmp_path, chaves={"k1": b"chave-antiga"}, chave_ativa="k1")
    _preencher(chain, 2)
    chain.rotacionar("k2", b"chave-nova", ator="gestor")
    so_nova = _cadeia(tmp_path, chaves={"k2": b"chave-nova"}, chave_ativa="k2")
    assert so_nova.verificar() == (False, 0)


def test_kid_adulterado_invalida_entrada(tmp_path):
    chain = _cadeia(tmp_path, chaves={"k1": b"a", "k2": b"b"}, chave_ativa="k1")
    _preencher(chain, 2)
    linhas = (tmp_path / "audit.jsonl").read_text().splitlines()
    linha = json.loads(linhas[1])
    linha["kid"] = "k2"
    linhas[1] = json.dumps(linha)
    (tmp_path / "audit.jsonl").write_text("\n".join(linhas) + "\n")
    assert _cadeia(tmp_path, chaves={"k1": b"a", "k2": b"b"}, chave_ativa="k1").verificar() == (False, 1)


def test_kid_desconhecido_invalida_e_recusa_gravacao(tmp_path):
    chain = _cadeia(tmp_path, chaves={"k1": b"a"}, chave_ativa="k1")
    _preencher(chain, 1)
    outra = _cadeia(tmp_path, chaves={"k9": b"z"}, chave_ativa="k9")
    assert outra.verificar() == (False, 0)
    with pytest.raises(ValueError):
        outra.registrar("x", "y")


def test_historico_legado_sem_kid_continua_verificavel(tmp_path):
    antiga = _cadeia(tmp_path, chave=b"legado")  # formato anterior: sem kid
    _preencher(antiga, 2)
    assert "kid" not in antiga.entradas[0]
    nova = _cadeia(tmp_path, chaves={"k2": b"nova"}, chave_ativa="k2", chave_legada=b"legado")
    assert nova.verificar() == (True, None)
    nova.registrar("op", "depois")
    assert nova.entradas[-1]["kid"] == "k2"
    assert _cadeia(tmp_path, chaves={"k2": b"nova"}, chave_ativa="k2", chave_legada=b"legado").verificar() == (True, None)


def test_rotacao_recusa_kid_repetido_ou_chave_vazia(tmp_path):
    chain = _cadeia(tmp_path, chaves={"k1": b"a"}, chave_ativa="k1")
    with pytest.raises(ValueError):
        chain.rotacionar("k1", b"outra", ator="g")
    with pytest.raises(ValueError):
        chain.rotacionar("k2", b"", ator="g")


def test_rotacao_nao_grava_a_chave_no_arquivo(tmp_path):
    chain = _cadeia(tmp_path, chaves={"k1": b"segredo-antigo"}, chave_ativa="k1")
    chain.rotacionar("k2", b"segredo-novo", ator="g")
    conteudo = (tmp_path / "audit.jsonl").read_text()
    assert "segredo" not in conteudo


def test_chaves_do_ambiente():
    env = {"SIGMA_AUDIT_KEY": "nova", "SIGMA_AUDIT_KEY_ID": "k2",
           "SIGMA_AUDIT_RETIRED_KEYS": "k1:antiga, k0:mais-antiga"}
    chaves, ativa, legada = chaves_do_ambiente(env)
    assert ativa == "k2" and chaves == {"k2": b"nova", "k1": b"antiga", "k0": b"mais-antiga"}
    assert legada is None
    # Sem KEY_ID: comportamento anterior, uma chave sem kid.
    assert chaves_do_ambiente({"SIGMA_AUDIT_KEY": "x"}) == ({}, None, b"x")
    assert chaves_do_ambiente({}) == ({}, None, None)


# --- Job de verificação -----------------------------------------------------

class _Alertas:
    def __init__(self):
        self.enviados = []

    def __call__(self, payload):
        self.enviados.append(payload)


def test_job_ancora_quando_integra(tmp_path):
    chain = _cadeia(tmp_path, chave=b"k")
    _preencher(chain)
    sink = AncoraArquivo(tmp_path / "ancoras.jsonl")
    alertas = _Alertas()
    r = executar_verificacao(chain, [sink], alerta=alertas)
    assert r == ResultadoVerificacao(integra=True, motivo=None, entradas=3, ancorada=True)
    assert sink.ultima()["entradas"] == 3 and alertas.enviados == []


def test_job_alerta_e_nao_avanca_ancora_quando_adulterada(tmp_path):
    chain = _cadeia(tmp_path, chave=b"k")
    _preencher(chain)
    sink = AncoraArquivo(tmp_path / "ancoras.jsonl")
    executar_verificacao(chain, [sink], alerta=_Alertas())
    caminho = tmp_path / "audit.jsonl"
    original = caminho.read_text()
    caminho.write_text(original.replace('"i": 1', '"i": 9'))
    assert caminho.read_text() != original
    alertas = _Alertas()
    r = executar_verificacao(_cadeia(tmp_path, chave=b"k"), [sink], alerta=alertas)
    assert r.integra is False and r.motivo == "cadeia_invalida" and r.ancorada is False
    assert sink.ultima()["entradas"] == 3
    assert alertas.enviados[0]["tipo"] == "audit.integridade_falhou"
    assert set(alertas.enviados[0]) == {"tipo", "motivo", "entradas", "ts"}


def test_job_alerta_em_remocao_total(tmp_path):
    chain = _cadeia(tmp_path, chave=b"k")
    _preencher(chain)
    sink = AncoraArquivo(tmp_path / "ancoras.jsonl")
    executar_verificacao(chain, [sink], alerta=_Alertas())
    (tmp_path / "audit.jsonl").unlink()
    alertas = _Alertas()
    r = executar_verificacao(_cadeia(tmp_path, chave=b"k"), [sink], alerta=alertas)
    assert r.integra is False and r.motivo == "cadeia_menor_que_ancora"
    assert alertas.enviados and alertas.enviados[0]["motivo"] == "cadeia_menor_que_ancora"


def test_job_falha_do_alerta_nao_derruba_a_verificacao(tmp_path):
    chain = _cadeia(tmp_path, chave=b"k")
    _preencher(chain)
    (tmp_path / "audit.jsonl").write_text("lixo\n")

    def quebra(_):
        raise OSError("sem rede")

    r = executar_verificacao(_cadeia(tmp_path, chave=b"k"), [AncoraArquivo(tmp_path / "a.jsonl")], alerta=quebra)
    assert r.integra is False


def test_job_ancora_em_todos_os_destinos_e_tolera_falha_de_um(tmp_path):
    chain = _cadeia(tmp_path)
    _preencher(chain)
    publicados = []

    class Quebrado:
        def publicar(self, a):
            raise OSError("fora do ar")

        def ultima(self):
            return None

    bom = AncoraArquivo(tmp_path / "ok.jsonl")
    r = executar_verificacao(chain, [Quebrado(), bom], alerta=_Alertas())
    assert r.ancorada is True and bom.ultima()["entradas"] == 3


def test_webhook_envia_json_sem_segredos(monkeypatch):
    enviados = []

    class Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout):
        enviados.append((req.full_url, json.loads(req.data), timeout))
        return Resp()

    monkeypatch.setattr("sigma_eng.audit_anchor.urllib.request.urlopen", fake_urlopen)
    webhook = AncoraWebhook("https://n8n.exemplo.test/hook")
    webhook.publicar({"entradas": 1, "ultimo_hash": "a" * 64, "ts": "2026-11-01T00:00:00+00:00", "kid": None})
    url, corpo, timeout = enviados[0]
    assert url == "https://n8n.exemplo.test/hook" and corpo["tipo"] == "audit.ancora"
    assert timeout <= 10 and webhook.ultima() is None


def test_webhook_rejeita_esquema_nao_http():
    with pytest.raises(ValueError):
        AncoraWebhook("file:///etc/passwd")


def test_do_ambiente_sem_kid_mantem_formato_anterior(tmp_path):
    env = {"SIGMA_AUDIT_KEY": "k"}
    chain = AuditChain.do_ambiente(tmp_path / "a.jsonl", env)
    chain.registrar("a", "x")
    assert "kid" not in chain.entradas[0]
    assert AuditChain(tmp_path / "a.jsonl", chave=b"k").verificar() == (True, None)


def test_do_ambiente_com_kid_e_chaves_aposentadas(tmp_path):
    antiga = AuditChain(tmp_path / "a.jsonl", chaves={"k1": b"antiga"}, chave_ativa="k1")
    antiga.registrar("a", "x")
    env = {"SIGMA_AUDIT_KEY": "nova", "SIGMA_AUDIT_KEY_ID": "k2", "SIGMA_AUDIT_RETIRED_KEYS": "k1:antiga"}
    chain = AuditChain.do_ambiente(tmp_path / "a.jsonl", env)
    chain.registrar("a", "y")
    assert chain.verificar() == (True, None) and chain.entradas[-1]["kid"] == "k2"
