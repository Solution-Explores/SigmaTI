# 03 · Metodologia experimental

Princípios: **semente fixa**, **repetições** (n ≥ 30), **saída em CSV**, **scripts versionados**, e relatar média com desvio-padrão (ou mediana e p95 para tempos).

## Métricas e definições

| Métrica | Definição | Instrumento |
|---|---|---|
| Latência de sonda | Tempo do handshake TCP (`perf_counter`) | `probe_service` |
| Perda | falhas ÷ amostras | `probe_many` |
| Jitter | média de \|Δ latência\| entre amostras consecutivas | `probe_many` |
| TTD / MTTD | `detectado_em − inicio_real` | `incidents.metricas` |
| MTTA / MTTR | `reconhecido − detectado` / `resolvido − detectado` | `incidents.metricas` |
| Atraso de detecção | amostras entre o início da falha e o 1º alarme | `anomaly.avaliar` |
| Precisão / Revocação / F1 | por amostra, contra rótulos | `anomaly.avaliar` |
| Burn rate | erro observado ÷ erro permitido (1 = ritmo exato do SLO) | `slo.burn_rate` |

## Experimentos

| ID | Objetivo | Hipótese | Status |
|---|---|---|---|
| **E1** | Qualidade dos detectores com falha injetada em séries sintéticas | H1 | ✅ Implementado (`experimentos/exp_deteccao.py`) |
| **E2** | Latência ponta a ponta do alerta até o painel (RF01 ≤ 5 s) | H4 | Ensaio local implementado: scripts/validate_collection.py; tela pendente #15 |
| **E3** | Burn rate em rede real: tempo até `page` com sonda caída | H2 | ⚠️ Medido em laboratório 03/11: queda de 10 min pagina em 52 s; corte de 10 s **pagina indevidamente** |
| **E4** | Fuzzing da cadeia de hash (adulterar, remover, reordenar N entradas) | H3 | ⚠️ Medido em 04/11: 100% nas três mutações do critério; **truncamento do fim não é detectado** pela verificação, só pela âncora |
| **E5** | Latência da resposta da IA (RNF04 ≤ 15 s) com anonimização | H4 | ⬜ A fazer |

### E1 · Resultados (implementado)

Setup: 600 amostras lognormais (mediana ≈ 20 ms, σ = 0,15), uma falha por série a partir da amostra 300, 30 sementes (0–29).

| cenário | detector | detecção | atraso (amostras) | FP/série | F1 |
|---|---|---|---|---|---|
| degrau (+40 ms, 60 am.) | EWMA(α=0,1; k=4) | 100% | 0 | 1,37 | 0,908 |
| degrau | MAD(w=60; k=5) | 100% | 0 | 0,23 | 0,998 |
| pico (+80 ms, 3 am.) | EWMA | 100% | 0 | 1,90 | 0,783 |
| pico | MAD | 100% | 0 | 0,20 | 0,971 |
| deriva (+0,5 ms/am., 120 am.) | EWMA | 20% | 12,5 | 52,07 | 0,002 |
| deriva | MAD | 17% | 17,6 | 0,30 | 0,005 |

**Leitura:**
- MAD tem menos falsos positivos que EWMA porque a mediana/MAD resistem à cauda pesada da lognormal.
- **Ambos falham na deriva lenta**: cada passo fica dentro de k·σ, e o modelo acompanha a rampa. Detectores de mudança acumulada (CUSUM, Page-Hinkley) são o caminho natural.
- **Achado de projeto:** com o EWMA congelando o modelo em anomalias, uma mudança permanente de patamar travava o detector em alarme (180 FP/série). `reaprender_apos=50` reduziu para 52, ao custo de F1 menor no degrau (0,987 → 0,908): o detector deixa de alarmar quando aceita o novo patamar. Esse *trade-off* é parametrizável e deve ser calibrado com dados reais.

Reproduzir: `python -m experimentos.exp_deteccao`.

### E2 · Latência falha → SSE (ensaio local implementado; painel pendente)

O script `scripts/validate_collection.py` injeta 30 quedas de um serviço TCP em loopback, depois de comprovar uma medição disponível. Registra t0 antes de fechar o listener e t1 ao receber o evento por SSE HTTP real; produz CSV e JSON com mediana, p95, máximo e proporção ≤5 s. Mede também 200 alvos lógicos locais, reinício da API, replay e revogação da sessão. PostgreSQL em schema descartável, nomes e credenciais fictícios.

