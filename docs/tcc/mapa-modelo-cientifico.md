# Mapa do modelo científico: situação do projeto, seção por seção

Painel de status criado em 05/11/2026. O modelo é o `modelo-cientifico.pdf` da Aurum Revista Multidisciplinar. Este mapa **não é o artigo**: serve para saber, de relance, o que o projeto já sustenta e o que falta para cada seção do modelo. Quando uma seção avançar, atualize a coluna "Situação".

[Voltar ao índice do TCC](README.md) · [Plano de pesquisa](plano-de-pesquisa-2026-11-05.md) · [Edital](edital-tcc-ii-2026-2.md)

Legenda: **Pronto** = há material suficiente, falta só escrever. **Parcial** = há material, mas incompleto. **Ausente** = não existe.

| Seção do modelo | Situação | Material de origem | O que falta |
|---|---|---|---|
| Título, autores, titulação, Lattes ou ORCID | Parcial | [Proposta ao orientador](proposta-orientador.md) | Dados pessoais de cada autor (máximo 3, pelo edital) e o nome do orientador e do coorientador |
| Resumo (100 a 250 palavras) e palavras-chave | Pronto | [Balanço dos dados](balanco-dos-dados.md) | Escrever, depois que as lacunas de medição forem decididas |
| Abstract e keywords | Pronto | Derivado do resumo | Traduzir com ferramenta de IA, como o modelo manda |
| 1.1 Apresentação do tema | Pronto | [Visão do produto](../visao-do-produto.md), [estudo de caso](../arquitetura/estudo-de-caso.md) | Reescrever em forma de artigo |
| 1.2 Delimitação do problema | Pronto | Seção "Problemática" do estudo de caso | Reescrever |
| 1.3 Objetivos (um geral, específicos com traço) | Parcial | Hipóteses H1 a H4 em [visão de engenharia](../../engenharia/docs/00-visao-de-engenharia.md) | Destilar **um** objetivo geral e os específicos |
| 1.4 Justificativa | Parcial | Visão do produto, seções 1 e 2 | Escrever relevância científica e social, e a aplicabilidade |
| **1.5 Revisão da literatura** | **Ausente** | O [roteiro do TCC](../../engenharia/docs/06-roteiro-tcc.md) marca "Fundamentação" sem material | Levantar fontes por tema e redigir. Ver o [plano de pesquisa](plano-de-pesquisa-2026-11-05.md) |
| 2 Metodologia: tipo de pesquisa | Parcial | [Metodologia experimental](../../engenharia/docs/03-metodologia-experimental.md) | Classificar explicitamente (aplicada, experimental, quantitativa, estudo de caso) |
| 2 Metodologia: estudo de caso | Parcial | Estudo de caso da Fcecon | Descrever local, problema, aplicação e resultados, com a topologia anonimizada |
| 2 Metodologia: técnicas e instrumentos | Pronto | Metodologia experimental, seção "Experimentos" (E1 a E5) | Redigir |
| 2 Metodologia: análise dos dados | Pronto | Metodologia experimental, "Métricas e definições" | Fluxograma do método (ver figuras) |
| 3 Resultados | Pronto nos números | [Balanço dos dados](balanco-dos-dados.md): E1, E3, E4, E6, #46 e #25 medidos | E5 sem medição, E2 só em ensaio local, deriva lenta com 16,7% |
| 3 Discussão com a literatura | Ausente | Depende da seção 1.5 | Comparar resultados com os autores levantados |
| Tabelas, quadros e figuras | Parcial | `evidencias/` (uma figura: custo da auditoria) | Diagrama de arquitetura, fluxograma do método, gráficos de E1 e E3 |
| 4 Conclusão | Pronto | [Limitações](limitacoes.md) | Tabela "hipótese confirmada ou refutada" e retomada dos objetivos |
| 4.1 Pesquisas futuras | Pronto | Backlog pós-banca (issues #10, #12, #16 a #31) | Selecionar 3 a 5 itens |
| Referências em ABNT | **Ausente** | Nenhuma lista no repositório | Montar a partir da revisão da literatura |

## Hipóteses do trabalho e estado da evidência

| Hipótese | Enunciado resumido | Estado |
|---|---|---|
| H1 | EWMA e MAD detectam degrau e pico com atraso de até 1 amostra | Confirmada para degrau e pico; **refutada** para deriva lenta (16,7%) |
| H2 | Burn rate em duas janelas pagina em quedas totais e não em picos curtos | Medida em laboratório (E3); rede real pendente |
| H3 | A cadeia de hash detecta 100% de adulterações, remoções e reordenações | Medida em 04/11 (E4); **truncamento do fim não é detectado** sem a âncora externa |
| H4 | O pipeline atende RF01 (≤ 5 s) e RNF04 (≤ 15 s) | RF01 em ensaio local; **RNF04 sem evidência** (E5 não feito) |

## Regras de formato que valem para a versão final

Times New Roman 12, A4, margens de 2,5 cm (superior e inferior) e 3 cm (esquerda e direita), espaçamento 1,5, recuo de parágrafo de 1,25 cm. Figuras com título embaixo (Times 12) e fonte (Times 10). Referências em ordem alfabética, ABNT. O modelo não informa limite de páginas: perguntar ao orientador.
