---
tags: [artigo-cientifico, rascunho]
---
# SIGMA: monitoramento ativo de rede hospitalar de baixo custo, com detecção estatística, auditoria íntegra e anonimização para diagnóstico assistido por IA

**SIGMA: low-cost active monitoring of a hospital network with statistical detection, tamper-evident auditing and anonymization for AI-assisted diagnosis**

> **Rascunho de 13/11/2026, não definitivo.** Segue a estrutura do modelo `modelo-cientifico.pdf` (Aurum Revista Multidisciplinar), fornecido pelo professor. Serve para mostrar o estado do projeto: o que está sustentado por medição e o que falta. Todo número vem de evidência do repositório (a origem está na seção "Fontes dos dados", no fim). Os trechos marcados `[PENDENTE: ...]` não têm material ainda. A análise de situação está em [`mapa-modelo-cientifico.md`](mapa-modelo-cientifico.md). A formatação final (Times New Roman 12, margens, espaçamento 1,5) é feita na exportação.

**[PENDENTE: nome completo do autor 1]**
Informações do autor: [PENDENTE: maior titulação; Uninorte, Engenharia da Computação; e-mail, Lattes ou ORCID]

**[PENDENTE: nome completo do autor 2]**
Informações do autor: [PENDENTE: idem]

**[PENDENTE: autor 3, se houver (máximo de 3 pelo edital)]**

Orientador: [PENDENTE: nome, titulação e vínculo]

---

## RESUMO

Hospitais dependem da disponibilidade da rede de dados, mas as equipes de TI de fundações públicas, com orçamento restrito, costumam atuar de forma reativa. Este trabalho apresenta o SIGMA, um sistema de monitoramento ativo de custo zero de licença, concebido para um hospital oncológico, e avalia em bancada se ele reduz o tempo de detecção e dá rastreabilidade às respostas, preservando a LGPD. A pesquisa é aplicada, experimental e quantitativa, com estudo de caso. Foram medidos, com dados sintéticos e semente fixa, detectores estatísticos (EWMA e MAD), o alerta por taxa de consumo do orçamento de erros (burn rate), uma trilha de auditoria com cadeia de hash, a anonimização de logs antes do envio a modelos de linguagem e a latência do alerta até o painel. Os detectores identificaram 100% dos degraus e picos, mas só 17% a 20% das derivas lentas. A latência de alerta ficou abaixo de 5 s em 100% das quedas, com p95 entre 0,78 e 0,84 s. A cadeia de hash detectou 100% das adulterações, remoções e trocas de linhas, e 0% dos cortes no fim da trilha sem uma âncora externa. A anonimização obteve 95,12% de recall de transformação, abaixo da meta de 99%, e 100% de proteção contra vazamento, graças ao bloqueio com falha segura. Todas as medições ocorreram em loopback. O requisito de 15 s para a resposta da IA e a validade em rede hospitalar real permanecem sem evidência.

**Palavras-chave:** monitoramento de redes; detecção de anomalias; burn rate; trilha de auditoria; anonimização.

## ABSTRACT

*[PENDENTE: gerar a versão em inglês com ferramenta de IA, como o modelo manda, e revisar. Rascunho abaixo.]*

Hospitals depend on network availability, yet IT teams in budget-constrained public foundations tend to work reactively. This paper presents SIGMA, a zero-license-cost active monitoring system designed for an oncology hospital, and evaluates on a test bench whether it shortens detection time and makes response actions traceable while preserving compliance with the Brazilian data protection law (LGPD). The research is applied, experimental and quantitative, built around a case study. Using synthetic data and fixed random seeds, we measured statistical detectors (EWMA and MAD), an error-budget burn-rate alert, a hash-chained audit trail, log anonymization before sending data to language models, and alert latency up to the dashboard. The detectors caught 100% of step and spike failures but only 17% to 20% of slow drifts. Alert latency stayed under 5 s in 100% of outages (p95 between 0.78 and 0.84 s). The hash chain detected 100% of tampering, deletions and swaps, and 0% of truncations at the end of the trail without an external anchor. Anonymization reached 95.12% transformation recall, below the 99% target, and 100% leak protection thanks to fail-closed blocking. All measurements ran over loopback. The 15 s requirement for the AI response and validity on a real hospital network remain without evidence.

**Keywords:** network monitoring; anomaly detection; burn rate; audit trail; anonymization.

---

## 1 INTRODUÇÃO

### 1.1 APRESENTAÇÃO DO TEMA

A Tecnologia da Informação tem papel estrutural em ambientes de saúde de alta complexidade. Prontuários eletrônicos, comunicação entre setores, equipamentos médicos e ferramentas de gestão dependem da estabilidade e da disponibilidade contínua da rede de dados. Em um hospital oncológico, em que a continuidade do atendimento é vital, uma falha de rede deixa de ser apenas um problema técnico e passa a representar um risco assistencial e institucional.

