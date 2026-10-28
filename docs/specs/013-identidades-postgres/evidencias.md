# Identidades PostgreSQL — incremento de #6/#7

19/10/2026, UTC−4. Base `develop@5d848a9`; branch `codex/persistencia`.
Implementação e revisão técnica pelo Codex. Sem aprovação de merge ou revisão
independente atribuída a outro integrante. A demonstração de 20/10 às 18h ainda
depende dos demais blocos do plano.

## O que mudou

Migração Alembic `001_identity` para usuários e sessões. Adaptador SQLAlchemy
2/Psycopg 3 fora de `sigma_eng`, com interface Protocol. Novas contas PostgreSQL
usam Argon2id. Importação PBKDF2 é explícita e atômica; login válido atualiza o
hash. Bootstrap solicita senha localmente, sem contas padrão ou senha em argv.

JWT e contratos login/logout/me preservados. Sessão válida sobrevive ao reinício;
logout e alterações de senha/perfil/desativação invalidam sessões duravelmente.
Reativar conta não reativa sessões antigas. Emissão e alteração usam bloqueio da
identidade; hash esperado recusa emissão após troca concorrente de credenciais.
Rehash não sobrescreve troca de senha concorrente nem invalida sessões válidas.

Banco configurado indisponível impede início ou retorna 503 genérico; não usa
fallback em memória. Modo antigo de laboratório só vale sem URL PostgreSQL.
Runner cria banco descartável, migra, testa e remove apenas seu contêiner/volume
e arquivo temporário de credenciais. CI adicional usa PostgreSQL 15 no digest
fixado do Compose, publicando JUnit e resumo sanitizado.

## Validação local

Windows, Python 3.12.14, SQLAlchemy 2.0.55, Psycopg 3.3.6, Alembic 1.20.0,
argon2-cffi 25.1.0. `pip check` e `git diff --check` aprovados.

```powershell
.venv/Scripts/python.exe scripts/validate_postgres.py --image postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826
```

**383 aprovados**, zero falhas/ignorados, 223,21 s: 375 anteriores e oito testes
PostgreSQL iniciais. Aviso Alembic de path_separator corrigido na configuração.

Revisão acrescentou rollback integral de importação, downgrade/upgrade em banco
descartável, bootstrap real e expiração. Grupo final:

```powershell
.venv/Scripts/python.exe scripts/validate_postgres.py --image postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826 --tests tests/test_postgres_identity.py
```

**12 aprovados em 17,69 s**, sem avisos. O cenário de reinício abre outro processo
Python e passa token por stdin, nunca argv. Demais cenários: revogação após
reinício, mudança de senha/perfil/desativação/reativação, rehash e emissão após
troca concorrente, banco indisponível, login/logout/503 sem detalhe privado.
Arquivos locais ignorados: `test-results/postgres-regression.xml` e
`test-results/postgres-run.json`; nenhum segredo publicado.

## Limites e próxima entrega

Duas tentativas de download PostgreSQL 15 falharam com `tls: bad record MAC`.
Sem mudar digest, stack existente ou verificação TLS, o ensaio local usou a
imagem PostgreSQL 17 já instalada. PostgreSQL 15 precisa passar no CI antes da
integração. Outros projetos Docker foram preservados.

Não conclui #7: faltam alvos, medições particionadas, incidentes, aprovações,
execuções, retenção/downsampling, aquecimento e recuperação operacional.
Limitador de login segue por processo; login/logout usam AuditChain JSONL,
sem auditoria transacional PostgreSQL nesta etapa. Não fechar #6/#7 com base
neste incremento. Próximos blocos continuam #14, #8, #15 e restauração #25,
depois de aprovar a fundação.

[Esquema e reprodução](../../../engenharia/docs/07-persistencia-identidades.md).
