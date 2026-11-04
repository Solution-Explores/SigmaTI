# E4 — fuzzing da cadeia de hash da trilha de auditoria

Execução de **04/11/2026**, em máquina física, com a `develop` em `857e3ff`.
Script [`experimentos/exp_fuzzing_cadeia.py`](../experimentos/exp_fuzzing_cadeia.py),
semente fixa **20261104**, dado bruto em
[`e4_fuzzing_cadeia.csv`](e4_fuzzing_cadeia.csv) (um caso por linha) e resumo em
[`e4_fuzzing_cadeia_resumo.csv`](e4_fuzzing_cadeia_resumo.csv).

```
cd engenharia && python -m experimentos.exp_fuzzing_cadeia --n 1000 --casos-por-tipo 250
```

**Critério da issue #11:** trilha de N = 1000 entradas, uma mutação aleatória por
caso, e `verificar()` apontando um índice **menor ou igual** ao da mutação em 100%
dos casos.

## Resultado

Mil casos sobre uma trilha de mil entradas, 250 por tipo de mutação.

| Mutação | Casos | Detectada por `verificar()` | Índice ≤ ao mutado | Detectada pela âncora |
|---|---:|---:|---:|---:|
| `byte` — um byte de uma linha trocado | 250 | **250 (100%)** | 250 | 0 |
| `remocao` — uma linha apagada | 250 | **250 (100%)** | 250 | 250 |
| `troca` — duas linhas trocadas de lugar | 250 | **250 (100%)** | 250 | 0 |
| `truncamento` — 1 a 5 linhas apagadas do fim | 250 | **0 (0%)** | 0 | 250 (100%) |

Nos 750 casos das três primeiras mutações, o índice reportado foi **exatamente** o
índice mutado, nunca um anterior: a verificação não só detecta, como localiza. As
mutações de byte nunca precisaram ser reamostradas — nenhuma caiu em posição sem
efeito sobre o JSON, porque as linhas são compactas e não têm espaço supérfluo.

## O caso que falha, e por quê

**Cortar o fim do arquivo não é detectado por `verificar()`.** Uma trilha truncada
continua internamente coerente: as entradas que sobraram encadeiam corretamente
entre si, e a verificação percorre tudo sem achar defeito. Nos 250 casos de
truncamento, `verificar()` devolveu "íntegra" todas as vezes.

Isto **não** é um defeito da cadeia de hash: é o limite conhecido de qualquer
cadeia encadeada lida só a partir dela mesma. Quem apaga o fim apaga também o
registro de que aquele fim existia. É exatamente para isso que existe o
`ancora()`: o resumo com a contagem de entradas e o último hash, guardado **fora
da máquina**. Comparado com a âncora anterior, o truncamento aparece em 100% dos
casos, porque a contagem e o último hash mudam.

A consequência prática, que precisa estar no texto do TCC: a integridade da trilha
depende de a âncora ser guardada em outro lugar e conferida. Sem isso, a garantia
da cadeia é "ninguém alterou nem removeu o meio", não "ninguém removeu nada".

A âncora também não vê mutações no meio (0 de 250 em `byte` e `troca`), porque nem
a contagem nem o último hash mudam. As duas conferências são complementares, e a
operação precisa das duas.

## Limites desta medição

- Uma trilha, uma semente, um tamanho (N = 1000). Não há variação de tamanho nem
  repetição com sementes diferentes.
- Uma mutação por caso. Mutações combinadas (alterar uma linha **e** corrigir o
  encadeamento das seguintes) não foram testadas; um adversário com a chave HMAC
  pode reescrever a trilha inteira, e isso está fora do que a cadeia promete.
- A chave usada é fixa e está no script, só para o experimento ser reproduzível.
  Não é chave de produção.
- Os dados da trilha são fictícios (`ator-N`, `alvo-N`), sem nada pessoal.

## O que isto fecha e o que não fecha

Fecha o E4 da #11, com o desvio declarado: o critério de 100% vale para as três
mutações que ele cita (byte, remoção e troca). O quarto tipo, truncamento do fim,
foi acrescentado por conta própria, falha por construção e está registrado aqui
em vez de omitido.

**A #11 continua aberta:** o E5 (RNF04, resposta da IA em ≤ 15 s) segue sem
medição.
