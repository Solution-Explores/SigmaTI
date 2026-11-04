# Limitações do trabalho

Material para o capítulo 7 do TCC (Conclusão), escrito em **04/11/2026**, antes
do congelamento de código (11/11) e da banca (18/11).

O propósito deste documento é um só: **ter os números desfavoráveis escritos
antes de alguém perguntar por eles.** Cada limitação abaixo tem a medição que a
sustenta e o arquivo onde ela está. Nenhuma delas invalida o trabalho; todas
limitam o que o texto pode afirmar.

[Voltar ao índice do TCC](README.md) · [Balanço dos dados](balanco-dos-dados.md)

---

## 1. A limitação que governa todas as outras: nada foi medido em rede real

**Todas as medições deste trabalho foram feitas em `127.0.0.1`**, numa única
máquina, contra alvos TCP sintéticos. O sistema nunca foi executado na rede do
hospital, e nenhuma medição usou tráfego real.

Consequências diretas:

- Os tempos de detecção medidos (MTTD de 0,7 a 0,8 s) são **limites inferiores**
  do que se veria em rede real: não há latência de rede, perda de pacote,
  retransmissão, nem concorrência com tráfego de produção.
- O detector de anomalias foi calibrado em **séries sintéticas lognormais**, uma
  escolha defensável para RTT (cauda pesada), mas que não é tráfego hospitalar.
  A issue #12 pede duas semanas de RTT real para refazer o E1; isso não acontece
  até a banca.
- Não há dados sobre topologia, VLANs, firewall intermediário ou roteamento.

O trabalho é, portanto, uma **validação em bancada de um sistema projetado para
um hospital**, não um estudo de caso de operação hospitalar. A diferença precisa
estar escrita no capítulo de conclusão, e não só nas ameaças à validade.

## 2. A degradação lenta quase não é detectada

O experimento E1 mediu três formas de falha, com 30 repetições cada
(`engenharia/resultados/e1_deteccao.md`):

| Cenário | Taxa de detecção (MAD) | F1 médio |
|---|---:|---:|
| degrau | 100% | 0,998 |
| pico | 100% | 0,971 |
| **deriva** | **16,7%** | **0,005** |

Nenhum dos dois detectores implementados pega degradação lenta: 20% com EWMA e
16,7% com MAD. Um serviço que piora aos poucos — exatamente o caso de um disco
envelhecendo ou de um enlace saturando devagar — passa invisível.

A causa é conhecida e não é um defeito de implementação: detectores de desvio
sobre janela móvel incorporam a deriva à própria linha de base. A família de
detectores adequada (CUSUM, Page-Hinkley) está na issue #10 e **não foi
implementada**. Dez dias não bastam para implementar e validar um detector novo
com honestidade, e a decisão registrada foi deixar isto como limitação, com o
número explícito, em vez de entregar um detector não avaliado.

## 3. A anonimização não atinge a meta que o próprio trabalho definiu

O critério original do RF05 era recall de transformação **≥ 99%**. No conjunto
cego — escrito por outra pessoa, sem ver as regras, como o orientador exigiu —
o resultado foi (`docs/historico/resultados/experimento-e6-conjunto-cego.md`):

| Métrica | Valor | IC 95% (Wilson) |
|---|---:|---|
| Recall de **transformação** | **95,12%** | [83,86% – 98,65%] |
| Recall de **proteção** (transformação + bloqueio *fail-closed*) | 100,00% | [91,43% – 100,00%] |
| Precisão operacional | 97,50% | [87,12% – 99,56%] |
| Falsos positivos em mensagem negativa | 5,00% (1/20) | [0,89% – 23,61%] |

**O critério original está REPROVADO**, e o texto deve dizer isso com essas
palavras. Dois identificadores de nome não foram transformados; foram
**bloqueados** pelo detector residual, de modo que nada vazou para fora — zero
vazamentos em 41 identificadores. É um resultado diferente do pedido, e melhor
do que "falhou": o sistema falha fechado.

A segunda limitação é estatística e não se resolve com mais regras. Com n = 41,
ou mesmo com os 53 identificadores do corpus completo, **o intervalo de
confiança não permite afirmar 99%**: mesmo sem nenhuma falha, o limite inferior
de Wilson só alcança 99% com cerca de **381 identificadores**. Qualquer
afirmação de "99% de recall" neste trabalho seria precisão inventada. A
reformulação do critério está na issue #5 e aguarda o orientador.

