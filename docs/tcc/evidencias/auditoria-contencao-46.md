# Contenção da trilha de auditoria (#46)

Complemento de [auditoria-custo-46.md](auditoria-custo-46.md). Aquele registro mede o custo por operação em um processo; este mede **vários processos gravando ao mesmo tempo na mesma trilha**, a lacuna que a #46 declarava ("contenção entre processos não foi medida").

## Método

- Trilha sintética de 100.000 entradas, mesma chave HMAC e mesmo formato de `AuditChain`. Cada rodada parte de uma cópia idêntica.
- N processos independentes disparam `registrar()` no mesmo instante, em rajada contínua (o pior caso), e uma variante com 100 ms entre gravações.
- Por gravação: latência. Por rodada: erros (por exemplo, o lock de 10 s expirando), vazão e, no fim, `verificar()` completo e contagem de entradas. **Em todas as rodadas a cadeia ficou íntegra, sem entrada perdida nem duplicada: sim.**
- Antes: `develop` `b657509` (código do #60), 5 gravações por processo (cada uma leva cerca de 1,5 s). Depois: PR #65, 20 gravações por processo. Mesmo script: `scripts/benchmark_auditoria_contencao.py`.
- Máquina: computador físico Windows 10, 16 GB, 12 processadores lógicos, SSD, Python 3.12.10, 03/11/2026. Uma execução por condição (sem repetições): os valores mostram a ordem de grandeza, não um intervalo de confiança.

## Resultado: antes (`develop`, rajada)

| Processos | Gravações ok | Erros (lock) | Mediana (ms) | p95 (ms) | Máx. (ms) | Gravações/s | 1ª gravação, mediana (ms) | Demais, mediana (ms) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5/5 | 0 | 1.548 | 1.570 | 1.570 | 0,5 | 1.570 | 1.545 |
| 4 | 20/20 | 0 | 4.798 | 10.919 | 11.019 | 0,5 | 4.108 | 4.888 |
| 8 | 26/40 | 14 | 6.215 | 11.141 | 11.355 | 0,5 | 7.097 | 6.186 |

## Resultado: depois (PR #65, rajada)

| Processos | Gravações ok | Erros (lock) | Mediana (ms) | p95 (ms) | Máx. (ms) | Gravações/s | 1ª gravação, mediana (ms) | Demais, mediana (ms) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20/20 | 0 | 38,9 | 40,9 | 1.018 | 10,8 | 1.018 | 38,8 |
| 4 | 80/80 | 0 | 39,2 | 1.094 | 5.509 | 10,9 | 3.583 | 39,2 |
| 8 | 159/160 | 1 | 39,4 | 3.460 | 10.251 | 10,7 | 4.973 | 39,3 |

## Resultado: depois (PR #65, 100 ms entre gravações)

| Processos | Gravações ok | Erros (lock) | Mediana (ms) | p95 (ms) | Máx. (ms) | Gravações/s | 1ª gravação, mediana (ms) | Demais, mediana (ms) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 80/80 | 0 | 71,7 | 1.296 | 4.569 | 9,3 | 2.832 | 71,6 |
| 8 | 160/160 | 0 | 237 | 3.335 | 9.163 | 9,8 | 5.007 | 236 |

## O que isso mostra

- **A contenção melhorou muito.** Com 8 processos, antes, 14 de 40 gravações (35%) falharam por lock expirado e a mediana foi de cerca de 6 s, com menos de 1 gravação por segundo. Depois, 1 de 160 (0,6%) falhou, a mediana ficou em cerca de 39 ms e a vazão subiu para cerca de 11 gravações por segundo, mais de 15 vezes.
- **Resta um limite, e ele é a partida fria.** A primeira gravação de cada processo novo não tem cache e custa uma verificação completa, sob o lock exclusivo. Com 100.000 entradas isso leva cerca de 1 s nesta máquina. Quando vários processos nascem juntos, essas verificações se enfileiram: com 8, a primeira gravação chega a cerca de 10 s e passa do limite de 10 s do lock, a explicação mais provável para o erro que sobrou. O script não registra em qual gravação o erro ocorreu, então isso é inferência, não medição direta. As gravações seguintes, já com cache, ficam em dezenas de milissegundos, mas esperam atrás de quem está em partida fria (p95 alto na coluna "demais").
- **Quando isso importa.** A API roda com um único worker, então a partida fria acontece uma vez por reinício. O caso medido (8 processos novos ao mesmo tempo sobre uma trilha de 100 mil entradas) é o pior, não o uso normal.
- **O erro é uma gravação recusada, não corrupção:** a cadeia continuou íntegra em todas as rodadas.

## Limites desta medição

- Uma execução por condição, uma máquina, um tamanho (100.000). Não houve 1 milhão de entradas, VM Linux nem cache de arquivo frio.
- O "antes" usa 5 gravações por processo e o "depois" 20, para o "antes" terminar em tempo razoável. As métricas por gravação são comparáveis; o tempo total, não.
- A trilha é sintética e montada sem `fsync` por linha. Sob o `fsync` real, cada gravação custa mais.

## Como reproduzir

```bash
python scripts/benchmark_auditoria_contencao.py --tamanho 100000 --processos 1 4 8 --gravacoes 20
python scripts/benchmark_auditoria_contencao.py --tamanho 100000 --processos 4 8 --gravacoes 20 --intervalo-ms 100
```

Para o "antes", rode o mesmo comando em um checkout da `develop` sem o #65. O script usa o `engenharia/` do checkout em que está.

Dados brutos: `dados/auditoria-contencao-antes.json`, `dados/auditoria-contencao-depois.json` e `dados/auditoria-contencao-depois-espacado.json`.

## Possíveis passos depois (não feitos aqui)

- Aquecer o estado verificado na inicialização da API, antes de aceitar tráfego, para a primeira requisição não pagar a verificação.
- Verificar a trilha fora do lock exclusivo na partida fria, e conferir só o trecho acrescentado ao tomar o lock.
- Tornar o tempo limite do lock configurável.
