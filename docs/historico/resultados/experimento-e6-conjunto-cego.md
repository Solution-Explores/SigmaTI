# E6 — avaliação por identificador do corpus sintético

Amostras: 46; identificadores: 41.
Recall de transformação: 95.12% (IC 95% Wilson: [83.86%, 98.65%]).
Recall de proteção (transformação + bloqueio fail-closed): 100.00% (IC 95% Wilson: [91.43%, 100.00%]).
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

## Método e limites

Cada ocorrência tem valor original, classe e substituição esperada anotados. Nomes também têm fragmentos proibidos. Remover outro identificador da mensagem não aprova a ocorrência.
Bloqueio seguro (fail-closed, como no detector residual de nomes do IBGE) é contado separadamente do recall de transformação, compondo o recall de proteção contra vazamento externo. Os intervalos de confiança (95%) utilizam o método de Wilson para proporções binomiais. A precisão operacional combina ocorrências transformadas com mensagens negativas alteradas; não equivale à precisão por span de um modelo de reconhecimento de entidades.
Os resultados descrevem somente este corpus sintético. Não demonstram anonimização universal, conformidade jurídica ou ausência de vazamentos em dados hospitalares. Nomes sem contexto fora da lista de primeiros nomes frequentes do IBGE, OIDs numéricos com sub-sequências de 4 octetos compatíveis com IPv4 e hostnames fora dos padrões/lista configurados exigem novos casos e regras.
IPv4 é generalizado para /24 e IPv6 para /64. A identificação contextual não substitui avaliação de risco de reidentificação.

Com poucos identificadores, a meta de 99% não é demonstrável: mesmo sem nenhuma falha, o limite inferior do IC de Wilson só chega a 99% com cerca de 381 identificadores. Por isso o recall é relatado com o intervalo, e a conclusão vale só para este corpus.

Critério original (recall de transformação ≥ 99%, sem vazamento, FP ≤ 5%): REPROVADO.
Proteção contra vazamento externo (transformação + bloqueio, sem vazamento, FP ≤ 5%), relatada ao lado: ATENDIDA.
