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