Este trabalho trata do monitoramento dessa rede. O sistema estudado, o SIGMA, substitui um modelo de suporte puramente reativo por um monitoramento ativo: sondas medem a disponibilidade e a latência dos serviços, detectores estatísticos identificam degradações, um painel mostra o estado da rede em tempo quase real e um assistente de inteligência artificial (IA) sugere diagnósticos a partir de logs previamente anonimizados.

### 1.2 DELIMITAÇÃO DO PROBLEMA DE PESQUISA

Na instituição do estudo de caso, uma fundação pública de saúde, a equipe de TI trabalha sem visibilidade em tempo real da rede e descobre as falhas quando os usuários as relatam de modo informal. As consequências são a demora para detectar e consertar incidentes, a sobrecarga de tarefas manuais e a ausência de dados históricos para prevenir falhas. A situação se agrava pelo orçamento restrito, pela dificuldade de contratar pessoal especializado e pela falta de métodos organizados de governança de TI.

O problema de pesquisa é: em uma rede hospitalar com equipe de TI reduzida, é possível reduzir o tempo de detecção (MTTD) e dar rastreabilidade às ações de resposta usando apenas componentes de custo zero de licença, preservando a LGPD?

O trabalho se limita à avaliação em bancada, com dados sintéticos. O sistema não foi executado na rede do hospital, e nenhuma medição usou tráfego real. Essa delimitação governa a interpretação de todos os resultados (seção 3.8).

### 1.3 OBJETIVOS

#### 1.3.1 Objetivo geral

Avaliar, em bancada, se um sistema de monitoramento ativo de custo zero de licença reduz o tempo de detecção de falhas de rede e dá rastreabilidade às ações de resposta, preservando a LGPD.

#### 1.3.2 Objetivos específicos

- Medir a capacidade de detectores estatísticos online (EWMA e MAD) de identificar degraus, picos e derivas lentas de latência (hipótese H1);
- Medir a latência entre a falha e o alerta exibido no painel, contra a meta de 5 s (hipótese H4, parte do RF01);
- Avaliar o alerta por burn rate em duas janelas diante de uma queda prolongada e de um corte curto (hipótese H2);
- Verificar, por fuzzing, se a trilha de auditoria com cadeia de hash detecta adulterações, remoções e reordenações (hipótese H3);
- Medir a anonimização de logs antes do envio à IA, em um conjunto de teste escrito por outra pessoa, e registrar o custo da auditoria conforme o histórico cresce;
- Declarar os requisitos que ficaram sem evidência, em especial o tempo de resposta da IA (RNF04) e a validade em rede real.

### 1.4 JUSTIFICATIVA

**Motivação.** O tema surgiu de um problema observado: a equipe de TI de um hospital oncológico descobre falhas de rede só depois do impacto. O trabalho parte da realidade desse hospital e a leva a uma avaliação com métricas definidas e reprodutíveis.

**Relevância social.** Reduzir o tempo de detecção de falhas protege a continuidade de sistemas que sustentam o atendimento. A solução usa só componentes de código aberto e camadas gratuitas de IA, o que a torna viável para instituições públicas sem orçamento para licenças.

**Relevância científica.** Em vez de apenas demonstrar um sistema, o trabalho define o que significa "funcionar", mede e declara os resultados desfavoráveis. Entre eles estão um achado negativo documentado (detectores por limiar não cobrem a deriva lenta) e um defeito de projeto encontrado pela própria medição (incidentes de disponibilidade que nunca se fechavam sozinhos). A metodologia é reprodutível: semente fixa, repetições, saída em CSV e scripts versionados.

**Aplicabilidade prática.** O banco de dados e a automação sobem por Docker Compose, a API e a sonda rodam no host, e o sistema foi restaurado a partir de backup em uma segunda máquina física. Os resultados, porém, só valem para a bancada. A aplicação em rede real é trabalho futuro.

### 1.5 REVISÃO TEÓRICA

> **[PENDENTE: esta seção não tem texto de literatura levantado.]** O que segue organiza os temas que o projeto exige e cita as obras mais prováveis. Os dados bibliográficos foram escritos de memória e **precisam ser conferidos na fonte** antes de qualquer citação definitiva. Cada tema precisa de 3 a 5 fontes e de uma discussão de como o SIGMA se relaciona com elas.

#### 1.5.1 Observabilidade, SLI, SLO e burn rate

A engenharia de confiabilidade de sites (SRE) trata a disponibilidade como um objetivo mensurável. Define-se um indicador de nível de serviço (SLI), uma meta (SLO) e, como consequência, um orçamento de erros. O burn rate é a razão entre o erro observado e o erro permitido: o valor 1 corresponde ao consumo exato do orçamento no período do SLO. Alertas com duas janelas, uma curta e uma longa, buscam paginar quedas reais sem acordar a equipe por picos isolados (BEYER et al., 2016; BEYER et al., 2018). [PENDENTE: confirmar os valores de limiar adotados na literatura e relacioná-los ao limiar de 14,4 usado pelo módulo.]

#### 1.5.2 Detecção online de mudanças em séries de latência

