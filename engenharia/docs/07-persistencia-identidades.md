# Identidades e sessões persistentes — primeira entrega de #6/#7

O adaptador fica em `backend/persistence/`, fora de `sigma_eng`. PostgreSQL é selecionado
por `SIGMA_DATABASE_URL`. Quando informado, erros de banco/migração impedem o início
ou retornam 503 genérico; não há fallback para memória. O modo anterior com
`SIGMA_USERS_FILE` permanece apenas para laboratório e testes legados.

## Inicialização

Instale `requirements-dev.txt`. Configure no ambiente, sem registrar credenciais
nos comandos compartilhados, `SIGMA_DATABASE_URL` com URL `postgresql+psycopg`.
O banco deve ser novo ou previamente preparado pelo operador. A configuração
Docker existente mantém o banco sem porta publicada; o cliente deve estar na
mesma rede. O runner publica somente um banco descartável em loopback.

```powershell
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m scripts.manage_identity create gestor gestor_ti
```

A senha é solicitada localmente duas vezes, não vai para argv/logs, e exige
12–128 caracteres no bootstrap. Nenhuma conta é criada automaticamente.
Configure também as variáveis existentes de IA, CORS e JWT e inicie Uvicorn
conforme o guia de instalação. Preserve a chave JWT após reinício para manter
as sessões até expiração/revogação. Rotacionar a chave invalida tokens.

Importação explícita dos arquivos PBKDF2 antigos:

```powershell
.venv/Scripts/python.exe -m scripts.manage_identity import-hashes .local/users.json
```

Arquivos são validados e contas existentes são recusadas. Login válido atualiza
PBKDF2 para Argon2id; login incorreto não altera o hash. Novas contas PostgreSQL
já usam Argon2id. Rehash preserva sessões; troca de senha, perfil, desativação ou
recriação invalidam todas as sessões da identidade.

## Esquema e garantias

Migração Alembic `001_identity`:

| Tabela | Campos principais |
|---|---|
| usuarios | username PK, senha_hash, papel restrito aos três perfis, ativo, versao |
| sessoes | jti PK, username FK/indexado, papel, versao_usuario, emitida_em, expira_em indexado, revogada |

Datas são `TIMESTAMPTZ` em UTC. Não são armazenados JWT completo ou senha em
claro. Validação consulta sessão e identidade atuais. Logout persiste revogação;
reiniciar a API não reativa sessões revogadas. Alterações de identidade e emissão
de sessão usam bloqueio de linha; emissão após troca concorrente de credenciais
é recusada. Rehash compara o hash anterior para não sobrescrever troca de senha
concorrente. A API mantém os contratos login/logout/me.

`alembic downgrade base` remove usuários/sessões: somente em banco descartável
ou operação deliberada com backup. Não execute no banco operacional para testar.

## Validação e limites

`python scripts/validate_postgres.py` cria PostgreSQL 15 descartável no digest do
Compose, aplica migração, executa a regressão e remove apenas seu contêiner/volume.
Publica JUnit e resumo sanitizado em `test-results/`. `--image` permite ensaio
adicional explicitamente identificado. O CI tem job próprio para esse runner.
O grupo PostgreSQL é ignorado na execução unitária sem `SIGMA_TEST_DATABASE_URL`,
nunca no runner.

Este incremento não conclui #7: alvos, medições particionadas, incidentes,
aprovações, execuções, retenção/downsampling, aquecimento e auditoria transacional
de operações são o próximo incremento. O limitador de login existente permanece
por processo; a auditoria de login/logout continua na AuditChain JSONL existente.
Backup/restauração e aceite integral do painel ainda têm etapas próprias.

Referências técnicas: [SQLAlchemy transactions](https://docs.sqlalchemy.org/en/20/core/connections.html),
[Argon2 PasswordHasher](https://argon2-cffi.readthedocs.io/en/stable/api.html).
