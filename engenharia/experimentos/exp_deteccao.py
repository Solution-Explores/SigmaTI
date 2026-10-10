"""Experimento E1 — detecção de anomalias de latência com falha injetada.

Hipótese H1: detectores estatísticos online (EWMA e MAD) detectam degradações
de latência com atraso de poucas amostras e falsos positivos desprezíveis.

Método: série de base lognormal (cauda pesada, como RTT real), com um evento
de falha por série — ``degrau`` (+X ms), ``pico`` (3 amostras) ou ``deriva``
(rampa lenta). 30 repetições por cenário, sementes 0..29. Resultado em CSV e
tabela Markdown em ``resultados/``.

Uso (a partir de ``engenharia/``)::

    python -m experimentos.exp_deteccao
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

from sigma_eng.anomaly import EwmaDetector, MadDetector, avaliar
from sigma_eng.stats import mean, stdev

N, INICIO, REPS = 600, 300, 30
SAIDA = Path(__file__).resolve().parent.parent / "resultados"


def gerar(cenario: str, seed: int) -> tuple[list[float], list[bool]]:
    rng = random.Random(seed)
    serie = [rng.lognormvariate(3.0, 0.15) for _ in range(N)]  # mediana ≈ 20 ms
    rot = [False] * N
    if cenario == "degrau":
        for i in range(INICIO, INICIO + 60):
            serie[i] += 40
            rot[i] = True
    elif cenario == "pico":
        for i in range(INICIO, INICIO + 3):
            serie[i] += 80
            rot[i] = True
    elif cenario == "deriva":
        for k, i in enumerate(range(INICIO, INICIO + 120)):
            serie[i] += 0.5 * k  # +0,5 ms por amostra, chega a +60 ms
            rot[i] = True
    else:
        raise ValueError(cenario)
    return serie, rot


DETECTORES = {
    "EWMA(a=0.1,k=4)": lambda: EwmaDetector(alpha=0.1, k=4.0),
    "MAD(w=60,k=5)": lambda: MadDetector(janela=60, k=5.0),
}


def main() -> None:
    linhas = []
    for cenario in ("degrau", "pico", "deriva"):
        for nome, fabrica in DETECTORES.items():
            res = [avaliar(fabrica(), *gerar(cenario, s)) for s in range(REPS)]
            detect = [r.eventos_detectados / r.eventos for r in res]
            atrasos = [r.atraso_medio for r in res if r.atraso_medio is not None]
            linhas.append({
                "cenario": cenario, "detector": nome,
                "taxa_deteccao": round(mean(detect), 3),
                "atraso_medio_amostras": round(mean(atrasos), 2) if atrasos else "",
                "atraso_dp": round(stdev(atrasos), 2) if atrasos else "",
                "falsos_positivos_por_serie": round(mean([r.fp for r in res]), 2),
                "f1_medio": round(mean([r.f1 for r in res]), 3),
            })
    SAIDA.mkdir(exist_ok=True)
    with (SAIDA / "e1_deteccao.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    cab = list(linhas[0])
    md = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    md += ["| " + " | ".join(str(l[c]) for c in cab) + " |" for l in linhas]
    (SAIDA / "e1_deteccao.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
