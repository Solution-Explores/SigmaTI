# E3 — burn rate com queda prolongada e com corte curto

Medição de 03/11/2026, em máquina física, no SHA `23e1a94` (a `develop` `55a1796`
mais os dois commits de documentação deste PR, que não tocam o coletor, o
agendador nem a API).

Critério da issue #11: **alvo caído por 10 min deve chegar a `page`; corte de 10 s
não deve paginar.**

> **Atualização de 04/11/2026.** O defeito que esta medição encontrou foi
> corrigido no mesmo dia (#71, PR #79), e o E3 foi remedido: a condição B deixou
> de paginar, com o incidente fechando sozinho em 10,334 s. Este documento
> permanece como o estado **antes** da correção, que é o que justifica a #71. O
> depois está em [`e3-pos-71.md`](e3-pos-71.md).


Script `scripts/medir_e3.py`, dado bruto em
[`dados/e3-burn-rate.json`](dados/e3-burn-rate.json) com as 301 amostras da
condição A e as 61 da condição B.

```
python scripts/medir_e3.py --output <saida>.json --minutos-a 10 --segundos-b 10 --observacao-b 5
```

SLO usado: 99,9% em 30 dias. Regras de burn rate do SRE Workbook, como
implementadas em `sigma_eng/slo.py`: cada regra exige a janela longa **e** a curta
acima do limiar.

## Resultado em uma linha

| Condição | Esperado | Medido | |
|---|---|---|:-:|
| A · queda de 10 min | chega a `page` | `page` em **52,0 s** | ✅ |
| B · corte de 10 s | não pagina | `page` em **45,0 s** | ❌ |

A primeira metade do critério passa com folga. **A segunda falha**, e a causa não
está no cálculo de burn rate.

## Condição A — queda de 10 minutos

O alvo foi derrubado e mantido caído por 10 minutos, com o burn rate amostrado a
cada 2 segundos sobre o intervalo que o sistema registra.

| Segundos desde a queda | burn 1 h | burn 5 min | Regras disparadas |
|---:|---:|---:|---|
| 44 | 12,299 | 147,594 | — |
| 48 | 13,411 | 160,930 | — |
| 50 | 13,967 | 167,600 | — |
| **52** | **14,522** | 174,267 | **`page` (limiar 14,4)** |
| 600 | 166,784 | 1000,000 | `page` 14,4 · `page` 6,0 · `ticket` 3,0 · `ticket` 1,0 |

O disparo em 52 s confere com a previsão analítica. Numa queda contínua, a janela
de 5 minutos passa de 14,4 em cerca de 4,3 segundos, e a de 1 hora só em cerca de
51,8 segundos; como a regra exige as duas, quem manda é a janela longa. O
experimento mediu 52,0 s com passo de amostragem de 2 s, portanto o valor real
está entre 50 e 52 s.

Ao fim dos 10 minutos as quatro regras estavam disparadas, incluindo as duas de
`ticket`. É o escalonamento esperado para uma indisponibilidade que persiste.

## Condição B — corte de 10 segundos

O alvo foi derrubado, e **10 segundos depois o serviço voltou na mesma porta**. A
volta foi confirmada pela própria coleta: há medição com sucesso registrada
depois da recuperação. O burn rate foi então amostrado por 5 minutos.

| | |
|---|---|
| Alvo voltou a responder | sim, confirmado pelas medições |
| Incidente resolvido pelo sistema | **não** |
| `page` disparou | **sim, em 45,0 s** |
| burn 1 h aos 5 min de observação | 86,427 |

**O alvo estava no ar e o sistema paginou.** Não é erro de medição: é consequência
de o incidente nunca ter sido fechado.

### A lógica de alerta está correta

O mesmo cálculo, com o intervalo de indisponibilidade recortado nos 10 segundos
reais de queda, **não dispara nada, em nenhum instante de avaliação**:

| Avaliado em | burn 5 min | burn 30 min | burn 1 h | burn 2 h | burn 6 h | Alertas |
|---|---:|---:|---:|---:|---:|---|
| no instante da recuperação | 33,333 | 5,556 | 2,778 | 1,389 | 0,463 | nenhum |
| 1 min depois | 33,333 | 5,556 | 2,778 | 1,389 | 0,463 | nenhum |
| 5 min depois | 0,000 | 5,556 | 2,778 | 1,389 | 0,463 | nenhum |

A janela curta chega a 33,3, bem acima de 14,4, e é justamente a exigência da
janela longa — 2,778, abaixo do limiar — que impede o plantão. A regra das duas
janelas do SRE Workbook está implementada corretamente e faz exatamente o que
deveria fazer com um pico isolado.

## A causa: o incidente nunca se fecha sozinho

`resolvido_em` é escrito em **um único lugar** do código,
`backend/persistence/operational.py`, dentro de `change_incident`, que atende as
rotas `/api/eng/incidentes/{id}/reconhecer` e `/resolver`. Na gravação de
medições, `_incident` só é chamado quando `not success`; quando a medição volta a
ter sucesso, **nada** fecha o incidente de disponibilidade em aberto.

Consequência: o sistema sabe quando um alvo caiu e não sabe quando ele voltou.
Para o cálculo de SLO, toda queda é uma queda que continua até alguém clicar em
resolver. Qualquer oscilação de rede de poucos segundos vira, em menos de um
minuto, um `page`.

Isso também recontextualiza o MTTR de 0,191 s registrado em
[`incidentes-mttd-burn.md`](incidentes-mttd-burn.md): aquele número existe porque
o script de medição resolvia cada incidente imediatamente por chamada de API. Em
operação, o MTTR do sistema é o tempo até a intervenção humana, não o tempo até o
serviço voltar.

## O que isto significa para o texto do TCC

- O **E3 passa pela metade**, e a metade que falha é mais interessante que a que
  passa. Vale escrever assim.
- A **detecção** e o **alerta por múltiplas janelas** estão validados
  experimentalmente: 52 s até o `page` numa queda real, e nenhum alerta num pico
  isolado corretamente delimitado.
- O que falta é **resolução automática de incidente de disponibilidade**: fechar o
  incidente quando a sonda voltar a ter sucesso. É mudança pequena e localizada,
  mas é mudança de comportamento do sistema, com a #57 ainda aberta sobre rotas
  que respondem sucesso sem efeito.

## Limites

- Loopback, uma máquina, uma execução de cada condição. Não há repetição com
  intervalo de confiança.
- O passo de amostragem foi de 2 s na condição A e 5 s na B, então os instantes
  de disparo têm essa granularidade.
- O SLO de 99,9% em 30 dias é o padrão do módulo, não um objetivo acordado com o
  hospital. Os tempos até `page` dependem dele: com outro alvo, mudam.
- A condição B não foi repetida com durações intermediárias. Não se sabe a partir
  de que duração de corte o sistema passaria a paginar legitimamente.
