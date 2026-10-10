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
| **E2** | Latência ponta a ponta do alerta até o painel (RF01 ≤ 5 s) | H4 | ⬜ A fazer |
| **E3** | Burn rate em rede real: tempo até `page` com sonda caída | H2 | ⬜ A fazer |
| **E4** | Fuzzing da cadeia de hash (adulterar, remover, reordenar N entradas) | H3 | ⬜ A fazer (há testes unitários) |
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

### E2 · Latência alerta → painel (a fazer)

1. Injetar a falha em um alvo (`iptables -A INPUT -p tcp --dport X -j DROP` no alvo de teste).
2. Registrar `t0` (comando de injeção) e `t1` (evento SSE recebido por um cliente de teste).
3. n ≥ 30 repetições; reportar mediana, p95 e proporção ≤ 5 s.

### E3 · Burn rate em rede real (a fazer)

Derrubar a sonda por 10 min com SLO de 99,9%; medir o tempo até o primeiro `page` e confirmar que um corte de 10 s **não** pagina.

### E4 · Fuzzing da cadeia (a fazer)

Gerar cadeias de N=1000 entradas; aplicar mutação aleatória (alterar um byte de um campo, remover ou trocar duas linhas) e verificar que `verificar()` reporta o índice ≤ ao da mutação em 100% dos casos.

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
