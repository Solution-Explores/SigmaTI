import json
from datetime import datetime, timedelta, timezone

import pytest

from sigma_eng.approvals import AprovacaoError, ApprovalService
from sigma_eng.audit_chain import AuditChain

T0 = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)


class Relogio:
    def __init__(self):
        self.t = T0

    def __call__(self):
        return self.t


def test_cadeia_integra(tmp_path):
    c = AuditChain(tmp_path / "a.jsonl")
    for i in range(5):
        c.registrar("ana", "x", f"r{i}")
    assert c.verificar() == (True, None) and len(c) == 5


def test_adulteracao_detectada(tmp_path):
    p = tmp_path / "a.jsonl"
    c = AuditChain(p)
    for i in range(5):
        c.registrar("ana", "x", f"r{i}")
    linhas = p.read_text().splitlines()
    e = json.loads(linhas[2])
    e["ator"] = "outro"
    linhas[2] = json.dumps(e)
    p.write_text("\n".join(linhas) + "\n")
    assert AuditChain(p).verificar() == (False, 2)


def test_remocao_e_reordenacao_detectadas(tmp_path):
    p = tmp_path / "a.jsonl"
    c = AuditChain(p)
    for i in range(5):
        c.registrar("ana", "x", f"r{i}")
    linhas = p.read_text().splitlines()
    p.write_text("\n".join(linhas[:1] + linhas[2:]) + "\n")
    assert AuditChain(p).verificar()[0] is False
    p.write_text("\n".join([linhas[1], linhas[0]] + linhas[2:]) + "\n")
    assert AuditChain(p).verificar()[0] is False


def test_hmac_impede_recalculo_sem_chave(tmp_path):
    p = tmp_path / "a.jsonl"
    c = AuditChain(p, chave=b"segredo")
    c.registrar("ana", "x")
    assert AuditChain(p, chave=b"segredo").verificar() == (True, None)
    assert AuditChain(p, chave=b"errada").verificar() == (False, 0)
    assert AuditChain(p).verificar() == (False, 0)


def test_persistencia_continua_a_cadeia(tmp_path):
    p = tmp_path / "a.jsonl"
    AuditChain(p).registrar("ana", "x")
    c2 = AuditChain(p)
    c2.registrar("bia", "y")
    assert AuditChain(p).verificar() == (True, None) and len(AuditChain(p)) == 2


def _svc(**kw):
    rel = Relogio()
    return ApprovalService(relogio=rel, **kw), rel


def test_fluxo_aprovacao_e_auditoria():
    audit = AuditChain()
    svc, _ = _svc(auditoria=audit)
    ap = svc.solicitar("reiniciar-switch", "tecnico1")
    svc.aprovar(ap.id, "gestor1", "gestor_ti", "ok")
    assert svc.obter(ap.id).estado == "approved"
    assert [e["acao"] for e in audit.entradas] == ["approval.requested", "approval.approved"]
    assert audit.verificar()[0]


def test_autoaprovacao_proibida():
    svc, _ = _svc()
    ap = svc.solicitar("x", "tecnico1")
    with pytest.raises(AprovacaoError, match="solicitante"):
        svc.aprovar(ap.id, "tecnico1", "gestor_ti")


def test_papel_insuficiente():
    svc, _ = _svc()
    ap = svc.solicitar("x", "t1", papel_minimo="gestor_ti")
    with pytest.raises(AprovacaoError, match="papel insuficiente"):
        svc.aprovar(ap.id, "ana", "analista_redes")


def test_aprovacao_vencida_nao_pode_ser_aprovada():
    svc, rel = _svc(ttl=timedelta(minutes=5))
    ap = svc.solicitar("x", "t1")
    rel.t += timedelta(minutes=6)  # vence sem varredura periódica
    with pytest.raises(AprovacaoError, match="expired"):
        svc.aprovar(ap.id, "ana", "gestor_ti")
    assert svc.obter(ap.id).estado == "expired" and svc.pendentes() == []


def test_decisao_final_e_imutavel():
    svc, _ = _svc()
    ap = svc.solicitar("x", "t1")
    svc.rejeitar(ap.id, "ana", "gestor_ti")
    with pytest.raises(AprovacaoError):
        svc.aprovar(ap.id, "bia", "gestor_ti")
