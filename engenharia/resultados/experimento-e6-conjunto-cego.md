# E6 — avaliação por identificador do conjunto cego (#5)

Amostras: 46 (26 positivas e 20 negativas); identificadores anotados: 41.
Recall de transformação: 95.12% (39/41, IC 95% Wilson: [83.86%, 98.65%]).
Recall de proteção (transformação + bloqueio fail-closed): 100.00% (41/41, IC 95% Wilson: [91.43%, 100.00%]).
Taxa de bloqueio por identificador: 4.88% (2/41, teto operacional: ≤ 20.00%).
Precisão operacional: 97.50% (IC 95% Wilson: [87.12%, 99.56%]).
Falsos positivos por mensagem negativa: 5.00% (1/20, IC 95% Wilson: [0.89%, 23.61%]).
Identificadores bloqueados: 2; vazados: 0.

| Classe | Total | Removidos/generalizados | Bloqueados | Vazados |
|---|---:|---:|---:|---:|
| cns | 2 | 2 | 0 | 0 |
| cpf | 3 | 3 | 0 | 0 |
| data_nascimento | 1 | 1 | 0 | 0 |
| email | 2 | 2 | 0 | 0 |
| endereco | 2 | 2 | 0 | 0 |
| hostname | 9 | 9 | 0 | 0 |
| ipv4 | 2 | 2 | 0 | 0 |
| ipv6 | 2 | 2 | 0 | 0 |
| login | 3 | 3 | 0 | 0 |
| mac | 3 | 3 | 0 | 0 |
| nome | 6 | 4 | 2 | 0 |
| prontuario | 1 | 1 | 0 | 0 |
| registro_atendimento | 1 | 1 | 0 | 0 |
| rg | 1 | 1 | 0 | 0 |
| telefone | 3 | 3 | 0 | 0 |

## Proveniência e independência metodológica

- **Autoria e registro no Git:** o conjunto (`backend/tests/data/corpus_cego_pii.json`) foi redigido por Iohan Jheremy e commitado em `034dc64` (`2026-11-02 00:54:57 -0400`) na branch `feature/5-regressao-conjunto-cego`, aproximadamente 11 horas após o commit das regras de anonimização (`875db84`, `2026-11-01 13:34:08 -0400`). Como o formato do experimento exige o campo `substituto` (marcador exato produzido pelo sanitizador), o autor conhecia os marcadores de saída da implementação, de modo que o histórico do Git comprova autoria distinta das regras, mas não isolamento temporal anterior à implementação.
- **Sobreposição de molde com a conferência:** 14 dos 26 casos positivos reproduzem a estrutura sintática dos 14 casos da conferência de 31/10/2026 com novos valores lexicais; portanto, medem cobertura e não-regressão dos padrões conhecidos, e não generalização irrestrita para formatos inéditos.

## Método e limites

Cada ocorrência tem valor original, classe e substituição esperada anotados. Nomes também têm fragmentos proibidos. Remover outro identificador da mensagem não aprova a ocorrência.
Bloqueio seguro (fail-closed, como no detector residual de nomes do IBGE) é contado separadamente do recall de transformação, compondo o recall de proteção contra vazamento externo. Os intervalos de confiança (95%) utilizam o método de Wilson para proporções binomiais. A precisão operacional combina ocorrências transformadas com mensagens negativas alteradas; não equivale à precisão por span de um modelo de reconhecimento de entidades.
Os resultados descrevem somente este corpus sintético. Não demonstram anonimização universal, conformidade jurídica ou ausência de vazamentos em dados hospitalares. Nomes sem contexto fora da lista de primeiros nomes frequentes do IBGE, nomes totalmente em caixa alta sem contexto (quando `RE_NOME_SEM_CONTEXTO` exige inicial maiúscula seguida de minúsculas), OIDs numéricos com sub-sequências de 4 octetos compatíveis com IPv4 e hostnames fora dos padrões/lista configurados exigem novos casos e regras.
IPv4 é generalizado para /24 e IPv6 para /64. A identificação contextual não substitui avaliação de risco de reidentificação.

Com 41 identificadores, o limite inferior do IC 95% de Wilson para 41/41 é 91.43%. Demonstrar estatisticamente um limite inferior ≥ 99% com 95% de confiança exigiria cerca de 381 identificadores sem nenhuma falha. Por isso a meta de 99% vale apenas como estimativa pontual neste corpus, e não como garantia estatística demonstrada.

Critério original (recall de transformação ≥ 99%, sem vazamento, FP ≤ 5%): REPROVADO.
Proteção contra vazamento externo (transformação + bloqueio, sem vazamento, FP ≤ 5%, bloqueio ≤ 20%), relatada ao lado: ATENDIDA.
