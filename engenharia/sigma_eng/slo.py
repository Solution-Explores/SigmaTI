"""SLO, error budget e alertas de burn rate em múltiplas janelas.

Decisões de projeto:
  * indisponibilidade é a **união** dos intervalos (incidentes sobrepostos não
    são contados duas vezes);
  * incidentes que cruzam a borda da janela são **recortados** (conta só a
    parte que cai dentro dela);
  * burn rate segue a definição do SRE Workbook (razão entre o erro observado
    e o erro permitido).

Funções puras: recebem intervalos e instantes, sem banco nem relógio global.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Sequence

Interval = tuple[datetime, datetime]


@dataclass(frozen=True)
class SLO:
    nome: str
    alvo_pct: float = 99.9  # disponibilidade-alvo, em %
    janela_dias: int = 30

    def __post_init__(self) -> None:
        if not 0 < self.alvo_pct < 100:
            raise ValueError("alvo_pct deve estar em (0, 100)")
        if self.janela_dias < 1:
            raise ValueError("janela_dias deve ser >= 1")

    @property
    def erro_permitido(self) -> float:
        """Fração de tempo que pode estar indisponível (1 - alvo)."""
        return 1 - self.alvo_pct / 100


def merge_intervals(intervals: Iterable[Interval]) -> list[Interval]:
    """União de intervalos: ordena e funde sobrepostos ou adjacentes."""
    ordered = sorted((s, e) for s, e in intervals if e > s)
    merged: list[Interval] = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def downtime_minutes(intervals: Iterable[Interval], inicio: datetime, fim: datetime) -> float:
    """Minutos de indisponibilidade dentro de [inicio, fim], sem dupla contagem."""
    if fim <= inicio:
        raise ValueError("fim deve ser posterior a inicio")
    clipped = [(max(s, inicio), min(e, fim)) for s, e in intervals]
    return sum((e - s).total_seconds() for s, e in merge_intervals(clipped)) / 60


def availability_pct(intervals: Iterable[Interval], inicio: datetime, fim: datetime) -> float:
    total = (fim - inicio).total_seconds() / 60
    return 100 * (total - downtime_minutes(intervals, inicio, fim)) / total


@dataclass(frozen=True)
class BudgetStatus:
    status: str  # healthy | at_risk | breaching
    disponibilidade_pct: float
    orcamento_total_min: float
    consumido_min: float
    restante_min: float
    restante_pct: float
    esgota_em: datetime | None

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d["esgota_em"] = self.esgota_em.isoformat() if self.esgota_em else None
        return d


def error_budget(slo: SLO, intervals: Sequence[Interval], agora: datetime, risco_pct: float = 25.0) -> BudgetStatus:
    """Situação do orçamento de erros na janela que termina em ``agora``."""
    inicio = agora - timedelta(days=slo.janela_dias)
    total_min = slo.janela_dias * 24 * 60
    budget = total_min * slo.erro_permitido
    down = downtime_minutes(intervals, inicio, agora)
    disp = 100 * (total_min - down) / total_min
    restante = max(0.0, budget - down)
    restante_pct = 100 * restante / budget
    if disp < slo.alvo_pct:
        status = "breaching"
    elif restante_pct <= risco_pct:
        status = "at_risk"
    else:
        status = "healthy"

    # Projeção: ritmo dos últimos 7 dias (ou da janela inteira, se menor).
    ref_dias = min(7, slo.janela_dias)
    down_ref = downtime_minutes(intervals, agora - timedelta(days=ref_dias), agora)
    ritmo_min_por_dia = down_ref / ref_dias
    esgota = None
    if ritmo_min_por_dia > 0 and restante > 0:
        esgota = agora + timedelta(days=restante / ritmo_min_por_dia)
    return BudgetStatus(status, round(disp, 4), round(budget, 3), round(down, 3), round(restante, 3), round(restante_pct, 2), esgota)


def burn_rate(slo: SLO, intervals: Sequence[Interval], agora: datetime, janela: timedelta) -> float:
    """Razão entre o erro observado na janela e o erro permitido pelo SLO.

    1.0 = consumindo o orçamento exatamente no ritmo que o esgota no fim da
    janela do SLO; 14.4 = esgotaria 2% do orçamento mensal em 1 hora.
    """
    inicio = agora - janela
    erro_obs = downtime_minutes(intervals, inicio, agora) / (janela.total_seconds() / 60)
    return erro_obs / slo.erro_permitido


# (janela longa, janela curta, limiar, ação) — SRE Workbook, cap. 5, para SLO de 30 dias.
BURN_RULES = (
    (timedelta(hours=1), timedelta(minutes=5), 14.4, "page"),
    (timedelta(hours=6), timedelta(minutes=30), 6.0, "page"),
    (timedelta(days=1), timedelta(hours=2), 3.0, "ticket"),
    (timedelta(days=3), timedelta(hours=6), 1.0, "ticket"),
)


def burn_alerts(slo: SLO, intervals: Sequence[Interval], agora: datetime) -> list[dict]:
    """Regras disparadas. Exige a janela longa **e** a curta acima do limiar:
    a longa evita alarme por pico isolado; a curta encerra o alerta logo após a recuperação."""
    fired = []
    for longa, curta, limiar, acao in BURN_RULES:
        b_long = burn_rate(slo, intervals, agora, longa)
        b_short = burn_rate(slo, intervals, agora, curta)
        if b_long >= limiar and b_short >= limiar:
            fired.append(
                {
                    "acao": acao,
                    "limiar": limiar,
                    "janela_longa": str(longa),
                    "janela_curta": str(curta),
                    "burn_longa": round(b_long, 2),
                    "burn_curta": round(b_short, 2),
                }
            )
    return fired
