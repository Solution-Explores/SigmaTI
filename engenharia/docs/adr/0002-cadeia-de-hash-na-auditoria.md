# ADR 0002 · Auditoria com cadeia de hash e HMAC opcional

- **Status:** aceito
- **Contexto:** hospital público; ações sobre a rede (reinício de serviço, aprovações) precisam ser comprovadas. Uma tabela de auditoria comum permite que quem tem acesso ao banco altere registros sem rastro.
- **Decisão:** cada entrada inclui o hash da anterior (SHA-256) ou HMAC-SHA256 se houver chave. JSON canônico (chaves ordenadas, sem espaços). Armazenamento em JSONL com `fsync` por entrada.
- **Alternativas:** assinatura assimétrica por entrada (mais pesada, exige gestão de chaves); *blockchain* (complexidade sem ganho para um único operador); Merkle tree (útil para provas parciais, desnecessário aqui).
- **Consequências:** (+) detecção de adulteração/remoção/reordenação; (−) não impede apagar o arquivo inteiro: exige ancorar o último hash externamente; (−) o `fsync` por entrada limita a taxa (aceitável para eventos de operação, não para telemetria).
