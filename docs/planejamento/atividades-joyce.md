# Atividades da Joyce — levantamento

Reunião de todas as atividades atribuídas à Joyce, feita em 01/11/2026 para o Vinícius rever e redirecionar ao novo design system, com base no protótipo `design-system/exemplo/`. Este arquivo **só lista**: não traz veredito de manter, ajustar ou descartar nenhuma tarefa.

## Fontes

- Backlog completo: `design-system/tarefas-joyce.md` na branch `feature/tarefas-joyce` (commit `afac415`), escrito em 21/10/2026.
- Cartões do Trello: `docs/historico/rascunhos/trello-atualizacao-2026-10-21/joyce-planejado.json` (42 cartões, todos com o estado "planejado; não iniciado" nesse snapshot de 21/10; todos ligados às issues #15 e #31).
- Pull requests da Joyce: consulta ao GitHub em 01/11/2026.
- Protótipo de referência: `design-system/exemplo/` (ver a última seção).

Sobre os tamanhos: **P** é até meio dia e **M** é até um dia, estimativas de escopo para uma pessoa, não prazo. O backlog não tem data final confirmada.

## Resumo

| Fase | Tarefas | Quantidade | Tamanhos |
|---|---|---:|---|
| Fase 0 · Ambientação | DS-01 a DS-02 | 2 | 2 P + 0 M |
| Fase 1 · Decisões de marca (entregas documentais) | DS-03 a DS-05 | 3 | 1 P + 2 M |
| Fase 2 · Fundação | DS-06 a DS-08 | 3 | 2 P + 1 M |
| Fase 3 · Componentes | DS-09 a DS-15 | 7 | 4 P + 3 M |
| Fase 4 · Estrutura | DS-16 a DS-19 | 4 | 3 P + 1 M |
| Fase 5 · Telas com dados existentes | DS-20 a DS-31 | 12 | 3 P + 9 M |
| Fase 6 · Fechamento | DS-32 a DS-34 | 3 | 0 P + 3 M |
| Condicionais de integração (não iniciar antes do gate) | DS-35 a DS-42 | 8 | 1 P + 7 M |
| **Total** | DS-01 a DS-42 | **42** | 16 P + 26 M |

São 34 tarefas que avançam sem API nova (DS-01 a DS-34) e 8 condicionais (DS-35 a DS-42) que esperam a integração de Vinny e Iohan. Mais 8 rascunhos de integração (API-01 a API-08), que não são issues criadas.

## As 42 tarefas

Cada tarefa herda o checklist C0 descrito mais abaixo. A coluna "Depende de" mostra a ordem prevista no backlog.

### Fase 0 · Ambientação

| Id | Título | Tam. | Depende de | Objetivo |
|---|---|---|---|---|
| DS-01 | Percorra o mock e registre a matriz de perfis | P | nenhuma | Conhecer as seis telas e reconhecer o que cada perfil realmente pode ver antes de redesenhar. |
| DS-02 | Corrija a hierarquia de títulos do Diagnóstico | P | DS-01 | Permitir que o leitor de tela entenda as seções do diagnóstico, sem alterar formulário ou resultado. |

### Fase 1 · Decisões de marca (entregas documentais)

| Id | Título | Tam. | Depende de | Objetivo |
|---|---|---|---|---|
| DS-03 | Escolha a variante da marca e uma paleta oficial | M | DS-01, DS-02 | Definir uma identidade coerente sem confundir a marca com disponibilidade dos serviços. |
| DS-04 | Entregue o logotipo vetorial para os dois temas | M | DS-03 | Disponibilizar uma marca legível, sem o fundo opaco dos JPGs, para uso futuro no cabeçalho. |
| DS-05 | Defina a fonte e os direitos de uso | P | DS-03 | Garantir leitura consistente sem depender de uma fonte remota nem de licença presumida. |

### Fase 2 · Fundação

| Id | Título | Tam. | Depende de | Objetivo |
|---|---|---|---|---|
| DS-06 | Centralize os tokens sem mudar a aparência | P | DS-03, DS-04, DS-05 | Dar à equipe um único lugar para ajustar a aparência sem criar novas versões de cada cor. |
| DS-07 | Aplique as escalas de espaço e tipografia aprovadas | P | DS-06 | Melhorar ritmo de leitura e alinhamento, inclusive com nomes compridos e números de métricas. |
| DS-08 | Implemente os dois temas e meça o contraste | M | DS-07 | Aplicar a paleta decidida mantendo leitura e estados confiáveis em claro e escuro. |

### Fase 3 · Componentes

| Id | Título | Tam. | Depende de | Objetivo |
|---|---|---|---|---|
| DS-09 | Extraia o botão com estados completos | M | DS-08 | Distinguir ação principal, secundária, destrutiva, ocupada e desabilitada sem depender só de opacidade. |
| DS-10 | Padronize etiquetas de estado e severidade | P | DS-09 | Permitir reconhecer disponibilidade, prioridade e orçamento sem interpretar apenas uma cor. |
| DS-11 | Extraia os painéis e seus títulos semânticos | P | DS-10 | Organizar grupos de conteúdo com contorno e hierarquia consistentes. |
| DS-12 | Extraia a estrutura da tabela acessível | M | DS-11 | Reutilizar tabelas com legenda, cabeçalhos e rolagem localizada sem perder a leitura por teclado. |
| DS-13 | Extraia os alertas e mensagens de ação | P | DS-12 | Dar destaque consistente a erro, informação e sucesso sem anunciar falsos resultados. |
| DS-14 | Extraia estados vazios e de carregamento | P | DS-13 | Explicar por que não há conteúdo e o que fazer, sem confundir carregamento, falha e lista vazia. |
| DS-15 | Extraia campos e mensagens de formulário | M | DS-14 | Manter rótulos, ajuda e validação claros nos formulários, inclusive quando desabilitados. |

### Fase 4 · Estrutura

| Id | Título | Tam. | Depende de | Objetivo |
|---|---|---|---|---|
| DS-16 | Monte o cabeçalho com marca e papel por extenso | P | DS-15 | Identificar o sistema, a pessoa conectada e suas capacidades sem códigos internos no cabeçalho. |
| DS-17 | Organize a navegação lateral no desktop | P | DS-16 | Facilitar alternância entre as áreas existentes sem copiar permissões ou páginas futuras do protótipo. |
| DS-18 | Adapte o menu para celular com foco previsível | M | DS-17 | Permitir navegar a 390 px sem uma fileira de abas ocupar a tela. |
| DS-19 | Compacte os avisos sem esconder a demonstração | P | DS-18 | Liberar espaço no topo mantendo explícitos dados fictícios e API simulada. |

### Fase 5 · Telas com dados existentes

| Id | Título | Tam. | Depende de | Objetivo |
|---|---|---|---|---|
| DS-20 | Aplique o visual novo ao Login | M | DS-19 | Tornar entrada e falhas de credencial legíveis e previsíveis sem criar cadastro público. |
| DS-21 | Reorganize a Saúde sem reinterpretar os dados | M | DS-20 | Priorizar situação, última medição e orçamento preservando a diferença entre dado real e lacuna de observação. |
| DS-22 | Transforme a Saúde em cartões no celular | M | DS-21 | Ler cada serviço completo a 390 px sem precisar cruzar seis colunas. |
| DS-23 | Traduza tipos e formate durações de incidentes | P | DS-22 | Ler Latência e 40 min mantendo precisão, amostras e unidade original do contrato. |
| DS-24 | Destaque prioridade e ações dos incidentes no desktop | M | DS-23 | Distinguir prioridade e ciclo de vida sem misturar falha medida com atendimento. |
| DS-25 | Adapte os incidentes para cartões no celular | M | DS-24 | Usar as ações e consultar identificação e detecção sem cortar conteúdo a 390 px. |
| DS-26 | Reorganize a criação de solicitações de aprovação | M | DS-25 | Dar à área obrigatória de Aprovações uma entrada clara para solicitar revisão por outra pessoa. |
| DS-27 | Padronize os cartões de decisão e seus bloqueios | M | DS-26 | Explicar autoria, expiração e papel insuficiente antes de pedir uma decisão justificada. |
| DS-28 | Separe integridade e eventos no visual da Auditoria | M | DS-27 | Evitar que a integridade da trilha de sondas pareça atestar também os eventos operacionais. |
| DS-29 | Apresente eventos de Auditoria em cartões no celular | P | DS-28 | Ler horário, operador, ação e recurso sem comprimir uma tabela a 390 px. |
| DS-30 | Aplique o visual novo ao formulário do Diagnóstico | M | DS-29 | Deixar claro o que será enviado e quando a solicitação está em processamento. |
| DS-31 | Reorganize o resultado e o conteúdo generalizado | P | DS-30 | Mostrar a resposta da IA como apoio e tornar visível o conteúdo enviado, sem prometer anonimização pelo mock. |

### Fase 6 · Fechamento

| Id | Título | Tam. | Depende de | Objetivo |
|---|---|---|---|---|
| DS-32 | Atualize capturas de Login, Saúde e Incidentes | M | DS-31 | Permitir revisar e comparar as três primeiras telas exatamente como foram implementadas. |
| DS-33 | Atualize capturas de Aprovações, Auditoria e Diagnóstico | M | DS-32 | Documentar também as áreas obrigatórias que a referência visual omite ou simplifica. |
| DS-34 | Consolide o design implementado e o estado atual | M | DS-33 | Entregar uma referência factual da interface implementada e das pendências, sem confundir protótipo com produto. |

### Condicionais de integração (não iniciar antes do gate)

| Id | Título | Tam. | Depende de | Objetivo |
|---|---|---|---|---|
| DS-35 | Exiba responsabilidade e a ação de assumir | M | DS-34 + API-01 entregue e gate validado pela integração | Mostrar quem assumiu e permitir a assunção somente após contrato concorrente e autorização confirmados. |
| DS-36 | Apresente a solicitação de escalonamento | M | DS-34 + API-02 entregue e gate validado pela integração | Encaminhar o incidente com motivo visível sem trocar estado localmente como se já tivesse sido salvo. |
| DS-37 | Apresente a conversa de IA ligada ao incidente | M | DS-34 + API-03 entregue e gate validado pela integração | Exibir uma lista simples de mensagens e um envio contextual depois que o contrato existir. |
| DS-38 | Apresente a lista de relatórios disponíveis | M | DS-34 + API-04 entregue e gate validado pela integração | Distinguir relatório disponível, em geração e vazio sem fingir que existe um arquivo exportado. |
| DS-39 | Apresente metadados seguros de credenciais | M | DS-34 + API-05 entregue e gate validado pela integração | Identificar a origem e o estado de uma credencial sem expor chaves nem prometer rotação fictícia. |
| DS-40 | Apresente a lista de equipamentos já cadastrados | M | DS-34 + API-06 entregue e gate validado pela integração | Consultar alvos existentes com os mesmos papéis de leitura da API, sem inventar um cadastro que o mock não atende. |
| DS-41 | Apresente o estado global da coleta existente | P | DS-34 + API-07 entregue e gate validado pela integração | Mostrar se o coletor está habilitado e suas métricas sem transformar SSE conectado em saúde da coleta. |
| DS-42 | Apresente a lista atual de usuários | M | DS-34 + API-08 entregue e gate validado pela integração | Permitir ao Gestor consultar a lista disponível sem inventar papel, estado ou ações ausentes na resposta. |

## Rascunhos de integração (API-01 a API-08)

São rascunhos de pedido para Vinny e Iohan, não issues criadas nem contratos aprovados. Rotas marcadas como proposta não existem na base conferida.

| Id | Assunto | Situação | Bloqueia | Rotas |
|---|---|---|---|---|
| API-01 | Assumir incidente com responsável e versão | API nova, muda o modelo (`reconhecer` hoje não significa assumir) | DS-35 | POST `/api/eng/incidentes/{id}/assumir` (proposta) |
| API-02 | Escalar incidente com destino, motivo e versão | API nova, muda o modelo | DS-36 | POST `/api/eng/incidentes/{id}/escalar` (proposta) |
| API-03 | Conversa de IA ligada ao incidente, com estados explícitos | API nova (`POST /api/alertas` é avulso, sem chat) | DS-37 | GET/POST `/api/eng/incidentes/{id}/ia/mensagens` (proposta) |
| API-04 | Relatórios reais e seus arquivos | API nova sobre contrato incompleto (`GET /api/relatorios` devolve lista vazia) | DS-38 | POST `/api/relatorios`, GET `/api/relatorios/{id}/arquivo`, agendamentos (propostas) |
| API-05 | Ciclo de vida das credenciais | API nova (`/api/chaves/rotacao` só devolve texto) | DS-39 | GET `/api/credenciais`, POST `.../rotacionar` e `.../revogar` (propostas) |
| API-06 | Equipamentos: alvos, cadastro e ativação | Integração simples (rotas existem) | DS-40 | GET/POST `/api/eng/alvos`, PATCH `/api/eng/alvos/{id}` (existentes) |
| API-07 | Estado global da coleta | Integração simples (rota existe, ausente no mock) | DS-41 | GET `/api/eng/coleta/status` (existente); "última comunicação por origem" é proposta |
| API-08 | Usuários e administração futura | Integração simples para listar e criar; API nova para detalhe, desativar e redefinir | DS-42 | GET/POST `/api/usuarios` (existentes); PATCH e redefinição (propostas) |

**Gate para liberar cada tarefa DS-35 a DS-42:** Vinny e Iohan confirmam rota, campos e autorização, implementam ou conectam a API, estendem `api.js`, o mock e os hooks quando necessário, entregam fixtures (normal, vazio, lento, erro, 403) e registram um teste de contrato ou aceite real. Só então a Joyce consome o adaptador pronto.

## Pull requests abertos da Joyce

| PR | Tarefa | Branch → base | Estado em 01/11/2026 |
|---|---|---|---|
| #52 | DS-01 Ambientação do mock e capturas iniciais | `feature/ds-01-ambientacao` → `feature/front-design-system` | Aberto, pronto para revisão |
| #53 | DS-02 Hierarquia de títulos do Diagnóstico | `feature/ds-02-titulos-diagnostico` → `feature/front-design-system` | Aberto, pronto para revisão. Na revisão, "Enviar alerta" e "Resultado" seguem como h2 (o PR diz h3), então a hierarquia pula o nível 3 |
| #54 | DS-03 Marca e paleta, aguardando decisão | `feature/ds-03-marca-paleta` → `feature/front-design-system` | Aberto, rascunho. Só documentação; o registro da decisão está em branco |
| #55 | DS-04 Logotipos SVG da identidade v4 | `feature/ds-04-logotipos` → `feature/ds-03-marca-paleta` | Aberto, rascunho, empilhado no #54. 9 SVGs válidos, sem script nem referência externa |

Os quatro mostram só o check `validate-compose` vermelho (causa registrada na issue #56: as branches são antigas). A base `feature/front-design-system` está 46 commits atrás da `develop` e ainda usa o caminho `sigma-frontend/`; na `develop` a pasta é `frontend/`. As tarefas DS-05 a DS-42 ainda não têm PR.

## Regras que valem para todas as tarefas (C0)

1. Dois temas, desktop 1440 px e celular 390 px, sem corte de texto nem rolagem horizontal da página, com captura antes e depois.
2. Contraste medido no resultado renderizado: texto a 4,5:1 ou mais, borda de campo a 3:1 ou mais, foco visível. Troca de tema sem transição de cores.
3. Todo estado tem texto além da cor. Ausência de dado não é disponibilidade nem zero. Manter "Sem dados recentes", "Até X min", "Sem início real de falha registrado" e a nota de observação parcial.
4. Teclado: Tab, Shift+Tab, Enter e Espaço; link "Ir para o conteúdo"; foco no título ao mudar de área; alvos de pelo menos 44×44 px; tudo em português.
5. `npm run lint`, `npm test` e `npm run build` aprovados, com comando, resultado e commit registrados no PR.
6. Se mudar texto visível ou nome acessível: listar antes e depois, ajustar o teste afetado no mesmo PR e avisar Vinny e Iohan.
7. Não editar `src/api.js`, `useResource.js`, `useEvents.js`, `useActionRequest.js` nem `src/mock/mockApi.js`. Dados fictícios dos campos já contratados podem mudar em `src/mock/data.js`.
8. Extrair só componentes de apresentação, sem refatorar handlers, política de perfil, timers nem autenticação. Aprovações não executa nenhum comando de rede.
9. Para cada tela, cobrir dados normais, carregando, vazio ou inicial, erro e sem permissão, nos dois temas e a 390 px, usando as URLs do mock (`?cenario=vazio|erro|lento|falha-trilha`).

Usuários do mock: `suporte.joyce` (2 áreas), `analista.joyce` (4) e `gestor.joyce` (5), com qualquer senha não vazia. O aceite real e o axe dos E2E ficam com Vinny e Iohan no mesmo PR.

## Protótipo de referência (feito pelo Vinícius)

Fica em `design-system/exemplo/` na branch `feature/tarefas-joyce`, e também em `feature/front-design-system`. É um protótipo navegável feito no FigCraft em 18/10/2026, com 106 telas em 11 páginas.

| Arquivo | Conteúdo |
|---|---|
| `README.md` | Visão geral, o que muda em relação ao painel atual, o que é só front e o que depende de API, ordem sugerida para a Joyce, cuidados antes de copiar |
| `handoff.md` | Páginas, fluxos por perfil (N1, analista, gestor, celular) e regras para a implementação |
| `tokens.css` e `tokens.json` | Cores exportadas nos modos claro e escuro |
| `MASTER.md` | Regras visuais de uma versão experimental anterior (17/10); os caminhos citados não existem no repositório |
| `review.html` e `previews/` | Galeria e uma imagem por tela |
| `sigma-fluxos.figcraft` | Arquivo editável (precisa do FigCraft 0.7) |

Diferenças que o próprio README do protótipo aponta em relação ao painel atual:

| Tema | Painel atual | Protótipo |
|---|---|---|
| Navegação | Abas horizontais | Menu lateral com ícones; menu expansível abaixo de 1024 px |
| Fonte | `system-ui` | Segoe UI, com `system-ui` de reserva |
| Cor principal | `#12568e` e `#91caff` | `#1D4ED8` (claro) e `#60A5FA` (escuro) |
| Estados | Badge com borda colorida | Etiqueta com fundo suave e texto |
| Celular | Tabelas com rolagem horizontal | Tabelas viram cartões; detalhe em abas |
| Botões | Raio 6 px | Raio 8 px, altura 44 px, variante destrutiva vermelha |
| Espaçamento | Sem escala formal | 4, 8, 12, 16, 24, 32, 48 |

Ordem que o README do protótipo sugere para a Joyce: fundação (cores, fonte, espaço, botões), estrutura (menu lateral, cabeçalho, etiquetas), telas que já têm dados (Saúde, Incidentes, Aprovações, Auditoria, Diagnóstico) e, por último, as telas que dependem de API nova. O protótipo não tem a área de Aprovações "quatro olhos", que continua obrigatória no painel.

## Divergências já registradas na conferência do backlog

O próprio backlog lista pontos em que documentos e código não coincidem. Em resumo:

- O guia de instalação manda trocar para a `develop`, mas ela não tinha `design-system` nem `src/mock` na data da conferência.
- O README do protótipo diz que sessão expirada e coleta atrasada são reproduzíveis com `?cenario=`; o mock só trata `vazio`, `erro`, `lento` e `falha-trilha`.
- O que funciona no mock não prova o servidor real: o mock não valida expiração de token, e `/api/alertas` só generaliza IPv4 para /24.
- Usuários não estão só em memória: com PostgreSQL configurado, a identidade vem de `PostgresIdentityStore`. `GET /api/usuarios` devolve só nomes.
- `PATCH /api/eng/alvos/{id}` aceita só `{ativo: boolean}`, e não existe `GET /alvos/{id}`.
- O protótipo prevê fila, assunção e escalonamento a N1; o painel permite apenas Saúde e Diagnóstico a esse perfil, e a mudança exige decisão e servidor.
- No conflito (409) de incidente a tela não recarrega, ao contrário de Aprovações; não corrigir na DS-24, apenas avisar o integrador.
- Confirmados no código: estado desabilitado só com `opacity .65`, h2 internos sob h2 no Diagnóstico, badge sem `nowrap`.
- `MASTER.md` do protótipo cita `tokens.css`, hash/history, storage e transições de 180 ms que o painel atual não tem; é referência histórica.
- O protótipo usa a linha `--line` suave (1,29:1 no claro e 1,64:1 no escuro) e o seletor `data-sigma`; o código usa `data-theme=light`. Não importar o `tokens.css` bruto.
- Cores vivas da identidade visual (`#0EA5E9`, `#1AB2FF`, verdes) não passam como texto branco ou texto pequeno sobre branco (2,4 a 2,8:1).
- O protótipo tem 106 quadros em 11 seções, e a pasta `previews` tem 107 PNG (`account.png` extra). Contar estados, não páginas do produto.
- Aprovações não existe no protótipo, mas é obrigatória.
- `ApprovalItem` tem estado, timer e submitter; extrair o visual sem reescrever expiração e decisão (DS-27).
- Resolver incidente não tem confirmação; aplicar confirmação muda interação e fica fora do escopo autônomo, a decidir por Vinny e Iohan.

O backlog também registra que não foi rodada a aplicação nem o CI nessa conferência, e que a evidência de cada tarefa precisa vir do próprio PR.
