# engenharia/sigma_eng/anomaly.py

- Detector · class · L18-L19 — class Detector(Protocol)
- update · method · L19-L19 — def update(self, x: float) -> bool
- EwmaDetector · class · L22-L60 — class EwmaDetector
- __init__ · method · L32-L45 — def __init__(self, alpha: float = 0.1, k: float = 4.0, aquecimento: int = 20, piso_desvio: float = 1e-9, congelar_em_anomalia: bool = True, reaprender_apos: int = 50) -> None
- update · method · L47-L60 — def update(self, x: float) -> bool
- MadDetector · class · L63-L88 — class MadDetector
- __init__ · method · L66-L71 — def __init__(self, janela: int = 60, k: float = 5.0, aquecimento: int = 20, piso_escala: float = 1e-9) -> None
- _mediana · method · L74-L77 — def _mediana(v: Sequence[float]) -> float
- update · method · L79-L88 — def update(self, x: float) -> bool
- Avaliacao · class · L92-L104 — class Avaliacao
- as_dict · method · L103-L104 — def as_dict(self) -> dict
- avaliar · function · L107-L140 — def avaliar(detector: Detector, serie: Sequence[float], rotulos: Sequence[bool]) -> Avaliacao
