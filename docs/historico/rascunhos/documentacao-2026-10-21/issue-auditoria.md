**Não bloqueia a demo.** Registrar agora; investigar e medir após a demonstração. Este item não substitui a revisão do PR #43.

## Contexto
O PR #43 coordena `AuditChain` entre instâncias e processos com um lock lateral. No [audit_chain.py do SHA 8662ea9](https://github.com/Solution-Explores/SigmaTI/blob/8662ea9f5bba32546d65cc440ca1718d1be7c550/engenharia/sigma_eng/audit_chain.py), `_coordenar()` relê o JSONL a cada `registrar()`, `verificar()`, `resumo()`, `entradas` e `len()`; `registrar()` verifica a cadeia completa antes de anexar. `auth.obter_auditor()` cria uma instância por login/logout, cujo construtor também lê o arquivo.

## Problema
O custo por gravação é O(n) em leitura e HMAC, sob lock exclusivo. [Provável] Com uma trilha longa, aumenta a latência e a espera de escritores concorrentes. O lock tem timeout de 10 s; **não foi medido em qual tamanho/carga isso vira gargalo**. Os **7/7** testes focados da `rodada-2026-10-22b` comprovam correção concorrente, não capacidade com meses de histórico.

## Propostas a discutir
1. Cache do último `seq/hash` e tamanho do arquivo; leitura incremental do trecho anexado.
2. Avaliar verificação integral em `verificar()/resumo()` e otimização de `registrar()`. A otimização deve preservar a recusa de novas gravações após adulteração; validar apenas a última entrada, isoladamente, pode perder essa garantia.
3. Reaproveitar uma instância por caminho, preservando coordenação entre processos.
4. Medir antes/depois com 10k, 100k e 1M de entradas.

## Próximo passo
Responsável: @Vinny1313. Revisor independente: @iohanjheremy. Triagem e definição do benchmark propostas para **27/10/2026**, após a demo; não é prazo de implementação.

## Critérios de aceite
- [ ] Definir limite acordado para o custo adicional de login com 100k entradas; 50 ms é uma proposta, não resultado medido.
- [ ] Benchmark reproduzível antes/depois, com latência e contenção.
- [ ] `engenharia/tests/test_audit_shared.py` continua passando, inclusive processos concorrentes.
- [ ] Adulteração histórica continua detectável e continua bloqueando novas gravações.

Refs #6, #13 e PR #43.