Reprodução, limites e configuração: [coleta e eventos](09-coleta-eventos.md). Os resultados do laboratório não comprovam renderização do painel (#15), 200 equipamentos físicos nem comportamento de DROP/firewall real. Repetir no ambiente de homologação com relógios sincronizados e condições representativas.

### E3 · Burn rate (medido em laboratório; rede real pendente)

Executado em 03/11/2026 em loopback, máquina física, com SLO de 99,9% em 30 dias. Script `scripts/medir_e3.py`; evidência e dado bruto em [`docs/tcc/evidencias/e3-burn-rate.md`](../../docs/tcc/evidencias/e3-burn-rate.md).

**Condição A, queda de 10 min:** `page` em **52,0 s**, com passo de amostragem de 2 s. Confere com a previsão analítica de 51,8 s, em que a janela longa de 1 h é a que determina o disparo. Ao fim dos 10 min as quatro regras estavam disparadas, incluindo as duas de `ticket`. **Critério atendido.**

**Condição B, corte de 10 s:** o serviço voltou na mesma porta, a coleta registrou sucesso, e o sistema **paginou em 45,0 s**. **Critério não atendido.** A causa não é o cálculo de burn rate: com o intervalo de indisponibilidade recortado nos 10 s reais, nenhuma regra dispara em nenhum instante de avaliação (janela curta 33,3, janela longa 2,778, limiar 14,4). O defeito é que o incidente de disponibilidade **nunca é fechado automaticamente**: `resolvido_em` só é escrito pelas rotas manuais `/reconhecer` e `/resolver`, e a gravação de medição com sucesso não encerra o incidente em aberto. Para o cálculo de SLO, toda queda continua até a intervenção humana.

Pendente: repetir em rede real, com repetições e intervalo de confiança, e com durações intermediárias de corte, para saber a partir de que duração o `page` passa a ser legítimo.

### E4 · Fuzzing da cadeia (medido em 04/11/2026)

Trilha de N = 1000 entradas, uma mutação aleatória por caso, 250 casos por tipo, semente fixa 20261104. Script `experimentos/exp_fuzzing_cadeia.py`, resultado em [`resultados/e4_fuzzing_cadeia.md`](../resultados/e4_fuzzing_cadeia.md) e dado bruto em `resultados/e4_fuzzing_cadeia.csv`.

| Mutação | Casos | `verificar()` detecta | Índice ≤ ao mutado | Âncora detecta |
|---|---:|---:|---:|---:|
| um byte de uma linha trocado | 250 | 100% | 250 | 0 |
| uma linha apagada | 250 | 100% | 250 | 250 |
| duas linhas trocadas de lugar | 250 | 100% | 250 | 0 |
| 1 a 5 linhas apagadas do fim | 250 | **0%** | 0 | 100% |

Nos 750 casos das três mutações do critério, o índice reportado foi exatamente o índice mutado. O critério da #11 passa.

O quarto tipo foi acrescentado além do critério e **falha por construção**: uma trilha cortada no fim continua coerente consigo mesma, então a verificação não tem como saber que havia mais. É o que o `ancora()` resolve, comparado com o resumo guardado fora da máquina — ali o truncamento aparece em 100% dos casos. As duas conferências são complementares: a âncora, por sua vez, não vê mutação no meio.

### E5 · RNF04 (a fazer)

Medir tempo de resposta do chat com o filtro de anonimização ativo, n ≥ 30, por horário do dia (camada gratuita do provedor varia).

## Ameaças à validade

| Tipo | Ameaça | Mitigação |
|---|---|---|
| Construto | Séries sintéticas lognormais podem não refletir o tráfego hospitalar | Coletar RTT real por ≥ 2 semanas e repetir E1 |
| Interna | Parâmetros (α, k, janela) escolhidos sem ajuste | Varredura de parâmetros e validação cruzada temporal |
| Externa | Resultados de um só hospital | Declarar como estudo de caso |
| Conclusão | Falhas injetadas são mais "limpas" que as reais | Rotular incidentes reais retroativamente |
| Medição | Relógios não sincronizados distorcem MTTD | NTP/chrony nos hosts; registrar o offset |
| Construto | A cadeia de hash, lida só a partir dela mesma, não detecta truncamento do fim (E4, 0 de 250 casos) | Guardar a âncora (`ancora()`) fora da máquina e conferir; declarar o limite no texto |
