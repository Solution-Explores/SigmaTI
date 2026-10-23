# Backup, restauração e atualização

Procedimento para fazer backup offline do SIGMA, restaurá-lo em um banco novo e atualizar uma instalação. Vale para a arquitetura atual, em que a coleta é ativa (TCP e HTTP) e roda no processo da API. Não existe coletor de captura de pacotes a instalar.

## Pré-requisitos

- Linux, Python 3.12+, Git e Docker Engine com Compose.
- Acesso administrativo ao contêiner PostgreSQL.
- Um checkout confiável, em um SHA aprovado.

O frontend segue o procedimento npm do [guia de instalação](instalacao.md).

## Instalar na máquina

Não rode `install.sh` sobre um banco desconhecido. O script instala as dependências fixadas e aplica as migrações no banco de `SIGMA_DATABASE_URL`. Ele não cria usuários de sistema, não altera o firewall e não habilita serviços.

```bash
export SIGMA_DATABASE_URL='postgresql+psycopg://USUARIO:SENHA@127.0.0.1:5432/sigmadb'
bash scripts/install.sh
.venv/bin/python -m scripts.manage_identity --help
```

Se o banco é o do Compose e a API roda no host, use o overlay que publica a porta 5432 só em loopback:

```bash
docker compose -f docker-compose.yml -f deploy/db-host.yml up -d db
```

Preencha todas as credenciais do `.env.example` e não publique a saída de `compose config`, que contém segredos. Em instalações existentes, confira conflito de porta e credenciais gravadas antes de aplicar o overlay.

## Serviço Linux

A unidade `deploy/sigma-coleta.service` executa a API com a coleta, sem privilégios de captura. O modelo espera o código em `/opt/sigma`, a conta `sigma` e o estado em `/var/lib/sigma`.

1. Prepare os diretórios e o usuário. A conta lê o checkout e escreve só no estado.
2. Crie `/etc/sigma/sigma.env` com dono `root:root` e modo `0600`, contendo:
   - as variáveis da API e `SIGMA_DATABASE_URL`;
   - `SIGMA_AUDIT_KEY` e `SIGMA_JWT_SECRET`;
   - `SIGMA_AUDIT_PATH=/var/lib/sigma/audit.jsonl`;
   - `SIGMA_COLLECTION_ENABLED=1`.
3. Copie a unidade para `/etc/systemd/system/` e ajuste os caminhos se precisar.
4. Rode `systemd-analyze verify`, `systemctl daemon-reload` e `systemctl enable --now sigma-coleta.service`.

Mantenha as allowlists de sondagem e não use redes de terceiros. O serviço usa um worker e escuta em `127.0.0.1:8000`. Na inicialização ele cria a trilha de auditoria. Confira as permissões e inclua a trilha no backup.

A ativação no systemd ainda não foi validada em um host real. O CI não tem esse serviço habilitado.

## Backup offline

Pare a API, a coleta e todos os outros escritores, inclusive processos manuais. A opção `--quiesced` é uma declaração sua, não um bloqueio. O `pg_dump` é consistente no banco, mas a trilha externa só acompanha o mesmo ponto se tudo estiver parado. O script detecta mudança na trilha durante a exportação. Não retome os escritores antes do fim do backup.

A chave HMAC da trilha (`SIGMA_AUDIT_KEY`, ao menos 32 bytes) é necessária e deve ficar **fora do pacote**. Para verificar uma trilha existente, use a chave original, nunca uma nova.

```bash
sudo systemctl stop sigma-coleta.service
# Pare também os outros escritores. Exporte a chave por canal confiável.
bash scripts/backup.sh --container sigma-db \
  --audit /var/lib/sigma/audit.jsonl --bundle /mnt/backup/sigma-AAAAMMDD-HHMM --quiesced
.venv/bin/python scripts/recovery.py verify --bundle /mnt/backup/sigma-AAAAMMDD-HHMM
# Retome os serviços só depois de verificar o backup.
```

O diretório novo contém:

- `database.dump`: `pg_dump` em formato custom;
- `audit.jsonl`: a trilha de auditoria;
- `manifest.json`: hashes SHA-256, versão principal do PostgreSQL, contagens e fingerprints de todas as tabelas públicas.

O diretório usa modo `0700` e os arquivos `0600` em POSIX, e um teste Linux confere isso. O inventário lê as tabelas para comparar o conteúdo e exige capacidade compatível com o banco. Não é um ensaio de escala. Ele cobre o schema `public`. Bancos com schemas externos precisam de adaptação.

O pacote tem dados e hashes de senha, e **não tem criptografia embutida**. Guarde-o em armazenamento externo com ACL, criptografia e retenção da instituição. O HMAC detecta adulteração por quem não tem a chave. Ele não protege contra perda do disco nem substitui uma âncora externa.

Guarde com recuperação separada e acesso restrito: a chave HMAC, o segredo JWT, as chaves de origem e da IA, a configuração de implantação e as credenciais administrativas. Nunca versione nem anexe a um PR o pacote ou a chave, nem os publique como artifact.

