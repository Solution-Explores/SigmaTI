"""Benchmark do custo da trilha de auditoria (#46): gravação, login e verificação por tamanho da trilha.

Uso (da raiz do repositório; só dados sintéticos, nada é gravado fora da pasta temporária):
  python scripts/benchmark_auditoria.py --tamanhos 1000 10000 100000 --repeticoes 7 --saida resultado.json

Para comparar antes/depois, rode o mesmo comando com ``PYTHONPATH`` apontando para o ``engenharia/``
do código antigo e do novo. A trilha é montada direto no disco (sem fsync por linha) com o mesmo
formato e a mesma chave HMAC que ``AuditChain`` usa, e é conferida por ``verificar()`` antes de medir.

Operações medidas (ms, mediana e p95 entre as repetições):
  login             nova instância + registrar(), com 0,2 s entre tentativas (uso normal)
  gravacao_repouso  nova instância + registrar() com a trilha parada há mais de 3 s
  gravacao_rajada   registrar() sem intervalo: a escrita anterior é recente demais para o cache
                    confiar no timestamp, e os bytes são reconferidos (pior caso do cache)
  verificar         verificar() completo (sempre O(n); é a checagem explícita e a do job diário)
  partida_fria      primeira gravação de um processo novo (sem cache nenhum)
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engenharia"))

from sigma_eng.audit_chain import GENESIS, AuditChain  # noqa: E402

CHAVE = b"benchmark-auditoria-chave-sintetica-32b"


def montar_trilha(caminho: Path, tamanho: int) -> None:
    """Escreve ``tamanho`` entradas válidas, no mesmo formato de AuditChain, sem fsync por linha."""
    anterior = GENESIS
    ts = datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat()
    with caminho.open("wb") as fh:
        for seq in range(tamanho):
            corpo = {"seq": seq, "ts": ts, "ator": "benchmark", "acao": "benchmark.evento",
                     "recurso": "alvo-%d" % (seq % 200), "detalhes": {"n": seq}, "anterior": anterior}
            dados = json.dumps(corpo, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            entrada = {**corpo, "hash": hmac.new(CHAVE, dados, hashlib.sha256).hexdigest()}
            fh.write((json.dumps(entrada, ensure_ascii=False) + "\n").encode())
            anterior = entrada["hash"]


def p95(valores: list[float]) -> float:
    ordenado = sorted(valores)
    return ordenado[min(len(ordenado) - 1, int(round(0.95 * (len(ordenado) - 1))))]


def resumo(valores: list[float]) -> dict:
    return {"mediana_ms": round(statistics.median(valores), 2), "p95_ms": round(p95(valores), 2),
            "min_ms": round(min(valores), 2), "max_ms": round(max(valores), 2), "amostras": len(valores)}


def medir(fn) -> float:
    inicio = time.perf_counter()
    fn()
    return (time.perf_counter() - inicio) * 1000


def partida_fria(caminho: Path) -> float:
    """Gravação em um processo novo, como depois de reiniciar a API."""
    codigo = ("import sys,time; sys.path.insert(0, r'%s'); from sigma_eng.audit_chain import AuditChain; "
              "t=time.perf_counter(); AuditChain(sys.argv[1], chave=%r).registrar('a','partida.fria'); "
              "print((time.perf_counter()-t)*1000)" % (ROOT / "engenharia", CHAVE))
    saida = subprocess.run([sys.executable, "-c", codigo, str(caminho)], capture_output=True, text=True, check=True)
    return float(saida.stdout.strip())


def rodar(tamanho: int, repeticoes: int, pasta: Path) -> dict:
    caminho = pasta / f"audit-{tamanho}.jsonl"
    montar_trilha(caminho, tamanho)
    abrir = lambda: AuditChain(caminho, chave=CHAVE)
    ok, indice = abrir().verificar()
    assert ok, f"trilha sintética inválida na entrada {indice}"
    resultado = {"tamanho": tamanho, "bytes": caminho.stat().st_size}
    resultado["verificar"] = resumo([medir(lambda: abrir().verificar()) for _ in range(repeticoes)])
    resultado["partida_fria"] = resumo([partida_fria(caminho) for _ in range(max(3, repeticoes // 2))])
    abrir().registrar("benchmark", "aquecimento")
    login = []
    for _ in range(repeticoes):
        time.sleep(0.2)  # fora da janela de escrita recente do cache
        login.append(medir(lambda: abrir().registrar("login", "auth.login")))
    resultado["login"] = resumo(login)
    repouso = []
    for _ in range(max(3, repeticoes // 2)):
        time.sleep(3.2)  # trilha parada: sai da janela de 2 s do cache
        repouso.append(medir(lambda: abrir().registrar("login", "auth.login")))
    resultado["gravacao_repouso"] = resumo(repouso)
    resultado["gravacao_rajada"] = resumo([medir(lambda: abrir().registrar("api", "evento.rajada")) for _ in range(repeticoes)])
    return resultado


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tamanhos", type=int, nargs="+", default=[1000, 10000, 100000])
    parser.add_argument("--repeticoes", type=int, default=7)
    parser.add_argument("--saida", type=Path, help="JSON com o resultado")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="auditoria-bench-") as tmp:
        resultados = []
        for tamanho in args.tamanhos:
            resultado = rodar(tamanho, args.repeticoes, Path(tmp))
            resultados.append(resultado)
            linha = "  ".join(f"{k}={resultado[k]['mediana_ms']}ms" for k in
                              ("login", "gravacao_repouso", "gravacao_rajada", "verificar", "partida_fria"))
            print(f"{tamanho:>8} entradas  {linha}", flush=True)
    relatorio = {"python": sys.version.split()[0], "plataforma": sys.platform, "resultados": resultados}
    if args.saida:
        args.saida.write_text(json.dumps(relatorio, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