E a limitação de fundo: o corpus é **sintético**. Os resultados não demonstram
anonimização universal, conformidade jurídica com a LGPD, nem ausência de
vazamento em dados hospitalares reais.

## 4. O requisito de 15 segundos da IA não tem nenhuma evidência

O RNF04 exige resposta do diagnóstico assistido em **≤ 15 s**. Não existe uma
única medição com provedor real e filtro de anonimização ativo. O ensaio
existente usa provedor simulado, que responde em memória.

É um **requisito não funcional declarado sem evidência**, e tem de aparecer
assim na conclusão, não como "atendido". O E5 continua sem medição, e por isso a
issue #11 não fecha.

## 5. O painel não pode mostrar MTTD, por construção

`/api/eng/incidentes/resumo` devolve `MTTD: {"n": 0}` **sempre**. Não é defeito
de frontend nem de consulta: **nada na aplicação grava o instante real da
falha**. O que existe é `detectado_em`, o instante em que a sonda constatou a
queda — e a diferença entre os dois é justamente o MTTD.

O MTTD de 0,712 s (e 0,795 s na repetição) foi medido **por fora**, com um
cronômetro no script de medição, que sabe quando derrubou o serviço. O sistema,
em operação, não tem essa informação, e exibi-la exigiria decidir de onde ela
vem — uma mudança de esquema, não de tela.
Detalhe em [`evidencias/incidentes-mttd-burn.md`](evidencias/incidentes-mttd-burn.md).

## 6. MTTA e MTTR não são tempos de operador, e o MTTR tem dois sentidos

Os valores medidos de MTTA (0,159 s; 0,283 s na repetição) e MTTR (0,191 s;
0,359 s) **não medem o tempo de um técnico**. São reconhecimento e resolução
imediatos por chamada de API, feitos pelo script de medição. Citá-los como tempo
de resposta humana seria afirmar algo que o experimento não mediu.

A partir da correção da #71, o MTTR passou a ter **dois sentidos conviventes**:

- incidente fechado pelo sistema mede o **tempo até o serviço voltar**;
- incidente fechado à mão mede o **tempo até alguém clicar**.

`/api/eng/incidentes/resumo` agrega os dois na mesma média. Toda citação de MTTR
no texto precisa dizer qual dos dois está em jogo. O MTTA não tem essa
ambiguidade, porque só conta incidentes com `reconhecido_em`, e o fechamento
automático não escreve esse campo.

## 7. A cadeia de hash não detecta truncamento do fim

O experimento E4 (04/11, 1000 casos sobre uma trilha de 1000 entradas) mediu
quatro tipos de adulteração:

| Mutação | `verificar()` detecta | Âncora detecta |
|---|---:|---:|
| um byte de uma linha trocado | 100% | 0% |
| uma linha apagada | 100% | 100% |
| duas linhas trocadas de lugar | 100% | 0% |
| **1 a 5 linhas apagadas do fim** | **0%** | 100% |

Nos 750 casos das três primeiras, a verificação apontou **exatamente** o índice
mutado. No quarto tipo, falhou em 250 de 250 — e falha por construção: uma
trilha cortada no fim continua coerente consigo mesma, porque quem apaga o fim
apaga também o registro de que aquele fim existia.

A consequência para o texto é uma frase, e ela precisa ser dita com precisão: a
garantia da trilha é **"ninguém alterou nem removeu o meio"**. Ela só passa a ser
"ninguém removeu nada" se a âncora (`ancora()`: contagem de entradas e último
hash) for guardada **fora da máquina** e conferida. Essa custódia externa é um
procedimento operacional, e não está implementada como rotina.
Detalhe em `engenharia/resultados/e4_fuzzing_cadeia.md`.

## 8. Rotas que respondem sucesso sem efeito (#57)

A issue #57 registra rotas de API que devolvem `200` sem realizar a ação, entre
elas rotação de chaves e registro de incidente. Enquanto ela estiver aberta,
"verificado por teste" significa **verificado pelo teste que existe** — e a #57
diz que alguns desses testes podem estar provando menos do que parece.

