"""E6: avalia cada identificador anotado, separando vazamento e bloqueio seguro."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sanitizer import sanitizar_texto


def carregar_corpus(caminho):
    corpus = json.loads(Path(caminho).read_text(encoding="utf-8"))
    for caso in corpus:
        anotacoes = caso["identificadores"]
        if caso["tipo"] == "positivo" and not anotacoes:
            raise ValueError("Caso positivo sem anotações individuais.")
        for a in anotacoes:
            if (not isinstance(a, dict) or not a.get("classe") or not a.get("valor")
                    or not a.get("substituto") or a["valor"] not in caso["entrada"]):
                raise ValueError("Anotação individual inválida.")
    return corpus


def executar_experimento(corpus):
    classes = defaultdict(lambda: {"total": 0, "removidos": 0, "bloqueados": 0, "vazados": 0})
    detalhes = []
    negativos = fp = bloqueados = 0
    for caso in corpus:
        resultado = sanitizar_texto(caso["entrada"])
        if not resultado.sucesso:
            bloqueados += 1
        if caso["tipo"] == "negativo":
            negativos += 1
            fp += int(not resultado.sucesso or resultado.texto_sanitizado != caso["entrada"])
            continue
        if not caso["identificadores"]:
            raise ValueError("Caso positivo sem anotações individuais.")
        for a in caso["identificadores"]:
            if not isinstance(a, dict):
                raise ValueError("E6 exige identificadores anotados individualmente.")
            estat = classes[a["classe"]]
            estat["total"] += 1
            if not resultado.sucesso:
                estado = "bloqueados"
            else:
                saida = resultado.texto_sanitizado
                restante = saida.replace(a["substituto"], "")
                preservado = any(re.search(re.escape(v), restante, re.IGNORECASE)
                                 for v in a.get("proibidos", [a["valor"]]))
                estado = "removidos" if not preservado and a["substituto"] in saida else "vazados"
            estat[estado] += 1
            detalhes.append({"caso": caso["id"], "classe": a["classe"], "estado": estado})
    total = sum(c["total"] for c in classes.values())
    removidos = sum(c["removidos"] for c in classes.values())
    vazados = sum(c["vazados"] for c in classes.values())
    bloqueados_id = sum(c["bloqueados"] for c in classes.values())
    recall = 100 * removidos / total if total else 0
    precisao = 100 * removidos / (removidos + fp) if removidos + fp else 0
    taxa_fp = 100 * fp / negativos if negativos else 0
    return {"total_amostras": len(corpus), "total_identificadores": total,
            "removidos": removidos, "bloqueados": bloqueados_id, "vazados": vazados,
            "casos_bloqueados": bloqueados, "negativos": negativos, "fp": fp,
            "recall": recall, "precisao": precisao, "taxa_fp": taxa_fp,
            "por_classe": dict(classes), "detalhes": detalhes,
            "aprovado": total > 0 and vazados == 0 and recall >= 99 and taxa_fp <= 5}


def gerar_relatorio_markdown(m, destino):
    linhas = ["# E6 — avaliação por identificador do corpus sintético", "",
              f"Amostras: {m['total_amostras']}; identificadores: {m['total_identificadores']}.",
              f"Recall de transformação: {m['recall']:.2f}%; precisão operacional: {m['precisao']:.2f}%.",
              f"Falsos positivos por mensagem negativa: {m['taxa_fp']:.2f}%.",
              f"Identificadores bloqueados: {m['bloqueados']}; vazados: {m['vazados']}.", "",
              "| Classe | Total | Removidos/generalizados | Bloqueados | Vazados |",
              "|---|---:|---:|---:|---:|"]
    for classe, d in sorted(m["por_classe"].items()):
        linhas.append(f"| {classe} | {d['total']} | {d['removidos']} | {d['bloqueados']} | {d['vazados']} |")
    linhas += ["", "## Método e limites", "",
               "Cada ocorrência tem valor original, classe e substituição esperada anotados. "
               "Nomes também têm fragmentos proibidos. Remover outro identificador da mensagem não aprova a ocorrência.",
               "Bloqueio seguro é contado separadamente e não aumenta o recall de transformação. "
               "A precisão operacional combina ocorrências transformadas com mensagens negativas alteradas; "
               "não equivale à precisão por span de um modelo de reconhecimento de entidades.",
               "Os resultados descrevem somente este corpus sintético. Não demonstram anonimização universal, "
               "conformidade jurídica ou ausência de vazamentos em dados hospitalares. Nomes sem contexto e "
               "hostnames fora dos padrões/lista configurados exigem novos casos e regras.",
               "IPv4 é generalizado para /24 e IPv6 para /64. A identificação contextual não substitui "
               "avaliação de risco de reidentificação.", "",
               f"Resultado do corpus: {'APROVADO' if m['aprovado'] else 'REPROVADO'}."]
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "tests/data/corpus_sintetico_pii.json")
    parser.add_argument("--output", type=Path, default=ROOT / "engenharia/resultados/experimento-e6-anonimizacao.md")
    args = parser.parse_args()
    m = executar_experimento(carregar_corpus(args.corpus))
    gerar_relatorio_markdown(m, args.output)
    print(json.dumps({k: v for k, v in m.items() if k not in {"detalhes", "por_classe"}}, ensure_ascii=False))
    return 0 if m["aprovado"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
