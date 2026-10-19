"""Métricas de resposta a incidentes: MTTD, MTTA e MTTR.

Definições (fixas, para que os números do TCC sejam comparáveis):
  * TTD  = detectado_em   - inicio_real      (exige o instante real da falha)
  * TTA  = reconhecido_em - detectado_em
  * TTR  = resolvido_em   - detectado_em
  * MTTD/MTTA/MTTR = média; além disso, mediana e p95, porque a cauda longa
    de incidentes domina a média.
Incidentes sem o campo necessário são ignorados na métrica correspondente, e a
contagem usada (``n``) é devolvida junto.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .stats import mean, percentile


@dataclass
class Incidente:
    id: str
    severidade: str = "P3"
    inicio_real: datetime | None = None  # momento da falha (injeção ou análise posterior)
    detectado_em: datetime | None = None
    reconhecido_em: datetime | None = None
    resolvido_em: datetime | None = None

    def intervalo_indisponivel(self) -> tuple[datetime, datetime] | None:
        """Intervalo para o cálculo de SLO (da falha, ou da detecção, até a resolução)."""
        inicio = self.inicio_real or self.detectado_em
        if inicio and self.resolvido_em and self.resolvido_em > inicio:
            return inicio, self.resolvido_em
        return None


def _segundos(a: datetime | None, b: datetime | None) -> float | None:
    if a is None or b is None:
        return None
    delta = (b - a).total_seconds()
    return delta if delta >= 0 else None  # relógios fora de ordem não entram


def _resumo(valores: list[float]) -> dict:
    if not valores:
        return {"n": 0}
    return {
        "n": len(valores),
        "media_s": round(mean(valores), 2),
        "mediana_s": round(percentile(valores, 50), 2),
        "p95_s": round(percentile(valores, 95), 2),
    }


def metricas(incidentes: Iterable[Incidente]) -> dict:
    incs = list(incidentes)
    return {
        "total": len(incs),
        "MTTD": _resumo([v for i in incs if (v := _segundos(i.inicio_real, i.detectado_em)) is not None]),
        "MTTA": _resumo([v for i in incs if (v := _segundos(i.detectado_em, i.reconhecido_em)) is not None]),
        "MTTR": _resumo([v for i in incs if (v := _segundos(i.detectado_em, i.resolvido_em)) is not None]),
    }
