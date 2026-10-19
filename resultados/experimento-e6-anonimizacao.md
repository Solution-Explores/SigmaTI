# E6 — avaliação por identificador do corpus sintético

Amostras: 56; identificadores: 50.
Recall de transformação: 100.00%; precisão operacional: 100.00%.
Falsos positivos por mensagem negativa: 0.00%.
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
| nome | 9 | 9 | 0 | 0 |
| prontuario | 3 | 3 | 0 | 0 |

## Método e limites

Cada ocorrência tem valor original, classe e substituição esperada anotados. Nomes também têm fragmentos proibidos. Remover outro identificador da mensagem não aprova a ocorrência.
Bloqueio seguro é contado separadamente e não aumenta o recall de transformação. A precisão operacional combina ocorrências transformadas com mensagens negativas alteradas; não equivale à precisão por span de um modelo de reconhecimento de entidades.
Os resultados descrevem somente este corpus sintético. Não demonstram anonimização universal, conformidade jurídica ou ausência de vazamentos em dados hospitalares. Nomes sem contexto e hostnames fora dos padrões/lista configurados exigem novos casos e regras.
IPv4 é generalizado para /24 e IPv6 para /64. A identificação contextual não substitui avaliação de risco de reidentificação.

Resultado do corpus: APROVADO.
