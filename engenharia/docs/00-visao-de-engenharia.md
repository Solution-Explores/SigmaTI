# 00 · Visão de engenharia

## Por que "engenharia" e não só "software"

O MVP do SIGMA demonstra o fluxo (alerta → anonimização → IA → painel). Um TCC de Engenharia da Computação precisa ir além da demonstração: **definir o que significa "funcionar", medir, e mostrar que o resultado se sustenta**. Esta camada acrescenta:

| Dimensão | No MVP | Com o núcleo de engenharia |
|---|---|---|
| Requisitos | Metas em texto (RF01: 5 s) | Métrica definida, instrumento de medição e teste automatizado |
| Detecção | Alerta quando o pfSense avisa | Detectores estatísticos online, com precisão/revocação/atraso medidos |
| Confiabilidade | Sem indicador | SLO, orçamento de erros e burn rate multi-janela |
| Resposta | MTTR citado, não calculado | MTTD/MTTA/MTTR com definição fixa e estatística de cauda |
| Integridade | Logs comuns | Trilha de auditoria com cadeia de hash (adulteração é detectável) |
| Operação segura | Ações manuais | Runbooks com dry-run, allowlist e aprovação humana por passo |
| Reprodutibilidade | — | Experimentos com semente fixa e saída em CSV |

## Problema de pesquisa

> Em uma rede hospitalar com equipe de TI reduzida, é possível reduzir o tempo de detecção (MTTD) e dar rastreabilidade às ações de resposta usando apenas componentes de custo zero de licença, preservando a LGPD?

## Hipóteses (testáveis)

- **H1.** Detectores estatísticos online (EWMA, MAD) detectam degradações de latência do tipo degrau/pico com atraso ≤ 1 amostra e menos de 2 falsos positivos por 600 amostras. *(Testada em E1; confirmada para degrau/pico, **refutada para deriva lenta**.)*
- **H2.** O alerta de burn rate em duas janelas pagina em quedas totais em até 5 min e **não** pagina em picos de segundos. *(Testes unitários; E3 mede em rede real.)*
- **H3.** A cadeia de hash detecta 100% das adulterações, remoções e reordenações de registros. *(Testes unitários; E4 faz fuzzing.)*
- **H4.** O pipeline completo atende RF01 (≤ 5 s) e RNF04 (≤ 15 s) no hardware do hospital. *(E2 e E5.)*

## Contribuições

1. Núcleo de monitoramento medido e testado (58 testes), inspirado em funcionalidades do Vigilark.
2. Quatro propriedades de correção e segurança garantidas por testes de regressão (ver [mapeamento](01-mapeamento-vigilark-sigma.md#propriedades-garantidas-com-teste)).
3. Metodologia experimental reproduzível (`experimentos/`).
4. Um achado negativo documentado: detectores por limiar não cobrem deriva lenta, o que motiva trabalho futuro com CUSUM/Page-Hinkley.
