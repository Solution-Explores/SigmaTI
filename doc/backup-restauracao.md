# Implantação e recuperação — #25

## Escopo e pré-requisitos

Implementação própria para a arquitetura atual; nenhum código do Sentinel privado foi copiado. Linux, Python 3.12+, Git, Docker Engine/Compose e acesso administrativo ao contêiner PostgreSQL. A coleta implementada é ativa (TCP/HTTP) no processo da API; não existe coletor de captura de pacotes a instalar. A unidade `deploy/sigma-coleta.service` serve essa API/coleta, sem privilégios de captura. Frontend continua pelo procedimento npm do README.

Use um checkout confiável e SHA aprovado. Não execute `install.sh` sobre banco desconhecido: ele instala dependências fixadas e aplica migrações no `SIGMA_DATABASE_URL` informado. Não cria usuários de sistema, altera firewall ou habilita serviços automaticamente.

```bash
# No checkout, com variáveis exportadas por configuração confiável:
export SIGMA_DATABASE_URL='postgresql+psycopg://USUARIO:SENHA@127.0.0.1:5432/sigmadb'
bash scripts/install.sh
.venv/bin/python -m scripts.manage_identity --help
```

Se o banco for o Compose atual e a API rodar no host, use o overlay:
`docker compose -f docker-compose.yml -f deploy/db-host.yml up -d db`.
Preencha todas as credenciais exigidas em `.env.example`; não publique `compose config` com segredos. O overlay publica 5432 somente em loopback. Em instalações existentes, confira conflito de porta e credenciais persistidas antes de aplicá-lo.

## Serviço Linux

Modelo destinado a `/opt/sigma`, conta `sigma` e estado em `/var/lib/sigma`. O administrador deve preparar os diretórios/usuário, dar leitura do checkout à conta e escrita somente no estado. Copie a unidade para `/etc/systemd/system/`, adapte caminhos se necessário e execute `systemd-analyze verify`, `systemctl daemon-reload` e `systemctl enable --now sigma-coleta.service` após conferir o ambiente. Essas ações são deliberadas, não parte automática de install.sh.

`/etc/sigma/sigma.env` deve ser protegido (root:root,0600), conter as variáveis da API, `SIGMA_DATABASE_URL`, `SIGMA_AUDIT_KEY`, `SIGMA_JWT_SECRET`, `SIGMA_AUDIT_PATH=/var/lib/sigma/audit.jsonl` e `SIGMA_COLLECTION_ENABLED=1`. Preserve as allowlists de sondagem; não use redes de terceiros. O serviço usa um worker e loopback8000. A inicialização cria a trilha quando necessária; confira permissões e o backup dela. Ativação systemd em host real permanece por validar; o CI não é uma máquina com esse serviço habilitado.

## Criar backup offline

Pare a API/coleta e **todos os demais escritores**, inclusive processos manuais. `--quiesced` é uma declaração operacional, não um mecanismo que bloqueia escritores desconhecidos. pg_dump é consistente no banco; uma trilha externa requer essa parada para representar o mesmo ponto operacional. O script detecta mudança da trilha durante a exportação; a comparação de tabelas após restaurar detecta divergência do inventário. Não retome escritores antes do fim do backup.

A chave HMAC usada na trilha é necessária (pelo menos32bytes em SIGMA_AUDIT_KEY), exportada por configuração confiável, **fora do pacote**. Não gere outra chave para verificar uma trilha existente.

```bash
sudo systemctl stop sigma-coleta.service
# Também parar outros escritores; executar com Docker autorizado e chave exportada.
bash scripts/backup.sh --container sigma-db \
  --audit /var/lib/sigma/audit.jsonl --bundle /mnt/backup/sigma-AAAAMMDD-HHMM --quiesced
.venv/bin/python scripts/recovery.py verify --bundle /mnt/backup/sigma-AAAAMMDD-HHMM
# Retomar somente após backup verificado.
```

O diretório novo contém `database.dump` (pg_dump custom), `audit.jsonl` e `manifest.json`. O manifesto autentica hashes SHA256, versão principal PostgreSQL, contagens e fingerprints de todas as tabelas públicas. Diretório0700/arquivos0600 em POSIX; um teste Linux confere esses modos. O inventário lê as tabelas para comparar o conteúdo e exige capacidade compatível com o banco; não é um ensaio de escalabilidade. O banco SIGMA usa schema público; bancos com schemas externos não estão cobertos pelo inventário e não devem usar este procedimento sem adaptação.

O pacote contém dados e hashes de senha: **não há criptografia embutida**. Use armazenamento externo com ACL, criptografia e retenção da instituição. HMAC detecta alteração por quem não tem a chave; não protege contra perda do disco, nem substitui âncora externa. A chave HMAC, segredo JWT, chaves de origem/IA, configuração de implantação e credenciais administrativas devem ter recuperação separada, com acesso restrito. Não versionar, anexar ao PR nem publicar o bundle/chave como artifact.

