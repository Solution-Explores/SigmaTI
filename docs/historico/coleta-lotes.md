# Coleta com persistência em lotes — #8

Branch `fix/coleta`, sobre a correção de auditoria `a97fe1b` do PR #43.
**Em validação; não constitui aceite de carga.** #7 e #14 receberam aceite
explícito do usuário em 20/10/2026 e foram encerradas separadamente.

## Contrato

O scheduler preserva o limite de trabalhos configurado (32 no E2), sem fila de
novas sondas ou sobreposição por alvo. Resultados de sondas já reservadas podem
ser agrupados em até 32 medições de alvos distintos. Não há espera artificial:
as chegadas se agrupam enquanto a transação anterior está em curso.

O repositório opcional `BatchMonitoringRepository` confirma todos os resultados
somente após o commit da transação. O adaptador individual continua disponível
para repositórios sem essa capacidade e para compatibilidade com as APIs.
O total de futures pendentes permanece limitado pelas vagas do scheduler.
O shutdown cancela a coleta, mas drena gravações já reservadas antes de retornar.

Quando todas as vagas estão ocupadas, o alvo permanece na única oportunidade
já existente em `_due`. Não se cria task, future ou fila de sondas adicionais.
O relógio tenta os vencimentos mais antigos primeiro quando uma vaga libera.
Períodos inteiros vencidos continuam descartados, sem recuperar vários ciclos
em rajada. Atraso efetivo continua medido por `max_lag_seconds`; a asserção
original de menos de 0,5 s não foi alterada. Sobreposição de um mesmo alvo
continua descartando o ciclo, preservando a reserva de threads lentas.

## Integridade

- Partições são preparadas antes dos locks dos alvos, seguindo a ordem da
  ingestão individual. Os alvos são bloqueados em ordem estável para evitar
  deadlocks entre lotes sobrepostos.
- Lock de alvo e leitura de detector são comandos separados, executados em
  sequência pelo servidor no pipeline. Assim a leitura sob READ COMMITTED
  ocorre depois da aquisição dos locks; um join poderia usar snapshot antigo.
- Estado EWMA/MAD é calculado no núcleo Python e persistido junto das medições,
  agregados por minuto/hora, incidentes e eventos operacionais.
- UUIDs existentes usam a ingestão individual dentro da MESMA transação,
  preservando a comparação de payload e a idempotência. Um conflito reverte
  inclusive amostras novas anteriores do lote.
- Amostras, detectores, agregados e incidentes usam arrays parametrizados,
  com templates constantes. Tipos numéricos são normalizados; não há SQL
  composto a partir de hostnames, dados de clientes ou valores do detector.
- Incidentes permanecem únicos por alvo/tipo ativo, e eventos preservam a
  ordenação global até o commit. Os eventos de um lote são inseridos por um
  único comando, ordenado e protegido pelo mesmo advisory lock global.
  Erros do driver são convertidos em falha
  genérica de persistência; o scheduler não imprime o texto da exceção.

A atomicidade agrupa as falhas: se uma medição inválida ou um evento falhar,
o lote inteiro é revertido e os seus futures falham. Não há confirmação parcial
nem retry automático ilimitado. A memória em voo não é fila durável.
O mesmo vale para um alvo que deixe de existir entre a sonda e o commit: o
`KeyError` descarta as até 32 medições do lote, não apenas a dele. Hoje não há
remoção de alvos (o `PATCH` só desativa); se ela for criada, isolar esse caso.

O pipeline utiliza a conexão Psycopg da transação SQLAlchemy existente; o
adaptador não emite commit antecipado. A biblioteca binária fixada nas
dependências suporta o recurso. Referência técnica:
[Psycopg pipeline](https://www.psycopg.org/psycopg3/docs/advanced/pipeline.html).

## Verificação

Primeiro E2 completo aprovado após corrigir a contrapressão do calendário:
617 medições concluídas na janela, nenhuma nova perda, erros zero e atraso
máximo de 0,176 s. Trinta quedas, reinício sem duplicação, replay e logout
também passaram. O teste e seus limites não foram alterados. Regressão completa
e repetições adicionais ainda estavam em execução neste registro.

Uma tentativa posterior manteve as medições, mas reprovou atraso de 0,68 s.
Após agrupar também os eventos, a rodada final focada passou em 79,03 s:
26 testes PostgreSQL, incluindo E2, nenhuma perda na janela, 599 medições e
atraso máximo de cerca de 0,03 s. Os 16 testes do scheduler passaram em 5,61 s.
Os testes de coordenação esperam eventos explícitos entre threads, sem polling
que dependa da velocidade do ambiente. A regressão completa e as repetições
desse código final continuam sendo exigidas antes do aceite.

`tests/test_postgres_batches.py` cobre retries, conflitos, rollback com eventos,
equivalência EWMA/MAD, lotes concorrentes, limites, tipos mistos e meses distintos.
`engenharia/tests/test_scheduler.py` cobre espera pelo commit, drenagem no stop
e falha de todos os waiters. A carga continua usando o teste original de 200
alvos/2 s/32 trabalhos e suas asserções, sem redução de escopo.

As primeiras variantes ainda reprovaram a carga local; métricas e relatórios
ficam em `test-results/revisao-issues-base/`. `missed_clock`, `missed_overlap` e
`missed_capacity` distinguem motivos de descarte no relógio de coleta; erros
de política, persistência ou liderança continuam contribuindo para `missed`.
`capacity_deferrals` conta tentativas adiadas por falta de vaga; não são
medições confirmadas nem períodos descartados. `missed_capacity` só aumenta
quando a espera de capacidade perde um período inteiro.

Nenhuma validação hospitalar, provedor real ou VM foi usada nesta entrega.
