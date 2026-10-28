# Rascunho de issue (abrir depois da demonstração)

**Título:** Auditoria: custo de gravação e verificação cresce com o tamanho da trilha

## Contexto
O PR #43 coordena a `AuditChain` entre instâncias e processos com um lock lateral (`audit.jsonl.lock`). Em [engenharia/sigma_eng/audit_chain.py](../../engenharia/sigma_eng/audit_chain.py), dentro de `_coordenar()`:
- cada `registrar()`, `verificar()`, `resumo()`, `entradas` e `len()` relê o JSONL inteiro;
- `registrar()` também recalcula o HMAC de todas as entradas antes de anexar a nova.

Além disso, `auth.obter_auditor()` cria uma `AuditChain` nova a cada login e logout, e o construtor também lê o arquivo.

## Problema
O custo de cada gravação é O(n) em leitura e em HMAC, e acontece com o lock exclusivo. Com meses de logins e sondagens, o login fica mais lento e as gravações concorrentes esperam mais. Depois de 10 s, a espera vira `TimeoutError` (`LOCK_TIMEOUT_SECONDS`).

## Proposta (a discutir)
1. Guardar em cache o último `seq`/`hash` e o tamanho do arquivo. Reler só o trecho anexado desde a última leitura.
2. Verificar a cadeia inteira só em `verificar()` e `resumo()`. Em `registrar()`, conferir apenas o encadeamento com a última entrada.
3. Reaproveitar uma instância de `AuditChain` por caminho, em vez de criar uma por requisição.
4. Medir antes e depois, por exemplo com 10k, 100k e 1M de entradas.

## Critérios de aceite
- Login com uma trilha de 100k entradas abaixo de um limite acordado, por exemplo 50 ms extras.
- Os testes de `engenharia/tests/test_audit_shared.py` continuam passando, inclusive os de concorrência entre processos.
- Uma trilha adulterada continua sendo detectada por `verificar()` e continua bloqueando novas gravações.
