# Balanço dos dados do TCC

Situação em **03/11/2026**, com a `develop` em `55a1796`. O propósito é um só:
dizer, para cada afirmação que o texto precisa sustentar, se existe número
medido, onde ele está, e o que ele **não** cobre. A banca é em 18/11 e o
congelamento de código em 11/11, então o que não estiver medido até lá entra no
texto como limitação, não como resultado.

Três estados: **medido** (há número, dado bruto e script reprodutível),
**verificado** (há prova de funcionamento, sem número a citar) e **lacuna**
(não existe evidência).

---

## 1. Resumo

| | Quantos |
|---|---:|
| Medido, com dado bruto no repositório | 8 |
| Verificado por teste automatizado, sem número a citar | 5 |
| Lacuna que ainda dá tempo de fechar até 11/11 | 2 |
| Lacuna que vai para as limitações | 4 |
| Defeito encontrado ao medir, ainda sem correção | 1 |

O texto tem base empírica para detecção, latência de alerta, resposta a
incidentes, burn rate, anonimização, custo de auditoria e restauração de backup.
**Não tem** nada medido sobre o requisito de 15 segundos da IA (RNF04) nem sobre
rede real.

A medição do E3, feita em 03/11 depois da primeira versão deste balanço,
encontrou um defeito: incidentes de disponibilidade nunca se fecham sozinhos, e
por isso um corte de 10 segundos gera `page`. Está na seção 2.8.

---

## 2. Medido

### 2.1 Detecção em séries sintéticas (E1)

`engenharia/resultados/e1_deteccao.md` e `.csv`.

| Cenário | Detector | Taxa de detecção | F1 médio |
|---|---|---:|---:|
| degrau | MAD(w=60,k=5) | 100% | 0,998 |
| pico | MAD(w=60,k=5) | 100% | 0,971 |
| deriva | MAD(w=60,k=5) | **16,7%** | 0,005 |

**O número incômodo é o da deriva, e ele precisa estar no texto.** Nenhum dos dois
detectores pega degradação lenta: 20% com EWMA e 16,7% com MAD. É a razão de
existir a issue #10 (CUSUM e Page-Hinkley) e deve aparecer como limitação
conhecida, não ser omitido. O MAD é melhor que o EWMA em falsos positivos por
série (0,3 contra 52,07 na deriva), o que justifica a escolha do padrão.

### 2.2 Latência de alerta, falha → painel (RF01 ≤ 5 s)

Três rodadas consecutivas de 03/11, com 200 alvos, em máquina física. Registradas
na issue #8.

| Rodada | p95 | Máximo | Dentro de 5 s | Atraso máx. do calendário |
|---:|---:|---:|---:|---:|
| 1 | 0,835 s | 0,868 s | 100% | 0,039 s |
| 2 | 0,781 s | 0,803 s | 100% | 0,040 s |
| 3 | 0,794 s | 0,832 s | 100% | 0,044 s |

Meta do atraso do calendário: 0,5 s. Pior caso das três: 0,044 s, cerca de onze
vezes abaixo.

### 2.3 MTTD, MTTA, MTTR e burn rate

[`evidencias/incidentes-mttd-burn.md`](evidencias/incidentes-mttd-burn.md), dado
bruto em `evidencias/dados/incidentes-mttd-burn.json`, script
`scripts/medir_incidentes.py`. 30 repetições.

| Métrica | Média | p95 |
|---|---:|---:|
| MTTD (queda → SSE) | 0,712 s | 0,794 s |
| MTTA | 0,159 s | 0,246 s |
| MTTR | 0,191 s | 0,266 s |

Burn rate contra SLO de 99,9% em 30 dias: 7,519 em 1 h, abaixo do limiar de 14,4,
portanto sem alerta — comportamento correto para trinta quedas de menos de um
segundo.

**Dois avisos que precisam acompanhar esses números no texto.** MTTD é limite
superior, porque inclui a entrega pelo SSE. E MTTA e MTTR **não são humanos**: são
reconhecimento e resolução imediatos por chamada de API. Medem o caminho do
sistema, não o tempo de um técnico. Citá-los sem essa ressalva seria afirmar algo
que o experimento não mediu.

### 2.4 Anonimização por identificador (E6)

`engenharia/resultados/experimento-e6-anonimizacao.md`. 59 amostras, 53
identificadores de nove classes. Recall de transformação 100%, zero vazamentos,
zero falsos positivos.

**O limite é estatístico, e é o que trava a #5.** Com n = 53 e nenhum erro, o
intervalo de confiança de Wilson não permite afirmar recall ≥ 99%; o piso que os
dados sustentam fica perto de 93%. Provar ≥ 99% exige cerca de **381
identificadores** no conjunto cego. Está no PR #68.

### 2.5 Custo de auditoria por tamanho da trilha (#46)

[`evidencias/auditoria-custo-46.md`](evidencias/auditoria-custo-46.md), figura em
`.svg`, dados em `evidencias/dados/`.

### 2.6 Contenção de auditoria (#46)

[`evidencias/auditoria-contencao-46.md`](evidencias/auditoria-contencao-46.md).
Com 8 processos em rajada, as falhas por expiração de lock caíram de **35%
(26/40) para 0,6% (159/160)**, e a vazão subiu de ~0,5 para ~10,7 gravações por
segundo. Cadeia íntegra em todas as rodadas.

Limite que fica: a partida a frio de cada processo novo custa uma verificação
completa sob o lock exclusivo.

### 2.7 Restauração de backup em máquina separada (#25)

[`../specs/018-backup-restauracao/segunda-maquina.md`](../specs/018-backup-restauracao/segunda-maquina.md).
Aprovado em 03/11, em máquina fisicamente distinta, com manifesto conferido por
SHA-256 e impressão digital de tabela, incidentes reproduzidos e trilha de
auditoria íntegra. Desvio declarado: o `manage_identity` exigiu console real, e a
senha foi lida de arquivo protegido.

