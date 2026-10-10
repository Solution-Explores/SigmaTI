"""Detecção de anomalias em séries de latência: EWMA (z-score) e MAD (robusto).

Dois detectores *online* (uma amostra por vez, memória O(1) e O(janela)) para
que possam rodar na sonda. ``avaliar`` mede precisão, revocação e atraso de
detecção contra rótulos conhecidos — base dos experimentos do TCC.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Protocol, Sequence

MAD_ESCALA = 1.4826  # torna o MAD consistente com o desvio-padrão sob normalidade


class Detector(Protocol):
    def update(self, x: float) -> bool: ...


class EwmaDetector:
    """Média e variância móveis exponenciais; sinaliza |x - média| > k·desvio.

    ``congelar_em_anomalia``: não atualiza o modelo com amostras anômalas, para que
    uma degradação sustentada não vire o "novo normal" nem mascare o alerta.
    ``reaprender_apos``: após N anomalias consecutivas o modelo volta a aprender,
    aceitando o novo patamar. Sem isso o congelamento trava o detector em alarme
    permanente quando o patamar muda de forma definitiva (achado do experimento E1).
    """

    def __init__(self, alpha: float = 0.1, k: float = 4.0, aquecimento: int = 20,
                 piso_desvio: float = 1e-9, congelar_em_anomalia: bool = True,
                 reaprender_apos: int = 50) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("alpha deve estar em (0, 1]")
        if k <= 0 or aquecimento < 1:
            raise ValueError("k > 0 e aquecimento >= 1")
        self.alpha, self.k, self.aquecimento = alpha, k, aquecimento
        self.piso, self.congelar = piso_desvio, congelar_em_anomalia
        self.reaprender_apos = reaprender_apos
        self._seguidas = 0
        self.n = 0
        self.media = 0.0
        self.var = 0.0

    def update(self, x: float) -> bool:
        self.n += 1
        if self.n == 1:
            self.media = x
            return False
        desvio = max(math.sqrt(self.var), self.piso)
        anomalia = self.n > self.aquecimento and abs(x - self.media) > self.k * desvio
        self._seguidas = self._seguidas + 1 if anomalia else 0
        if not (anomalia and self.congelar and self._seguidas <= self.reaprender_apos):
            diff = x - self.media
            incr = self.alpha * diff
            self.media += incr
            self.var = (1 - self.alpha) * (self.var + diff * incr)
        return anomalia


class MadDetector:
    """Mediana e MAD numa janela deslizante; sinaliza |x - mediana| > k·1,4826·MAD."""

    def __init__(self, janela: int = 60, k: float = 5.0, aquecimento: int = 20,
                 piso_escala: float = 1e-9) -> None:
        if janela < 5 or aquecimento > janela:
            raise ValueError("janela >= 5 e aquecimento <= janela")
        self.k, self.aquecimento, self.piso = k, aquecimento, piso_escala
        self.buf: deque[float] = deque(maxlen=janela)

    @staticmethod
    def _mediana(v: Sequence[float]) -> float:
        s = sorted(v)
        m = len(s) // 2
        return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2

    def update(self, x: float) -> bool:
        anomalia = False
        if len(self.buf) >= self.aquecimento:
            med = self._mediana(self.buf)
            mad = self._mediana([abs(v - med) for v in self.buf])
            escala = max(MAD_ESCALA * mad, self.piso)
            anomalia = abs(x - med) > self.k * escala
        if not anomalia:  # anomalias não contaminam a janela de referência
            self.buf.append(x)
        return anomalia


@dataclass
class Avaliacao:
    vp: int
    fp: int
    fn: int
    precisao: float
    revocacao: float
    f1: float
    atraso_medio: float | None  # amostras entre o início do evento e o 1º alarme
    eventos: int
    eventos_detectados: int

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def avaliar(detector: Detector, serie: Sequence[float], rotulos: Sequence[bool]) -> Avaliacao:
    """Compara alarmes com rótulos verdadeiros (``True`` = amostra em falha).

    Métricas por amostra (VP/FP/FN) e por evento (atraso até o primeiro alarme).
    Um evento é um trecho contíguo de rótulos ``True``.
    """
    if len(serie) != len(rotulos):
        raise ValueError("serie e rotulos devem ter o mesmo tamanho")
    alarmes = [detector.update(x) for x in serie]
    vp = sum(a and r for a, r in zip(alarmes, rotulos))
    fp = sum(a and not r for a, r in zip(alarmes, rotulos))
    fn = sum((not a) and r for a, r in zip(alarmes, rotulos))
    prec = vp / (vp + fp) if vp + fp else 0.0
    rev = vp / (vp + fn) if vp + fn else 0.0
    f1 = 2 * prec * rev / (prec + rev) if prec + rev else 0.0

    atrasos: list[int] = []
    eventos = 0
    i = 0
    while i < len(rotulos):
        if rotulos[i]:
            j = i
            while j < len(rotulos) and rotulos[j]:
                j += 1
            eventos += 1
            primeiro = next((t for t in range(i, j) if alarmes[t]), None)
            if primeiro is not None:
                atrasos.append(primeiro - i)
            i = j
        else:
            i += 1
    return Avaliacao(vp, fp, fn, round(prec, 4), round(rev, 4), round(f1, 4),
                     round(sum(atrasos) / len(atrasos), 2) if atrasos else None,
                     eventos, len(atrasos))
