# Status do TCC: artigo e monografia

Atualizado em 13/11/2026. Os dois rascunhos existem como **base de conhecimento**: servem para o grupo saber como está a escrita e a documentação do trabalho e para o orientador ter um parâmetro do que já há. Nenhum deles é, por ora, a versão que será entregue, e não há decisão de formato pendente.

- **Artigo científico**, no modelo `modelo-cientifico.pdf` (Aurum Revista Multidisciplinar): [artigo-cientifico-rascunho.md](artigo-cientifico-rascunho.md).
- **Monografia**, nos sete capítulos que o orientador publicou em [`engenharia/docs/06-roteiro-tcc.md`](../../engenharia/docs/06-roteiro-tcc.md): [monografia-rascunho.md](monografia-rascunho.md).

Os capítulos de introdução, metodologia, resultados e conclusão da monografia reaproveitam o texto e os números do artigo, então as duas versões não divergem. Os capítulos 3 (requisitos e arquitetura) e 4 (implementação) só existem na monografia.

[Voltar ao índice do TCC](README.md) · [Plano de pesquisa](plano-de-pesquisa-2026-11-05.md) · [Edital](edital-tcc-ii-2026-2.md)

Legenda: **Sólido** = escrito e sustentado por dado no repositório. **Parcial** = escrito, mas com limite ou lacuna que muda o que se pode afirmar, ou que precisa de conferência. **Ausente** = sem texto ou sem material.

## Resumo da situação

| Situação | Artigo | Monografia |
|---|---:|---:|
| Sólido | 14 | 12 |
| Parcial | 7 | 9 |
| Ausente | 5 | 5 |

Cada rascunho tem 28 marcadores `[PENDENTE]`, que `grep PENDENTE` lista. O que é número está sólido. Faltam literatura, decisões do orientador, figuras, dados dos autores e a conferência do capítulo 4 contra o código.

## O que já temos de rascunho, para não recomeçar do zero

