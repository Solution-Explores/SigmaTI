"""E6: avalia cada identificador anotado, separando vazamento e bloqueio seguro."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
from sanitizer import sanitizar_texto


def intervalo_wilson(sucessos: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de Wilson (95%) em percentual para proporções."""
    if total <= 0:
        return (0.0, 0.0)
    p = sucessos / total
    denom = 1.0 + (z * z) / total
    centro = (p + (z * z) / (2.0 * total)) / denom
    margem = (z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * total)) / total)) / denom
    inf = max(0.0, (centro - margem) * 100.0)
    sup = min(100.0, (centro + margem) * 100.0)
    return (inf, sup)


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
    protegidos = removidos + bloqueados_id
    recall = 100 * removidos / total if total else 0
    recall_protecao = 100 * protegidos / total if total else 0
    taxa_bloqueio = 100 * bloqueados_id / total if total else 0
    precisao = 100 * removidos / (removidos + fp) if removidos + fp else 0
    taxa_fp = 100 * fp / negativos if negativos else 0
    ic_recall = intervalo_wilson(removidos, total)
    ic_protecao = intervalo_wilson(protegidos, total)
    ic_precisao = intervalo_wilson(removidos, removidos + fp)
    ic_fp = intervalo_wilson(fp, negativos)
    return {"total_amostras": len(corpus), "total_identificadores": total,
            "removidos": removidos, "bloqueados": bloqueados_id, "vazados": vazados,
            "casos_bloqueados": bloqueados, "negativos": negativos, "fp": fp,
            "recall": recall, "ic_recall": ic_recall,
            "recall_protecao": recall_protecao, "ic_protecao": ic_protecao,
            "taxa_bloqueio": taxa_bloqueio,
            "precisao": precisao, "ic_precisao": ic_precisao,
            "taxa_fp": taxa_fp, "ic_fp": ic_fp,
            "por_classe": dict(classes), "detalhes": detalhes,
            # Critério original do E6 (21/10), mantido: transformação conta, bloqueio não.
            "aprovado": total > 0 and vazados == 0 and recall >= 99 and taxa_fp <= 5,
            # Proteção contra vazamento externo, relatada ao lado (com teto de bloqueio para evitar 'bloquear tudo').
            "aprovado_protecao": (total > 0 and vazados == 0 and recall_protecao >= 99
                                  and taxa_fp <= 5 and taxa_bloqueio <= 20)}


def gerar_relatorio_markdown(m, destino):
    ic_rec = m["ic_recall"]
    ic_prot = m["ic_protecao"]
    ic_prec = m["ic_precisao"]
    ic_fp = m["ic_fp"]
    linhas = ["# E6 — avaliação por identificador do corpus sintético", "",
              f"Amostras: {m['total_amostras']}; identificadores: {m['total_identificadores']}.",
              f"Recall de transformação: {m['recall']:.2f}% (IC 95% Wilson: [{ic_rec[0]:.2f}%, {ic_rec[1]:.2f}%]).",
              f"Recall de proteção (transformação + bloqueio fail-closed): {m['recall_protecao']:.2f}% (IC 95% Wilson: [{ic_prot[0]:.2f}%, {ic_prot[1]:.2f}%]).",
              f"Precisão operacional: {m['precisao']:.2f}% (IC 95% Wilson: [{ic_prec[0]:.2f}%, {ic_prec[1]:.2f}%]).",
              f"Falsos positivos por mensagem negativa: {m['taxa_fp']:.2f}% ({m['fp']}/{m['negativos']}, IC 95% Wilson: [{ic_fp[0]:.2f}%, {ic_fp[1]:.2f}%]).",
              f"Identificadores bloqueados: {m['bloqueados']}; vazados: {m['vazados']}.", "",
              "| Classe | Total | Removidos/generalizados | Bloqueados | Vazados |",
              "|---|---:|---:|---:|---:|"]
    for classe, d in sorted(m["por_classe"].items()):
        linhas.append(f"| {classe} | {d['total']} | {d['removidos']} | {d['bloqueados']} | {d['vazados']} |")
    linhas += ["", "## Método e limites", "",
               "Cada ocorrência tem valor original, classe e substituição esperada anotados. "
               "Nomes também têm fragmentos proibidos. Remover outro identificador da mensagem não aprova a ocorrência.",
               "Bloqueio seguro (fail-closed, como no detector residual de nomes do IBGE) é contado separadamente "
               "do recall de transformação, compondo o recall de proteção contra vazamento externo. "
               "Os intervalos de confiança (95%) utilizam o método de Wilson para proporções binomiais. "
               "A precisão operacional combina ocorrências transformadas com mensagens negativas alteradas; "
               "não equivale à precisão por span de um modelo de reconhecimento de entidades.",
               "Os resultados descrevem somente este corpus sintético. Não demonstram anonimização universal, "
               "conformidade jurídica ou ausência de vazamentos em dados hospitalares. Nomes sem contexto fora da lista "
               "de primeiros nomes frequentes do IBGE, OIDs numéricos com sub-sequências de 4 octetos compatíveis com IPv4 "
               "e hostnames fora dos padrões/lista configurados exigem novos casos e regras.",
               "IPv4 é generalizado para /24 e IPv6 para /64. A identificação contextual não substitui "
               "avaliação de risco de reidentificação.", "",
               "Com poucos identificadores, a meta de 99% não é demonstrável: mesmo sem nenhuma falha, o limite "
               "inferior do IC de Wilson só chega a 99% com cerca de 381 identificadores. Por isso o recall é "
               "relatado com o intervalo, e a conclusão vale só para este corpus.", "",
               f"Critério original (recall de transformação ≥ 99%, sem vazamento, FP ≤ 5%): "
               f"{'APROVADO' if m['aprovado'] else 'REPROVADO'}.",
               f"Proteção contra vazamento externo (transformação + bloqueio, sem vazamento, FP ≤ 5%), "
               f"relatada ao lado: {'ATENDIDA' if m['aprovado_protecao'] else 'NÃO ATENDIDA'}."]
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "backend/tests/data/corpus_sintetico_pii.json")
    parser.add_argument("--output", type=Path, default=ROOT / "engenharia/resultados/experimento-e6-anonimizacao.md")
    args = parser.parse_args()
    m = executar_experimento(carregar_corpus(args.corpus))
    gerar_relatorio_markdown(m, args.output)
    print(json.dumps({k: v for k, v in m.items() if k not in {"detalhes", "por_classe"}}, ensure_ascii=False))
    return 0 if m["aprovado"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
