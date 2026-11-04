# MTTD, MTTA, MTTR e burn rate medidos

Medição de 03/11/2026, em **máquina física** (Windows 10, 16 GB, 12 processadores
lógicos, SSD), no SHA `55a1796`, que é a `develop` integrada. São os números
destinados ao texto do TCC.

Comando, reprodutível:

```
python scripts/medir_incidentes.py --output <saida>.json --repeats 30
```

com `SIGMA_TEST_DATABASE_URL` apontando para um PostgreSQL descartável. Dados
brutos, com as 30 amostras individuais, em
[`dados/incidentes-mttd-burn.json`](dados/incidentes-mttd-burn.json).

## O que foi medido

Trinta repetições independentes. Em cada uma: um alvo TCP é criado em loopback,
espera-se a primeira medição bem-sucedida, o serviço é derrubado, e o relógio
corre do instante da queda até o quadro SSE `incident.created` chegar ao cliente.
Em seguida o incidente é reconhecido e resolvido pela API real, e os carimbos
`detectado_em`, `reconhecido_em` e `resolvido_em` são lidos do banco.

O ensaio E2 que já existia (`scripts/validate_collection.py`) media só a
detecção; ele nunca reconhecia nem resolvia incidente, e por isso não produzia
MTTA, MTTR nem indisponibilidade para o SLO. O script novo reusa o mesmo arreio
e fecha o ciclo.

## Resultados

Tempos em segundos, n = 30 em todos:

| Métrica | Média | Mediana | p95 | Máximo |
|---|---:|---:|---:|---:|
| **MTTD** (queda → SSE) | 0,712 | 0,720 | 0,794 | 0,810 |
| **MTTA** (detecção → reconhecimento) | 0,159 | 0,177 | 0,246 | 0,258 |
| **MTTR** (detecção → resolução) | 0,191 | 0,213 | 0,266 | 0,302 |

**Conferência cruzada.** Os mesmos incidentes, reconstruídos com `inicio_real` e
passados pela biblioteca do TCC (`sigma_eng.incidents.metricas`), devolvem
MTTD de média 0,71 s, mediana 0,72 s e p95 0,79 s — iguais dentro do
arredondamento da biblioteca, que usa duas casas. A biblioteca está medindo o
que diz medir.

## SLO e burn rate

SLO declarado para o cálculo: **99,9% de disponibilidade em 30 dias**, que é o
padrão do módulo `sigma_eng.slo`. Os 30 incidentes resolvidos dão 30 intervalos
de indisponibilidade, unidos sem dupla contagem.

| | |
|---|---:|
| Disponibilidade na janela | 99,999% |
| Orçamento total de erro | 43,2 min |
| Consumido | 0,451 min |
| Restante | 42,749 min (98,96%) |
| Estado | `healthy` |

Burn rate, pela definição do SRE Workbook (razão entre o erro observado na
janela e o erro permitido):

| Janela | Burn rate |
|---|---:|
| 1 h | 7,519 |
| 6 h | 1,253 |
| 24 h | 0,313 |

**Nenhum alerta disparou**, e isso é o comportamento correto, não uma falha. A
regra de 1 hora exige burn rate ≥ 14,4 na janela longa **e** na curta (5 min);
7,519 fica abaixo. A de 6 horas exige ≥ 6,0, e 1,253 fica abaixo. As trinta
quedas foram concentradas em menos de um minuto de execução e cada uma foi
resolvida em menos de 0,31 s, então o consumo de orçamento é pequeno em termos
absolutos mas alto quando dividido por uma janela de uma hora. É exatamente o
pico isolado que a exigência das duas janelas existe para não transformar em
plantão.

## Limite estrutural encontrado: a API não entrega MTTD

O endpoint `GET /api/eng/incidentes/resumo` devolve `MTTD: {"n": 0}` **sempre**,
e vai continuar devolvendo. A razão é no código: o cálculo de TTD exige
`inicio_real`, o instante real da falha, e nada na aplicação registra esse
campo. O endpoint monta cada `Incidente` sem ele
(`backend/routers/operational.py`), e a tabela `incidentes` não tem a coluna.
O próprio teste do painel fixa esse comportamento
(`backend/tests/test_panel_api.py`: `assert data["metricas"]["MTTD"]=={"n":0}`).

