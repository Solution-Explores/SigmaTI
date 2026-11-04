"""Job periódico de verificação da auditoria (#13)."""
import asyncio

from sigma_eng.audit_anchor import AncoraArquivo
from sigma_eng.audit_chain import AuditChain

from audit_job import verificar_periodicamente


def test_job_ancora_na_partida_e_alerta_quando_adulterado(tmp_path):
    chain = AuditChain(tmp_path / "audit.jsonl", chave=b"k")
    chain.registrar("a", "x")
    chain.registrar("a", "y")
    sink = AncoraArquivo(tmp_path / "ancoras.jsonl")
    alertas = []

    async def cenario():
        tarefa = asyncio.create_task(verificar_periodicamente(chain, [sink], alertas.append, intervalo=0.05))
        await asyncio.sleep(0.3)
        assert sink.ultima()["entradas"] == 2 and alertas == []
        (tmp_path / "audit.jsonl").unlink()
        await asyncio.sleep(0.3)
        tarefa.cancel()
        try:
            await tarefa
        except asyncio.CancelledError:
            pass

    asyncio.run(cenario())
    assert alertas and alertas[0]["tipo"] == "audit.integridade_falhou"
    assert sink.ultima()["entradas"] == 2
