# Plano de pesquisa: o que correr atrás para o artigo e a banca

Criado em 05/11/2026. Segue a lista de prioridades definida a partir do [mapa do modelo científico](mapa-modelo-cientifico.md). O artigo no modelo da Aurum Revista é, por ora, um rascunho de referência do estado do projeto. O plano abaixo define o que levantar e decidir, sem reescrever o código.

[Voltar ao índice do TCC](README.md) · [Edital](edital-tcc-ii-2026-2.md)

**Responsáveis e prazos são propostas.** Nada aqui foi combinado com o orientador nem entre os autores. Combinar a divisão na revisão de 07/11.

## Calendário de referência

| Data | Marco | Fonte |
|---|---|---|
| 07/11 | Revisão para dividir o trabalho entre os autores | [tarefas do Iohan](../planejamento/tarefas-iohan-sprint-1.md) |
| 10/11 | Fim da Sprint 2 | [plano pós-demo](../planejamento/plano-pos-demo-issues-abertas.md) |
| 11/11 | Congelamento de código (só correção P0) | idem |
| 11 a 17/11 | Sprint 3: texto, slides e ensaio | idem |
| 18/11 | Início da preparação da apresentação | informado pelo Vinícius |
| 23/11 | Entrega da versão para avaliação da banca (cronograma do edital; a seção 4.1 do edital diz 03/11 e 15/11, a confirmar) | [edital](edital-tcc-ii-2026-2.md) |
| 01 a 10/12 | Bancas | edital |
| até 16/12 | Versão final com as correções | edital |

## Prioridade 1: revisão da literatura e referências

**Por que primeiro.** É a única seção sem nenhum material, e a discussão dos resultados depende dela.

| Passo | Entregável | Prazo proposto | Responsável proposto |
|---|---|---|---|
| 1.1 Dividir os temas entre os autores | Lista de temas com dono | 07/11 | Vinícius e Iohan |
| 1.2 Levantar 3 a 5 fontes por tema, priorizando livros, periódicos, normas e RFCs | Planilha ou nota com autor, ano, título, tipo e link | 11/11 | cada dono de tema |
| 1.3 Fichar cada fonte: o que afirma e onde o projeto se relaciona | Fichamento de 3 a 5 linhas por fonte | 17/11 | cada dono de tema |
| 1.4 Redigir a seção 1.5 e a discussão da seção 3 | Texto da revisão e da discussão | 22/11 | Vinícius, com revisão do Iohan |
| 1.5 Montar as referências em ABNT, em ordem alfabética | Lista final | 22/11 | quem redigir |

**Temas de busca e candidatas iniciais.** Estas obras são as que o projeto mais provavelmente precisa citar, listadas de memória. **Conferir autores, ano, edição e páginas na fonte antes de citar**, porque nenhuma foi verificada aqui.

