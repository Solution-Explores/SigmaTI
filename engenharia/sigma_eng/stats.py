"""Estatística descritiva mínima (stdlib), usada por sondas, SLO e experimentos."""

from __future__ import annotations

import math
from typing import Iterable, Sequence


def percentile(values: Iterable[float], q: float) -> float:
    """Percentil ``q`` (0-100) por interpolação linear entre ranks vizinhos.

    Equivale ao método 7 de Hyndman & Fan (padrão do NumPy). Levanta
    ``ValueError`` para amostra vazia ou ``q`` fora de [0, 100].
    """
    data = sorted(values)
    if not data:
        raise ValueError("amostra vazia")
    if not 0 <= q <= 100:
        raise ValueError("q deve estar em [0, 100]")
    if len(data) == 1:
        return float(data[0])
    rank = (len(data) - 1) * q / 100
    low = math.floor(rank)
    high = math.ceil(rank)
    frac = rank - low
    return float(data[low] + (data[high] - data[low]) * frac)


def mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("amostra vazia")
    return sum(values) / len(values)


def stdev(values: Sequence[float]) -> float:
    """Desvio-padrão amostral (n-1). Zero para amostra com um único valor."""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def median(values: Iterable[float]) -> float:
    return percentile(values, 50)


def summary(values: Sequence[float]) -> dict[str, float]:
    """Resumo padrão (n, média, desvio, mín, p50, p95, p99, máx)."""
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "mean": round(mean(values), 3),
        "stdev": round(stdev(values), 3),
        "min": round(min(values), 3),
        "p50": round(percentile(values, 50), 3),
        "p95": round(percentile(values, 95), 3),
        "p99": round(percentile(values, 99), 3),
        "max": round(max(values), 3),
    }