## Restaurar em banco novo / outra máquina

1. Instale o mesmo SHA do projeto em uma máquina Linux autorizada e as dependências, **sem aplicar migrações no destino antes do restore**. O dump já contém o esquema e alembic_version.
2. Copie o diretório do pacote e confira permissões. Transfira a chave original por canal separado e confiável. Configure a mesma versão principal PostgreSQL do manifesto, em contêiner novo, banco criado e vazio. Credenciais/nomes podem diferir; dentro do contêiner precisam estar configurados POSTGRES_USER/POSTGRES_DB.
3. Mantenha a API e demais escritores desligados. A trilha de destino não pode existir. O comando recusa banco com relações existentes, chave errada, hashes divergentes, links nos arquivos do pacote e diferença de versão principal. Não usa `--clean`, não remove tabelas e não sobrescreve trilhas.

```bash
# SIGMA_AUDIT_KEY original já exportada; contêiner de DESTINO deliberadamente escolhido:
bash scripts/restore.sh --container sigma-db-recuperado \
  --bundle /mnt/backup/sigma-AAAAMMDD-HHMM --audit /var/lib/sigma/audit-restaurado.jsonl --quiesced
```

4. pg_restore usa transação única e falha no primeiro erro. Depois, fingerprints/contagens são comparados; a trilha só é preenchida após a comparação. Se a validação posterior falhar, **mantenha offline e descarte apenas o destino novo de ensaio**: não há rollback automático do banco já confirmado nem de migração. Não reutilize um destino parcialmente restaurado.
5. Configure SIGMA_DATABASE_URL para o banco restaurado e SIGMA_AUDIT_PATH para a nova trilha, sem restaurar chaves por dentro do dump. Decida a política de sessões: manter o segredo JWT recupera a validade temporal das sessões persistidas, inclusive as já revogadas; uma nova chave encerra tokens antigos. Não reative credenciais comprometidas só porque existem no backup.
6. Inicie a API e confira login, IDs/contagem de incidentes, aprovações, SLO e GET `/api/eng/auditoria/verificar`. Compare a versão/manifesto e guarde a evidência sem dados brutos. Recrie o contêiner preservando **o volume de destino** e repita a conferência. Nunca use `down -v` no ambiente operacional.

O dump não inclui globais do cluster, roles administrativas, n8n/Grafana/Zabbix, certificados, segredos nem frontend. Objetos são restaurados sob o usuário do destino, sem privilégios/owners da origem. A integridade JSONL cobre as sondas; eventos operacionais PostgreSQL são comparados separadamente pelo inventário.

## Atualização

Faça o backup offline antes de migrar. `bash scripts/update.sh SHA_APROVADO PASTA_BACKUP_NOVA` exige checkout limpo, avanço fast-forward, SIGMA_DB_CONTAINER, SIGMA_AUDIT_PATH, SIGMA_AUDIT_KEY, SIGMA_DATABASE_URL e SIGMA_WRITERS_STOPPED=1. Recusa o serviço sigma-coleta ainda ativo. Não faz reset, descarte de alterações ou retorno automático após migração. Em falha, mantenha offline e restaure para banco novo conforme acima. Valide a nova versão antes de reiniciar o serviço.

## Smoke reproduzível e CI

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
bash scripts/smoke.sh --install --output test-results/recovery-NOVO
# Windows: .venv/Scripts/python.exe scripts/validate_recovery.py --output test-results/recovery-NOVO
```

O smoke sobe dois PostgreSQL descartáveis com credenciais efêmeras, instala/migra a origem (install.sh no Linux), inicia a API real, injeta falha TCP, espera SSE em até5s, verifica auditoria, exporta offline, testa recusas, restaura, compara **todas as linhas de13tabelas**, recria o contêiner com o volume e consulta a API restaurada. Nenhum provedor IA real é chamado. Saída não zero indica falha. Limpeza remove somente contêineres e volume com nomes aleatórios criados pelo próprio runner.

Relatório: `report.json`. O bundle e `audit-key.txt` são mantidos localmente no diretório de ensaio; a chave fica **fora** de `bundle/`. São fictícios, mas restritos, e não devem ser publicados. CI publica **somente report.json**. O bundle usa formato portátil pg_dump e poderá ser levado à outra máquina; o roteiro acima registra o aceite externo quando houver máquina disponível.

**Dois contêineres no mesmo host não atendem ao aceite de outra máquina.** O usuário reservou essa execução para depois; #25 permanece aberta. Ativação systemd e atualização de uma instalação real também não são atestadas pelo smoke isolado. Referências: [pg_dump15](https://www.postgresql.org/docs/15/app-pgdump.html), [pg_restore15](https://www.postgresql.org/docs/15/app-pgrestore.html).
