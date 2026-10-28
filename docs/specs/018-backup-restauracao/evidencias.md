# #25 — recuperação local e pacote para outra máquina

Base develop@f3f6ede. Branch feature/25-backup-restauracao. Usuário autorizou preparar pacote e deixou segunda máquina para depois.

Implementados backup PostgreSQL custom, trilha JSONL, manifesto HMAC-SHA256, conferência de todas as tabelas públicas e restauração em banco vazio da mesma versão principal. Scripts Linux de instalação, atualização offline, wrappers de backup/restore/smoke e modelo systemd para a API/coleta ativa existente. Implementação própria; Sentinel privado não acessado.

## Resultado local 20/10/2026 UTC−4
- Smoke com PostgreSQL17 explícito:19checks aprovados,13tabelas reproduzidas,2entradas de auditoria íntegras. Uma falha TCP chegou ao cliente SSE em0,6092s. Recriação com volume manteve todos os registros; identidade e incidente recuperados pela API real.
- Recusas testadas: chave errada, dump adulterado antes de tocar no destino e banco já ocupado.
- Unidade:7aprovados/1ignorado Windows (permissões POSIX executadas no CI Linux).
- CI previsto: PostgreSQL15 fixado, shell syntax, install.sh e smoke real; publicar somente report.json.

## Limites
Duas instâncias locais não são segunda máquina. Bundle/chave separados em test-results/recovery-first (ignorado, não publicar). Permissões POSIX não atestam ACL Windows. Ativação systemd e atualização real ainda requerem validação em host Linux autorizado. Backup não é criptografado; segredos e globais/n8n não fazem parte do dump. #25 permanece aberta até o aceite externo. Guia completo: docs/guias/backup-restauracao.md.

## Ensaio final local
23 checks aprovados;13tabelas/2entradas de auditoria. Latência SSE de uma falha sintética:0.6468s. Inclui arquivo autenticado porém inválido para pg_restore (destino continua vazio e sem trilha publicada), novas escritas após restore e sequência de eventos avançando sem colisão. Unidade repetida:7aprovados/1ignorado em4,98s. Sintaxe dos5scripts conferida com Git Bash. CI Linux ainda pendente neste registro.
