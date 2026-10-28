# engenharia/sigma_eng/slo.py

- SLO · class · L24-L38 — class SLO
- __post_init__ · method · L29-L33 — def __post_init__(self) -> None
- erro_permitido · method · L36-L38 — def erro_permitido(self) -> float
- merge_intervals · function · L41-L50 — def merge_intervals(intervals: Iterable[Interval]) -> list[Interval]
- downtime_minutes · function · L53-L58 — def downtime_minutes(intervals: Iterable[Interval], inicio: datetime, fim: datetime) -> float
- availability_pct · function · L61-L63 — def availability_pct(intervals: Iterable[Interval], inicio: datetime, fim: datetime) -> float
- BudgetStatus · class · L67-L79 — class BudgetStatus
- as_dict · method · L76-L79 — def as_dict(self) -> dict
- error_budget · function · L82-L105 — def error_budget(slo: SLO, intervals: Sequence[Interval], agora: datetime, risco_pct: float = 25.0) -> BudgetStatus
- burn_rate · function · L108-L116 — def burn_rate(slo: SLO, intervals: Sequence[Interval], agora: datetime, janela: timedelta) -> float
- burn_alerts · function · L128-L146 — def burn_alerts(slo: SLO, intervals: Sequence[Interval], agora: datetime) -> list[dict]
