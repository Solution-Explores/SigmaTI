# E6 — avaliação por identificador do corpus sintético

Amostras: 59; identificadores: 53.
Recall de transformação: 100.00% (IC 95% Wilson: [93.24%, 100.00%]).
Recall de proteção (transformação + bloqueio fail-closed): 100.00% (IC 95% Wilson: [93.24%, 100.00%]).
Precisão operacional: 100.00% (IC 95% Wilson: [93.24%, 100.00%]).
Falsos positivos por mensagem negativa: 0.00% (0/25, IC 95% Wilson: [0.00%, 13.32%]).
Identificadores bloqueados: 0; vazados: 0.

| Classe | Total | Removidos/generalizados | Bloqueados | Vazados |
|---|---:|---:|---:|---:|
| cns | 3 | 3 | 0 | 0 |
| cpf | 5 | 5 | 0 | 0 |
| email | 4 | 4 | 0 | 0 |
| hostname | 8 | 8 | 0 | 0 |
| ipv4 | 10 | 10 | 0 | 0 |
| ipv6 | 5 | 5 | 0 | 0 |
| mac | 3 | 3 | 0 | 0 |
| nome | 12 | 12 | 0 | 0 |
| prontuario | 3 | 3 | 0 | 0 |

## Método e limites

Cada ocorrência tem valor original, classe e substituição esperada anotados. Nomes também têm fragmentos proibidos. Remover outro identificador da mensagem não aprova a ocorrência.
Bloqueio seguro (fail-closed, como no detector residual de nomes do IBGE) é contado separadamente do recall de transformação, compondo o recall de proteção contra vazamento externo. Os intervalos de confiança (95%) utilizam o método de Wilson para proporções binomiais. A precisão operacional combina ocorrências transformadas com mensagens negativas alteradas; não equivale à precisão por span de um modelo de reconhecimento de entidades.
Os resultados descrevem somente este corpus sintético. Não demonstram anonimização universal, conformidade jurídica ou ausência de vazamentos em dados hospitalares. Nomes sem contexto fora da lista de primeiros nomes frequentes do IBGE, OIDs numéricos com sub-sequências de 4 octetos compatíveis com IPv4 e hostnames fora dos padrões/lista configurados exigem novos casos e regras.
IPv4 é generalizado para /24 e IPv6 para /64. A identificação contextual não substitui avaliação de risco de reidentificação.

Resultado do corpus: APROVADO.