É a dependência mais incômoda do trabalho, porque afeta a confiança em tudo o
que o balanço classifica como "verificado, sem número a citar": RNF07 (chaves),
RF07 (acesso), RF05 (falha segura do filtro), RNF05 e RNF06. A issue é do outro
integrante da equipe e não tem responsável atribuído no GitHub.

## 9. O que foi medido, foi medido pouco

| Medição | Repetições | O que falta |
|---|---|---|
| E3, burn rate (queda de 10 min e corte de 10 s) | **2** de cada condição | intervalo de confiança; durações intermediárias de corte |
| MTTD, MTTA, MTTR | 2 execuções de 30 repetições | mais execuções, em máquinas diferentes |
| Rodadas de carga (200 alvos) | 3 consecutivas | — |
| E1, detecção | 30 por cenário | — |
| E4, fuzzing | 1000 casos, **uma** semente | variação de N e de semente |

E há um efeito de ambiente medido sem querer: as duas execuções de MTTD deram
**0,712 s** e **0,795 s** de média, com MTTA variando 0,159 → 0,283 s. A
segunda rodou com outro contêiner PostgreSQL e um servidor de desenvolvimento
ligados na mesma máquina. **A diferença entre execuções é maior que o desvio
dentro de cada uma**, então o texto deve citar as duas, não escolher a melhor, e
não apresentar um valor único de MTTD com três casas decimais.

Além disso, o passo de amostragem do E3 foi de 2 s (condição A) e 5 s (condição
B), então os instantes de disparo têm essa granularidade: o `page` da condição A
está entre 50 e 52 s, e 52,0 s é o valor observado.

## 10. Desvios de ambiente declarados

- **A VM do VirtualBox ficou inacessível** na segunda metade da Sprint 2, porque
  o disco ficou na outra máquina. As medições de 03 e 04/11 foram feitas em
  **máquina física**, e não na VM prevista no planejamento. O desvio está
  declarado em cada registro.
- **As quatro execuções instáveis** investigadas na #45 coincidiram com paradas
  do VirtualBox; em máquina física, 120 execuções isoladas dos quatro testes não
  produziram **nenhuma** falha. A causa, portanto, é de ambiente, não do código
  — mas a **revisão independente** exigida pelo critério da issue não aconteceu,
  e por isso a caixa segue desmarcada.
- O SLO de 99,9% em 30 dias usado em todos os cálculos de burn rate é o
  **padrão do módulo**, não um objetivo acordado com o hospital. Todos os tempos
  até `page` dependem dele: com outro alvo, mudam.
- O relógio é o da própria máquina em todas as medições. Em rede real, NTP
  contra PTP altera o MTTD, e esse efeito **não foi quantificado** (issue #27).

## 11. O que o fechamento automático de incidente ainda não resolve

A correção da #71 fecha o incidente de disponibilidade com **um** sucesso da
sonda. Um alvo que oscile a cada poucos segundos passa a abrir e fechar
incidentes repetidamente. O que protege o plantão disso não é o ciclo de vida do
incidente, e sim a regra de burn rate de duas janelas — foi o que o E3 mostrou:
a janela curta chegou a 34,4, bem acima do limiar de 14,4, e o alerta não saiu
porque a janela longa ficou em 2,871.

Fica sem resposta: **a partir de que duração de queda o sistema deve paginar
legitimamente?** A condição B não foi repetida com durações intermediárias. É
hoje uma pergunta sobre o SLO acordado, não sobre um defeito.

---

## Como usar isto no texto

1. A seção 1 (nada em rede real) é a limitação de maior alcance e deve abrir o
   capítulo. As demais são específicas.
2. As seções 2, 3 e 4 são resultados desfavoráveis **de hipóteses do próprio
   trabalho**: a deriva refuta parcialmente H1, o recall de 95,12% reprova o
   critério original do RF05, e o RNF04 não tem evidência nenhuma. Uma banca de
   computação pergunta por esses três.
3. As seções 5, 6 e 7 são limites **do que o sistema sabe**, não do que ele faz:
   MTTD indisponível, MTTR ambíguo, truncamento invisível sem custódia externa
   da âncora.
4. A seção 9 é a mais fácil de esquecer e a mais barata de escrever: dizer
   quantas vezes cada coisa foi medida.