### 2.8 Burn rate com queda prolongada e com corte curto (E3)

[`evidencias/e3-burn-rate.md`](evidencias/e3-burn-rate.md), dado bruto em
`evidencias/dados/e3-burn-rate.json`, script `scripts/medir_e3.py`.

| Condição | Esperado | Medido | |
|---|---|---|:-:|
| Queda de 10 min | chega a `page` | `page` em **52,0 s** | ✅ |
| Corte de 10 s | não pagina | `page` em **45,0 s** | ❌ |

**O critério da #11 passa pela metade, e a metade que falha vale mais no texto.**
A lógica de alerta está correta: com o intervalo recortado nos 10 segundos reais
de queda, nenhuma regra dispara em nenhum instante de avaliação. O que falha é o
ciclo de vida do incidente — ver 2.9.

### 2.9 Defeito encontrado: incidentes não se fecham sozinhos

`resolvido_em` é escrito em um único lugar do código, dentro de
`change_incident`, que atende as rotas manuais `/reconhecer` e `/resolver`. A
gravação de uma medição com sucesso **não** encerra o incidente de
disponibilidade em aberto. O sistema sabe quando um alvo caiu e não sabe quando
ele voltou.

Dois efeitos, ambos relevantes para o texto:

1. Qualquer oscilação de poucos segundos vira `page` em menos de um minuto, como
   a condição B mediu.
2. O MTTR de 0,191 s da seção 2.3 só existe porque o script resolvia cada
   incidente por chamada de API. **Em operação, o MTTR do sistema é o tempo até a
   intervenção humana**, não o tempo até o serviço voltar.

A correção é pequena e localizada — fechar o incidente quando a sonda voltar a ter
sucesso — mas é mudança de comportamento, a dez dias do congelamento, com a #57
aberta sobre rotas que respondem sucesso sem efeito.

---

## 3. Verificado, sem número a citar

Estes têm prova de funcionamento na suíte automatizada (522 testes passando, 1
ignorado, na execução de aceite de 03/11), mas não produzem uma grandeza para o
texto.

| O que | Onde está a prova |
|---|---|
| RNF07: requisição sem chave recusada, chave revogada, rotação | testes de identidade e de API |
| RF07: acesso sem login negado, perfil sem permissão barrado, senhas só em hash | `frontend/e2e-operational/panel.spec.js` e testes de auth |
| RF05: falha segura do filtro, sem tabela de correspondência | testes do sanitizador |
| RNF06: nada perdido ao recriar contêineres | aceite de instalação e recuperação |
| RNF05: serviços sobem com um comando | `validate_infrastructure.py`, `validate_compose_credentials.py` |

Vale lembrar a **#57**: rotas de API que respondem sucesso sem efeito, entre elas
rotação de chaves e registro de incidente. Enquanto ela estiver aberta, "verificado"
nesta seção significa verificado pelo teste que existe, e a #57 diz que algum
desses testes pode estar provando menos do que parece. É a dependência mais
incômoda da lista, e está esperando o Iohan.

---

## 4. Lacunas que ainda dá tempo de fechar

### 4.1 E4 — fuzzing da cadeia de hash

A #11 pede N = 1000 mutações aleatórias com 100% de detecção. Hoje existem testes
unitários de adulteração, não o experimento com volume e semente fixa. O
verificador da cadeia já está pronto; falta o laço e o CSV.

### 4.2 Deriva lenta (#10)

Não é lacuna de medição: está medido e o resultado é ruim (16,7%). A decisão a
tomar é se entra no texto só como limitação ou se CUSUM é implementado antes do
congelamento. **Recomendo deixar como limitação**, com o número explícito. Dez dias
não são suficientes para implementar e validar um detector novo com honestidade.

---

## 5. Lacunas que vão para as limitações

| Lacuna | Por quê |
|---|---|
| **RNF04 / E5: IA em ≤ 15 s** | Nenhuma medição com provedor real e anonimização ativa. O ensaio usa provedor simulado. É um requisito não funcional declarado **sem evidência** — tem de ser dito assim |
| **Rede real (#12)** | Tudo foi medido em loopback. O E1 foi calibrado em séries sintéticas, e a #12 pede duas semanas de RTT real. Não acontece até 18/11 |
| **MTTD no painel** | Estruturalmente impossível hoje: nada grava o instante real da falha, e `/api/eng/incidentes/resumo` devolve `MTTD: n=0` sempre. Detalhado em `evidencias/incidentes-mttd-burn.md` |
| **Sincronização de relógio (#27)** | O MTTD medido depende de relógios na mesma máquina. Em rede real, NTP contra PTP muda o número, e isso não foi quantificado |

---

## 6. O que fazer com isto

1. **Decidir o que fazer com o defeito da seção 2.9.** Corrigir antes do
   congelamento e remedir, ou declarar no texto que o SLO é calculado sobre
   intervalos que só fecham por intervenção humana. As duas são defensáveis; o
   que não é defensável é citar burn rate sem dizer isto.
2. **Escrever a seção de limitações com os números negativos dentro**: 16,7% na
   deriva, recall sustentável de ~93% e não 99%, RNF04 sem evidência, tudo em
   loopback. Uma banca de computação pergunta justamente por esses, e tê-los
   escritos antes é melhor que ser pego sem eles.
3. **Não citar MTTA e MTTR como tempo de operador.** São do sistema.
4. **Resolver a #57** ou declarar explicitamente que algumas rotas podem responder
   sucesso sem efeito. Isso afeta a confiança em tudo da seção 3.