| Tema | Candidatas |
|---|---|
| SRE, SLI/SLO e burn rate | Beyer et al., *Site Reliability Engineering* (O'Reilly, 2016); Beyer et al., *The Site Reliability Workbook* (O'Reilly, 2018) |
| Detecção de mudança e anomalias (EWMA, MAD, CUSUM, Page-Hinkley) | Page (1954), *Continuous inspection schemes*, Biometrika; Roberts (1959), *Control chart tests based on geometric moving averages*, Technometrics; Lucas e Saccucci (1990), *Exponentially weighted moving average control schemes*, Technometrics; Hampel (1974), *The influence curve and its role in robust estimation*, JASA |
| Auditoria com cadeia de hash | Schneier e Kelsey (1999), *Secure audit logs to support computer forensics*, ACM TISSEC; Crosby e Wallach (2009), *Efficient data structures for tamper-evident logging*, USENIX Security |
| Privacidade e conformidade | Lei nº 13.709/2018 (LGPD); ISO/IEC 27001 |
| Sondagem de rede e segurança da sonda | RFC 9293 (TCP); RFC 8446 (TLS 1.3); Jackson et al., *Protecting browsers from DNS rebinding attacks* (a issue #14 mitiga esse tipo de ataque) |
| Transporte de eventos | Especificação de Server-Sent Events do WHATWG |
| Trabalhos relacionados (ferramentas de monitoramento) | Documentação do Zabbix, Nagios e Prometheus, e artigos que as comparem |
| Definições de MTTD, MTTA e MTTR | Buscar uma fonte primária; as definições deste projeto estão em [metodologia](../../engenharia/docs/03-metodologia-experimental.md) |

**Pronto quando:** cada afirmação do mapa marcada como "depende da literatura" tem pelo menos uma fonte, e a lista de referências está em ABNT.

## Prioridade 2: conversa com o orientador

Enviar uma pauta única até 07/11 (Vinícius). Perguntas:

1. Qual é o limite de páginas, quando as orientações da disciplina definirem o formato final? (Os rascunhos do artigo e da monografia são base de conhecimento e parâmetro para o orientador, e não uma escolha em aberto.)
2. Como é a submissão à revista, e qual é o prazo? O edital (seção 1.5) torna a publicação obrigatória para a nota.
3. Quem consta como autor (máximo 3) e quem é orientador e coorientador?
4. **Datas definitivas:** as orientações da aula de TCC de 12/11 trazem as datas definitivas, que o Vinícius vai enviar para registro. Até lá, vale o calendário do edital, que tem duas datas de entrega do PDF (03/11 e 23/11).
5. Dia e horário da banca, nas mesmas orientações.
6. As pendências antigas: critério de recall da #5, limite de login da #46 e licença do repositório.

**Pronto quando:** as respostas das perguntas 1 a 4 estão registradas neste arquivo.

## Prioridade 3: decidir o destino das lacunas de medição

Decisão até 10/11, executada ou registrada até o congelamento de 11/11. A recomendação vem do [balanço dos dados](balanco-dos-dados.md) e dos fatos do repositório.

| Lacuna | Situação | Recomendação | Se virar limitação |
|---|---|---|---|
| E5 / RNF04: IA em até 15 s | Sem medição com provedor real e anonimização ativa | Medir só se houver provedor real disponível e um dia de trabalho. Senão, declarar | Texto: "requisito declarado sem evidência" |
| Deriva lenta (#10) | Medida: 16,7% de detecção | Deixar como limitação (o balanço recomenda: 10 dias não bastam para um detector novo validado) | Número explícito no texto |
| Rede real (#12) | Tudo em loopback; a issue pede 2 semanas de RTT real | Não cabe antes da banca | Limitação principal, é a que governa as outras |
| E2 no painel | Só ensaio local | Registrar o ensaio local com o ambiente declarado | Texto: ambiente e escopo |
| #57: rotas que respondem sucesso sem efeito | Aberta, depende do Iohan | Corrigir ou declarar que alguns testes provam menos do que parecem | Texto na seção de verificado |

**Pronto quando:** cada linha tem decisão e dono, e o [mapa](mapa-modelo-cientifico.md) e as [limitações](limitacoes.md) refletem o resultado.

## Prioridade 4: figuras e tabelas

| Figura ou tabela | Origem dos dados | Prazo proposto | Responsável proposto |
|---|---|---|---|
| Diagrama de arquitetura | [Estudo de caso](../arquitetura/estudo-de-caso.md) e [stack](../arquitetura/stack-de-tecnologia.md) | 14/11 | a definir |
| Fluxograma da metodologia | Metodologia experimental | 14/11 | a definir |
| Gráfico de detecção por detector (E1) | `engenharia/resultados` | 17/11 | quem tiver o dado |
| Gráfico de burn rate (E3) | [E3](evidencias/e3-burn-rate.md) | 17/11 | idem |
| Figura do custo da auditoria (#46) | [Pronta](evidencias/auditoria-custo-46.svg) | feito | |
| Tabela das hipóteses e o resultado de cada uma | [Mapa](mapa-modelo-cientifico.md) | 17/11 | Vinícius |

Seguir o formato do modelo: título embaixo em Times 12, fonte em Times 10, numeração por capítulo.

## Prioridade 5: ética e dados do hospital

| Item | Ação | Prazo proposto |
|---|---|---|
| Autorização (CEP ou institucional) | Perguntar à Coordenação ou ao orientador se é exigida. Os dados são sintéticos e não há pacientes; o edital (3.1) exige aprovação só para coleta com seres humanos, animais, dados sensíveis ou matéria regulada | 07/11, junto com a pauta |
| Citar a Fcecon e a topologia | Confirmar com o hospital o que pode ser citado. O diário de 04/10 já lista o risco de revelar a estrutura da rede | 14/11 |
| Declarar o uso de IA | O edital (3.3) pede declaração. Redigir um parágrafo sobre o uso do Claude no desenvolvimento e na redação | 22/11 |

## Riscos

| Risco | Efeito | Resposta |
|---|---|---|
| O 03/11 do edital (seção 4.1) valer, e já passou | A entrega ao orientador estaria atrasada | Pergunta 4 da prioridade 2, urgente |
| Revisão da literatura sem dono claro | Seção ausente na versão para a banca | Dividir os temas em 07/11 |
| Disputar tempo com o congelamento de 11/11 | Código e texto competem | Texto não bloqueia código; decisões de medição até 10/11 |
| Citar obra com dado bibliográfico errado | Referência falsa | Conferir cada candidata na fonte antes de citar |