| Assunto | O que já existe | Onde |
|---|---|---|
| Contexto, problema e solução | Texto pronto e revisado | [estudo de caso](../arquitetura/estudo-de-caso.md), [visão do produto](../visao-do-produto.md) |
| Requisitos RF01 a RF07, RNF01 a RNF09 e métricas de validação | Tabelas completas | estudo de caso, seções 3 a 6 |
| Hipóteses H1 a H4, problema de pesquisa e contribuições | Prontos | [visão de engenharia](../../engenharia/docs/00-visao-de-engenharia.md) |
| Metodologia, experimentos E1 a E5 e ameaças à validade | Prontos | [metodologia experimental](../../engenharia/docs/03-metodologia-experimental.md) |
| Arquitetura, stack e decisões de segurança | Prontos | [stack de tecnologia](../arquitetura/stack-de-tecnologia.md), [ADRs](../../engenharia/docs/adr/) |
| Rastreabilidade requisito, módulo e teste | Tabela (desatualizada em RF05) | [04-rastreabilidade](../../engenharia/docs/04-rastreabilidade.md) |
| Implementação do núcleo e da coleta | Guias por módulo | `engenharia/docs/01`, `02`, `07`, `08`, `09` |
| Números medidos (E1 a E4, E6, auditoria, backup) | Prontos, com dado bruto | [balanço dos dados](balanco-dos-dados.md), `evidencias/`, `engenharia/resultados/` |
| Limitações do trabalho | Capítulo pronto, com 11 itens | [limitações](limitacoes.md) |
| Linha do tempo e contribuições da equipe | Prontos | [relatório das Sprints 1 e 2](relatorio-sprints-1-e-2.md) (PR #97), diários de bordo |
| Trabalhos futuros | Lista pronta | `06-roteiro-tcc.md` e o backlog (#10, #12, #26 a #30) |
| Texto de IA, literatura, figuras | **Não existem** | |

## Status do artigo científico

| Seção | Situação | O que falta |
|---|---|---|
| Autores, titulação, Lattes ou ORCID, orientador | **Ausente** | Dados de cada autor (máximo 3) e do orientador |
| Resumo e palavras-chave | **Sólido** | Reler quando as lacunas de medição mudarem |
| Abstract e keywords | **Parcial** | Revisar a tradução com ferramenta de IA |
| 1.1 Tema | **Sólido** | Nada de conteúdo |
| 1.2 Problema | **Sólido** | Nada de conteúdo |
| 1.3 Objetivos | **Sólido** | O orientador deve validar a redação |
| 1.4 Justificativa | **Sólido** | Pode ganhar fonte para a relevância social |
| **1.5 Revisão teórica (6 subseções)** | **Ausente** | Levantar 3 a 5 fontes por tema e redigir. **O maior buraco** |
| 2.1 Tipo de pesquisa | **Sólido** | O orientador validar a classificação |
| 2.2 Estudo de caso | **Parcial** | Diagrama de arquitetura; autorização para nomear a instituição |
| 2.3 Técnicas e instrumentos | **Sólido** | E5 sem medição |
| 2.4 Procedimentos de análise | **Sólido** | Fluxograma do método |
| 2.5 Ambiente e ameaças à validade | **Sólido** | Nada |
| 3.1 Detecção (E1) | **Sólido** | Discussão com a literatura |
| 3.2 Latência do alerta, MTTD, MTTA e MTTR | **Parcial** | Rodadas anteriores ao PR #79 e não repetidas (#8 aberta) |
| 3.3 Burn rate (E3) | **Parcial** | Duas execuções por condição, em loopback; E3 da `v1.0.0` não executado |
| 3.4 Cadeia de hash (E4) | **Sólido** | Nada |
| 3.5 Custo e contenção da auditoria | **Parcial** | Limite de login não acordado (#46); opção D (PR #94) não medida |
| 3.6 Anonimização (E6) | **Parcial** | Critério original reprovado; reformulação da #5 aguarda o orientador; amostra pequena |
| 3.7 Backup e restauração | **Sólido** | Nada |
| 3.8 Discussão com a literatura | **Ausente** | Depende da seção 1.5 |
| Figuras | **Ausente** | Arquitetura, fluxograma, gráficos de E1 e E3 |
| 4 Conclusão e hipóteses | **Sólido** | Nada de conteúdo |
| 4.1 Pesquisas futuras | **Sólido** | Nada |
| Declaração de uso de IA | **Parcial** | Confirmar com o orientador se entra |
| Referências em ABNT | **Ausente** | 13 referências escritas **de memória**: conferir cada uma na fonte |

## Status da monografia (sete capítulos do orientador)

| Capítulo e seção | Situação | O que falta |
|---|---|---|
| Capa, folha de rosto, listas e sumário | **Ausente** | Dados institucionais e geração na exportação |
| Resumo e abstract | **Sólido** e **Parcial** | Mesmos do artigo; revisar a tradução |
| **1 Introdução** (1.1 tema a 1.7 organização) | **Sólido** | O orientador validar objetivos e hipóteses |
| **2 Fundamentação** (2.1 SRE, 2.2 detecção, 2.3 hash, 2.4 LGPD, 2.5 redes, 2.6 relacionados) | **Ausente** | Literatura inteira. O orientador listou o que quer: SRE, EWMA, MAD, CUSUM, hash, LGPD, TCP e TLS. TLS e SSRF ainda nem têm texto |
| 3.1 Estudo de caso e restrições | **Parcial** | Autorização para nomear a instituição |
| 3.2 Requisitos RF e RNF | **Sólido** | Nada |
| 3.3 Rastreabilidade | **Parcial** | RF03 sem medição (E5), RF06 não entregue (#16), RF02 sem pfSense. A tabela do orientador está desatualizada em RF05; conferir os nomes de teste do backend |
| 3.4 Arquitetura | **Parcial** | Diagrama de implantação híbrido (o orientador pede); pfSense e n8n estão no desenho, não na `v1.0.0` |
| 3.5 Decisões de projeto (ADRs) | **Sólido** | Nada |
| 3.6 Segurança e privacidade | **Sólido** | Nada |
| 4.1 a 4.3 Núcleo, Vigilark e propriedades testadas | **Sólido** | Nada |
| 4.4 Persistência e coleta | **Sólido** | Conferir parâmetros com o código |
| 4.5 Auditoria | **Sólido** | Nada |
| 4.6 Anonimização | **Parcial** | Escrito a partir da documentação e dos relatórios, **sem ler `sanitizer.py`**: conferir com o código |
| 4.7 API e autenticação | **Parcial** | Conferir com o código; o hash é PBKDF2, e o RF07 cita bcrypt ou Argon2 |
| 4.8 Implantação, backup e restauração | **Parcial** | Passo a passo de implantação para o apêndice |
| 4.9 Testes e CI | **Sólido** | Nada |
| 5 Metodologia (5.1 a 5.4) | **Sólido** | Fluxograma do método |
| 6.1 Detecção, 6.4 Cadeia de hash, 6.7 Restauração | **Sólido** | Nada |
| 6.2 Latência, 6.3 Burn rate, 6.5 Auditoria, 6.6 Anonimização | **Parcial** | Os mesmos limites do artigo (3.2, 3.3, 3.5, 3.6) |
| 6.8 Discussão com a literatura | **Ausente** | Depende do capítulo 2 |
| 7 Conclusão (hipóteses, limitações, contribuições, futuros, finais) | **Sólido** | Nada de conteúdo |
| Declaração de uso de IA | **Parcial** | Confirmar com o orientador |
| Referências | **Ausente** | As mesmas 13 do artigo, a conferir |
| Apêndices e anexos | **Ausente** | Passo a passo de implantação, mocks da anonimização, rastreabilidade completa |

## As hipóteses do trabalho

| Hipótese | Estado da evidência |
|---|---|
| H1: EWMA e MAD detectam degrau e pico | Confirmada para degrau e pico (100%); **refutada** para deriva lenta (17% a 20%) |
| H2: burn rate em duas janelas | Confirmada em laboratório, com duas execuções; rede real pendente |
| H3: cadeia de hash | Confirmada para adulteração, remoção e troca (750 casos); **refutada** para truncamento do fim sem a âncora |
| H4: RF01 em até 5 s e RNF04 em até 15 s | RF01 atendido em ensaio local; **RNF04 sem evidência** (E5 não realizado) |

## O que correr atrás, por prioridade

Vale para os dois rascunhos, e só os itens 1 e 4 pesam mais na monografia.

1. **Revisão teórica e referências.** É o único bloco sem texto e bloqueia a discussão. Dividir os seis temas entre os autores, levantar as fontes, redigir e conferir os dados bibliográficos. Na monografia vira o capítulo 2 inteiro, mais longo. Precisa também de trabalhos relacionados (Zabbix, Nagios, Prometheus), que respondem "o que o SIGMA acrescenta".
2. **Decisões do orientador, que fecham os "Parcial".** Levar à conversa de sábado (14/11):
   - o limite de páginas e o fluxo de submissão à revista, quando as orientações da disciplina definirem o formato final;
   - autores (máximo 3), orientador e coorientador, e o fluxo de submissão à revista;
   - o critério de aceite do recall da anonimização (#5): reformular ou manter o reprovado;
   - o limite de tempo do login da auditoria (#46);
   - **dia e horário da banca e a data de entrega do PDF: as datas definitivas saem das orientações da aula de TCC de 12/11. O Vinícius vai enviá-las, e este painel, o plano de pesquisa e o resumo do edital devem ser atualizados com elas;**
   - se a instituição pode ser nomeada e se o texto leva a declaração de uso de IA.
3. **Medições que ainda dão para fazer.** Cada uma fecha ou vira limitação declarada, que os rascunhos já trazem:
   - repetir as rodadas de carga da #8 depois do #79;
   - E3 na `v1.0.0`, com mais execuções;
   - E5, o tempo de resposta da IA: sem provedor real e sem anonimização ativa, vai como "sem evidência".
4. **Conferir o capítulo 4 da monografia contra o código.** Foi escrito a partir dos documentos de `engenharia/docs/` e dos relatórios, sem ler `sanitizer.py`, a autenticação nem o agendador. Ler o código e corrigir o que divergir antes de entregar.
5. **Figuras.** Diagrama de implantação híbrido (o orientador pede), fluxograma do método, gráficos de detecção (E1) e de burn rate (E3). Só existe a figura do custo da auditoria.
6. **Dados dos autores, declaração de IA, tradução do abstract, capa e apêndices.**

## Limites que o texto precisa manter

Os dois rascunhos já dizem cada um com todas as letras. Se o texto for reescrito, eles não podem sumir:

- **Tudo foi medido em loopback**, em uma máquina, com dados sintéticos. Nada foi medido em rede real.
- **RNF04 (15 s da IA) está sem evidência.**
- **O recall de transformação de 95,12% reprovou o critério de 99%.** Provar 99% com 95% de confiança exigiria cerca de 381 identificadores sem falha.
- **MTTA e MTTR não são tempos de operador.** O MTTD é limite superior e o painel não o mostra.
- **O truncamento do fim da trilha só é detectado pela âncora externa.**
- **Poucas repetições** no E3 (duas) e na auditoria (cinco).

## Regras de formato do artigo (modelo Aurum)

Times New Roman 12, A4, margens de 2,5 cm (superior e inferior) e 3 cm (esquerda e direita), espaçamento 1,5, recuo de parágrafo de 1,25 cm. Figuras com título embaixo (Times 12) e fonte (Times 10). Referências em ordem alfabética, ABNT. O modelo não informa limite de páginas. A monografia segue a norma de formatação do curso, que este repositório não traz.