A média móvel exponencialmente ponderada (EWMA) acompanha a série e sinaliza desvios do nível esperado (ROBERTS, 1959; LUCAS; SACCUCCI, 1990). A mediana e o desvio absoluto mediano (MAD) são estimadores robustos a caudas pesadas (HAMPEL, 1974), o que interessa a latências de rede. Detectores de mudança acumulada, como o CUSUM (PAGE, 1954) e o Page-Hinkley, acumulam pequenos desvios e são o caminho natural para derivas lentas, que escapam de limiares por amostra. [PENDENTE: trazer um trabalho que trate detecção de anomalias em latência de rede e comparar com o resultado de E1.]

#### 1.5.3 Trilha de auditoria com cadeia de hash

Em uma cadeia de hash, cada registro carrega o resumo criptográfico do anterior, de modo que alterar, apagar ou reordenar um registro invalida os seguintes. Registros assinados com HMAC dificultam a falsificação por quem não tem a chave (SCHNEIER; KELSEY, 1999). A literatura sobre registros à prova de adulteração discute estruturas de dados que permitem verificação eficiente (CROSBY; WALLACH, 2009). Uma cadeia lida só a partir de si mesma não pode saber que foi truncada no fim, o que exige um ponto de ancoragem guardado fora do sistema. [PENDENTE: conferir a formulação do problema do truncamento nas obras citadas.]

#### 1.5.4 Privacidade, LGPD e anonimização

A Lei nº 13.709/2018 (LGPD) regula o tratamento de dados pessoais e fundamenta a decisão de generalizar logs antes de enviá-los a um provedor de IA em nuvem (BRASIL, 2018). A norma ISO/IEC 27001 organiza a gestão da segurança da informação. O projeto adota generalização por regras: máscara de sub-rede para endereços IP, categoria para equipamentos e mascaramento de nomes e identificadores. A avaliação usa intervalos de confiança de Wilson para proporções (WILSON, 1927). [PENDENTE: levantar literatura de anonimização de logs e de reidentificação, e o enquadramento do art. 12 da LGPD, que o estudo de caso deixa para o DPO ou o jurídico.]

#### 1.5.5 Sondagem de rede e segurança da sonda

A sonda mede o tempo do estabelecimento de conexão TCP (EDDY, 2022). Resolver o nome duas vezes, uma para validar e outra para conectar, abre espaço para ataques de DNS rebinding e de corrida entre verificação e uso (JACKSON et al., 2009). O SIGMA conecta ao endereço IP já validado, sem segunda resolução. Os eventos chegam ao painel por Server-Sent Events (WHATWG, [PENDENTE: ano e URL]).

#### 1.5.6 Trabalhos relacionados

[PENDENTE: comparar o SIGMA com ferramentas de monitoramento de código aberto, como Zabbix, Nagios e Prometheus, e com trabalhos acadêmicos de monitoramento hospitalar. É o ponto que responde "o que o SIGMA acrescenta". Nenhuma comparação foi levantada.]

---

## 2 METODOLOGIA

### 2.1 TIPO DE PESQUISA

A pesquisa é **aplicada**, **experimental** e de abordagem **quantitativa**, com o apoio de um **estudo de caso**. É aplicada porque propõe e avalia uma solução tecnológica para um problema real. É experimental porque testa hipóteses em condições controladas: falhas injetadas, semente fixa, repetições e saída em CSV. A descrição do objeto é feita no estudo de caso.

### 2.2 ESTUDO DE CASO COM APLICABILIDADE

O local de aplicação é um hospital oncológico, de uma fundação pública, cuja equipe de TI opera sem monitoramento em tempo real (seção 1.2). O SIGMA foi desenhado para essa realidade: custo zero de licença, três camadas (painel, API e banco), implantação híbrida (banco PostgreSQL e automação em contêineres Docker Compose; API, painel e sonda no sistema operacional do host) e IA em nuvem alimentada só com dados generalizados.

**Arquitetura em resumo.** A sonda mede a conexão TCP e HTTP de cada serviço e envia as medições à API, autenticada por chave exclusiva (RNF07). A API guarda medições e incidentes em PostgreSQL, aplica os detectores e o alerta por burn rate e empurra os eventos ao painel por SSE. O painel exige login com perfis de acesso (RF07). Antes de qualquer envio à IA, a API aplica a anonimização (RF05), com falha segura: se o filtro falhar, nada sai. Um módulo de auditoria registra as ações em uma trilha com cadeia de hash e HMAC. **A versão avaliada é a `v1.0.0`**, que só tem sondagem TCP e HTTP; não há ICMP, SNMP nem integração com o firewall nesta versão.

[PENDENTE: incluir o diagrama de arquitetura (Figura 2.1).]

**Proteção da instituição.** Todas as evidências usam dados fictícios. Os endereços de exemplo ficam nos blocos reservados para documentação (RFC 5737 e RFC 3849), e nenhum endereço, VLAN ou setor reais do hospital aparece (RNF09). [PENDENTE: confirmar com o hospital e o orientador se a instituição pode ser nomeada no artigo.]

### 2.3 TÉCNICAS E INSTRUMENTOS DE COLETA DE DADOS

