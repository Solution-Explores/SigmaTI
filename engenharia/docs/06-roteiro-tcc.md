# 06 · Roteiro do TCC e trabalhos futuros

## Estrutura sugerida

| Capítulo | Conteúdo | Material nesta pasta |
|---|---|---|
| 1. Introdução | Problema hospitalar, MTTD/MTTR, objetivos, hipóteses H1–H4 | [00](00-visao-de-engenharia.md) |
| 2. Fundamentação | SRE (SLI/SLO/orçamento de erros), detecção de anomalias (EWMA, MAD, CUSUM), cadeias de hash, LGPD, redes (TCP, TLS) | — |
| 3. Requisitos e arquitetura | RF/RNF com rastreabilidade, ADRs, diagrama de implantação híbrido | [04](04-rastreabilidade.md), [adr/](adr/) |
| 4. Implementação | Módulos, decisões de projeto e propriedades verificadas por testes | [01](01-mapeamento-vigilark-sigma.md), [02](02-guia-de-implementacao.md) |
| 5. Metodologia de avaliação | Métricas, experimentos, ameaças à validade | [03](03-metodologia-experimental.md) |
| 6. Resultados | E1–E5, discussão do achado negativo (deriva) | `resultados/` |
| 7. Conclusão | Hipóteses confirmadas/refutadas, limitações, trabalhos futuros | — |

## Para aprofundar o lado de hardware (engenharia da computação)

Ideias com forte caráter de engenharia, ordenadas por viabilidade:

1. **Sonda embarcada**: portar `probe.py` para MicroPython/ESP32 ou Raspberry Pi em cada VLAN, enviando medições por MQTT/HTTPS com chave própria (RNF07). Medir consumo, precisão do relógio e perda.
2. **Sincronização de tempo**: avaliar o impacto do desvio de relógio (NTP vs PTP) no MTTD medido; propagar *offset* nas medições.
3. **Modelo de filas** para o pipeline alerta → fila → IA (M/M/1 ou M/G/1) e comparação com a latência medida em E2/E5.
4. **Telemetria SNMP/NetFlow**: sinais além de TCP (taxa de erros de interface, ocupação de CPU de switches) como entrada dos detectores.
5. **Detecção multivariada** e mudança acumulada (CUSUM/Page-Hinkley) para cobrir a deriva lenta.
6. **Verificação formal** da máquina de estados de aprovação (TLA+ ou model checking em Python) e dos invariantes da cadeia.

As issues do repositório detalham cada item.
