# Estado operacional — incremento da issue #7

19/10/2026, UTC−4. Base `develop@27d2b552d361deceb3650ba2a47ead959b0ab6bd`.
Branch `codex/estado-operacional`. Implementação e revisão técnica pelo Codex.

## Integração autorizada do PR #35

O usuário autorizou explicitamente a integração do PR #35 nesta conversa.
Merge realizado com proteção do head revisado `31471da`, em `27d2b55`.
Não se atribui revisão independente a outro integrante. Main não alterada.
CI do merge aprovado:

- [API/pacote/PostgreSQL](https://github.com/Solution-Explores/SigmaTI/actions/runs/39345514086).
- [Infraestrutura](https://github.com/Solution-Explores/SigmaTI/actions/runs/39345514065).

## Implementação operacional

Migração `002_operational`: alvos, medições mensais com índice alvo/ts,
agregados minuto/hora, incidente ativo único, aprovações, execuções, detectores,
SLO e eventos transacionais. Interfaces Protocol no núcleo puro e adaptador
PostgreSQL fora do pacote. Memória para testes de estado, sem fallback do banco.

ApprovalService e RunbookRunner persistem snapshots e revisões. Decisão
concorrente usa CAS; expiração e separação de identidades continuam valendo.
Execução interrompida não repete efeitos externos automaticamente. EWMA/MAD
preservam o aquecimento. APIs protegidas oferecem cadastro/leitura de alvos,
consulta de medidas/agregados/incidentes, reconhecimento/resolução, decisões,
SLO, execução por ID e eventos para gestor.

Revisão encontrou e corrigiu a disputa entre resolver e registrar falha:
ambos agora bloqueiam primeiro o alvo. Retry não altera amostra já existente
nem duplica agregado/incidente. Eventos e alterações confirmam juntos;
falha injetada reverte medição, agregados e incidente.

## Evidências locais iniciais

Windows, Python 3.12.14, PostgreSQL 17 descartável já instalado (digest
`3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826`).
Versão 15 permanece no runner/CI com digest do Compose; não foi substituída.

- 27 testes anteriores de aprovação/runbooks aprovados em 12,41 s.
- Primeiros 14 cenários PostgreSQL operacionais aprovados em 11,99 s.
- Após acrescentar API HTTP em dois processos, identidades e contratos em
  memória: 34 testes aprovados em 41,84 s. Dois casos adicionais de concorrência
  e idempotência foram acrescentados depois; a regressão final os inclui.
- `pip check` e `git diff --check` aprovados.

O teste HTTP inicia processo Uvicorn A, autentica e grava dados; encerra A;
inicia processo B; confirma JWT, aprovação pendente e execução waiting_approval
e resolve o incidente. Logs não contêm senha/JWT/chave. Detectores também são
recuperados em processo independente. Somente dados fictícios/executor simulado.
Contêineres/volumes e servidores de testes são próprios e removidos no finally.
O CI e a regressão completa do novo head devem ser consultados no PR; não
reutilizar o CI do merge #35 como aprovação deste incremento.

## Limites

Sem sondagem contínua/SSE (#8), correção DNS/Host/SNI (#14), páginas operacionais
(#15), runbooks via interface (#21/#22), restauração (#25) ou âncora externa
criptográfica (#13). O estado dos detectores está persistível, mas ainda não é
atualizado por coleta contínua. Manutenção de retenção é comando explícito,
não um job automático. Login/logout e limitação distribuída não foram alterados.

[Esquema, contratos e reprodução](../../engenharia/docs/08-estado-operacional.md).


## Regressão local antes da publicação

Execução completa com PostgreSQL 17 real: **411 aprovados em 385,87 s**, sem
falhas/ignorados. A matriz integral das novas rotas foi acrescentada após a coleta
dessa execução e passou separadamente: **1 teste em 5,72 s**, verificando 56
combinações de rota/perfil, inclusive sessão ausente. A projeção pública da
execução, revisada para omitir comandos/variáveis/saída bruta, passou em teste
HTTP específico: **1 aprovado em 4,40 s**.

O head publicado exige CI completo próprio com todos esses cenários coletados.
A proteção das fixtures mantém SIGMA_DATABASE_URL vazio no modo memória, para
que dotenv não reintroduza banco operacional. Só o runner configura o banco
PostgreSQL descartável de testes. Main permanece inalterada.