Os dados são medidas feitas pelos próprios scripts do projeto, todos versionados, com semente fixa quando há aleatoriedade e saída em CSV ou JSON no repositório.

| Experimento | Objeto | Instrumento | Repetições |
|---|---|---|---|
| E1 | Detectores EWMA e MAD | `experimentos/exp_deteccao.py` | 30 sementes, 600 amostras por série |
| E2 | Latência da falha ao alerta no painel (SSE) | `scripts/validate_collection.py` | 3 rodadas de 200 alvos; 30 quedas por rodada |
| E2' | MTTD, MTTA e MTTR | `scripts/medir_incidentes.py` | 30 repetições |
| E3 | Burn rate (queda prolongada e corte curto) | `scripts/medir_e3.py` | 2 execuções por condição |
| E4 | Fuzzing da cadeia de hash | `experimentos/exp_fuzzing_cadeia.py` | 1.000 entradas, 250 casos por tipo, semente 20261104 |
| E6 | Anonimização em conjunto cego | `scripts/executar_experimento_e6.py` | 46 amostras, 41 identificadores |
| #46 | Custo e contenção da auditoria | benchmarks em `docs/tcc/evidencias/` | 5 repetições (custo); 8 processos (contenção) |
| #25 | Backup e restauração | roteiro de restauração | 1 restauração em segunda máquina |

O E5, tempo de resposta da IA com anonimização ativa (RNF04, meta de 15 s), **não foi medido**.

### 2.4 PROCEDIMENTOS DE ANÁLISE DOS DADOS

Tempos são relatados por mediana, média e p95. Proporções usam o intervalo de confiança de Wilson a 95%. As métricas são definidas antes da medição: o MTTD é `detectado_em − inicio_real`; o MTTA e o MTTR são `reconhecido − detectado` e `resolvido − detectado`; o atraso de detecção é o número de amostras entre o início da falha e o primeiro alarme; precisão, revocação e F1 são por amostra; o burn rate é o erro observado dividido pelo erro permitido. O SLO usado é de 99,9% em 30 dias, o padrão do módulo, e não um objetivo acordado com o hospital. Os resultados são confrontados com os critérios de cada requisito (RF01 em até 5 s, RF05 com recall de transformação de pelo menos 99% e outros).

[PENDENTE: incluir o fluxograma do método (Figura 2.2).]

### 2.5 AMBIENTE DE EXECUÇÃO E AMEAÇAS À VALIDADE

As medições foram feitas em loopback, em uma única máquina física (Windows 10, 16 GB, 12 processadores lógicos, SSD, Python 3.12) ou, em parte, em máquina virtual. O PostgreSQL rodou em contêiner. Alvos e falhas são sintéticos. As ameaças à validade principais são:

