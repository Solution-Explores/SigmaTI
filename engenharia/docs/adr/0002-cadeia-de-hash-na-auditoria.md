# ADR 0002 · Auditoria com cadeia de hash e HMAC opcional

- **Status:** aceito
- **Contexto:** hospital público; ações sobre a rede (reinício de serviço, aprovações) precisam ser comprovadas. Uma tabela de auditoria comum permite que quem tem acesso ao banco altere registros sem rastro.
- **Decisão:** cada entrada inclui o hash da anterior (SHA-256) ou HMAC-SHA256 se houver chave. JSON canônico (chaves ordenadas, sem espaços). Armazenamento em JSONL com `fsync` por entrada.
- **Alternativas:** assinatura assimétrica por entrada (mais pesada, exige gestão de chaves); *blockchain* (complexidade sem ganho para um único operador); Merkle tree (útil para provas parciais, desnecessário aqui).
- **Consequências:** (+) detecção de adulteração/remoção/reordenação; (−) não impede apagar o arquivo inteiro: exige ancorar o último hash externamente; (−) o `fsync` por entrada limita a taxa (aceitável para eventos de operação, não para telemetria).

## Atualização de 01/11/2026 (issue #13)

- **Status:** aceito, estendido.
- **Rotação de chave:** com `SIGMA_AUDIT_KEY_ID`, cada entrada nova leva `kid` dentro do corpo assinado, e a verificação usa a chave daquele id. `SIGMA_AUDIT_RETIRED_KEYS` mantém as chaves antigas para o histórico continuar verificável; `SIGMA_AUDIT_LEGACY_KEY` cobre entradas gravadas antes de existir `kid`. A rotação (`AuditChain.rotacionar`) grava o evento `audit.key_rotated`, assinado pela chave anterior, e depois passa a usar a nova. Sem `SIGMA_AUDIT_KEY_ID` o formato anterior continua valendo.
- **Âncora externa:** `AuditChain.ancora()` resume contagem, último hash, horário e `kid`, sem dado pessoal. Os destinos são um arquivo de acréscimo em outro volume ou servidor (`SIGMA_AUDIT_ANCHOR_PATH`) e um webhook (`SIGMA_AUDIT_ANCHOR_WEBHOOK`, por exemplo o n8n enviando e-mail ao Gestor de TI). Se a cadeia atual for menor que a âncora ou o hash na posição ancorada diferir, a remoção total, o truncamento ou a reescrita são detectados.
- **Verificação agendada:** ao iniciar e a cada `SIGMA_AUDIT_JOB_INTERVAL_SECONDS` (padrão 86400), a API verifica a cadeia e compara com a última âncora legível. Íntegra: publica nova âncora. Divergente: alerta pelo webhook e não avança a âncora, para preservar a evidência.
- **Limites:** quem controlar o destino da âncora e a chave pode reescrever ambos, então o destino deve ficar fora do alcance de quem opera a máquina da API. O webhook só publica e não é lido de volta, então a comparação automática depende do destino em arquivo. Guardar `SIGMA_AUDIT_KEY` em cofre continua pendente e é tratado na #23.

## Atualização de 02/11/2026 (issue #46): custo da gravação e do login

- **Problema medido:** a cada gravação, login ou verificação, a trilha era relida e todos os HMAC refeitos. O custo crescia na proporção do tamanho: login de 49 ms com 1 mil entradas, 429 ms com 10 mil e 4,3 s com 100 mil (meta proposta: 50 ms).
- **Decisão:** `registrar()`, `ancora()` e `len()` passam a usar um **estado verificado em memória**, por arquivo e chaves, compartilhado entre instâncias do mesmo processo (o login cria uma instância por chamada): contagem, último hash, `kid` da última entrada e o SHA-256 dos bytes verificados. A cada chamada, só o trecho acrescentado é lido e conferido pelo encadeamento e pelo HMAC. `verificar()` e `resumo()` continuam percorrendo a trilha inteira, de propósito: são a checagem explícita (API e job diário).
- **A recusa após adulteração continua:** se o trecho já verificado mudar (editar, remover, reordenar, trocar o arquivo), o SHA-256 não bate, o estado é descartado, a verificação completa roda e a gravação é recusada. Outra chave nunca aproveita o estado de uma chave diferente.
- **Quando os bytes são reconferidos:** o estado só dispensa a leitura se o tamanho e o timestamp não mudaram, a última escrita tem mais de 100 ms e a última conferência dos bytes foi há menos de 30 s (`REVALIDAR_CONTEUDO_SEGUNDOS`). Em qualquer outro caso, os bytes antigos são relidos e comparados (cerca de 100 ms para 30 MB). Primeira gravação de um processo novo: verificação completa, uma vez.
- **Limite aceito:** quem editar o arquivo mantendo o tamanho **e** restaurando o timestamp, depois de 100 ms da última escrita, só é pego pelo `registrar()` na próxima reconferência (até 30 s) ou na hora por `verificar()`/job. A chave HMAC continua impedindo forjar uma cadeia válida; isso só atrasa o bloqueio da gravação. Teste: `test_limite_documentado_...`.
- **Resultado (PC doméstico Windows, Python 3.12, SSD, 5 repetições, mediana):**

| Entradas | Login antes | Login depois | Gravação em rajada depois | Verificação completa (igual antes e depois) |
|---:|---:|---:|---:|---:|
| 1.000 | 49,3 ms | 12,6 ms | 13,1 ms | 38 ms |
| 10.000 | 428,7 ms | 12,2 ms | 23,2 ms | 360 ms |
| 100.000 | 4.291 ms | 12,9 ms | 125,8 ms | 3.809 ms |

  O piso de cerca de 12 ms é o `fsync`. "Rajada" é gravar sem intervalo: a escrita anterior é recente demais para confiar no timestamp, então os bytes são reconferidos (126 ms com 100 mil). A primeira gravação depois de reiniciar a API continua custando uma verificação completa (3,9 s com 100 mil); o job de verificação ao iniciar (#13) a executa e aquece o estado.
- **Não medido:** 1 milhão de entradas, contenção entre processos, cache de arquivo frio, diferença entre Windows e Linux na VM. Reproduzir: `python scripts/benchmark_auditoria.py --tamanhos 1000 10000 100000`.
