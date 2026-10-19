import pytest

from sigma_eng.approvals import ApprovalService
from sigma_eng.runbooks import ResultadoPasso, RunbookError, RunbookRunner, interpolar, parsear

MD = """
# Switch sem resposta
```sigma:step{id=ping, timeout=10s}
ping -c 1 ${HOST}
```
texto
```sigma:step{id=reiniciar, requires_approval=true, timeout=1m}
systemctl restart ${SERVICO}
```
```sigma:step{id=verificar}
echo ok
```
"""
VARS = {"HOST": "10.0.0.1", "SERVICO": "snmpd"}


def fake(chamadas):
    def ex(argv, timeout):
        chamadas.append(list(argv))
        return ResultadoPasso("", True, "ok")
    return ex


def test_parse():
    p = parsear(MD)
    assert [x.id for x in p] == ["ping", "reiniciar", "verificar"]
    assert p[1].requer_aprovacao and p[1].timeout_s == 60 and p[0].timeout_s == 10


def test_ids_duplicados():
    with pytest.raises(RunbookError):
        parsear("```sigma:step{id=a}\necho 1\n```\n```sigma:step{id=a}\necho 2\n```")


def test_dry_run_e_padrao_e_nao_executa():
    ch = []
    r = RunbookRunner(["ping", "systemctl", "echo"], fake(ch))
    ex = r.executar("r1", parsear(MD), VARS)
    assert ex.status == "completed" and ch == [] and all(x.simulado for x in ex.resultados)


def test_aprovacao_por_passo_real():
    ch = []
    r = RunbookRunner(["ping", "systemctl", "echo"], fake(ch))
    svc = ApprovalService()
    ex = r.executar("r1", parsear(MD), VARS, dry_run=False)
    assert ex.status == "waiting_approval" and ex.aguardando == "reiniciar" and len(ch) == 1
    ap = svc.solicitar("runbook:r1:reiniciar", "tecnico1")
    with pytest.raises(RunbookError):  # ainda pendente
        r.retomar(ex, ap)
    svc.aprovar(ap.id, "gestor1", "gestor_ti")
    ex = r.retomar(ex, svc.obter(ap.id))
    assert ex.status == "completed" and len(ch) == 3


def test_aprovacao_de_outro_passo_e_recusada():
    r = RunbookRunner(["ping", "systemctl", "echo"], fake([]))
    svc = ApprovalService()
    ex = r.executar("r1", parsear(MD), VARS, dry_run=False)
    ap = svc.solicitar("runbook:r1:outro", "t1")
    svc.aprovar(ap.id, "g", "gestor_ti")
    with pytest.raises(RunbookError):
        r.retomar(ex, svc.obter(ap.id))


def test_allowlist():
    r = RunbookRunner(["echo"], fake([]))
    with pytest.raises(RunbookError, match="allowlist"):
        r.executar("r", parsear("```sigma:step{id=a}\nrm -rf /\n```"), {})


@pytest.mark.parametrize("valor", ["10.0.0.1; rm -rf /", "$(id)", "a b", "-rf", "`id`", "x|y", ""])
def test_injecao_em_variavel_bloqueada(valor):
    with pytest.raises(RunbookError):
        interpolar("ping ${HOST}", {"HOST": valor})


def test_variavel_nao_resolvida():
    with pytest.raises(RunbookError, match="não resolvidas"):
        interpolar("ping ${HOST}", {})


def test_valida_tudo_antes_de_executar():
    ch = []
    r = RunbookRunner(["echo"], fake(ch))
    md = "```sigma:step{id=a}\necho 1\n```\n```sigma:step{id=b}\nrm x\n```"
    with pytest.raises(RunbookError):
        r.executar("r", parsear(md), {}, dry_run=False)
    assert ch == []  # nada rodou pela metade


def test_falha_interrompe():
    def ruim(argv, t):
        return ResultadoPasso("", False, erro="boom", codigo=1)
    r = RunbookRunner(["echo"], ruim)
    md = "```sigma:step{id=a}\necho 1\n```\n```sigma:step{id=b}\necho 2\n```"
    ex = r.executar("r", parsear(md), {}, dry_run=False)
    assert ex.status == "failed" and len(ex.resultados) == 1


def test_executor_real_sem_shell():
    r = RunbookRunner(["echo"])
    ex = r.executar("r", parsear("```sigma:step{id=a}\necho oi; id\n```"), {}, dry_run=False)
    assert ex.status == "completed"
    assert ex.resultados[0].saida.strip() == "oi; id"  # ';' é argumento literal, não operador
