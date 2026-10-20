"""Contratos de estado do núcleo continuam funcionando sem banco/framework."""
import pytest
from sigma_eng.approvals import ApprovalService, AprovacaoError
from sigma_eng.runbooks import RunbookRunner, parsear
from sigma_eng.state import MemoryStateRepository, StateConflict


def test_shared_memory_approval_repository_restores_and_prevents_override():
    repo = MemoryStateRepository()
    first, second = ApprovalService(repository=repo), ApprovalService(repository=repo)
    ap = first.solicitar("synthetic", "requester")
    second.aprovar(ap.id, "decider", "gestor_ti")
    assert first.obter(ap.id).estado == "approved"
    with pytest.raises(AprovacaoError):
        first.rejeitar(ap.id, "other", "gestor_ti")


def test_execution_snapshot_is_a_defensive_copy():
    repo = MemoryStateRepository()
    runner = RunbookRunner(["echo"], repository=repo)
    result = runner.executar("synthetic", parsear("```sigma:step{id=a}\necho a\n```"), {})
    result.resultados.clear()
    assert len(runner.obter(result.id).resultados) == 1
    stored = repo.get("executions", result.id)
    with pytest.raises(StateConflict):
        repo.save("executions", result.id, stored, stored["versao"] - 1)