Isso não é defeito de medição; é consequência de uma decisão de projeto. O
sistema sabe quando **detectou** a falha, não quando ela **começou**. Descobrir o
instante real exige ou injeção controlada, como neste ensaio, ou análise
posterior das medições. Por isso o MTTD deste documento vem de um experimento com
injeção, e não da operação.

Consequência prática: a tarefa de **exibir MTTD no painel** não é trabalho de
frontend. Exige antes decidir de onde vem o `inicio_real` — por exemplo, a última
medição bem-sucedida antes da falha, que o banco já guarda. MTTA e MTTR, esses
sim, a API já tem condição de calcular com o que está gravado.

## Atualização de 04/11: repetição depois da correção da #71

A correção da #71 (PR #79) fez o sistema fechar sozinho o incidente de
disponibilidade quando a sonda volta a responder. Isso **não** muda esta
medição, e a repetição serviu para confirmar a previsão: o
`medir_incidentes.py` derruba o alvo e o mantém derrubado até resolver por
chamada de API, então nenhuma medição com sucesso aparece para fechar o
incidente. Os 30 intervalos de indisponibilidade continuaram vindo da
resolução por API, como antes.

Segunda execução, 30 repetições, SHA `74db26b`, dado bruto em
[`dados/incidentes-pos-71.json`](dados/incidentes-pos-71.json):

| Métrica | 03/11 (média / p95) | 04/11 (média / p95) |
|---|---:|---:|
| MTTD | 0,712 / 0,794 s | **0,795 / 0,889 s** |
| MTTA | 0,159 / 0,246 s | **0,283 / 0,478 s** |
| MTTR | 0,191 / 0,266 s | **0,359 / 0,605 s** |
| burn rate em 1 h | 7,519 | **9,611** |
| orçamento consumido | 0,451 de 43,2 min | **0,577 de 43,2 min** |

Nenhum alerta disparou nas duas execuções, e a conferência cruzada pela
biblioteca do TCC voltou a bater com o medido (0,790 / 0,890 s contra 0,795 /
0,889 s).

**Os números de 04/11 são todos maiores, e não é por causa da correção.** Ela
acrescenta uma única atualização no caminho de uma medição com **sucesso**, e o
MTTD, o MTTA e o MTTR desta medição não passam por lá — o alvo fica derrubado do
começo ao fim. A explicação provável é carga da máquina: a execução de 04/11
rodou com outro contêiner PostgreSQL e um servidor de desenvolvimento do front
ligados, o que a de 03/11 não tinha.

**O que fazer com isso no texto do TCC:** citar as duas execuções, não escolher a
melhor. A diferença entre elas — 0,712 e 0,795 s de MTTD médio — é maior que o
desvio dentro de cada uma, e é a medida honesta de quanto a máquina influencia o
resultado. Um valor único de "MTTD do sistema" com três casas decimais seria
precisão inventada.

**O MTTR, porém, muda de significado a partir da correção.** Nesta medição ele
continua sendo o tempo até a resolução por chamada de API, porque o alvo nunca
volta. Em operação, um incidente fechado pelo sistema mede o tempo até o serviço
voltar, e um fechado à mão, o tempo até alguém clicar.
`/api/eng/incidentes/resumo` mistura os dois. Ver
[`e3-pos-71.md`](e3-pos-71.md).

## Limites desta medição

- Uma máquina, uma sessão, loopback. Não cobre rede hospitalar nem latência real.
- **MTTD é limite superior**: inclui a entrega pelo SSE, não só a detecção.
- **MTTA e MTTR não são humanos.** São de reconhecimento e resolução imediatos por
  chamada de API, feitos pelo próprio script. Medem o caminho do sistema, não o
  tempo de um técnico. O texto do TCC precisa dizer isso onde citar os números.
- O SLO de 99,9% em 30 dias é o padrão do módulo, não um objetivo acordado com o
  hospital. O burn rate acima é válido para esse alvo declarado.
- Não foi executado em VM. O planejamento pedia a rodada final na VM; a VM está
  na outra máquina e não está acessível aqui. Fica declarado como desvio.
