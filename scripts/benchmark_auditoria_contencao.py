"""Contenção da trilha de auditoria (#46): vários processos gravando ao mesmo tempo na mesma trilha.

Complementa ``benchmark_auditoria.py``, que mede um processo por vez. Aqui N processos disparam
``registrar()`` juntos sobre uma trilha de tamanho fixo e se mede a latência por gravação, os erros
(por exemplo, o lock de 10 s expirando) e, no fim, se a cadeia continua íntegra, sem entrada perdida
nem duplicada. Só dados sintéticos, em pasta temporária.

Uso (da raiz do repositório):
  python scripts/benchmark_auditoria_contencao.py --tamanho 100000 --processos 1 4 8 \\
      --gravacoes 20 --saida contencao.json

Para comparar antes/depois, rode o mesmo comando em dois checkouts (o do código antigo e o do novo):
o script usa o ``engenharia/`` do checkout em que está. ``--intervalo-ms`` espaça as gravações de cada
processo (0 = rajada contínua, o pior caso).
"""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engenharia"))
sys.path.insert(0, str(ROOT / "scripts"))

from benchmark_auditoria import CHAVE, montar_trilha, p95  # noqa: E402
from sigma_eng.audit_chain import AuditChain  # noqa: E402


def trabalhador(caminho: Path, gravacoes: int, intervalo_ms: float, inicio: float, indice: int) -> int:
    """Um processo: espera o instante combinado, grava ``gravacoes`` vezes e imprime o resultado em JSON."""
    latencias, erros = [], {}
    primeira_ok = False
    while time.time() < inicio:
        time.sleep(0.001)
    for i in range(gravacoes):
        t0 = time.perf_counter()
        try:
            AuditChain(caminho, chave=CHAVE).registrar("worker-%d" % indice, "contencao.evento", detalhes={"i": i})
            latencias.append((time.perf_counter() - t0) * 1000)
            if i == 0:
                primeira_ok = True
        except Exception as exc:  # o que interessa é o tipo: lock expirado, trilha inválida etc.
            erros[type(exc).__name__] = erros.get(type(exc).__name__, 0) + 1
        if intervalo_ms:
            time.sleep(intervalo_ms / 1000)
    # A primeira gravação de um processo novo não tem cache: custa uma verificação completa sob o lock.
    print(json.dumps({"primeira_ms": latencias[0] if latencias and primeira_ok else None,
                      "latencias_ms": latencias[1:] if primeira_ok else latencias, "erros": erros}))
    return 0


