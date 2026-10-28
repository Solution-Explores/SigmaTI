# Revisão dos achados de #6, #7, #8 e #14

20/10/2026, America/Manaus. Base local examinada: `develop@8cb1e23b0e83066e52d3f81dd7ef05ce82dfc93c`.
Revisão de código, critérios originais consultados no GitHub e evidências existentes.
Nesta revisão não foram iniciados VM, PostgreSQL ou sondas hospitalares.
Somente diagnósticos e testes locais focados, com dados temporários e loopback.

## Resultado por issue

| Issue | Resultado da revisão | Condição para prosseguir |
|---|---|---|
| [#6](https://github.com/Solution-Explores/SigmaTI/issues/6) | [Certo] Identidades PostgreSQL/Argon2id, JWT, revogação, RBAC e limite de login implementados. Duas falhas da auditoria JSONL reproduzidas novamente. | Corrigir A1/A2 e suas regressões antes do aceite integral. |
| [#7](https://github.com/Solution-Explores/SigmaTI/issues/7) | [Certo] Há implementação e testes integrados para os três critérios originais; nenhuma nova lacuna de implementação identificada nesta leitura. | Revisar o aceite com os testes PostgreSQL já registrados. Não confundir com nova execução nesta rodada. |
| [#8](https://github.com/Solution-Explores/SigmaTI/issues/8) | [Certo] Scheduler/SSE implementados, mas a carga reprovou posteriormente na VM. A recomendação anterior de encerramento não é sustentada pelo conjunto atual das evidências. | Investigar e corrigir a causa; repetir o cenário original sem relaxar critérios. |
| [#14](https://github.com/Solution-Explores/SigmaTI/issues/14) | [Certo] Conexão numérica ao IP validado, Host/SNI preservados e regressões de DNS alternante estão implementados. | Conferir resultado dos testes focados e formalizar aceite; a frase “para revisão” do guia é pendência editorial. |

As quatro issues estavam abertas na consulta. Nenhuma foi encerrada nesta revisão.

## A1 — escritores independentes quebram a cadeia (#6)

[Certo] `auth.py:408` cria uma nova `AuditChain` a cada `obter_auditor()`.
Em `engenharia/sigma_eng/audit_chain.py`, cada instância carrega `_entradas` apenas
no construtor e usa seu próprio `threading.Lock`. `registrar()` deriva sequência e
hash anterior dessa lista; o append e o fsync não coordenam instâncias distintas.

Reprodução determinística local, sem concorrência necessária: criar seed;
carregar A/B; A grava login; B grava logout. Resultado: três entradas em disco,
verificação fresca inválida no índice 2; A continua reportando duas entradas e
integridade verdadeira. [Provável] Requisições concorrentes podem produzir essa
intercalação; a frequência em produção não foi medida.

Correção necessária: coordenar leitura canônica do último registro, validação e
append entre todos os escritores do mesmo arquivo, inclusive processos distintos.
Um singleton ou lock por objeto não resolve o requisito entre processos.
Definir comportamento explícito para arquivo inválido, erro de I/O e timeout do
lock; não anunciar gravação de auditoria bem-sucedida quando ela falhar.

Aceite da correção:

- Duas instâncias pré-carregadas gravam e produzem sequência/hash válidos.
- Processos escritores simultâneos terminam com todos os eventos esperados,
  sem duplicações ou linhas truncadas, e verificação por leitor novo íntegra.
- Lock é liberado também em exceção; comportamento funciona em Windows e Linux.
- Falha de auditoria segue política explícita de resposta/observabilidade,
  sem credenciais, tokens ou dados brutos no log.

## A2 — verificação usa snapshot antigo (#6 e consumidor #15)

[Certo] `main.py:94` constrói `engineering_audit` na importação e o entrega a
`create_router`. Em `engenharia/sigma_eng/api.py:121`, o endpoint verifica esse
objeto e obtém seu tamanho em memória. Novas gravações de auth não o atualizam.

Reprodução local pelo TestClient, modo laboratório: login HTTP 200 grava uma
entrada; `/api/eng/auditoria/verificar` retorna HTTP 200 com `entradas: 0` e
`integra: true`, enquanto o disco tem uma entrada válida. Não é teste de banco.

Correção necessária: ler uma visão coerente do arquivo corrente. Verificação e
contagem devem se referir ao mesmo snapshot; recriar um objeto sem coordenar a
leitura com escritores pode continuar lendo append incompleto.

Aceite: endpoint reconhece login/logout e gravação por outro processo sem
reiniciar API; alteração posterior do arquivo é detectada; nenhuma resposta usa
contagem e verificação de snapshots diferentes. Preservar RBAC e contrato HTTP.

## #7 — critérios originais e fronteiras

| Critério/proposta | Evidência no código e nos testes |
|---|---|
| Preservar pendentes e `waiting_approval` após reinício | `tests/test_postgres_operational.py::test_real_http_api_restart_preserves_session_and_pending_work`, `test_execution_waiting_approval_recovers_without_repeating_steps` |
| Repositório PostgreSQL real no CI | `.github/workflows/api-config.yml`, job `test-postgres`, runner `scripts/validate_postgres.py` |
| Esquema documentado | `engenharia/docs/07-persistencia-identidades.md`, `08-estado-operacional.md`, `09-coleta-eventos.md`; migrações 001–003 |
| Protocol, particionamento, retenção e agregados | `engenharia/sigma_eng/state.py`, `persistence/operational.py`, testes de partição/downsampling/retenção |

[Certo] O teste de reinício usa Uvicorn real e banco descartável. Sua presença e
o resultado anterior de regressão foram conferidos; não foi reexecutado nesta
revisão. A rodada anterior da VM aprovou 466/467 testes, com falha em coleta E2.
Isso não substitui ensaio de efeitos externos exatamente uma vez. Runbooks de
produção, âncora da auditoria e restauração externa pertencem a outros escopos.

## #8 — evidência posterior impede aceite da carga

[Certo] O PR #42, head `9b7556c9eae9f4fc035013e707853d670492f337`, estava aberto
na consulta. Sua conferência relata aprovação anterior e recomenda aceite da
#8. A reprodução posterior no mesmo código deve ser acrescentada antes de usar
esse documento para recomendar encerramento.

Evidência local: `D:/sigma-dev/laboratorio-vm/evidencias/rodada-isolada/resumo.json`
e `carga.json`. VM com quatro vCPUs, 4 GiB e PostgreSQL 15, VirtualBox sobre
hipervisor Windows. Foram 200 alvos lógicos TCP em loopback, intervalo de 2 s,
32 trabalhos e janela de 6 s. `missed` passou de 150 para 200; erros/timeouts
continuaram zero. O teste parou na asserção de `scripts/validate_collection.py:248`.
As verificações posteriores de reinício/replay dessa rodada não foram alcançadas.

Experimentos posteriores sem alteração do produto: quatro trabalhadores de
persistência reprovaram três rodadas; um trabalhador passou uma e reprovou duas,
com incrementos de 86 e 138 ciclos perdidos. Isso não valida mudar o padrão do
executor. Houve stall RCU da VM; relação causal não foi estabelecida.

O baixo atraso máximo do ciclo e a ausência de fila não compensam ciclos
descartados. [Certo] Há reprovação do critério nessa configuração; [Provável]
há contenção/capacidade insuficiente no caminho de persistência, mas ainda não
foi isolada a contribuição do produto e da virtualização.

Aceite futuro: preservar 200 alvos/2 s/32 trabalhos e asserções atuais; registrar
ambiente, métricas antes/depois, pelo menos três repetições completas e resultado
da regressão. Repetições são estratégia desta revisão, não requisito retroativo
da issue. Não reduzir carga, remover asserção ou anunciar uma aprovação isolada
como correção. Testes continuam parados por solicitação do usuário.

## #14 — critério atendido, limites preservados

[Certo] `resolve_target` valida todas as respostas; `_connect_ip` usa socket
numérico IPv4/IPv6. `probe_service` preserva hostname original para HTTP/SNI.
`engenharia/tests/test_probe_pinning.py` cobre DNS alternante em TCP/HTTP/HTTPS,
resposta mista/vazia, caminho numérico sem segunda resolução e redirect HTTP
real em loopback sem seguir o destino externo. Endereços externos dos testes
são respostas falsas; o teste não conecta nesses endereços.

`engenharia/docs/05-seguranca-e-pendencias.md` já descreve TOCTOU e limites,
mas ainda chama a correção integrada no PR #37 de “implementado para revisão”.
O PR #42 propõe ajustar essa redação. A issue original não exige ampliar PKI;
preservar SNI não prova confiança no certificado. O cartão combinado #14/#13
não pode ser concluído inteiro apenas pelo aceite de #14.

## Ordem de trabalho proposta

1. Corrigir A1 e A2 juntas em branch de correção, com testes entre processos e
   do endpoint; confirmar Windows/Linux antes de recomendar aceite de #6.
2. Atualizar a conferência do PR #42 com a reprovação posterior de #8. Revisar
   #7/#14 individualmente para aceite, sem arrastar o escopo de #13/#21/#25.
3. Retomar diagnóstico da carga quando autorizado, mantendo a falha e todas as
   evidências anteriores. Não criar configuração de desempenho sem validação.

## Verificação executada nesta revisão

[Certo] 92 testes locais aprovados em 70,44 s, sem ignorados: sessão/RBAC,
auditoria/aprovações e pinning da sonda. Comando, a partir da raiz do projeto,
usando `PYTHON_DOTENV_DISABLED=1`, `SIGMA_COLLECTION_ENABLED=0` e
`PYTHONPATH` apontando para a pasta `engenharia` deste checkout:

```powershell
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_session_auth.py engenharia/tests/test_audit_approvals.py engenharia/tests/test_probe_pinning.py --junitxml=test-results/revisao-issues-base/focados.xml
```

Separadamente, o diagnóstico do PR #42 foi executado contra o código local e
reproduziu A1/A2. Saída em `test-results/revisao-issues-base/auditoria.json`;
script adjacente `reproduzir-auditoria.py`, derivado do PR #42, head citado acima.
Exit zero do diagnóstico significa **falhas reproduzidas**, não falhas corrigidas.
Os 92 testes existentes verdes demonstram precisamente que essa cobertura não
detecta A1/A2. A correção exige acrescentar as regressões descritas nesta revisão.

Esta entrega é revisão técnica Codex, sem revisor humano independente.
Não altera comportamento do produto nem constitui homologação hospitalar.
