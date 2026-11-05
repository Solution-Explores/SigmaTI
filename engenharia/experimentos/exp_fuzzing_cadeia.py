"""Experimento E4 — fuzzing da cadeia de hash da trilha de auditoria.

Hipótese H4: a verificação da cadeia (``AuditChain.verificar``) aponta
adulteração de uma trilha já gravada, e aponta a **primeira** entrada
inválida, não uma qualquer.

Método: gravar uma trilha de ``N`` entradas, aplicar **uma** mutação
aleatória por caso e verificar. Três tipos de mutação, todos sobre o arquivo
já gravado, como faria quem edita o arquivo por fora:

- ``byte``: troca um byte de uma linha por outro byte imprimível. Se a linha
  continuar sendo o mesmo JSON (um espaço fora de string, por exemplo), a
  mutação é reamostrada, porque não alterou a trilha;
- ``remocao``: apaga uma linha;
- ``troca``: troca duas linhas de lugar;
- ``truncamento``: apaga de 1 a 5 linhas do fim, como faria quem corta o
  rabo do arquivo para esconder o que acabou de fazer.

Critério da issue #11: em 100% dos casos a verificação deve apontar um índice
**menor ou igual** ao da mutação. Cada caso é conferido de dois modos:

1. ``verificar()``, que só lê o arquivo;
2. a **âncora** (``ancora()``), comparada com a âncora guardada antes da
   mutação — é o que detecta truncamento do fim, que a verificação sozinha
   não vê, porque uma trilha encurtada continua internamente coerente.

A chave usada é fixa e serve só ao experimento; não é segredo de produção.

Uso (a partir de ``engenharia/``)::

    python -m experimentos.exp_fuzzing_cadeia
    python -m experimentos.exp_fuzzing_cadeia --n 1000 --casos-por-tipo 200
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import tempfile
from pathlib import Path

from sigma_eng.audit_chain import AuditChain

N_PADRAO = 1000
CASOS_POR_TIPO_PADRAO = 200
SEMENTE_PADRAO = 20261104
CHAVE = b"experimento-e4-chave-fixa-nao-secreta"
TIPOS = ("byte", "remocao", "troca", "truncamento")
IMPRIMIVEIS = bytes(range(0x21, 0x7F))
SAIDA = Path(__file__).resolve().parent.parent / "resultados"


def gravar_trilha(caminho: Path, n: int) -> AuditChain:
    """Trilha de ``n`` entradas, com dados fictícios e sem nada pessoal."""
    cadeia = AuditChain(caminho, chave=CHAVE)
    for i in range(n):
        cadeia.registrar(
            ator=f"ator-{i % 7}",
            acao=("consulta", "registro", "rotacao", "revogacao")[i % 4],
            recurso=f"alvo-{i % 23}",
            detalhes={"i": i, "nota": "dado ficticio do experimento E4"},
        )
    return cadeia


def mutar_byte(linhas: list[bytes], rng: random.Random) -> tuple[list[bytes], int, int]:
    """Troca um byte de uma linha. Devolve (linhas, índice mutado, reamostragens)."""
    reamostragens = 0
    while True:
        i = rng.randrange(len(linhas))
        linha = linhas[i]
        pos = rng.randrange(len(linha))
        novo = rng.choice(IMPRIMIVEIS)
        if novo == linha[pos]:
            continue
        candidata = linha[:pos] + bytes([novo]) + linha[pos + 1:]
        if _mesmo_json(linha, candidata):
            # Mutação sem efeito (espaço fora de string, por exemplo): não vale como caso.
            reamostragens += 1
            continue
        novas = list(linhas)
        novas[i] = candidata
        return novas, i, reamostragens


def _mesmo_json(a: bytes, b: bytes) -> bool:
    try:
        return json.loads(a) == json.loads(b)
    except ValueError:
        return False


def mutar_remocao(linhas: list[bytes], rng: random.Random) -> tuple[list[bytes], int, int]:
    i = rng.randrange(len(linhas))
    return linhas[:i] + linhas[i + 1:], i, 0


def mutar_troca(linhas: list[bytes], rng: random.Random) -> tuple[list[bytes], int, int]:
    i, j = sorted(rng.sample(range(len(linhas)), 2))
    novas = list(linhas)
    novas[i], novas[j] = novas[j], novas[i]
    return novas, i, 0


def mutar_truncamento(linhas: list[bytes], rng: random.Random) -> tuple[list[bytes], int, int]:
    """Corta de 1 a 5 linhas do fim. O índice mutado é a primeira que desapareceu."""
    k = rng.randint(1, 5)
    return linhas[:-k], len(linhas) - k, 0


MUTACOES = {"byte": mutar_byte, "remocao": mutar_remocao, "troca": mutar_troca,
            "truncamento": mutar_truncamento}


def executar(n: int, casos_por_tipo: int, semente: int) -> list[dict]:
    rng = random.Random(semente)
    linhas_casos: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="e4-fuzzing-") as tmp:
        base = Path(tmp) / "trilha-base.jsonl"
        cadeia = gravar_trilha(base, n)
        integra, indice = cadeia.verificar()
        if not integra:
            raise RuntimeError(f"trilha de base já inválida no índice {indice}")
        ancora_boa = cadeia.ancora()
        originais = base.read_bytes().splitlines()

        caso = 0
        for tipo in TIPOS:
            for _ in range(casos_por_tipo):
                caso += 1
                mutadas, indice_mutado, reamostragens = MUTACOES[tipo](originais, rng)
                # Um arquivo por caso: o estado verificado em memória (#46) é por caminho,
                # e reusar o mesmo nome deixaria o cache influenciar a medição.
                alvo = Path(tmp) / f"trilha-mutada-{caso}.jsonl"
                alvo.write_bytes(b"\n".join(mutadas) + b"\n")
                sob_teste = AuditChain(alvo, chave=CHAVE)
                ok, reportado = sob_teste.verificar()
                ancora = sob_teste.ancora()
                pela_ancora = (ancora["entradas"] != ancora_boa["entradas"]
                               or ancora["ultimo_hash"] != ancora_boa["ultimo_hash"])
                aponta_antes = reportado is not None and reportado <= indice_mutado
                linhas_casos.append({
                    "caso": caso,
                    "tipo": tipo,
                    "indice_mutado": indice_mutado,
                    "indice_reportado": "" if reportado is None else reportado,
                    "detectado_verificar": int(not ok),
                    "indice_menor_ou_igual": int(aponta_antes),
                    "detectado_ancora": int(pela_ancora),
                    "ultima_entrada": int(indice_mutado >= len(originais) - 1),
                    "entradas_restantes": ancora["entradas"],
                    "reamostragens": reamostragens,
                })
    return linhas_casos


def resumir(casos: list[dict]) -> list[dict]:
    resumo = []
    for tipo in TIPOS:
        do_tipo = [c for c in casos if c["tipo"] == tipo]
        detectados = sum(c["detectado_verificar"] for c in do_tipo)
        corretos = sum(c["indice_menor_ou_igual"] for c in do_tipo)
        ancora = sum(c["detectado_ancora"] for c in do_tipo)
        escapes = [c for c in do_tipo if not c["detectado_verificar"]]
        resumo.append({
            "tipo": tipo,
            "casos": len(do_tipo),
            "detectados_por_verificar": detectados,
            "taxa_verificar": round(detectados / len(do_tipo), 4),
            "indice_menor_ou_igual": corretos,
            "detectados_pela_ancora": ancora,
            "taxa_ancora": round(ancora / len(do_tipo), 4),
            "escapes_na_ultima_entrada": sum(c["ultima_entrada"] for c in escapes),
        })
    return resumo


def tabela(linhas: list[dict]) -> str:
    cab = list(linhas[0])
    md = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    md += ["| " + " | ".join(str(l[c]) for c in cab) + " |" for l in linhas]
    return "\n".join(md)


def main() -> None:
    p = argparse.ArgumentParser(description="E4: fuzzing da cadeia de auditoria")
    p.add_argument("--n", type=int, default=N_PADRAO, help="entradas por trilha")
    p.add_argument("--casos-por-tipo", type=int, default=CASOS_POR_TIPO_PADRAO)
    p.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    args = p.parse_args()

    casos = executar(args.n, args.casos_por_tipo, args.semente)
    resumo = resumir(casos)

    SAIDA.mkdir(exist_ok=True)
    with (SAIDA / "e4_fuzzing_cadeia.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(casos[0]))
        w.writeheader()
        w.writerows(casos)
    with (SAIDA / "e4_fuzzing_cadeia_resumo.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(resumo[0]))
        w.writeheader()
        w.writerows(resumo)

    print(f"trilha de {args.n} entradas, {len(casos)} casos, semente {args.semente}")
    print(tabela(resumo))


if __name__ == "__main__":
    main()
