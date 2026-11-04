"""Gera a figura do custo da auditoria (#46) em SVG a partir dos JSON de ``dados/``.

Uso:  python docs/tcc/evidencias/gerar_figura_auditoria.py
Só biblioteca padrão. Escala logarítmica nos dois eixos: na escala linear, 12 ms e 4.291 ms
não cabem no mesmo gráfico. Cores validadas para daltonismo (contraste e separação ok).
"""
import json
import math
from pathlib import Path

PASTA = Path(__file__).resolve().parent
COR_ANTES, COR_DEPOIS, TINTA, TINTA_SUAVE, GRADE = "#b45309", "#1d5fa6", "#1f2937", "#4b5563", "#e5e7eb"
META_MS = 50
W, H = 760, 440
ML, MR, MT, MB = 78, 150, 56, 64


def serie(nome):
    dados = json.loads((PASTA / "dados" / f"auditoria-custo-{nome}.json").read_text(encoding="utf-8"))
    return [(r["tamanho"], r["login"]["mediana_ms"]) for r in dados["resultados"]]


def main():
    antes, depois = serie("antes"), serie("depois")
    xmin, xmax, ymin, ymax = 4e2, 2.5e5, 1, 1e4
    px = lambda x: ML + (math.log10(x) - math.log10(xmin)) / (math.log10(xmax) - math.log10(xmin)) * (W - ML - MR)
    py = lambda y: H - MB - (math.log10(y) - math.log10(ymin)) / (math.log10(ymax) - math.log10(ymin)) * (H - MT - MB)
    fmt = lambda n: f"{n:,}".replace(",", ".")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-labelledby="t d" font-family="Segoe UI, Arial, sans-serif">',
         '<title id="t">Tempo de gravação da trilha de auditoria por tamanho da trilha, antes e depois da correção</title>',
         f'<desc id="d">Antes: {", ".join(f"{fmt(n)} entradas em {ms} ms" for n, ms in antes)}. '
         f'Depois: {", ".join(f"{fmt(n)} entradas em {ms} ms" for n, ms in depois)}. Meta proposta: {META_MS} ms.</desc>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{ML}" y="26" font-size="16" font-weight="600" fill="{TINTA}">Custo de uma gravação na auditoria (login)</text>',
         f'<text x="{ML}" y="44" font-size="12" fill="{TINTA_SUAVE}">mediana de 5 repetições · escala logarítmica nos dois eixos</text>']
    for y in (1, 10, 100, 1000, 10000):
        o.append(f'<line x1="{ML}" x2="{W-MR}" y1="{py(y):.1f}" y2="{py(y):.1f}" stroke="{GRADE}" stroke-width="1"/>')
        o.append(f'<text x="{ML-8}" y="{py(y)+4:.1f}" font-size="12" text-anchor="end" fill="{TINTA_SUAVE}">{fmt(y)} ms</text>')
    for x in (1000, 10000, 100000):
        o.append(f'<line x1="{px(x):.1f}" x2="{px(x):.1f}" y1="{H-MB}" y2="{H-MB+5}" stroke="{TINTA_SUAVE}"/>')
        o.append(f'<text x="{px(x):.1f}" y="{H-MB+22}" font-size="12" text-anchor="middle" fill="{TINTA_SUAVE}">{fmt(x)}</text>')
    o.append(f'<text x="{(ML+W-MR)/2:.0f}" y="{H-14}" font-size="12" text-anchor="middle" fill="{TINTA_SUAVE}">entradas na trilha de auditoria</text>')
    o.append(f'<line x1="{ML}" x2="{W-MR}" y1="{py(META_MS):.1f}" y2="{py(META_MS):.1f}" stroke="{TINTA_SUAVE}" stroke-dasharray="5 4"/>')
    o.append(f'<text x="{W-MR+8}" y="{py(META_MS)+4:.1f}" font-size="12" fill="{TINTA_SUAVE}">meta proposta: {META_MS} ms</text>')
    for pontos, cor, rotulo in ((antes, COR_ANTES, "antes"), (depois, COR_DEPOIS, "depois")):
        caminho = " ".join(f"{px(n):.1f},{py(ms):.1f}" for n, ms in pontos)
        o.append(f'<polyline points="{caminho}" fill="none" stroke="{cor}" stroke-width="2.5" stroke-linejoin="round"/>')
        for n, ms in pontos:
            o.append(f'<circle cx="{px(n):.1f}" cy="{py(ms):.1f}" r="5" fill="{cor}" stroke="#ffffff" stroke-width="2"/>')
            deslocamento = -12 if rotulo == "antes" else 20
            o.append(f'<text x="{px(n):.1f}" y="{py(ms)+deslocamento:.1f}" font-size="12" text-anchor="middle" fill="{TINTA}">{str(ms).replace(".", ",")} ms</text>')
        n, ms = pontos[-1]
        o.append(f'<text x="{px(n)+12:.1f}" y="{py(ms)+4:.1f}" font-size="13" font-weight="600" fill="{TINTA}">{rotulo}</text>')
    o.append("</svg>")
    saida = PASTA / "auditoria-custo-46.svg"
    saida.write_text("\n".join(o), encoding="utf-8")
    print("gravado", saida)


if __name__ == "__main__":
    main()
