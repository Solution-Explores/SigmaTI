# Revisão técnica do PR #35

19/10/2026, UTC−4. Base revisada: `4af0528`. Revisão e correções pelo Codex,
a pedido do usuário. Não representa revisão independente de outro integrante.

## Achados corrigidos

1. **Rotas de usuários bloqueavam o loop assíncrono.** Consulta SQL síncrona e
   criação de hash Argon2id eram executadas em handlers async. Os dois handlers
   agora são síncronos, executados pelo threadpool do FastAPI. O teste HTTP
   verifica que essas operações não executam no event loop e confirma criação
   e listagem reais no PostgreSQL.
2. **Auditoria indicava sucesso antes de existir sessão.** Uma recusa na emissão
   podia responder 401 após registrar auth.login.success. Agora a sessão precisa
   ser confirmada antes de limpar o limitador e registrar sucesso. Teste injeta
   a recusa e confere a resposta e ausência de sucesso na trilha.
3. **Rehash concorrente recusava login válido.** Dois logins podiam ler o mesmo
   PBKDF2; o segundo ignorava o resultado do CAS e tentava usar um hash que não
   fora gravado. O adaptador informa se atualizou. Se outro login atualizou,
   relê e verifica a credencial atual, papel, atividade e versão da identidade;
   não sobrescreve hash nem aceita alteração administrativa interveniente.
4. **Login iniciado antes de desativação/reativação.** Conferir só hash e papel
   permitia reutilizar uma verificação antiga quando esses campos não mudavam.
   A emissão do login agora compara também a versão da identidade lida antes
   da verificação de senha, sob bloqueio da linha. Nenhuma migração adicional:
   a coluna versao já fazia parte de `001_identity`.
5. **Entrada administrativa inválida virava erro interno/de banco.** Username,
   tamanho da senha e papel agora são validados pelo modelo da rota, com 422
   público sem refletir a senha. A política de comprimento existente foi
   preservada; não se introduziu uma política de complexidade nesta correção.

Os testes anteriores reproduziram a falha do rehash e a auditoria indevida;
o teste de execução de SQL no event loop também falhou antes da correção.
Novas regressões cobrem a versão da identidade e entradas inválidas.

## Validação local

```powershell
.venv/Scripts/python.exe scripts/validate_postgres.py --image postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826 --tests "tests/test_postgres_identity.py tests/test_session_auth.py tests/test_sprint_security.py"
```

**109 aprovados em 69,74 s**, sem falhas/ignorados. Inclui 17 cenários específicos
de persistência e as regressões de autenticação/RBAC e segurança. PostgreSQL real
descartável, dados fictícios, sem IA real. Contêiner e volume de teste removidos;
outros projetos preservados. `pip check` e `git diff --check` aprovados.

A execução completa anterior do CI em PostgreSQL 15 aprovou 387 testes no
commit inicial. O novo head exige nova execução completa; consultar os checks
do [PR #35](https://github.com/Solution-Explores/SigmaTI/pull/35) para seu resultado.
Não reutilizar o resultado anterior como se validasse as correções posteriores.

## Escopo e continuidade

O PR continua sendo incremento parcial de #6/#7. Persistência operacional,
auditoria transacional e limitação distribuída de login não foram acrescentadas
nesta revisão. Nenhuma issue foi fechada nem houve integração nesta etapa.
