# Ajustes de navegação e investigação — SigmaTI

## Resultado e escopo

[Certo] Implementados os cinco ajustes do plano: busca por identificador, hierarquia da visão geral, continuidade da investigação, nomes acessíveis únicos e contagem explícita de incidentes ativos. Alterações locais no frontend, sem dependências adicionais, modificação do backend ou publicação.

A skill ui-ux-pro-max foi consultada com `--design-system` e diretrizes React. Foram aproveitadas as recomendações de investigação por filtros, visibilidade dos dados, componentes controlados e semântica HTML. A identidade aprovada (azul institucional, dois temas, fonte local) foi preservada, em vez de substituir cores ou tipografia por sugestões automáticas.

## Comportamentos entregues

- IDs INC-008 e inc-008 encontram o mesmo registro. INC-004 é encontrado em Todos ou Resolvidos; não aparece no escopo Ativos.
- Primeira entrada: quatro ativos. Situação distingue Ativos, Todos, Abertos, Em análise e Resolvidos. Limpar filtros mostra os oito registros, sem busca ou severidade.
- Menu informa “4 ativos” e conserva a consulta ao retornar. Pesquisas, filtros e expansões de incidentes/equipamentos ficam em memória em App, inclusive ao alternar desktop/celular.
- Presets dos indicadores substituem filtros anteriores; a navegação comum não os redefine. São botões de aplicação de filtro e navegação, sem serializar consultas na URL.
- Prioritários ordenados: INC-008 (crítica), INC-007 e INC-006 (altas, horário decrescente). A distribuição usa os mesmos quatro ativos, incluindo a severidade baixa com zero registros.
- Controles de expansão mantêm a semântica nativa e recebem nomes com ID ou equipamento. Enter/Espaço operam o mesmo estado controlado da tabela e dos cartões.
- Simulador mantido em sua seção, sem chamadas automáticas e sem alterar os dados demonstrativos.

## Verificações executadas

- `npm run lint`: aprovado.
- `npm run build`: aprovado; 21 módulos e arquivos de produção gerados.
- `scripts/verify-interface.mjs`: 24 verificações; nove requisições interceptadas, nenhuma chamada real à API/IA e nenhum erro JavaScript de página.
- `scripts/verify-accessibility.mjs`: oito combinações de seção/tema, nomes únicos das expansões visíveis, operação por Enter/Espaço e expansão preservada entre representações.
- Contraste mínimo calculado nos textos avaliados: 5,76:1 no claro e 5,47:1 no escuro. Não equivale a certificação WCAG ou teste com leitor de tela real.
- 32 layouts: quatro seções, dois temas e larguras de 375, 768, 1024 e 1440px, sem rolagem horizontal; menu móvel também verificado.
- Em 1280×720 e 390×844, nos dois temas, o retângulo completo do primeiro título prioritário fica na primeira tela. Capturas sem rolagem produzidas pelo teste.
- Indicadores conferidos para os seis equipamentos, quatro ativos, três ativos críticos/altos, quatro resolvidos e severidades com 1/2/1/0 registros. Verificado que substituem consultas anteriores.
- Fluxo “buscar pacotes → expandir INC-008 → Equipamentos → retornar” preserva resultados e detalhes. Consulta e expansão de Equipamentos também preservadas. Recarregar reinicia em Ativos.
- Regressão do simulador: obrigatoriedade, espaços em branco, envio duplicado, contrato, sucesso, HTML tratado como texto, IA indisponível, HTTP 422/500, conexão recusada, JSON/formato inválidos e timeout de 20 segundos sem repetição automática.
- Detector executado uma vez em `sigma-frontend/src`: `[]`, sem achados. Resultado automatizado não substitui a revisão de usabilidade.

## Evidências

Pasta `evidencias/`: `checks.json`, `layouts.json`, `accessibility.json`, `detect.json`, oito capturas completas de visão geral/simulador e quatro capturas da primeira tela nas dimensões de aceite.

Chrome headless com Playwright do runtime local. Os testes usaram a instância preexistente em `127.0.0.1:5173`, com interceptação da rota da API. Ela foi preservada; nenhum servidor adicional foi iniciado. As evidências do redesenho anterior não foram sobrescritas.

## Revisão heurística após os ajustes

Esta é uma revisão de implementação, em um único contexto, dos dez critérios da avaliação anterior. Não é uma nova execução dual-agent de critique, não inclui usuários reais e não estabelece tendência numérica comparável à nota anterior.

| Heurística | Verificação após ajuste |
|---|---|
| Visibilidade do estado | [Certo] Resultado informa quantidade, total e situação; menu explica que o contador é de ativos. |
| Correspondência com o trabalho real | [Certo] IDs exibidos podem ser pesquisados; equipamentos, setores e dados demonstrativos preservados. |
| Controle e liberdade | [Certo] Consultas e detalhes sobrevivem à troca de seção; Limpar filtros oferece retorno explícito ao conjunto completo. |
| Consistência | [Certo] Indicadores, prioridades, opções e contagens derivam da mesma base; expansão consistente entre tabela e cartão. |
| Prevenção de erros | [Certo] Regressão confirma campos obrigatórios, bloqueio de duplicação e avisos de dados fictícios. |
| Reconhecimento | [Certo] Nomes acessíveis identificam cada registro; opções Ativos/Todos e Crítica e alta representam os subconjuntos. |
| Eficiência | [Certo] Indicadores e severidades aplicam consultas em uma ação; retorno pelo menu conserva o contexto. |
| Estética e organização | [Certo] Primeiro incidente visível nas duas dimensões de aceite; [Provável] a promoção reduzida diminui a competição pela atenção. |
| Recuperação de erros | [Certo] Estados vazios e falhas simuladas preservam o formulário e permitem novo envio manual. |
| Ajuda e orientação | [Certo] Campo de busca menciona ID; contagem informa situação; instruções do simulador mantidas. |

[Provável] Os ajustes reduzem o esforço de investigação, mas essa conclusão requer observação de técnicos reais para quantificar ganho de tempo. A continuidade é intencionalmente limitada à sessão; recarregar limpa o estado. Monitoramento real, persistência e autenticação seguem fora do escopo.

## Reproduzir

Na pasta `sigma-frontend`, executar lint, build e os dois scripts de navegador conforme o README. Para usar a instância na porta 5173, definir `SIGMA_UI_URL=http://127.0.0.1:5173`; o padrão dos scripts continua 5174 para testes isolados. Passar o caminho do Playwright como primeiro argumento quando ele vier do runtime do Codex.
