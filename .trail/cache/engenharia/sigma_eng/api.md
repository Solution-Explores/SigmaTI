# engenharia/sigma_eng/api.py

- exige_papel · function · L30-L31 — def exige_papel(papel: str)
- _redes · function · L43-L45 — def _redes() -> list[str]
- ProbeIn · class · L48-L52 — class ProbeIn(BaseModel)
- post_probe · function · L56-L63 — async def post_probe(body: ProbeIn) -> dict
- IntervaloIn · class · L66-L68 — class IntervaloIn(BaseModel)
- SloIn · class · L71-L75 — class SloIn(BaseModel)
- post_slo · function · L79-L86 — def post_slo(body: SloIn) -> dict
- IncidenteIn · class · L89-L95 — class IncidenteIn(BaseModel)
- post_metricas · function · L99-L100 — def post_metricas(body: list[IncidenteIn]) -> dict
- AnomaliaIn · class · L103-L105 — class AnomaliaIn(BaseModel)
- post_anomalias · function · L109-L116 — def post_anomalias(body: AnomaliaIn) -> dict
- get_verificar · function · L120-L122 — def get_verificar() -> dict
