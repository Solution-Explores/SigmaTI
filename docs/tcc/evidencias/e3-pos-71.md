# E3 remedido depois da correção da #71

Medição de **04/11/2026**, em máquina física, no SHA **`d11602d`** — a `develop`
`857e3ff` mais a correção da #71 deste PR. Dado bruto em
[`dados/e3-pos-71.json`](dados/e3-pos-71.json), com as 301 amostras da condição A
e as 61 da B.

```
python scripts/medir_e3.py --output <saida>.json --minutos-a 10 --segundos-b 10 --observacao-b 5
```

Mesmo script, mesmo SLO (99,9% em 30 dias) e mesmas regras de burn rate da
medição de 03/11, registrada em [`e3-burn-rate.md`](e3-burn-rate.md), que é o
estado **antes** da correção.

## O que mudou

| Condição | Esperado | 03/11, antes | 04/11, depois | |
|---|---|---|---|:-:|
| A · queda de 10 min | chega a `page` | `page` em 52,0 s | `page` em **52,0 s** | ✅ |
| B · corte de 10 s | não pagina | `page` em 45,0 s | **nenhum alerta** | ✅ |

**O critério da #11 passa inteiro.** A metade que falhava era consequência de o
incidente nunca se fechar sozinho, não do cálculo de burn rate — o que a medição
de 03/11 já havia mostrado recalculando com o intervalo recortado à mão. Agora o
sistema recorta o intervalo por conta própria, porque sabe quando o alvo voltou.

## Condição A — queda de 10 minutos

Nada mudou, e é isso que se queria: a correção não enfraqueceu a detecção.

| Segundos desde a queda | burn 1 h | burn 5 min | Regras disparadas |
|---:|---:|---:|---|
| 48 | 13,359 | 160,305 | — |
| 50 | 13,915 | 166,974 | — |
| **52** | **14,470** | 173,644 | **`page` (limiar 14,4)** |
| 600 | 166,738 | 1000,000 | `page` 14,4 · `page` 6,0 · `ticket` 3,0 · `ticket` 1,0 |

O disparo em 52,0 s confere com a previsão analítica de 51,8 s e com a medição de
03/11, no mesmo segundo. O incidente continua aberto durante toda a queda, como
deve: o alvo não voltou.

## Condição B — corte de 10 segundos

O alvo foi derrubado e, 10 segundos depois, o serviço voltou na mesma porta.

| | 03/11, antes | 04/11, depois |
|---|---|---|
| Alvo voltou a responder | sim | sim |
| **Incidente resolvido pelo sistema** | **não** | **sim** |
| Duração registrada da indisponibilidade | crescia sem fim | **10,334 s** |
| `page` disparou | sim, em 45,0 s | **não** |
| burn 1 h, máximo na observação | 86,427 | **2,871** |
| burn 5 min, máximo na observação | — | 34,446 |

A janela curta chega a 34,4, bem acima do limiar de 14,4, e é a exigência da
janela longa — 2,871, abaixo de 14,4 — que impede o plantão. A regra das duas
janelas do SRE Workbook faz exatamente o que deveria fazer com um pico isolado,
agora que o pico é mesmo isolado.

Ao fim dos 5 minutos de observação o burn de 5 minutos volta a 0,000, porque o
intervalo de 10 s saiu da janela. O de 1 hora segue em 2,871 até sair dela.

**Os 10,334 s registrados contra os 10 s reais** são o atraso de detecção mais o
de fechamento: o intervalo começa quando a sonda constata a falha e termina na
medição que constata a volta. Na primeira execução deste mesmo código, antes do
commit, o valor foi 10,977 s, com o mesmo resultado qualitativo — nenhum alerta
([`dados/e3-pos-71-ensaio-anterior.json`](dados/e3-pos-71-ensaio-anterior.json),
cujo campo `sha` registra a `develop`, porque a mudança ainda não estava
commitada; é a mesma correção).

## O que isto muda nos números já publicados

- **MTTR muda de significado, e para melhor.** Antes, `resolvido_em` só existia
  por clique humano, então o MTTR de 0,191 s de
  [`incidentes-mttd-burn.md`](incidentes-mttd-burn.md) só existia porque o script
  de medição resolvia cada incidente por chamada de API. Agora o MTTR de um
  incidente fechado pelo sistema é o tempo até o serviço voltar. **Os dois
  sentidos convivem** em `/api/eng/incidentes/resumo`: incidentes fechados à mão
  medem o tempo até alguém clicar, e os fechados pela coleta medem o tempo até a
  recuperação. Citar MTTR no texto exige dizer qual dos dois.
- **MTTA não muda.** `metricas()` só conta incidentes com `reconhecido_em`, e o
  fechamento automático não escreve esse campo. Incidentes que ninguém reconheceu
  continuam fora do MTTA, que é o correto.
- **O MTTD não muda.** A correção não toca a detecção, e o limite estrutural
  continua: nada grava o instante real da falha, então
  `/api/eng/incidentes/resumo` devolve `MTTD: n=0`.
- **A medição de MTTD, MTTA e MTTR foi repetida, e a previsão se confirmou:** o
  `medir_incidentes.py` derruba o alvo e o mantém derrubado até resolver por API,
  então nenhuma medição com sucesso aparece para fechar o incidente, e os 30
  intervalos continuaram vindo da resolução por API. Os números da repetição, no
  entanto, saíram todos maiores que os de 03/11 — MTTD médio 0,795 contra 0,712 s
  — com outro contêiner PostgreSQL e um servidor de front ligados na máquina. As
  duas execuções estão registradas em
  [`incidentes-mttd-burn.md`](incidentes-mttd-burn.md), e a recomendação é citar
  as duas no texto, não escolher a melhor: a diferença entre elas é a medida
  honesta de quanto a máquina influencia o resultado.

## Limites

- Uma máquina, loopback, **duas** execuções de cada condição, não trinta. Não há
  intervalo de confiança para os instantes de disparo.
- O passo de amostragem foi de 2 s na condição A e 5 s na B, então os instantes
  têm essa granularidade: o `page` real da condição A está entre 50 e 52 s.
- A condição B não foi repetida com durações intermediárias de corte. Continua
  sem resposta a partir de que duração o sistema passa a paginar legitimamente —
  o que agora é uma pergunta sobre o SLO, não sobre um defeito.
- O SLO de 99,9% em 30 dias é o padrão do módulo, não um objetivo acordado com o
  hospital. Os tempos até `page` dependem dele.
- O fechamento automático exige **um** sucesso. Um alvo que oscile a cada poucos
  segundos abre e fecha incidentes repetidamente; o que protege o plantão disso é
  a regra das duas janelas, não o ciclo de vida do incidente.
