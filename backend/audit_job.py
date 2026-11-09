"""Verificação periódica da trilha de auditoria com âncora externa (issue #13)."""

import asyncio
import logging

from sigma_eng.audit_anchor import executar_verificacao

logger = logging.getLogger("sigma.audit")

INTERVALO_PADRAO_SEGUNDOS = 86400


async def verificar_periodicamente(cadeia, destinos, alerta, intervalo: float = INTERVALO_PADRAO_SEGUNDOS) -> None:
    """Roda ao iniciar e depois a cada ``intervalo`` s, até ser cancelada.

    A verificação lê arquivos e pode chamar um webhook, então roda em thread
    para não bloquear o event loop. Exceções não derrubam o laço.
    """
    while True:
        try:
            await asyncio.to_thread(executar_verificacao, cadeia, destinos, alerta)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("AUDIT_JOB falhou: %s", type(exc).__name__)
        await asyncio.sleep(intervalo)