| Tipo | Ameaça | Tratamento |
|---|---|---|
| Construto | Séries lognormais sintéticas podem não refletir o tráfego hospitalar | Declarado; coleta de RTT real é trabalho futuro (#12) |
| Interna | Parâmetros dos detectores escolhidos sem ajuste | Declarado como limitação |
| Externa | Resultado de um só hospital | Tratado como estudo de caso |
| Conclusão | Falhas injetadas são mais "limpas" que as reais | Declarado |
| Medição | Relógios não sincronizados distorcem o MTTD | Medições na mesma máquina; efeito de NTP e PTP não quantificado (#27) |
| Independência | O autor do conjunto cego do E6 conhecia os marcadores de saída da implementação | Declarado na seção 3.6 |

---

## 3 RESULTADOS E DISCUSSÃO

### 3.1 DETECÇÃO DE DEGRADAÇÕES DE LATÊNCIA (E1, H1)

**Tabela 3.1.** Qualidade dos detectores em 30 séries sintéticas de 600 amostras (mediana de cerca de 20 ms; falha a partir da amostra 300).

| Cenário | Detector | Detecção | Atraso (amostras) | Falsos positivos por série | F1 |
|---|---|---:|---:|---:|---:|
| Degrau (+40 ms, 60 amostras) | EWMA (α = 0,1; k = 4) | 100% | 0 | 1,37 | 0,908 |
| Degrau | MAD (janela 60; k = 5) | 100% | 0 | 0,23 | 0,998 |
| Pico (+80 ms, 3 amostras) | EWMA | 100% | 0 | 1,90 | 0,783 |
| Pico | MAD | 100% | 0 | 0,20 | 0,971 |
| Deriva (+0,5 ms por amostra, 120 amostras) | EWMA | 20% | 12,5 | 52,07 | 0,002 |
| Deriva | MAD | 17% | 17,6 | 0,30 | 0,005 |

Fonte: `engenharia/resultados/e1_deteccao.md`.

O MAD tem menos falsos positivos que o EWMA, porque a mediana e o MAD resistem à cauda pesada da distribuição lognormal. **Os dois detectores falham na deriva lenta:** cada passo cabe dentro de k·σ e o modelo acompanha a rampa. A hipótese H1 é **confirmada para degrau e pico e refutada para deriva lenta**. Houve também um achado de projeto: com o EWMA congelando o modelo durante anomalias, uma mudança permanente de patamar travava o detector em alarme (180 falsos positivos por série). O parâmetro de reaprendizado reduziu isso para 52, ao custo de F1 menor no degrau (de 0,987 para 0,908), uma troca que precisa ser calibrada com dados reais. [PENDENTE: discutir com a literatura de CUSUM e Page-Hinkley (seção 1.5.2).]

### 3.2 LATÊNCIA DO ALERTA ATÉ O PAINEL, MTTD, MTTA E MTTR (RF01)

**Tabela 3.2.** Três rodadas, em 03/11/2026, em máquina física, com 200 alvos.

| Rodada | p95 | Máximo | Dentro de 5 s | Atraso máximo do calendário |
|---:|---:|---:|---:|---:|
| 1 | 0,835 s | 0,868 s | 100% | 0,039 s |
| 2 | 0,781 s | 0,803 s | 100% | 0,040 s |
| 3 | 0,794 s | 0,832 s | 100% | 0,044 s |

Fonte: `docs/tcc/balanco-dos-dados.md`, seção 2.2.

A meta do RF01 (5 s) foi atendida com folga em todas as rodadas, e o pior atraso do calendário (0,044 s) ficou cerca de onze vezes abaixo da meta de 0,5 s.

**Tabela 3.3.** Tempos de resposta a incidentes, 30 repetições.

| Métrica | Média | p95 |
|---|---:|---:|
| MTTD (queda até o SSE) | 0,712 s | 0,794 s |
| MTTA | 0,159 s | 0,246 s |
| MTTR | 0,191 s | 0,266 s |

Fonte: `docs/tcc/evidencias/incidentes-mttd-burn.md`.

**Duas ressalvas acompanham esses números.** O MTTD é um limite superior, porque inclui a entrega pelo SSE. O MTTA e o MTTR **não são tempos de operador**: são reconhecimento e resolução imediatos por chamada de API, e medem o caminho do sistema, não o tempo de um técnico. O burn rate de 1 h ficou em 7,519, abaixo do limiar de 14,4, e portanto sem alerta, o que é correto para trinta quedas de menos de um segundo. Além disso, as rodadas da Tabela 3.2 são anteriores a uma alteração do caminho de ingestão (PR #79); repeti-las na versão entregue era tarefa registrada e **não foi executada** até 10/11/2026.

### 3.3 ALERTA POR BURN RATE EM DUAS JANELAS (E3, H2)

O experimento usou SLO de 99,9% em 30 dias, em loopback e em máquina física. A condição A foi uma queda de 10 minutos; a condição B, um corte de 10 segundos.

**Tabela 3.4.** Tempo até o alerta de página (`page`).

| Condição | Esperado | 03/11 (antes da correção) | 04/11 (depois da correção) |
|---|---|---|---|
| A: queda de 10 min | chega a `page` | `page` em 52,0 s | `page` em 52,0 s |
| B: corte de 10 s | não pagina | `page` em 45,0 s | nenhum alerta |

Fonte: `docs/tcc/evidencias/e3-burn-rate.md` e `e3-pos-71.md`.

A previsão analítica para a condição A é de 51,8 s, e a medida foi de 52,0 s, com a janela longa de 1 h determinando o disparo. **A condição B revelou um defeito de projeto.** Em 03/11 o sistema paginou aos 45 s, contra o critério. A causa não estava no cálculo de burn rate: o incidente de disponibilidade nunca era fechado automaticamente, porque o fim do incidente só era escrito por rotas manuais. Depois que a gravação de uma medição com sucesso passou a encerrar o incidente aberto (#71, PR #79), o corte de 10 s não gerou alerta em duas execuções: o incidente fechou com 10,334 s de duração, e o burn de 1 h ficou em 2,871, abaixo do limiar de 14,4. A hipótese H2 é **confirmada em laboratório**. Ela se apoia em duas execuções por condição, em loopback, o que não permite intervalo de confiança. [PENDENTE: repetir em rede real e com durações intermediárias de corte; discutir os limiares com a literatura de SRE (seção 1.5.1).]

### 3.4 INTEGRIDADE DA TRILHA DE AUDITORIA (E4, H3)

**Tabela 3.5.** Fuzzing da cadeia de hash: trilha de 1.000 entradas, uma mutação por caso, semente 20261104.

| Mutação | Casos | `verificar()` detecta | Âncora externa detecta |
|---|---:|---:|---:|
| Um byte de uma linha trocado | 250 | 100% | 0% |
| Uma linha apagada | 250 | 100% | 100% |
| Duas linhas trocadas de lugar | 250 | 100% | 0% |
| 1 a 5 linhas apagadas do fim | 250 | **0%** | 100% |

Fonte: `engenharia/resultados/e4_fuzzing_cadeia.md`.

Nos 750 casos das três mutações do critério, o índice reportado foi exatamente o índice alterado. O quarto tipo foi acrescentado além do critério e **falha por construção**: uma trilha cortada no fim continua coerente consigo mesma. A âncora guardada fora da máquina detecta o truncamento em 100% dos casos, mas não vê mutação no meio. As duas conferências são complementares. A hipótese H3 é, portanto, **confirmada para adulteração, remoção e reordenação, e refutada para truncamento** sem a âncora.

### 3.5 CUSTO E CONTENÇÃO DA AUDITORIA

**Tabela 3.6.** Custo de uma gravação feita no login, por tamanho da trilha (mediana de 5 repetições, em milissegundos).

| Entradas | Tamanho do arquivo | Antes da correção | Depois da correção |
|---:|---:|---:|---:|
| 1.000 | 0,3 MB | 49,3 | 12,6 |
| 10.000 | 3,0 MB | 428,7 | 12,2 |
| 100.000 | 30,3 MB | 4.291,2 | 12,9 |

Fonte: `docs/tcc/evidencias/auditoria-custo-46.md`.

Antes da correção, cada gravação relia o arquivo inteiro e refazia o HMAC de todas as entradas: o custo crescia com o histórico (87 vezes mais tempo para 100 vezes mais entradas). Depois, caiu para 12 a 13 ms nos três tamanhos, cerca de 330 vezes mais rápido com 100 mil entradas e abaixo da meta proposta de 50 ms. O piso de 12 ms vem da gravação em disco com `fsync`. Gravações em rajada com 100 mil entradas passaram de 4.186 ms para 125,8 ms. Com 8 processos em rajada, as falhas por expiração de trava caíram de 35% (26 de 40) para 0,6%, e a vazão subiu de cerca de 0,5 para cerca de 10,7 gravações por segundo, com a cadeia íntegra em todas as rodadas.

**Limite que permanece:** a primeira gravação de um processo novo ainda verifica a trilha inteira, e custou 3.955 ms com 100 mil entradas. Um ponto de verificação assinado para essa partida a frio está em desenvolvimento (PR #94) e **não foi medido**. A issue #46 segue aberta, porque o limite de tempo do login ainda não foi acordado com o orientador.

### 3.6 ANONIMIZAÇÃO ANTES DO ENVIO À IA (RF05)

O conjunto cego foi escrito por outra pessoa da equipe, com o objetivo de testar as regras sem tê-las escrito. Tem 46 mensagens (26 com identificadores e 20 sem) e 41 identificadores anotados, de 15 classes.

**Tabela 3.7.** Resultado no conjunto cego.

| Métrica | Valor | IC 95% (Wilson) |
|---|---:|---|
| Recall de transformação | 95,12% (39 de 41) | 83,86% a 98,65% |
| Recall de proteção (transformação mais bloqueio com falha segura) | 100,00% (41 de 41) | 91,43% a 100,00% |
| Precisão operacional | 97,50% | 87,12% a 99,56% |
| Falsos positivos em mensagens sem identificador | 5,00% (1 de 20) | 0,89% a 23,61% |

Fonte: `engenharia/resultados/experimento-e6-conjunto-cego.md`.

**O critério original (recall de transformação de pelo menos 99%) está REPROVADO.** Dois identificadores de nome não foram transformados; foram **bloqueados** pelo detector residual, de modo que nada foi enviado à IA: zero vazamentos em 41 identificadores. O sistema falha fechado. A proteção contra vazamento externo (transformação mais bloqueio, sem vazamento, falsos positivos de até 5% e bloqueio de até 20%) foi atendida, com 4,88% de bloqueio.

**Limites que o texto deve manter.** Primeiro, o limite é estatístico: com 41 identificadores, mesmo sem nenhuma falha, o limite inferior de Wilson é de 91,43%. Demonstrar 99% com 95% de confiança exigiria cerca de 381 identificadores sem falha. Qualquer afirmação de "99% de recall" seria precisão inventada. Segundo, a independência do conjunto é parcial: o autor conhecia os marcadores de saída da implementação, e 14 dos 26 casos positivos repetem a estrutura de 14 casos de uma conferência anterior com valores novos, o que mede cobertura e não generalização. Terceiro, o corpus é **sintético**: o resultado não demonstra anonimização universal, conformidade jurídica com a LGPD nem ausência de vazamento em dados hospitalares reais. Um corpus anterior, de desenvolvimento, com 59 amostras e 53 identificadores, teve recall de 100%, mas por ter orientado a escrita das regras não vale como evidência de generalização. [PENDENTE: o critério de aceite da #5 foi reformulado? Aguarda o orientador. Discutir com a literatura de anonimização de logs (seção 1.5.4).]

### 3.7 BACKUP E RESTAURAÇÃO EM MÁQUINA SEPARADA (RNF06)

Em 03/11/2026, o pacote de backup gerado na máquina de origem foi restaurado em uma máquina fisicamente distinta, com manifesto conferido por SHA-256 e impressão digital de tabela, incidentes reproduzidos e trilha de auditoria íntegra. O plano original previa uma máquina virtual, e a mudança para máquina física foi decidida em 01/11. Como desvio, a operação de identidade exigiu console real e a senha foi lida de arquivo protegido. Fonte: `docs/specs/018-backup-restauracao/segunda-maquina.md`.

### 3.8 DISCUSSÃO

**O que os resultados sustentam.** Em bancada, o sistema detecta degraus e picos de latência sem atraso, entrega o alerta ao painel em menos de 1 s (p95), pagina uma queda real em cerca de 52 s sem acordar a equipe por um corte de 10 s, detecta adulterações da trilha de auditoria e falha de modo seguro na anonimização. A suíte automatizada tem mais de 500 testes (526 na `develop` em 10/11/2026), que cobrem também propriedades sem número a citar, como a recusa de requisição sem chave (RNF07) e o controle de acesso por perfil (RF07).

**O que eles não sustentam.**
- **Rede real.** Tudo foi medido em `127.0.0.1`, numa única máquina, contra alvos sintéticos. O sistema nunca rodou na rede do hospital. É a limitação que governa as demais, e a coleta de RTT real por duas semanas (#12) não cabe no prazo.
- **Resposta da IA em até 15 s (RNF04).** Nenhuma medição foi feita com provedor real e filtro de anonimização ativo. O ensaio usa provedor simulado. O requisito foi declarado **sem evidência** (E5 não realizado).
- **MTTD no painel.** O painel não consegue exibir o MTTD, por construção: nada grava o instante real da falha, e o resumo de incidentes devolveu `n=0` na avaliação de 04/11. O MTTD da Tabela 3.3 vem de um experimento, não do painel.
- **Deriva lenta.** Os detectores implementados detectam só 17% a 20% das derivas; CUSUM e Page-Hinkley seguem como trabalho futuro (#10).
- **Sincronização de relógio.** O efeito de NTP contra PTP sobre o MTTD medido não foi quantificado (#27).
- **Rotas sem efeito.** Uma auditoria identificou rotas da API que respondiam sucesso sem efeito. O defeito foi corrigido (#57, em 09/11), e as rotas planejadas respondem `501`.
- **Poucas repetições.** O E3 tem duas execuções por condição, e o custo da auditoria cinco repetições, sem intervalo de confiança.

**Relação com a literatura.** [PENDENTE: esta discussão exige a seção 1.5. Pontos a comparar: (a) o resultado de E1 com a literatura de detecção de mudança; (b) os limiares de burn rate com as práticas de SRE; (c) a limitação do truncamento com as obras de logs à prova de adulteração; (d) a anonimização por regras com a literatura de reidentificação; (e) o SIGMA com as ferramentas de monitoramento de código aberto.]

---

## 4 CONCLUSÃO

Este trabalho avaliou, em bancada, um sistema de monitoramento ativo de custo zero de licença para uma rede hospitalar. Em resposta ao objetivo geral, os resultados indicam que **o sistema reduz o tempo de detecção e dá rastreabilidade às ações, com limites claros**: os resultados valem para dados sintéticos em loopback, e não para a rede do hospital.

**Tabela 4.1.** Hipóteses e estado da evidência.

| Hipótese | Enunciado resumido | Resultado |
|---|---|---|
| H1 | EWMA e MAD detectam degrau e pico com atraso de até 1 amostra | **Confirmada** para degrau e pico (100%, atraso 0); **refutada** para deriva lenta (17% a 20%) |
| H2 | O burn rate em duas janelas pagina em quedas totais e não em picos curtos | **Confirmada em laboratório** (52,0 s na queda; nenhum alerta no corte de 10 s), com duas execuções; rede real pendente |
| H3 | A cadeia de hash detecta 100% das adulterações, remoções e reordenações | **Confirmada** nos três tipos (750 casos); **refutada** para truncamento do fim, que exige a âncora externa |
| H4 | O pipeline atende RF01 (até 5 s) e RNF04 (até 15 s) | RF01 **atendido** em ensaio local (p95 de 0,78 a 0,84 s); RNF04 **sem evidência** |

**Principais resultados.** Detectores por limiar cobrem degraus e picos, mas não derivas lentas. O alerta chega ao painel em menos de 1 s (p95). O burn rate separa uma queda de 10 minutos de um corte de 10 s, e a medição encontrou e levou à correção de um defeito de ciclo de vida de incidentes. A cadeia de hash detecta adulterações, e a âncora externa cobre o truncamento. A anonimização falha de modo seguro, com 100% de proteção, mas o recall de transformação (95,12%) ficou abaixo da meta de 99%. O custo da auditoria deixou de depender do tamanho do histórico.

**Contribuições.** (i) Um núcleo de monitoramento medido e testado, com metodologia reprodutível; (ii) um achado negativo documentado, a deriva lenta; (iii) dois defeitos de projeto encontrados pela própria medição (o fechamento de incidentes e o custo da auditoria); (iv) uma lista explícita do que ficou sem evidência.

### 4.1 SUGESTÕES PARA PESQUISAS FUTURAS

Devido à abrangência do tema, sugere-se:

- Coletar RTT real por pelo menos duas semanas e recalibrar os detectores, para dar validade externa ao E1 (#12);
- Implementar CUSUM e Page-Hinkley para cobrir a deriva lenta (#10);
- Medir o tempo de resposta da IA com provedor real e anonimização ativa, por horário do dia (E5, RNF04);
- Avaliar o impacto da sincronização de relógio (NTP e PTP) sobre o MTTD medido (#27);
- Ampliar o conjunto cego de anonimização até cerca de 381 identificadores, para sustentar estatisticamente a meta de 99%;
- Incluir sinais além do TCP, como SNMP e NetFlow (#29), e uma sonda embarcada por VLAN (#26);
- Modelar o pipeline alerta, fila e IA como sistema de filas e comparar com a latência medida (#28).

---

## DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL

[PENDENTE: confirmar com o orientador se o artigo leva esta declaração (o edital, na seção 3.3, exige declarar o uso de IA generativa quando autorizado). Texto proposto:] O código, os testes e a documentação do projeto, e parte da redação deste texto, foram produzidos com assistência de uma ferramenta de IA generativa (Claude Code, da Anthropic). Os autores revisaram o conteúdo e respondem pela autoria, pelos dados, pelas referências e pela rastreabilidade do trabalho.

---

## REFERÊNCIAS

> **[PENDENTE: conferir cada referência na fonte antes de citar.]** Os dados abaixo foram escritos de memória: autores, ano, volume, páginas e edição podem conter erros. Em ordem alfabética, como pede o modelo; a formatação ABNT final (negrito do título, espaçamento) é feita na exportação.

BEYER, B. et al. **Site reliability engineering**: how Google runs production systems. Sebastopol: O'Reilly Media, 2016.

BEYER, B. et al. **The site reliability workbook**: practical ways to implement SRE. Sebastopol: O'Reilly Media, 2018.

BRASIL. **Lei nº 13.709, de 14 de agosto de 2018**. Lei Geral de Proteção de Dados Pessoais (LGPD). Brasília, DF: Presidência da República, 2018.

CROSBY, S. A.; WALLACH, D. S. Efficient data structures for tamper-evident logging. In: USENIX SECURITY SYMPOSIUM, 18., 2009. **Proceedings** [...]. [PENDENTE: local e páginas].

EDDY, W. **Transmission control protocol (TCP)**. RFC 9293. Internet Engineering Task Force, 2022.

HAMPEL, F. R. The influence curve and its role in robust estimation. **Journal of the American Statistical Association**, v. 69, n. 346, pp. 383-393, 1974.

INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. **ISO/IEC 27001**: information security management systems. [PENDENTE: edição e ano].

JACKSON, C. et al. Protecting browsers from DNS rebinding attacks. **ACM Transactions on the Web**, v. 3, n. 1, 2009. [PENDENTE: páginas].

LUCAS, J. M.; SACCUCCI, M. S. Exponentially weighted moving average control schemes: properties and enhancements. **Technometrics**, v. 32, n. 1, pp. 1-12, 1990.

PAGE, E. S. Continuous inspection schemes. **Biometrika**, v. 41, n. 1-2, pp. 100-115, 1954.

ROBERTS, S. W. Control chart tests based on geometric moving averages. **Technometrics**, v. 1, n. 3, pp. 239-250, 1959.

SCHNEIER, B.; KELSEY, J. Secure audit logs to support computer forensics. **ACM Transactions on Information and System Security**, v. 2, n. 2, pp. 159-176, 1999.

WILSON, E. B. Probable inference, the law of succession, and statistical inference. **Journal of the American Statistical Association**, v. 22, n. 158, pp. 209-212, 1927.

[PENDENTE: WHATWG, HTML Living Standard, seção Server-sent events (ano, URL e data de acesso); documentação das ferramentas de monitoramento citadas na seção 1.5.6; RFC 5737 e RFC 3849.]

---

## FONTES DOS DADOS (remover na versão final)

| Seção | Arquivo no repositório |
|---|---|
| 1.1 a 1.4, 2.2 | `docs/arquitetura/estudo-de-caso.md`, `docs/visao-do-produto.md`, `engenharia/docs/00-visao-de-engenharia.md` |
| 2.3 a 2.5 | `engenharia/docs/03-metodologia-experimental.md` |
| 3.1 | `engenharia/resultados/e1_deteccao.md` |
| 3.2 | `docs/tcc/balanco-dos-dados.md`, `docs/tcc/evidencias/incidentes-mttd-burn.md` |
| 3.3 | `docs/tcc/evidencias/e3-burn-rate.md`, `e3-pos-71.md` |
| 3.4 | `engenharia/resultados/e4_fuzzing_cadeia.md` |
| 3.5 | `docs/tcc/evidencias/auditoria-custo-46.md`, `auditoria-contencao-46.md` |
| 3.6 | `engenharia/resultados/experimento-e6-conjunto-cego.md` (na `develop`) |
| 3.7 | `docs/specs/018-backup-restauracao/segunda-maquina.md` |
| 3.8, 4 | `docs/tcc/limitacoes.md`, `docs/tcc/relatorio-sprints-1-e-2.md` (PR #97) |

Estado das fontes em 13/11/2026: o relatório das Sprints 1 e 2 e o resultado do conjunto cego do E6 estão na `develop` ou no PR #97, ainda não nesta branch.