def rodada(base: Path, pasta: Path, tamanho: int, processos: int, gravacoes: int, intervalo_ms: float) -> dict:
    caminho = pasta / f"contencao-{processos}p.jsonl"
    shutil.copyfile(base, caminho)
    ponto = base.with_name(base.name + ".checkpoint")  # ponto de verificação (#46, opção D), se existir
    if ponto.exists():
        shutil.copyfile(ponto, caminho.with_name(caminho.name + ".checkpoint"))
    esperadas = processos * gravacoes
    inicio = time.time() + 3.0  # tempo para todos os processos importarem antes do disparo
    comandos = [[sys.executable, __file__, "--trabalhador", str(caminho), str(gravacoes), str(intervalo_ms),
                 str(inicio), str(i)] for i in range(processos)]
    t0 = time.perf_counter()
    filhos = [subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for c in comandos]
    saidas = [f.communicate(timeout=1800) for f in filhos]
    parede = time.perf_counter() - t0 - 3.0
    latencias, primeiras, erros, falhas_processo = [], [], {}, 0
    for filho, (out, err) in zip(filhos, saidas):
        if filho.returncode != 0 or not out.strip():
            falhas_processo += 1
            continue
        dado = json.loads(out.strip().splitlines()[-1])
        latencias += dado["latencias_ms"]
        if dado["primeira_ms"] is not None:
            primeiras.append(dado["primeira_ms"])
        for k, v in dado["erros"].items():
            erros[k] = erros.get(k, 0) + v
    cadeia = AuditChain(caminho, chave=CHAVE)
    integra, primeira_invalida = cadeia.verificar()
    entradas = len(cadeia)
    resultado = {
        "processos": processos, "gravacoes_por_processo": gravacoes, "intervalo_ms": intervalo_ms,
        "tamanho_inicial": tamanho, "gravacoes_esperadas": esperadas, "gravacoes_ok": len(latencias) + len(primeiras),
        "erros": erros, "processos_com_falha": falhas_processo,
        "entradas_finais": entradas, "entradas_esperadas": tamanho + len(latencias) + len(primeiras),
        "integra": integra, "primeira_invalida": primeira_invalida,
        "sem_perda_nem_duplicacao": entradas == tamanho + len(latencias) + len(primeiras),
        "tempo_total_s": round(parede, 2),
        "vazao_gravacoes_por_s": round(len(latencias) / parede, 2) if parede > 0 else None,
    }
    todas = latencias + primeiras
    if todas:
        resultado.update({"mediana_ms": round(statistics.median(todas), 2), "p95_ms": round(p95(todas), 2),
                          "max_ms": round(max(todas), 2)})
    if primeiras:
        resultado["partida_fria"] = {"amostras": len(primeiras), "mediana_ms": round(statistics.median(primeiras), 2),
                                     "max_ms": round(max(primeiras), 2)}
    if latencias:
        resultado["demais_gravacoes"] = {"amostras": len(latencias), "mediana_ms": round(statistics.median(latencias), 2),
                                         "p95_ms": round(p95(latencias), 2), "max_ms": round(max(latencias), 2)}
    return resultado


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--trabalhador":
        _, _, caminho, gravacoes, intervalo, inicio, indice = sys.argv
        return trabalhador(Path(caminho), int(gravacoes), float(intervalo), float(inicio), int(indice))
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tamanho", type=int, default=100000, help="entradas iniciais da trilha")
    parser.add_argument("--processos", type=int, nargs="+", default=[1, 4, 8])
    parser.add_argument("--gravacoes", type=int, default=20, help="gravações por processo")
    parser.add_argument("--intervalo-ms", type=float, default=0.0, help="espera entre gravações de cada processo")
    parser.add_argument("--saida", type=Path, help="JSON com o resultado")
    parser.add_argument("--sem-ponto", action="store_true",
                        help="apaga o ponto de verificação da trilha-base: mede a partida fria sem ele")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="auditoria-contencao-") as tmp:
        pasta = Path(tmp)
        base = pasta / "base.jsonl"
        montar_trilha(base, args.tamanho)
        ok, indice = AuditChain(base, chave=CHAVE).verificar()
        assert ok, f"trilha sintética inválida na entrada {indice}"
        if args.sem_ponto:
            base.with_name(base.name + ".checkpoint").unlink(missing_ok=True)
        resultados = []
        for n in args.processos:
            r = rodada(base, pasta, args.tamanho, n, args.gravacoes, args.intervalo_ms)
            resultados.append(r)
            print(f"{n:>2} processos  ok={r['gravacoes_ok']}/{r['gravacoes_esperadas']}  "
                  f"mediana={r.get('mediana_ms')}ms  p95={r.get('p95_ms')}ms  max={r.get('max_ms')}ms  "
                  f"erros={r['erros'] or 0}  integra={r['integra']}  sem_perda={r['sem_perda_nem_duplicacao']}",
                  flush=True)
            if "partida_fria" in r and "demais_gravacoes" in r:
                print(f"           1a gravacao de cada processo: mediana={r['partida_fria']['mediana_ms']}ms "
                      f"max={r['partida_fria']['max_ms']}ms | demais: mediana={r['demais_gravacoes']['mediana_ms']}ms "
                      f"p95={r['demais_gravacoes']['p95_ms']}ms max={r['demais_gravacoes']['max_ms']}ms", flush=True)
    relatorio = {"python": sys.version.split()[0], "plataforma": sys.platform, "tamanho": args.tamanho,
                 "resultados": resultados}
    if args.saida:
        args.saida.write_text(json.dumps(relatorio, indent=2), encoding="utf-8")
    return 0 if all(r["integra"] and r["sem_perda_nem_duplicacao"] and not r["processos_com_falha"] for r in resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main())