## Restaurar em um banco novo

1. **Prepare a máquina.** Instale o mesmo SHA do projeto e as dependências. **Não aplique migrações no destino antes do restore.** O dump já contém o schema e o `alembic_version`.
2. **Prepare o destino.** Copie o pacote e confira as permissões. Envie a chave original por um canal separado e confiável. Suba um contêiner novo com a mesma versão principal do PostgreSQL do manifesto e um banco vazio. Nomes e credenciais podem ser diferentes, mas o contêiner precisa de `POSTGRES_USER` e `POSTGRES_DB`.
3. **Mantenha tudo desligado.** A API e os outros escritores ficam parados, e a trilha de destino não pode existir. O comando recusa banco com relações, chave errada, hashes divergentes, links no pacote e versão principal diferente. Ele não usa `--clean`, não remove tabelas e não sobrescreve trilhas.

   ```bash
   # SIGMA_AUDIT_KEY original já exportada; contêiner de DESTINO escolhido de propósito:
   bash scripts/restore.sh --container sigma-db-recuperado \
     --bundle /mnt/backup/sigma-AAAAMMDD-HHMM --audit /var/lib/sigma/audit-restaurado.jsonl --quiesced
   ```

4. **Entenda a falha.** O `pg_restore` roda em uma transação e para no primeiro erro. Depois ele compara fingerprints e contagens, e só então preenche a trilha. Se a validação falhar, mantenha offline e descarte apenas o destino novo. Não há rollback do banco já confirmado. Nunca reutilize um destino restaurado pela metade.
5. **Configure.** Aponte `SIGMA_DATABASE_URL` para o banco restaurado e `SIGMA_AUDIT_PATH` para a nova trilha. Não restaure chaves de dentro do dump. Sobre as sessões: manter o segredo JWT mantém válidas as sessões persistidas, inclusive as já revogadas. Uma chave nova encerra todos os tokens antigos. Não reative credenciais comprometidas só porque estão no backup.
6. **Confira.** Inicie a API e verifique o login, os IDs e a contagem de incidentes, as aprovações, o SLO e `GET /api/eng/auditoria/verificar`. Compare a versão e o manifesto e guarde a evidência sem dados brutos. Recrie o contêiner **preservando o volume de destino** e repita a conferência. Nunca use `down -v` em ambiente operacional.

O dump não inclui globais do cluster, roles administrativas, n8n, Grafana, Zabbix, certificados, segredos nem o frontend. Os objetos voltam sob o usuário do destino, sem os privilégios e donos da origem. A integridade da trilha JSONL cobre as sondas. Os eventos operacionais no PostgreSQL são comparados à parte, pelo inventário.

## Atualizar

Faça o backup offline antes de migrar.

```bash
bash scripts/update.sh SHA_APROVADO PASTA_BACKUP_NOVA
```

O script exige:

- checkout limpo e avanço fast-forward;
- `SIGMA_DB_CONTAINER`, `SIGMA_AUDIT_PATH`, `SIGMA_AUDIT_KEY` e `SIGMA_DATABASE_URL`;
- `SIGMA_WRITERS_STOPPED=1`.

Ele recusa rodar com `sigma-coleta` ativo. Não faz reset, não descarta alterações e não volta sozinho depois de uma migração. Se falhar, mantenha offline e restaure em um banco novo, como acima. Valide a nova versão antes de reiniciar o serviço.

## Smoke test e CI

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
bash scripts/smoke.sh --install --output test-results/recovery-NOVO
# Windows: .venv/Scripts/python.exe scripts/validate_recovery.py --output test-results/recovery-NOVO
```

O smoke sobe dois PostgreSQL descartáveis com credenciais efêmeras e percorre o ciclo inteiro:

1. instala e migra a origem (`install.sh` no Linux) e inicia a API real;
2. injeta uma falha TCP e espera o SSE em até 5 s;
3. verifica a auditoria, exporta offline e testa as recusas;
4. restaura e compara todas as linhas das 13 tabelas;
5. recria o contêiner com o volume e consulta a API restaurada.

Nenhum provedor de IA real é chamado. Saída diferente de zero indica falha. A limpeza remove só os contêineres e o volume com nomes aleatórios que o próprio runner criou.

O relatório é `report.json`. O pacote e o `audit-key.txt` ficam no diretório do ensaio, com a chave fora de `bundle/`. São fictícios mas restritos, e não devem ser publicados. O CI publica só o `report.json`. O pacote usa o formato portátil do `pg_dump` e pode ser levado a outra máquina.

Limites: dois contêineres no mesmo host **não** cumprem o aceite em outra máquina. Essa execução ficou para depois, e a issue #25 continua aberta. O smoke isolado também não atesta a ativação no systemd nem a atualização de uma instalação real.

Referências: [pg_dump 15](https://www.postgresql.org/docs/15/app-pgdump.html) e [pg_restore 15](https://www.postgresql.org/docs/15/app-pgrestore.html).
