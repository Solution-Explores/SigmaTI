# Prévia — atualização do Trello em 21/10/2026

Fuso dos marcos: UTC−4. Datas do cronograma da demo são combinadas; datas posteriores da Joyce são propostas, sujeitas à disponibilidade e revisão. Sem conclusão automática por cadastro.

Etiquetas a criar/reutilizar: Demonstração 24/10; Front · Design system; Data proposta; Bloqueado · Integração; Pós-demo; Marco de entrega. Preservar etiquetas anteriores, corrigindo classificação claramente inadequada quando necessário.

Modelo das histórias: Como [perfil ou integrante], quero [objetivo], para [resultado]. Cada cartão contém responsável, revisor, issue/PR, dependências, critério e comentário datado com situação real.

Comentário #6: [Certo] 21/10: PR #43 aberto em 8662ea9, CI verde; auditoria concorrente 7/7 e candidato conjunto 489/489. Como operador autenticado, quero ações autorizadas e auditoria íntegra, para rastrear login/logout com segurança. Revisão independente por Iohan até 22/10 às 8h; Vinny integra em 22/10 após tratar achados. Validado em VM; aceite final em 23/10. Ainda não há aprovação independente nem merge confirmado. https://github.com/Solution-Explores/SigmaTI/issues/6 https://github.com/Solution-Explores/SigmaTI/pull/43

Comentário #8: [Certo] 21/10: PR #44 aberto em ddd4840, alvo fix/base-issues. Como equipe de operação, quero detectar quedas e receber SSE sem acumular atraso, para reagir ao incidente. Baseline0/5→candidato5/5,489/489,atraso0,093396s,erros0. Vinny altera alvo somente depois do merge #43; revisão Iohan em22/10 à noite; integração/aceite em23/10. Não houve aceite final. https://github.com/Solution-Explores/SigmaTI/issues/8 https://github.com/Solution-Explores/SigmaTI/pull/44

Plano Joyce: cadastrar DS-01–DS-42 do plano local feature/tarefas-joyce@963efd5, sem push/PR. DS-01–34: trabalho de front/documentação; DS-35–42: bloqueados pelas dependências API-01–08. Vínculos #15 e #31 como referência e coordenação; #15 original encerrada não significa redesign entregue. Revisor de front: Vinny; revisão de integração: Iohan. Não assumir trabalho iniciado sem registro da Joyce.
# Backlog do design system — Joyce

**Base conferida em 21/10/2026:** `feature/design-system-joyce@22adfdf960fe62113e3a7f717f1bed8a45198ed5`. O material ainda não está na `develop` consultada (`8cb1e23`). Este documento planeja trabalho; não declara código implementado, testes aprovados nesta edição ou aprovação de uma identidade.

[Certo] A referência visual é o protótipo, mas o contrato vigente vem do código. **34 tarefas podem avançar sem API nova; 8 tarefas condicionais ficam bloqueadas pela integração.** Não tentar reproduzir as 106 telas como 106 páginas. As decisões de marca são entregas de documento/assets de referência; a aplicação ao produto começa depois.

Responsável pelas tarefas de apresentação: **Joyce**. Vinny coordena prioridade/base e indica o revisor independente entre Vinny/Iohan, diferente de quem fez a entrega. A Joyce não precisa instalar Python, Docker ou PostgreSQL para o backlog autônomo.

## Como usar e entregar

- Uma tarefa por branch/PR pequeno, em ordem de dependências. **P**: até meio dia; **M**: até 1 dia. Não há tarefa G. Se o escopo ultrapassar1 dia, divida antes de iniciar, sem juntar tarefas para compensar espera de revisão.
- Não há data final confirmada. O campo **Prazo** fica vazio em cada fase; a sequência de duas semanas abaixo não é compromisso de calendário nem presume disponibilidade integral.
- Antes de iniciar uma tarefa, Vinny confirma se o material/mock já entrou em `develop`. Se ainda não entrou, usar a base de trabalho indicada por ele e não apontar um PR de código sem mock para uma base que não o contém. Não copiar arquivos de integração para resolver a diferença.
- Criar a branch da tarefa a partir da base autorizada; registrar escopo, dependências, capturas e verificação no PR conforme [fluxo do TCC](../../../guias/fluxo-de-trabalho-tcc.md). Não incorporar a reorganização futura `backend/frontend` sem atualizar este plano.
- Nesta entrega do plano: somente este arquivo e o link no README; commit local em `feature/tarefas-joyce`. **Sem issues, PR ou push sem aprovação do Vinny.** Os rascunhos do apêndice não são issues criadas.
- Arquivos `src/...` abaixo são relativos a `sigma-frontend/`. `design-system/...`, `DESIGN.md` e `doc/...` são relativos à raiz.

## C0 — aceite obrigatório em todas as tarefas

Cada tarefa herda integralmente este checklist, inclusive as documentais (nelas conferir pranchas/assets e o painel que serve de referência; não fingir que a decisão já entrou no aplicativo):

1. **Dois temas, desktop 1440 px e celular 390 px**, sem corte de texto nem rolagem horizontal da página. Para tabelas ainda não convertidas, rolagem localizada e acessível. Evidenciar com captura antes/depois ou prancha da decisão.
2. **Contraste medido:** texto≥4,5:1; borda funcional de campo≥3:1; foco visível sobre superfícies adjacentes. Medir o resultado renderizado, inclusive hover e composição de disabled; não usar opacidade como único sinal. Não copiar a borda fraca do protótipo. Tema troca **sem transição de cores**.
3. Estado sempre tem texto além da cor. Ausência de dado não é disponibilidade nem zero. Preservar **“Sem dados recentes”**, **“Até X min”**, **“Sem início real de falha registrado”**, a nota de observação parcial e a separação das trilhas.
4. Teclado: Tab/Shift+Tab, Enter/Espaço, foco visível, link Ir para o conteúdo e foco no título ao mudar de área. Alvos interativos de pelo menos 44×44 px; nomes acessíveis, labels e hierarquia válidos. Manter tudo em português.
5. Executar em `sigma-frontend/`: **`npm run lint`, `npm test` e `npm run build`**, todos aprovados, sem ignorar testes/assertivas para obter verde. Guardar comando/resultado/commit no PR. Documentação também registra a conferência da base; não precisa inventar testes novos que só espelhem a implementação.
6. Se mudar texto visível/nome acessível, **listar antes → depois, ajustar o teste afetado no mesmo PR e avisar Vinny/Iohan**. Há seletores por texto, papel, quantidade de botões e região; mudar semântica também pode afetá-los. Não basta declarar que “é só CSS”.
7. Preservar contrato e regras: não editar **`src/api.js`, `useResource.js`, `useEvents.js`, `useActionRequest.js` ou `src/mock/mockApi.js`**. Pode ajustar dados fictícios dos campos já contratados em `src/mock/data.js` para nomes longos, ausência de valor e estados. Sem campos futuros inventados para liberar uma tela.
8. Extrair componentes **só de apresentação**: callbacks e props atuais entram sem alteração; não refatorar os handlers, a política de perfil, timers de atualização/cancelamento ou fluxo de autenticação. Nenhum comando de rede é executado por Aprovações.

9. Para cada tela, cobrir dados normais, carregando, vazio ou estado inicial, erro e sem permissão nos dois temas e a 390 px. Usar as URLs existentes; quando o mock não alcançar o estado, identificar a fixture/teste de apresentação no PR. Não fabricar um cenário de URL. Login usa formulário vazio/credenciais inválidas em vez de lista vazia; Diagnóstico usa resultado inicial em vez de lista vazia.

**Verificação com integração:** os E2E existentes em `e2e/` e `e2e-operational/` iniciam Python/API, e os operacionais precisam de PostgreSQL e dados preparados. Joyce roda os três comandos acima e verifica o mock manualmente; Vinny/Iohan executam o aceite real/axe dos E2E no mesmo PR. Não prometer que `npm run test:e2e:operational` funciona sozinho em `dev:mock`. Para estados não alcançáveis no mock, usar testes de apresentação com props e `vi.mock` nas dependências, sem editar os hooks de produção; isso não comprova o servidor.

## Matriz do mock, sem rotas de tela inventadas

Rode `npm ci` uma vez e `npm run dev:mock`. A origem padrão é `http://localhost:5173`; se o Vite escolher outra porta, substitua a origem nas URLs. **Nas tarefas, `/` significa essa URL completa**; as áreas são escolhidas pelos botões após o login, não por `/saude` ou `/incidentes`.

| URL | Verificação real no código |
|---|---|
| `http://localhost:5173/` | Dados normais e ações existentes; tema começa escuro. |
| `http://localhost:5173/?cenario=vazio` | Listagens vazias e trilha com 0 entradas; Diagnóstico não é lista. |
| `http://localhost:5173/?cenario=erro` | 503 operacional e falha no SSE; **login continua permitido**. |
| `http://localhost:5173/?cenario=lento` | Cada requisição do mock espera 2,5 s; SSE tem espera própria de 300 ms. |
| `http://localhost:5173/?cenario=falha-trilha` | Trilha com integra=false; observar como Gestor em Auditoria. |

Usuários: **`suporte.joyce`**, **`analista.joyce`**, **`gestor.joyce`**, qualquer senha **não vazia**. Nome sem prefixo válido testa login inválido. Para quatro olhos, **`analista.a` → Sair → `gestor.b` sem recarregar**: o estado do mock é compartilhado pelo módulo nessa página. Recarregar perde sessão e mutações. Não usar duas abas para compartilhar pedidos do mock: cada aba tem estado independente. No cenário vazio, a lista permanece vazia mesmo depois de criar um pedido.

**Sem permissão:** N1 vê 2 áreas, Analista 4, Gestor 5; menu oculto não é um cartão “sem permissão”. Verificar 403 em componentes/fixtures, usando a mensagem existente e preservando RBAC; não há `?cenario=sem-permissao`. Também não existem URLs para sessão expirada, coleta atrasada, IA indisponível ou bloqueio LGPD. Não adicionar essas capacidades ao mock por conta própria.

## Ordem e capacidade

| Fase | Tarefas | Total | Prazo |
|---|---|---:|---|
|0 · Ambientação|DS-01–DS-02|2||
|1 · Decisões de marca (documentos)|DS-03–DS-05|3||
|2 · Fundação|DS-06–DS-08|3||
|3 · Componentes|DS-09–DS-15|7||
|4 · Estrutura|DS-16–DS-19|4||
|5 · Telas com dados existentes|DS-20–DS-31|12||
|6 · Fechamento|DS-32–DS-34|3||
|Condicionais de integração|DS-35–DS-42|8|não agendadas|

[Provável] Os tamanhos P/M são estimativas de escopo para uma pessoa; não são prazo contratado.

**Primeiras duas semanas, sem datas:** semana 1: DS-01 → 02 → 03 → 04 → 05 (≈3,5 dias de execução estimada, reservar restante para decisão/revisão). Semana 2: DS-06 → 07 → 08 → 09 → 10 (≈3,5 dias estimados + revisão). Se marca/base não estiverem aprovadas, registrar bloqueio, sem escolher paleta silenciosamente. Não assumir que isso ocupa a disponibilidade real da Joyce; Vinny ajusta a sequência. Depois: DS-11–15, DS-16–19, DS-20–31 e fechamento. DS-35–42 não entram nas duas semanas sem os respectivos gates.


## Fase 0 · Ambientação

**Prazo:** __________

### DS-01 — Percorra o mock e registre a matriz de perfis

- **Objetivo:** Conhecer as seis telas e reconhecer o que cada perfil realmente pode ver antes de redesenhar.
- **Arquivos prováveis:** design-system/evidencias/ambientacao.md; src/mock/data.js apenas se precisar de nomes longos.
- **Passos:** Instale com npm ci; rode npm run dev:mock; entre e saia em cada perfil; percorra todos os cenários; leia a galeria review.html e compare desktop/celular; anote dúvidas sem alterar o mockApi.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Matriz com 2/4/5 áreas para N1/Analista/Gestor, todas as cinco URLs abaixo e capturas iniciais. Distinguir erro de login de erro operacional; registrar o limite dos cenários e o estado atual dos três comandos.
- **Como verificar no mock:** suporte.joyce, analista.joyce e gestor.joyce; /, /?cenario=vazio, /?cenario=erro, /?cenario=lento e /?cenario=falha-trilha. Use qualquer senha não vazia.
- **Dependências:** nenhuma; ter a base/material e Node compatíveis. **Tamanho:** P. **Rótulos sugeridos:** front, documentação.

### DS-02 — Corrija a hierarquia de títulos do Diagnóstico

- **Objetivo:** Permitir que o leitor de tela entenda as seções do diagnóstico, sem alterar formulário ou resultado.
- **Arquivos prováveis:** src/Diagnostic.jsx; src/Diagnostic.test.jsx (novo teste de apresentação, se necessário).
- **Passos:** Mantenha o h2 da área em Operations; transforme Enviar alerta/Resultado em h3 e os títulos internos em h4; preserve IDs e aria-labelledby; confira a navegação por títulos.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Uma única hierarquia h1 → h2 → h3 → h4, IDs válidos, mesmos textos e mesmo envio. C0; sem mudança de nomes acessíveis esperada; conferir seletores de heading existentes. Este é o primeiro PR pequeno de interface.
- **Como verificar no mock:** suporte.joyce em /; botão Diagnóstico; depois /?cenario=lento e /?cenario=erro, enviando o formulário.
- **Dependências:** DS-01 **Tamanho:** P. **Rótulos sugeridos:** front, acessibilidade.

## Fase 1 · Decisões de marca — entregas documentais

**Prazo:** __________

### DS-03 — Escolha a variante da marca e uma paleta oficial

- **Objetivo:** Definir uma identidade coerente sem confundir a marca com disponibilidade dos serviços.
- **Arquivos prováveis:** design-system/identidade-visual/decisoes.md (novo); identidade-visual/README.md.
- **Passos:** Compare azul/verde nos JPGs, descrição original e tokens do protótipo; escolha uma fonte de cores e justifique ajustes de acessibilidade; desenhe papéis de marca, informação, bom, atenção, erro e desconhecido; peça decisão visual de Vinny.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Documento, sem CSS de produção: variante escolhida, tabela de cores claro/escuro e contraste de cada par; verde de marca distinto do estado Disponível; desconhecido neutro. C0 em pranchas e no painel atual como referência, sem alegar aplicação da escolha.
- **Como verificar no mock:** gestor.joyce em / e /?cenario=vazio; compare os estados da Saúde com as pranchas de marca nos dois temas.
- **Dependências:** DS-01, DS-02 **Tamanho:** M. **Rótulos sugeridos:** design-system, documentação.

### DS-04 — Entregue o logotipo vetorial para os dois temas

- **Objetivo:** Disponibilizar uma marca legível, sem o fundo opaco dos JPGs, para uso futuro no cabeçalho.
- **Arquivos prováveis:** design-system/identidade-visual/logo-claro.svg, logo-escuro.svg, simbolo.svg e README.md.
- **Passos:** Redesenhe a variante aprovada em vetor; mantenha fundo transparente e viewBox; converta lettering em curvas ou documente fonte/licença; inclua usos claro/escuro e tamanho mínimo; não substitua assets do aplicativo ainda.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); SVGs sem scripts, links externos ou texto cortado; versões consistentes em prancha de 390 px e desktop; nome SigmaTI legível e acessível no exemplo de uso. C0; entrega de documentação/assets de referência, não mudança no front.
- **Como verificar no mock:** gestor.joyce em / como comparação de cabeçalho; abrir SVGs e pranchas locais, claro/escuro, sem rota nova.
- **Dependências:** DS-03 **Tamanho:** M. **Rótulos sugeridos:** design-system, documentação, marca.

### DS-05 — Defina a fonte e os direitos de uso

- **Objetivo:** Garantir leitura consistente sem depender de uma fonte remota nem de licença presumida.
- **Arquivos prováveis:** design-system/identidade-visual/tipografia.md (novo); identidade-visual/README.md.
- **Passos:** Compare system-ui e a pilha Segoe UI do protótipo; escolha fonte e fallbacks; registre origem/licença se houver arquivo redistribuído; compare acentos, números e nomes longos; mantenha lettering do logo separado da fonte da interface.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Documento com pilha completa, pesos e estratégia local. Segoe UI instalada pode ser fallback; não redistribuir seu arquivo como se fosse livre. C0 em amostras, sem importar fonte remota ou alterar index.css nesta fase.
- **Como verificar no mock:** gestor.joyce em /, Saúde e Incidentes; use src/mock/data.js apenas para nomes extensos na avaliação visual.
- **Dependências:** DS-03 **Tamanho:** P. **Rótulos sugeridos:** design-system, documentação, tipografia.

## Fase 2 · Fundação

**Prazo:** __________

### DS-06 — Centralize os tokens sem mudar a aparência

- **Objetivo:** Dar à equipe um único lugar para ajustar a aparência sem criar novas versões de cada cor.
- **Arquivos prováveis:** src/styles/tokens.css (novo); src/App.css; src/index.css; DESIGN.md apenas para apontar a fonte.
- **Passos:** Copie os valores vigentes para tokens.css; importe uma vez; preserve .app-surface e data-theme=light; mantenha nomes antigos como aliases quando necessário; remova definições duplicadas do CSS de execução.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Antes/depois visualmente iguais; um arquivo canônico para valores de execução, sem hex duplicado por componente. C0; documentação e exportações do protótipo são derivadas/referência, não outra fonte normativa.
- **Como verificar no mock:** gestor.joyce em /; percorrer todas as áreas e alternar temas; /?cenario=erro e /?cenario=falha-trilha.
- **Dependências:** DS-03, DS-04, DS-05 **Tamanho:** P. **Rótulos sugeridos:** design-system, front.

### DS-07 — Aplique as escalas de espaço e tipografia aprovadas

- **Objetivo:** Melhorar ritmo de leitura e alinhamento, inclusive com nomes compridos e números de métricas.
- **Arquivos prováveis:** src/styles/tokens.css; src/App.css; src/index.css.
- **Passos:** Defina tokens para escala de espaço e tamanhos/pesos; aplique a fonte da DS-05; substitua valores repetidos nos seletores existentes, sem reorganizar páginas; preserve algarismos tabulares e quebra de texto.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Títulos, rótulos e conteúdo com escala documentada; sem truncar rótulos/valores a 390 px ou com zoom; foco e controle não ficam menores. C0; textos e seletores visíveis preservados.
- **Como verificar no mock:** gestor.joyce em /, Incidentes e Aprovações; suporte.joyce em /?cenario=vazio.
- **Dependências:** DS-06 **Tamanho:** P. **Rótulos sugeridos:** design-system, front, tipografia.

### DS-08 — Implemente os dois temas e meça o contraste

- **Objetivo:** Aplicar a paleta decidida mantendo leitura e estados confiáveis em claro e escuro.
- **Arquivos prováveis:** src/styles/tokens.css; src/App.css; design-system/identidade-visual/contraste.md (novo).
- **Passos:** Mapeie a DS-03 para tokens semânticos; diferencie borda funcional de separador decorativo; meça pares renderizados, hover e desabilitado; registre tabela e remova qualquer transição de cor.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); C0, com texto≥4,5:1 e borda de campo≥3:1 em cada tema; foco visível contra superfícies adjacentes; nenhum valor de contraste copiado sem medição. Troca imediata, preservando tema inicial escuro e estado em memória.
- **Como verificar no mock:** gestor.joyce em /, /?cenario=erro e /?cenario=falha-trilha; percorrer campos/botões e alternar temas antes das medições.
- **Dependências:** DS-07 **Tamanho:** M. **Rótulos sugeridos:** design-system, front, acessibilidade.

## Fase 3 · Componentes

**Prazo:** __________

### DS-09 — Extraia o botão com estados completos

- **Objetivo:** Distinguir ação principal, secundária, destrutiva, ocupada e desabilitada sem depender só de opacidade.
- **Arquivos prováveis:** src/components/Button.jsx e Button.css (novos); src/App.jsx; src/App.css; teste do componente.
- **Passos:** Extraia o botão nativo mantendo type, disabled, value e eventos; crie variantes; migre primeiro Entrar/Sair; documente a variante destrutiva e um padrão proposto de confirmação, sem interceptar Resolver incidente.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); estado desabilitado tem forma/texto de contexto e não aceita clique; destrutivo identificado por texto, sem afirmar nova confirmação implementada; type=submit/value preservados para Aprovações. Não mudar textos; se mudar, ajustar seletores/testes no mesmo PR e avisar integração.
- **Como verificar no mock:** gestor.joyce em / e /?cenario=lento para Entrando/Sair; demais variantes com props no teste visual do componente, sem alterar mockApi.js.
- **Dependências:** DS-08 **Tamanho:** M. **Rótulos sugeridos:** design-system, front, acessibilidade.

### DS-10 — Padronize etiquetas de estado e severidade

- **Objetivo:** Permitir reconhecer disponibilidade, prioridade e orçamento sem interpretar apenas uma cor.
- **Arquivos prováveis:** src/components/Badge.jsx e Badge.css; HealthContent em src/OperationalPages.jsx; src/App.css; teste de apresentação.
- **Passos:** Extraia o badge da Saúde; defina variantes por papel; ofereça P1/P2/P3 e estados de incidente para reutilização posterior; adicione nowrap sem reduzir fonte; trate valores desconhecidos com texto neutro.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Sem dados recentes fica inteiro sem estourar 390 px; unknown/inactive não usam cor de disponível; P1/P2/P3 mantêm o código, sem inventar equivalência clínica. Textos de negócio preservados.
- **Como verificar no mock:** suporte.joyce em /, Saúde, contendo up/down/unknown/inactive; severidades via fixtures do componente, antes da adoção em Incidentes.
- **Dependências:** DS-09 **Tamanho:** P. **Rótulos sugeridos:** design-system, front, acessibilidade.

### DS-11 — Extraia os painéis e seus títulos semânticos

- **Objetivo:** Organizar grupos de conteúdo com contorno e hierarquia consistentes.
- **Arquivos prováveis:** src/components/Panel.jsx e Panel.css; src/Diagnostic.jsx; src/App.css; testes de apresentação.
- **Passos:** Crie invólucro visual que aceite section/article/div e nível de heading explícito; migre apenas os dois painéis do Diagnóstico; mantenha aria-labelledby e regiões vivas onde estão.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); resultado e formulário mantêm suas associações e a hierarquia da DS-02; não acrescentar landmarks ou aria-live duplicados. Mesmo conteúdo e eventos de envio.
- **Como verificar no mock:** suporte.joyce em /, Diagnóstico; /?cenario=lento para resultado ocupado e /?cenario=erro para erro.
- **Dependências:** DS-10 **Tamanho:** P. **Rótulos sugeridos:** design-system, front, acessibilidade.

### DS-12 — Extraia a estrutura da tabela acessível

- **Objetivo:** Reutilizar tabelas com legenda, cabeçalhos e rolagem localizada sem perder a leitura por teclado.
- **Arquivos prováveis:** src/components/DataTable.jsx e DataTable.css; HealthContent em src/OperationalPages.jsx; src/App.css.
- **Passos:** Extraia apenas o invólucro/estilos da tabela de Saúde; preserve caption, scope=col/row, chaves e região focável; deixe renderização de células nas páginas; não crie busca/paginação nem cartões nesta tarefa.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); dados e ordem de colunas iguais; rolagem restrita à região, sem rolagem horizontal da página; cada célula conserva contexto de cabeçalho. A mudança para cartões fica na DS-22.
- **Como verificar no mock:** suporte.joyce em /, Saúde, nos dois temas a 390 px e desktop; /?cenario=vazio para conferir ausência de tabela.
- **Dependências:** DS-11 **Tamanho:** M. **Rótulos sugeridos:** design-system, front, acessibilidade.

### DS-13 — Extraia os alertas e mensagens de ação

- **Objetivo:** Dar destaque consistente a erro, informação e sucesso sem anunciar falsos resultados.
- **Arquivos prováveis:** src/components/Alert.jsx e Alert.css; ResourceState em src/OperationalPages.jsx; src/Diagnostic.jsx; testes.
- **Passos:** Extraia as caixas de erro; aceite role e conteúdo via props; mantenha retry como callback recebido; preserve textos oriundos de api.js e locais das ações; evite anúncios duplicados na atualização periódica.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); erro continua role=alert, sucesso role=status; Tentar novamente chama o mesmo refresh. Não traduzir mensagens editando api.js; mudança de rótulo local exige teste ajustado no PR e aviso à integração.
- **Como verificar no mock:** analista.joyce em /?cenario=erro, abrir Incidentes e tentar novamente; / normal para feedback de Reconhecer.
- **Dependências:** DS-12 **Tamanho:** P. **Rótulos sugeridos:** design-system, front, acessibilidade.

### DS-14 — Extraia estados vazios e de carregamento

- **Objetivo:** Explicar por que não há conteúdo e o que fazer, sem confundir carregamento, falha e lista vazia.
- **Arquivos prováveis:** src/components/EmptyState.jsx e LoadingState.jsx; HealthContent/ResourceState em src/OperationalPages.jsx; testes.
- **Passos:** Extraia os textos já existentes; use o mesmo loading do hook; adicione indicador decorativo apenas se ajudar; preserve instruções específicas por tela e não invente contagem zero durante carregamento.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); carregamento com texto e role=status; vazio não afirma disponibilidade; botão não promete cadastro indisponível para N1. Preservar texto atual; qualquer revisão de cópia atualiza testes no mesmo PR e avisa integração.
- **Como verificar no mock:** suporte.joyce em /?cenario=vazio e /?cenario=lento, Saúde; gestor.joyce em /?cenario=erro para comparar erro.
- **Dependências:** DS-13 **Tamanho:** P. **Rótulos sugeridos:** design-system, front, acessibilidade.

### DS-15 — Extraia campos e mensagens de formulário

- **Objetivo:** Manter rótulos, ajuda e validação claros nos formulários, inclusive quando desabilitados.
- **Arquivos prováveis:** src/components/Field.jsx e Field.css; src/Diagnostic.jsx; src/App.css; testes.
- **Passos:** Extraia apresentação de label/ajuda/erro, mantendo inputs nativos e controle de valor nas páginas; migre só os campos do Diagnóstico; preserve htmlFor, IDs, required e disabled; não reescreva handlers.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); borda≥3:1, foco e rótulo visíveis; ajuda/erro associados por aria-describedby quando presentes; não inventar erro da API nem esconder validação nativa. Campos e textos da requisição iguais.
- **Como verificar no mock:** suporte.joyce em /, Diagnóstico com campos vazios e preenchidos; /?cenario=lento para campos ocupados; /?cenario=erro para falha.
- **Dependências:** DS-14 **Tamanho:** M. **Rótulos sugeridos:** design-system, front, acessibilidade.

## Fase 4 · Estrutura

**Prazo:** __________

### DS-16 — Monte o cabeçalho com marca e papel por extenso

- **Objetivo:** Identificar o sistema, a pessoa conectada e suas capacidades sem códigos internos no cabeçalho.
- **Arquivos prováveis:** src/App.jsx; src/components/AppHeader.jsx; src/assets/brand/ (copiar SVGs aprovados); src/App.css; testes.
- **Passos:** Integre SVGs DS-04; crie mapa somente de apresentação para os três papéis; preserve session.papel nas verificações; mantenha botões de tema/Sair e link de salto; confira nomes extensos.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); mostra Suporte N1/Analista de Redes/Gestor de TI; imagem tem alternativa adequada sem repetir o título; sessão não vai a storage; sem conta/menu inexistente. Testes de texto ajustados no mesmo PR se rótulos mudarem, com aviso.
- **Como verificar no mock:** suporte.joyce, analista.joyce e gestor.joyce em /; alternar tema e sair em cada perfil.
- **Dependências:** DS-15 **Tamanho:** P. **Rótulos sugeridos:** front, design-system.

### DS-17 — Organize a navegação lateral no desktop

- **Objetivo:** Facilitar alternância entre as áreas existentes sem copiar permissões ou páginas futuras do protótipo.
- **Arquivos prováveis:** src/Operations.jsx; src/components/SideNav.jsx; src/App.css; src/OperationalPages.test.jsx.
- **Passos:** Apresente as mesmas entradas visíveis em uma lateral a partir do breakpoint decidido (referência1024 px); conserve pages/level e setPage; mantenha botões e aria-current; preserve o foco no h2 ao trocar área.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); navegação continua com 2/4/5 botões por perfil e mesma ordem; Aprovações não desaparece; nenhum link para Relatórios/Usuários/Equipamentos ainda. Sem router, hash ou permissões novas.
- **Como verificar no mock:** três usuários em /; percorrer áreas no desktop e verificar foco; a 390 px manter navegação utilizável antes da DS-18.
- **Dependências:** DS-16 **Tamanho:** P. **Rótulos sugeridos:** front, design-system, acessibilidade.

### DS-18 — Adapte o menu para celular com foco previsível

- **Objetivo:** Permitir navegar a 390 px sem uma fileira de abas ocupar a tela.
- **Arquivos prováveis:** src/components/SideNav.jsx; src/Operations.jsx; src/App.css; teste de navegação.
- **Passos:** Crie botão Abrir menu com aria-expanded/controls; prefira expansão no fluxo, sem modal; feche após seleção e devolva foco adequadamente ao cancelar; mantenha a filtragem por perfil; cubra teclado e resize.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); abrir/fechar por teclado, Escape devolve foco ao acionador, seleção leva ao título; itens recolhidos não recebem foco; 2/4/5 opções presentes quando aberto. Novo rótulo entra nos testes no mesmo PR; avisar integração para E2E que não abria menu.
- **Como verificar no mock:** suporte.joyce, analista.joyce e gestor.joyce em / a 390 px; abrir menu, trocar área, alternar tema e voltar ao desktop.
- **Dependências:** DS-17 **Tamanho:** M. **Rótulos sugeridos:** front, acessibilidade, responsivo.

### DS-19 — Compacte os avisos sem esconder a demonstração

- **Objetivo:** Liberar espaço no topo mantendo explícitos dados fictícios e API simulada.
- **Arquivos prováveis:** src/App.jsx; src/components/DemoNotice.jsx; src/App.css; testes.
- **Passos:** Agrupe os dois avisos em um bloco compacto; mantenha instruções do mock em detalhe expansível acessível; use a constante MOCK existente; diferencie aviso de simulação e estado de conexão SSE.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); aviso de dados fictícios sempre visível; mock indicado só quando MOCK está ativo, sem vazar instrução de senha para produção; conteúdo não cobre menu/cabeçalho a 390 px. Cópia alterada deve ser listada, testada no mesmo PR e comunicada à integração.
- **Como verificar no mock:** suporte.joyce em / e /?cenario=erro; confirmar que Modo mock não vira indicador de coleta saudável.
- **Dependências:** DS-18 **Tamanho:** P. **Rótulos sugeridos:** front, design-system.

## Fase 5 · Telas com dados existentes

**Prazo:** __________

### DS-20 — Aplique o visual novo ao Login

- **Objetivo:** Tornar entrada e falhas de credencial legíveis e previsíveis sem criar cadastro público.
- **Arquivos prováveis:** src/App.jsx; src/components/LoginPanel.jsx; src/App.css; teste de apresentação.
- **Passos:** Componha Panel, Field, Button e Alert; preserve autocomplete, required, bloqueio durante login e limpeza da senha; mantenha sequência login → me e logout nas falhas; não refatore autenticação.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); vazio/não preenchido validado, Entrando… e erro visíveis; usuário sem prefixo válido retorna erro; /?cenario=erro não simula falha de login. Rótulos Usuário/Senha/Entrar preservados; mudanças exigem E2E ajustado junto e aviso.
- **Como verificar no mock:** / sem sessão; suporte.joyce com senha não vazia, nome invalido.visual para erro, /?cenario=lento para demora de login; repetir retorno por Sair.
- **Dependências:** DS-19 **Tamanho:** M. **Rótulos sugeridos:** front, design-system, acessibilidade.

### DS-21 — Reorganize a Saúde sem reinterpretar os dados

- **Objetivo:** Priorizar situação, última medição e orçamento preservando a diferença entre dado real e lacuna de observação.
- **Arquivos prováveis:** HealthContent/HealthPage em src/OperationalPages.jsx; src/App.css; src/OperationalPages.test.jsx.
- **Passos:** Adote os componentes; destaque os seis estados de serviço do mock; mostre orçamento at_risk com texto, sem deduzir disponibilidade; mantenha todas as seis colunas e textos de limite/cobertura; estados de recurso usam componentes comuns.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Sem dados recentes, Até X min, Observação parcial, SLO não configurado e Sem projeção suficiente preservados; sem número para latência nula; todos os campos atuais continuam acessíveis. Badges de atenção não dependem de cor.
- **Como verificar no mock:** suporte.joyce em /, Saúde; /?cenario=vazio, /?cenario=lento e /?cenario=erro; comparar orçamento completo, parcial e esgotado.
- **Dependências:** DS-20 **Tamanho:** M. **Rótulos sugeridos:** front, design-system.

### DS-22 — Transforme a Saúde em cartões no celular

- **Objetivo:** Ler cada serviço completo a 390 px sem precisar cruzar seis colunas.
- **Arquivos prováveis:** HealthContent em src/OperationalPages.jsx; src/components/ServiceCard.jsx; src/App.css; teste de apresentação.
- **Passos:** Use o mesmo array de serviços e formatadores; em largura compacta exiba cartão com dl/rótulos para todos os campos; mantenha tabela no desktop; esconda a cópia inativa também da árvore acessível; preserve ordem/IDs.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); mesmas seis informações em tabela e cartão, sem duplicação de anúncio ou foco; nenhuma rolagem lateral da página; nome/host longo quebra, badge não corta. unknown e janela parcial continuam honestos.
- **Como verificar no mock:** suporte.joyce em / a 390 px e1440 px; /?cenario=vazio e /?cenario=lento; nomes longos via src/mock/data.js.
- **Dependências:** DS-21 **Tamanho:** M. **Rótulos sugeridos:** front, responsivo, acessibilidade.

### DS-23 — Traduza tipos e formate durações de incidentes

- **Objetivo:** Ler Latência e 40 min mantendo precisão, amostras e unidade original do contrato.
- **Arquivos prováveis:** src/presentation/formatters.js (novo); IncidentMetrics e cabeçalho da lista em src/OperationalPages.jsx; src/OperationalPages.test.jsx.
- **Passos:** Crie mapa de rótulos de tipo sem renomear campos; apresente durações em s/min/h com regra explícita de arredondamento; trate0, nulo, não finito; preserve detalhe com segundos quando necessário; deixe n=0 sem valor.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); C0;2400 s → 40min,10 s continua10 s,0 s não vira ausência; MTTD n=0 mantém Sem início real de falha registrado. Teste 10 s existente deve continuar válido ou ser ajustado justificadamente no mesmo PR; registrar toda cópia alterada à integração.
- **Como verificar no mock:** analista.joyce em /, Incidentes (MTTR2400 s, MTTA300 s); /?cenario=vazio para métricas n=0; fixtures para0 e decimais.
- **Dependências:** DS-22 **Tamanho:** P. **Rótulos sugeridos:** front, design-system.

### DS-24 — Destaque prioridade e ações dos incidentes no desktop

- **Objetivo:** Distinguir prioridade e ciclo de vida sem misturar falha medida com atendimento.
- **Arquivos prováveis:** IncidentsPage em src/OperationalPages.jsx; src/App.css; testes de apresentação.
- **Passos:** Adote Badge/Table/Alert/Button; mantenha estado derivado de resolvido_em e reconhecido_em; destaque ação disponível e motivo de bloqueio com dados locais; preserve transition e busy; não acrescente confirmação ou assunção.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); P1/P2/P3 e Aberto/Reconhecido/Resolvido textuais; reconhecer/resolver mantêm mesmas chamadas e restrições; sucesso só após resposta. Não prometer refresh no erro 409 que o código não faz. Confirmação destrutiva fica fora do escopo autônomo.
- **Como verificar no mock:** analista.joyce ou gestor.joyce em /, Incidentes; reconhecer primeiro item; tentar resolver outro; /?cenario=lento e /?cenario=erro para feedback.
- **Dependências:** DS-23 **Tamanho:** M. **Rótulos sugeridos:** front, design-system, acessibilidade.

### DS-25 — Adapte os incidentes para cartões no celular

- **Objetivo:** Usar as ações e consultar identificação e detecção sem cortar conteúdo a 390 px.
- **Arquivos prováveis:** IncidentsPage em src/OperationalPages.jsx; src/components/IncidentCard.jsx; src/App.css; testes.
- **Passos:** Reutilize os mesmos itens, formatadores e callbacks; agrupe nome, ID, detecção, estado e ações; preserve estado busy compartilhado; remova a representação inativa do foco/árvore acessível; não crie detalhe ou rota nova.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); informações e disponibilidade das ações equivalentes ao desktop; controles44 px, ID longo quebra; sem duas requisições por clique. N1 continua sem a área, embora o protótipo desenhe fila N1.
- **Como verificar no mock:** analista.joyce em / a 390 px; /?cenario=vazio, /?cenario=lento e /?cenario=erro; suporte.joyce confirma ausência da opção Incidentes.
- **Dependências:** DS-24 **Tamanho:** M. **Rótulos sugeridos:** front, responsivo, acessibilidade.

### DS-26 — Reorganize a criação de solicitações de aprovação

- **Objetivo:** Dar à área obrigatória de Aprovações uma entrada clara para solicitar revisão por outra pessoa.
- **Arquivos prováveis:** ApprovalsPage em src/OperationalPages.jsx; src/App.css; testes.
- **Passos:** Use Panel/Field/Button no details Nova solicitação; mantenha campos ação/perfil mínimo e limites atuais; destaque que a página registra decisões sem executar comandos; alinhe formulário em uma coluna no celular.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); envio mantém acao/papel_minimo, bloqueio durante creating e feedback só após resposta; nada sugere execução de switch/firewall. Textos/IDs atuais preservados ou testes atualizados no mesmo PR com aviso.
- **Como verificar no mock:** analista.a em /, Aprovações → Nova solicitação; /?cenario=lento e /?cenario=erro; /?cenario=vazio mantém criação disponível, mas a listagem desse cenário permanece vazia.
- **Dependências:** DS-25 **Tamanho:** M. **Rótulos sugeridos:** front, design-system, acessibilidade.

### DS-27 — Padronize os cartões de decisão e seus bloqueios

- **Objetivo:** Explicar autoria, expiração e papel insuficiente antes de pedir uma decisão justificada.
- **Arquivos prováveis:** ApprovalItem em src/OperationalPages.jsx; src/App.css; src/OperationalPages.test.jsx.
- **Passos:** Adote Panel/Field/Button/Badge sem alterar own, insufficient, expired ou submitter.value; traduza papel só na apresentação; deixe justificativa e botões próximos no celular; mantenha textos dos motivos e estado ocupado.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); autoaprovação e justificativa vazia bloqueadas; analista não decide exigência de gestor; relógio de expiração preservado; Aprovar/Rejeitar continuam value=approve/reject. Mapa de papel muda a cópia da mensagem: ajustar teste no PR e avisar integração.
- **Como verificar no mock:** analista.a cria em /, sai sem recarregar; gestor.b entra e decide. Para item próprio inicial usar analista.a no fixture solicitante em data.js; expiração/papel gestor via fixtures, sem mockApi.js. /?cenario=lento e /?cenario=erro.
- **Dependências:** DS-26 **Tamanho:** M. **Rótulos sugeridos:** front, design-system, acessibilidade.

### DS-28 — Separe integridade e eventos no visual da Auditoria

- **Objetivo:** Evitar que a integridade da trilha de sondas pareça atestar também os eventos operacionais.
- **Arquivos prováveis:** AuditContent/AuditPage em src/OperationalPages.jsx; src/App.css; testes.
- **Passos:** Use Panel/Alert/Table para as duas seções; destaque contagem sem inferir integridade em trilha vazia; mantenha a nota de armazenamento separado e limite100; preserve as duas buscas e refresh simultâneo.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); C0;128 íntegra versus0 vazia versusfalha são distintos por texto; falha usa role=alert; texto de eventos é escapado, sem HTML injetado; não adicionar hash/âncora que a API não envia.
- **Como verificar no mock:** gestor.joyce em /, Auditoria; /?cenario=falha-trilha, /?cenario=vazio, /?cenario=lento e /?cenario=erro; analista.joyce confirma área ausente.
- **Dependências:** DS-27 **Tamanho:** M. **Rótulos sugeridos:** front, design-system, acessibilidade.

### DS-29 — Apresente eventos de Auditoria em cartões no celular

- **Objetivo:** Ler horário, operador, ação e recurso sem comprimir uma tabela a 390 px.
- **Arquivos prováveis:** AuditContent em src/OperationalPages.jsx; src/components/AuditEventCard.jsx; src/App.css; testes.
- **Passos:** Mapeie os mesmos quatro campos para dl nos cartões; mantenha cabeçalho/limite da seção; quebre identificadores longos; esconda a tabela inativa do foco/leitor de tela.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); dados iguais nas duas representações, sem truncamento silencioso ou anúncios duplicados; eventos vazios não escondem a mensagem da trilha; sem botão de exportação sem API.
- **Como verificar no mock:** gestor.joyce em / a 390 px, Auditoria; /?cenario=vazio e /?cenario=falha-trilha; strings longas/inofensivas via data.js.
- **Dependências:** DS-28 **Tamanho:** P. **Rótulos sugeridos:** front, responsivo, acessibilidade.

### DS-30 — Aplique o visual novo ao formulário do Diagnóstico

- **Objetivo:** Deixar claro o que será enviado e quando a solicitação está em processamento.
- **Arquivos prováveis:** src/Diagnostic.jsx; src/App.css; testes de apresentação.
- **Passos:** Reorganize os componentes existentes mantendo equipamento, IP, descrição, required e payload; preserve bloqueio no envio e cancelamento pelo hook; garanta uma coluna no celular; não crie seletor de incidente ou chat.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Solicitar diagnóstico/Processando… identificáveis; campos e envio únicos; erro de permissão apresentado via fixture de teste, sem alterar api.js. Textos de regra preservados; rótulos alterados exigem teste atualizado e aviso.
- **Como verificar no mock:** suporte.joyce em /, Diagnóstico; enviar em /?cenario=lento e /?cenario=erro; fixtures de ApiError403 para sem permissão, pois não existe URL desse cenário.
- **Dependências:** DS-29 **Tamanho:** M. **Rótulos sugeridos:** front, design-system, acessibilidade.

### DS-31 — Reorganize o resultado e o conteúdo generalizado

- **Objetivo:** Mostrar a resposta da IA como apoio e tornar visível o conteúdo enviado, sem prometer anonimização pelo mock.
- **Arquivos prováveis:** src/Diagnostic.jsx; src/App.css; testes de apresentação.
- **Passos:** Separe estado inicial/ocupado/resultado/erro usando o loading já existente; preserve painel Dados enviados à IA e renderização como texto; mantenha ausência de resultado na falha; use largura flexível para textos longos.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); aria-live/aria-busy preservados; dados_enviados_nuvem visível, sem HTML; não derivar estado novo de string de diagnóstico e não afirmar proteção real de nomes pelo mock. Não criar gráfico, chat ou incidente automático.
- **Como verificar no mock:** suporte.joyce em / enviando dados fictícios; /?cenario=lento e /?cenario=erro; fixture de resultado indisponível para apresentação, já que não existe cenário específico no mock.
- **Dependências:** DS-30 **Tamanho:** P. **Rótulos sugeridos:** front, design-system, acessibilidade.

## Fase 6 · Fechamento

**Prazo:** __________

### DS-32 — Atualize capturas de Login, Saúde e Incidentes

- **Objetivo:** Permitir revisar e comparar as três primeiras telas exatamente como foram implementadas.
- **Arquivos prováveis:** design-system/capturas/ (arquivos dessas telas); design-system/capturas/README.md (novo índice).
- **Passos:** Capture ambas as larguras e temas; acrescente estados vazio/carregando/erro pertinentes; use perfis permitidos e anote commit, viewport, URL e área; elimine exposição de dados reais; não use captura do protótipo como evidência do produto.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); C0;12 imagens base=3 telas×2temas×2larguras e estados adicionais identificados; Login não tem vazio de coleção;390×844 e1440×1000, capturas legíveis sem corte. Registrar resultado dos comandos da branch capturada.
- **Como verificar no mock:** Login sem sessão; suporte.joyce em Saúde; analista.joyce em Incidentes; /, /?cenario=vazio, /?cenario=lento, /?cenario=erro conforme a tela.
- **Dependências:** DS-31 **Tamanho:** M. **Rótulos sugeridos:** documentação, front.

### DS-33 — Atualize capturas de Aprovações, Auditoria e Diagnóstico

- **Objetivo:** Documentar também as áreas obrigatórias que a referência visual omite ou simplifica.
- **Arquivos prováveis:** design-system/capturas/ (arquivos dessas telas); capturas/README.md.
- **Passos:** Capture as duas larguras e temas; registre autoaprovação, perfil insuficiente e expirado com fixtures; capture trilha íntegra/vazia/falha e diagnóstico inicial/ocupado/resultado/erro; identifique simulações de teste separadamente.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); C0;12 imagens base e adicionais nomeadas; ausência de Aprovações no FigCraft não é justificativa para faltar captura. Sem alegar teste de API real ou relógio/SSE a partir de fixture visual.
- **Como verificar no mock:** analista.a/gestor.b em Aprovações, gestor.joyce em Auditoria, suporte.joyce em Diagnóstico; / e quatro cenários documentados, com falha-trilha só na Auditoria.
- **Dependências:** DS-32 **Tamanho:** M. **Rótulos sugeridos:** documentação, front.

### DS-34 — Consolide o design implementado e o estado atual

- **Objetivo:** Entregar uma referência factual da interface implementada e das pendências, sem confundir protótipo com produto.
- **Arquivos prováveis:** DESIGN.md; design-system/02-estado-atual.md; design-system/03-tokens-e-componentes.md; design-system/README.md.
- **Passos:** Atualize tokens/escala/componentes e links das capturas; declare tokens.css canônico; revise os 12 pontos abaixo com evidências; registre decisões e itens bloqueados; peça à integração a atualização de exportações protegidas se aplicável.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); links válidos, descrição coincide com código e nenhum recurso futuro tratado como entregue; tabela de contraste final e comandos reais registrados; duas semanas são ordem sugerida, não data contratada.
- **Como verificar no mock:** gestor.joyce em todas as áreas em /; repetir /?cenario=vazio, erro, lento, falha-trilha em URLs separadas; conferir o documento contra as telas capturadas.
- **Dependências:** DS-33 **Tamanho:** M. **Rótulos sugeridos:** design-system, documentação.

## Divergências e limites encontrados na conferência

[Certo] Conferência estática no SHA da base, mais leitura de capturas, galeria HTML e imagens do protótipo. Não foi rodada a aplicação nem o CI nesta edição documental. O navegador não permitiu `file://`; a galeria foi lida como arquivo, sem contornar o bloqueio. O carregador Impeccable não executou por motor ausente/cache protegido; o contexto foi lido diretamente.

| Fonte/afirmação | Código conferido / diferença | Consequência no plano |
|---|---|---|
|01-instalação manda trocar para develop|A develop consultada não contém design-system nem src/mock; package.json da branch material tem dev:mock.|Confirmar base com Vinny antes do primeiro PR; não abrir mão do mock por seguir o comando antigo.|
|exemplo/README: estados de sessão expirada/coleta atrasada “já reproduzíveis com ?cenario”|mockApi.js só trata vazio, erro, lento, falha-trilha. SSE apenas abre e espera cancelamento, sem publicar incidentes/cursor.|Fixtures para apresentação; integração responsável por novos cenários e testes reais. Não afirmar reconexão/coleta real a partir do mock.|
|README/contrato: o que funciona no mock funciona na API real|O mock não valida expiração real/revogação dos tokens; a ação de decidir não confere expiração/justificativa como o serviço real, embora a UI bloqueie. /api/alertas apenas troca IPv4 por /24, sem anonimizador completo.|Mock comprova apresentação e fluxos simulados, não segurança, anonimização ou equivalência integral. Aceite real fica com integração.|
|exemplo/README: usuários existem “ainda em memória”|main.py → usuario_repo; auth.configure_auth usa PostgresIdentityStore quando configurado, com alternativa em memória para arquivo. GET /api/usuarios devolve só strings.|Não afirmar memória como única persistência nem desenhar papel/ativo que não vem no GET; API-08.|
|exemplo: “PATCH alvos” pode sugerir edição geral; tabela prevê detalhe de equipamento|routers/operational.py aceita apenas {ativo:boolean} no PATCH; não existe GET individual /alvos/{id} nessa base. GET lista e medições/agregados existem.|API-06 integra o existente; edição ampla/detalhe novo exige contrato adicional.|
|Protótipo/handoff oferece fila, assunção, escalonamento a N1|Operations.jsx permite Saúde/Diagnóstico; resumo e reconhecer/resolver exigem Analista. API tem leitura bruta de incidentes para Reader, mas não é o contrato de resumo usado pelo painel.|Preservar 2/4/5 áreas. Mudança de capacidades exige decisão e servidor, não mudar level ou mostrar botão por conta própria.|
|04-fluxos: ao conflito de incidente “tela recarrega”|IncidentsPage só mostra feedback no tratamento do erro 409; não chama refresh aí. ApprovalsPage chama refresh no erro 409.|Não prometer nem corrigir comportamento na DS-24; apontar ao integrador, preservando handlers.|
|02-estado/03-tokens: estado desabilitado, hierarquia e badge|Confirmados: :disabled usa opacity .65; Diagnostic tem h2 internos sob h2; badge não tem nowrap. Os h3 internos do resultado também precisam virar h4.|DS-02, DS-09, DS-10 cobrem o código real, não só o sintoma da captura.|
|MASTER.md do exemplo: tokens.css, hash/history, preferência do sistema/storage e transições de 180 ms|App usa App.css e index.css; tema dark inicial em useState; Operations usa state sem router/hash; testes E2E exigem storage vazio; CSS atual não tem transição.|MASTER é referência histórica. Não copiar storage/router/transição nem tentar usar caminhos que não existem.|
|Protótipo tem --line suave e usa seletor data-sigma=Escuro|Código usa data-theme=light na .app-surface. Contraste recalculado: #DCE3ED/branco=1,292:1; #304157/#111C2E=1,643:1.|Não importar tokens.css bruto; adaptar na DS-08 e separar borda de campo de separador decorativo.|
|Identidade visual oferece cores vivas para ação|Recalculados: branco/#0EA5E9=2,771:1; branco/#1AB2FF=2,371:1; verdes #10B981/#41BA50 sobre branco=2,537/2,511:1.|Escolher pares por tema e medir; não usar texto branco nesses botões ou verde vivo como texto pequeno sobre branco.|
|02-estado: 106 telas/sem identidade definida|A galeria tem 106 elementos article em 11 seções; previews tem 107 PNG, com account.png extra fora dela. Marca JPG chegou depois e ainda não está no App; variantes não aprovadas.|Contar quadros/estados, não páginas do produto; DS-03 decide, DS-04 vetoriza. Aprovações é obrigatória apesar de ausente no protótipo.|
|06-contrato sugere acrescentar campo novo ao mock e usar antes da API|mockApi.js tem lista fechada de rotas e monta respostas específicas; dado novo não cria contrato real nem endpoint.|Restrições desta tarefa prevalecem: só dados visuais de contrato atual; novos recursos ficam bloqueados no apêndice.|
|PRODUCT.md guarda pendência de reexecução após contraste|brief.md registra correção e reexecução local após remoção da transição. CSS confirma ausência de transição; evidência é histórica.|Não anunciar CI novo nem recertificar acessibilidade nesta edição; cobrar revalidação real de cada PR.|
|05-modelagem: todos *Content só props sem comportamento|HealthContent/IncidentMetrics/AuditContent são apresentação; ApprovalItem também tem estado, timer e submitter.value.|Extrair visual sem reescrever expiração/decisão, DS-27; arquivo compartilhado pede PRs sequenciais para evitar conflito.|

Os demais pontos de melhoria do estado atual foram conferidos: avisos separados em App, papel cru em session, tipos e severidade crus, métricas em segundos, tabela de Saúde com 6 colunas, CSS como fonte de execução e Resolver sem confirmação. Nenhuma dessas observações autoriza criar novas regras de negócio.

## Cobertura dos 12 pontos de melhoria

| Ponto de 02-estado-atual | Cobertura |
|---|---|
|1 · Identidade visual|DS-03/04/05 escolhem documentos/assets; DS-08/16 aplicam.|
|2 · Avisos grandes|DS-19 mantém simulação explícita em formato compacto.|
|3 · Papel como código|DS-16 no cabeçalho; DS-27 na explicação do perfil mínimo, sem mudar o enum.|
|4 · Severidade/estado sem hierarquia|DS-10 e DS-24/25; códigos preservados com texto.|
|5 · Tipo latencia cru|DS-23 mapa de apresentação, sem renomear campo.|
|6 · Tempos em segundos|DS-23, com n=0/zero/precisão preservados.|
|7 · Desabilitado por opacidade|DS-09; revalidado nas ações de DS-24/27.|
|8 · Títulos do Diagnóstico|DS-02 cobre h3 e h4 internos.|
|9 · Saúde no celular|DS-22; tabelas de outras áreas em DS-25/29.|
|10 · Badge quebra linha|DS-10, sem truncar o conteúdo.|
|11 · Tokens duplicados|DS-06 canônico, DS-08 valores medidos, DS-34 documentos derivados.|
|12 · Resolver sem confirmação|DS-09 documenta padrão destrutivo; **aplicar confirmação é fora do escopo autônomo** porque muda interação. Vinny/Iohan decidem antes de qualquer implementação; DS-24 preserva o clique atual.|

Para o ponto 12, rascunho de decisão de integração (não criado): **“UX: confirmar resolução de incidente sem alterar a transição”**. Rota já existe: POST /api/eng/incidentes/{id}/resolver, sem corpo. Motivo: reduzir acionamento acidental; decisão deve cobrir foco, Cancelar, Enter e testes. Não precisa de endpoint novo; até aprovação, nenhum diálogo é introduzido. Não usar “Rejeitar aprovação” como sinônimo de resolver ou apagar.


## Apêndice — Depende da integração (Vinny/Iohan)

**Estes são rascunhos, não issues criadas nem contratos aprovados.** Rotas marcadas PROPOSTA não existem nessa base e os JSON são exemplos fictícios a negociar. Não chamar nem implementar essas rotas na apresentação antes do gate. Nos itens “integração simples”, abrir depois uma tarefa de **consumo/mock da rota existente**, não pedir um endpoint duplicado.

**Gate para liberar cada DS-35–42:** Vinny/Iohan confirmam rota/campos e autorização, implementam ou conectam a API, estendem `api.js`/mock/hooks quando necessário, fornecem fixtures de normal/vazio/lento/erro/403 e registram um teste de contrato/aceite real. Joyce só então consome o adaptador pronto. Se não houver campo, mostrar ausência explicitamente ou não oferecer a área; não enviar uma funcionalidade falsa como pronta. Revisor e prazo de cada futura issue: a definir por Vinny, sem data neste plano.

### API-01 — Rascunhe assunção concorrente e responsabilidade
**Título sugerido:** API: assumir incidente com responsável e versão.
**Situação:** API nova/mudança de modelo; `reconhecer` hoje não significa assumir. **Bloqueia DS-35.**
**Rotas PROPOSTAS:** POST `/api/eng/incidentes/{id}/assumir`; acrescentar campos pactuados ao GET de resumo/detalhe. Exemplo de pedido e recorte de resposta:

```json
{"versao":3}
```
```json
{"id":"inc-ficticio-1","responsavel":"analista.visual","assumido_em":"2026-10-21T12:00:00Z","versao":4}
```

**Motivo:** cabeçalho “meus atendimentos” e ação Assumir exigem autoria persistente e controle de concorrência. **Aceite da integração:** responsável vem da sessão, não de campo enviado; operação atômica e 409 na versão desatualizada; 400/401/403/404 públicos consistentes; auditoria e teste de dois operadores. N1 só entra se a equipe aprovar a matriz nova; não copiar a permissão do protótipo.

### API-02 — Rascunhe o escalonamento auditado
**Título sugerido:** API: escalar incidente com destino, motivo e versão.
**Situação:** API nova/mudança de modelo; não existe encaminhamento no ciclo atual. **Bloqueia DS-36.**
**Rota PROPOSTA:** POST `/api/eng/incidentes/{id}/escalar`:

```json
{"papel_destino":"analista_redes","motivo":"Necessita investigação de rede","versao":4}
```
```json
{"id":"inc-ficticio-1","situacao_atendimento":"encaminhado","papel_destino":"analista_redes","versao":5}
```

**Motivo:** separar condição medida, estado de atendimento e responsabilidade; uma cor ou mudança local não encaminha um trabalho. **Aceite da integração:** decidir perfis de origem/destino, efeitos sobre o responsável e lista; transição persistida/auditada, conflito 409, validação do motivo e retorno confirmado. Registros de ação, solicitação de validação, reabertura e linha do tempo do protótipo requerem contratos/PRs próprios depois; não cabem na pequena DS-36.

### API-03 — Rascunhe a IA contextual ao incidente
**Título sugerido:** API: persistir conversa de diagnóstico por incidente com estados explícitos.
**Situação:** API nova; POST `/api/alertas` atual é avulso e não oferece chat nem incident_id. **Bloqueia DS-37.**
**Rotas PROPOSTAS:** GET/POST `/api/eng/incidentes/{id}/ia/mensagens`:

```json
{"pergunta":"Quais evidências devem ser conferidas?","versao_incidente":5}
```
```json
{"mensagens":[{"id":"msg-ficticia-1","estado":"concluido","conteudo_generalizado":"Falha em equipamento de rede","resposta":"Verifique as métricas do enlace."}]}
```

**Motivo:** exibir histórico e estados `processando/concluido/bloqueado/indisponivel` por contrato, sem adivinhar o estado pela frase da IA. **Aceite da integração:** incidente existe antes da solicitação; política de acesso aprovada, conteúdo generalizado antes de sair, auditoria sem dados brutos, cancelamento/orçamento medidos e testes com IA simulada; bloquear o envio quando sanitização falhar. Definir polling/SSE no adaptador, sem criar um canal pela Joyce.

### API-04 — Rascunhe relatórios reais e seus arquivos
**Título sugerido:** API: substituir catálogo vazio por relatórios autorizados e definir geração/agendamento.
**Situação:** API nova sobre contrato incompleto; GET `/api/relatorios` atual retorna apenas `{"relatorios":[]}`. **Bloqueia DS-38.**
**Rotas PROPOSTAS:** manter envelope do GET; POST `/api/relatorios` para gerar; GET `/api/relatorios/{id}/arquivo` com autenticação. Exemplo de criação e catálogo:

```json
{"tipo":"incidentes","inicio":"2026-10-01T00:00:00Z","fim":"2026-10-21T12:00:00Z"}
```
```json
{"relatorios":[{"id":"rel-ficticio-1","tipo":"incidentes","estado":"pronto","arquivo_disponivel":true}]}
```

**Motivo:** não mostrar “Exportação preparada” ou entrega do n8n sem arquivo real. Agendamento é outra fatia da integração: proposta POST `/api/relatorios/agendamentos`, exemplo `{"tipo":"incidentes","periodicidade":"semanal","fuso":"Etc/GMT+4","destino_id":"destino-ficticio"}`. **Aceite:** decidir Gestor somente, limites/período, erro de geração, proteção do arquivo e estado do job; não usar links públicos com token em query. A DS-38 cobre só catálogo/download; tela de agendamento/envio exige outro PR pequeno e aceite de integração.

### API-05 — Rascunhe o ciclo de vida das credenciais
**Título sugerido:** API: listar metadados de credenciais e implementar rotação/revogação auditadas.
**Situação:** API nova; POST `/api/chaves/rotacao` só devolve uma string de sucesso, sem rotação real. **Bloqueia DS-39.**
**Rotas PROPOSTAS:** GET `/api/credenciais`, POST `/api/credenciais/{id}/rotacionar` e POST `/api/credenciais/{id}/revogar`. Exemplo de listagem e pedido sensível:

```json
{"credenciais":[{"id":"cred-ficticia-1","origem_id":"origem-ficticia","estado":"ativa","criada_em":"2026-10-21T12:00:00Z","expira_em":null}]}
```
```json
{"motivo":"Rotação administrativa","versao":1}
```

**Motivo:** o protótipo desenha confirmações que o sistema não executa. **Aceite da integração:** autorização de Gestor, armazenamento seguro e auditoria sem segredo, revogação efetiva e estratégia de entrega única de uma chave nova fora da listagem. Se ainda não há cadastro de origens, propor GET/POST `/api/origens` com `{"nome":"Sonda fictícia","tipo":"sonda"}` em issue própria; não inventar origem na UI. DS-39 é apenas lista de metadados; formulários de origem/rotação/revogação são trabalhos seguintes, depois do servidor.

### API-06 — Integre os equipamentos sem duplicar rotas
**Título sugerido:** Integração front: disponibilizar alvos, cadastro e ativação no mock/cliente.
**Situação:** **integração simples** para o que existe em `routers/operational.py`; sem necessidade de nova rota para listar. **Bloqueia DS-40.**
**Rotas atuais:** GET `/api/eng/alvos?limit=100` (N1+); POST `/api/eng/alvos` e PATCH `/api/eng/alvos/{id}` (Analista+).
Exemplo de recorte de listagem e corpos válidos de criação/ativação:

```json
{"alvos":[{"id":"alvo-ficticio-1","nome":"Serviço de teste","host":"127.0.0.1","porta":8080,"kind":"tcp","ativo":true,"intervalo_s":2,"timeout_s":1,"detector":"ewma"}]}
```
```json
{"nome":"Serviço de teste","host":"127.0.0.1","porta":8080,"kind":"tcp","intervalo_s":2,"timeout_s":1,"detector":"ewma"}
```
```json
{"ativo":false}
```

**Motivo:** essas rotas não estão no mock nem em páginas do front. **Aceite da integração:** cliente/mock com mesmos limites, validação e RBAC; erro403 para escrita N1, vazio/lento/erro reproduzíveis. PATCH não edita host/nome; detalhe GET `/alvos/{id}` não existe nessa base. Se a tela exigir ambos, propor extensão separada em vez de presumir. Medições/agregados já têm GETs próprios, mas gráficos não entram na DS-40.

### API-07 — Integre o estado global de coleta com honestidade
**Título sugerido:** Integração front: consumir coleta/status sem confundir SSE com coleta.
**Situação:** **integração simples**, rota existente para Analista/Gestor, ausente no mock/painel. **Bloqueia DS-41.**
**Rota atual:** GET `/api/eng/coleta/status`. Quando o scheduler não está criado, a resposta real é:

```json
{"habilitada":false,"metricas":{}}
```

Com scheduler, o envelope contém métricas como started/completed/missed/timeouts/errors/active/peak_active/max_lag_seconds e leader/queued; os valores são do processo, não o inventário de sondas do desenho. **Motivo:** “Tempo real ativo” significa conexão do canal, não saúde das origens. **Aceite:** mock normal/desabilitado/erro e RBAC correto; ausência não vira0. Para cards “última comunicação por origem”, **extensão PROPOSTA** em rota a pactuar, exemplo `{"origens":[{"id":"origem-ficticia","ultima_comunicacao_em":null,"estado":"sem_dados"}]}`; definir limiar de atraso no servidor. Essa extensão é outro escopo e não libera por si só card N1.

### API-08 — Integre usuários e separe administração futura
**Título sugerido:** Integração front: consumir usuários persistidos e definir administração de contas.
**Situação:** **integração simples** para listar/criar, **API nova** para detalhe completo/desativar/reset. **Bloqueia DS-42.**
**Rotas atuais:** GET/POST `/api/usuarios` (Gestor). GET retorna usernames, não objetos com papéis:

```json
{"usuarios":["analista.visual","gestor.visual"]}
```

POST atual exige `username,password,papel`; resposta exemplificada: `{"username":"analista.visual","papel":"analista_redes","status":"criado"}`. Não registrar senha em captura/log nem persistir no navegador. PostgreSQL é usado quando configurado; não migrar persistência como parte do visual.

**Motivo:** o protótipo pressupõe lista com estado/perfil, redefinição e desativação que os endpoints atuais não fornecem. **Aceite da integração simples:** mock/cliente cobrem lista/criação e403. **Extensões PROPOSTAS**, em contrato versionado/compatível a decidir: GET de resumo com `{"usuarios":[{"username":"analista.visual","papel":"analista_redes","ativo":true}]}`; PATCH `/api/usuarios/{username}` com `{"ativo":false,"versao":1}`; POST `/api/usuarios/{username}/redefinir-acesso` com `{"motivo":"Solicitação administrativa"}`. Definir revogação de sessões, proteção do último Gestor, entrega segura e auditoria. Não reutilizar cegamente POST de criar conta para “reset”; DS-42 só lista os dados já liberados.

### Tarefas de apresentação condicionais (não iniciar antes do gate)

As tarefas abaixo **não ampliam o backlog autônomo**. Cada uma tem teto de um PR P/M e depende também de DS-34; outras partes das jornadas desenhadas continuam fora do escopo. Não criar stubs de tela nem botões prometendo capacidade ainda inexistente.


#### DS-35 — Exiba responsabilidade e a ação de assumir

- **Objetivo:** Mostrar quem assumiu e permitir a assunção somente após contrato concorrente e autorização confirmados.
- **Arquivos prováveis:** src/Operations.jsx (entrada aprovada); src/components/IncidentOwnership.jsx e seu teste; apresentação da lista de incidentes.
- **Passos:** Receba o contrato já integrado; use o cliente/hook pronto da integração; apresente responsável e ação em um único bloco; mantenha versão retornada, conflitos e bloqueio por perfil sob as regras do backend.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); nenhuma mudança na permissão de N1 por inferência do protótipo; assumir só confirma após200,409 mantém servidor como autoridade; sem controle ativo antes da dependência.
- **Como verificar no mock:** analista.joyce em /, Incidentes; /?cenario=lento e /?cenario=erro só após extensão do mock pela integração; conflito por fixture de teste.
- **Dependências:** DS-34 + API-01 entregue e gate validado pela integração. **Tamanho:** M. **Rótulos sugeridos:** design-system, front, integração, bloqueado.

#### DS-36 — Apresente a solicitação de escalonamento

- **Objetivo:** Encaminhar o incidente com motivo visível sem trocar estado localmente como se já tivesse sido salvo.
- **Arquivos prováveis:** src/components/EscalationForm.jsx e teste; apresentação da área de Incidentes.
- **Passos:** Use contrato e acesso aprovados; adicione formulário compacto de destino/motivo; preserve rascunho em memória na falha; apresente retorno confirmado; não implemente todo o detalhe/linha do tempo nesta tarefa.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); validação e perfil seguem API; sem sucesso otimista; não incluir Resolver/Reabrir em N1; novo texto coberto no teste do mesmo PR e comunicado à integração.
- **Como verificar no mock:** perfil aprovado na API-02 (por padrão analista.joyce, sem habilitar N1); / em Incidentes; vazio/erro/lento após suporte explícito da integração.
- **Dependências:** DS-34 + API-02 entregue e gate validado pela integração. **Tamanho:** M. **Rótulos sugeridos:** design-system, front, integração, bloqueado.

#### DS-37 — Apresente a conversa de IA ligada ao incidente

- **Objetivo:** Exibir uma lista simples de mensagens e um envio contextual depois que o contrato existir.
- **Arquivos prováveis:** src/components/IncidentConversation.jsx e teste; apresentação do incidente aprovada pela integração.
- **Passos:** Use adaptador pronto e estados tipados da integração; componha lista e campo de pergunta; apresente o conteúdo generalizado/erro; limite este PR à primeira conversa sem anexos, streaming novo ou execução de comandos.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); incident_id vem do incidente persistido; processamento/falha/bloqueio não inferidos do texto; mensagens escapadas; nenhum envio real no modo mock; dados privados nunca em storage.
- **Como verificar no mock:** analista.joyce em / no detalhe disponibilizado pela integração; fixtures de bloqueio/indisponível, pois as URLs atuais não simulam chat. Não inventar uma URL de tela atual.
- **Dependências:** DS-34 + API-03 entregue e gate validado pela integração. **Tamanho:** M. **Rótulos sugeridos:** design-system, front, integração, bloqueado.

#### DS-38 — Apresente a lista de relatórios disponíveis

- **Objetivo:** Distinguir relatório disponível, em geração e vazio sem fingir que existe um arquivo exportado.
- **Arquivos prováveis:** src/components/ReportsList.jsx e teste; entrada em Operations.jsx somente após liberação.
- **Passos:** Use catálogo real integrado; adote tabela/cartões existentes; mostre período/estado; permita só download autorizado disponibilizado pelo adaptador. Agendamento e envio externo ficam em PRs futuros, não neste.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); N1/Analista sem área se contrato mantiver Gestor; lista vazia honesta; sem link de exportação até autorização e arquivo confirmado; nenhum agendamento fictício.
- **Como verificar no mock:** gestor.joyce em / e nova área somente após mock atualizado; /?cenario=vazio, erro, lento em URLs separadas conforme a integração implementar.
- **Dependências:** DS-34 + API-04 entregue e gate validado pela integração. **Tamanho:** M. **Rótulos sugeridos:** design-system, front, integração, bloqueado.

#### DS-39 — Apresente metadados seguros de credenciais

- **Objetivo:** Identificar a origem e o estado de uma credencial sem expor chaves nem prometer rotação fictícia.
- **Arquivos prováveis:** src/components/CredentialList.jsx e teste; entrada de gestão liberada pela integração.
- **Passos:** Use dados sanitizados aprovados; apresente identificador, origem, estado e datas; use rótulos claros para ausências; não adicionar valores secretos, botões de rotação/revogação ou cofres nesta primeira entrega.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); não usa o stub /api/chaves/rotacao como prova de sucesso; sem segredo completo ou persistência no navegador; rotação/revogação exigem contrato e PRs posteriores além desta lista.
- **Como verificar no mock:** gestor.joyce em / na área que a integração adicionar; fixtures de credencial ativa/revogada/ausente, sem criar dados novos em mockApi.js pela Joyce.
- **Dependências:** DS-34 + API-05 entregue e gate validado pela integração. **Tamanho:** M. **Rótulos sugeridos:** design-system, front, integração, bloqueado.

#### DS-40 — Apresente a lista de equipamentos já cadastrados

- **Objetivo:** Consultar alvos existentes com os mesmos papéis de leitura da API, sem inventar um cadastro que o mock não atende.
- **Arquivos prováveis:** src/components/TargetsList.jsx e teste; src/Operations.jsx após cliente/mock prontos.
- **Passos:** Consuma o recurso integrado para /api/eng/alvos; apresente nome, host, porta, tipo e ativo; reaproveite tabela/cartões e estados; limite o PR à consulta. Formulário de cadastro e ativação são próximos PRs separados.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); N1 pode ler se mantida a autorização atual Reader; nenhuma ação de escrita para N1; limite da listagem explícito, nenhum detalhe de equipamento fictício.
- **Como verificar no mock:** suporte.joyce, analista.joyce e gestor.joyce em /, nova área somente após extensão do mock; vazio/erro/lento implementados pela integração.
- **Dependências:** DS-34 + API-06 entregue e gate validado pela integração. **Tamanho:** M. **Rótulos sugeridos:** design-system, front, integração, bloqueado.

#### DS-41 — Apresente o estado global da coleta existente

- **Objetivo:** Mostrar se o coletor está habilitado e suas métricas sem transformar SSE conectado em saúde da coleta.
- **Arquivos prováveis:** src/components/CollectionStatus.jsx e teste; composição de Analista/Gestor aprovada pela integração.
- **Passos:** Use adaptador pronto para coleta/status; trate habilitada=false e metricas vazias; apresente só as métricas existentes e seus rótulos; mantenha o aviso de tempo real separado.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); N1 não chama a rota restrita; habilitada=false significa coleta desabilitada, não rede indisponível; ausência de métrica não é zero; sem horário/origem inventados.
- **Como verificar no mock:** analista.joyce e gestor.joyce em /, bloco após integração; suporte.joyce confirma ausência; fixtures habilitada=false, metricas vazias e erro; ?cenario=coleta-atrasada não existe.
- **Dependências:** DS-34 + API-07 entregue e gate validado pela integração. **Tamanho:** P. **Rótulos sugeridos:** design-system, front, integração, bloqueado.

#### DS-42 — Apresente a lista atual de usuários

- **Objetivo:** Permitir ao Gestor consultar a lista disponível sem inventar papel, estado ou ações ausentes na resposta.
- **Arquivos prováveis:** src/components/UsersList.jsx e teste; entrada de gestão em Operations.jsx liberada pela integração.
- **Passos:** Use GET já integrado; apresente somente username enquanto a resposta for lista de strings; acrescente estado/perfil só após extensão contratada; não implemente reset/desativação/cadastro no mesmo PR.
- **Aceite verificável:** C0 completo (ambos os temas, 390 px, contraste, foco e os três comandos); Gestor somente; sem afirmar conta ativa/papel a partir de username; não expor senha/hash; sem botão de redefinição/desativação antes das rotas reais; criação existente pode virar outro PR pequeno.
- **Como verificar no mock:** gestor.joyce em /, área só após mock/cliente prontos; vazio/erro/lento conforme extensão; analista.joyce confirma restrição.
- **Dependências:** DS-34 + API-08 entregue e gate validado pela integração. **Tamanho:** M. **Rótulos sugeridos:** design-system, front, integração, bloqueado.

## Evidência para concluir uma tarefa

Registrar no PR: ID, escopo, base/commit, arquivos alterados, perfil/URL/área, viewport/tema, capturas antes/depois, pares de contraste medidos, percurso de teclado, comandos e resultados, textos/seletores alterados e validação do integrador quando aplicável. Finalizar só a tarefa que teve o critério comprovado; não fechar uma issue ampla por associação. Não adicionar data de entrega sem confirmação de Vinny.


## Textos adicionais antes da publicação

### https://trello.com/c/
NbEHZVro
[Certo] Atualização de 21/10/2026 (UTC−4). Como equipe de operação, quero detectar quedas e receber SSE sem acumular atraso, para reagir ao incidente. PR #44 aberto em ddd4840, ainda baseado em fix/base-issues. VM rodada-2026-10-22b: carga 0/5 na develop → 5/5 no candidato; 489/489 testes, atraso máximo 0,093396 s e 0 erros. P95 queda→SSE até 0,41 s no ensaio sintético. Vinny: integração e aceite em 23/10; Iohan: revisão em 22/10 após 22h. A mudança de alvo depende do merge do #43. Validado em VM; aceite final em 23/10. Ainda sem merge ou aprovação independente confirmados. https://github.com/Solution-Explores/SigmaTI/pull/44 https://github.com/Solution-Explores/SigmaTI/issues/8

### https://trello.com/c/
RH2Ftdst
[Certo] Atualização de 21/10/2026 (UTC−4). Como equipe, quero cartões rastreáveis para saber quem executa, quem revisa e qual evidência falta. Responsável pela organização: Vinny; revisor: Iohan. Conferência até 23/10 às 18h. Exigir história, responsável, revisor, data com significado, issue/PR e comentário de atividade. Planejada não significa em execução; revisão exige PR aberto. Joyce Yasmin: início proposto em 26/10, conta ainda não identificada no quadro. Datas pós-demo são propostas; revisões de backlog não são promessas de conclusão. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
fDovwdzt
[Certo] Atualização de 21/10/2026 (UTC−4). Como equipe, quero priorizar expansão após a demo para não diluir o aceite atual. Coordenação proposta: Vinny; revisão: Iohan. Revisão do backlog em 03/11 às 18h; não é prazo de implementação. #10, #16–#19, #21, #22 e #30 continuam trabalho futuro, sem início ou conclusão confirmados. Definir contratos e nova sprint antes de iniciar; tarefas visuais DS-35–42 dependem dos gates de integração. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
fxR7XxOZ
[Certo] Atualização de 21/10/2026 (UTC−4). Como equipe, quero planejar validações externas com recursos reais, para distinguir laboratório de homologação. Coordenação proposta: Vinny; revisão: Iohan. Revisão de viabilidade em 03/11 às 18h, sem compromisso de execução nessa data. #11, #12, #20, #24 e #26–#29 são trabalho futuro dependente de infraestrutura, autorização ou coleta prolongada. Não houve homologação hospitalar nem validação externa por estas rodadas. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
qAz30ebN
[Certo] Atualização de 21/10/2026 (UTC−4). Como mantenedor, quero medir o custo da auditoria por volume e concorrência para decidir otimização com evidência. Triagem proposta por Vinny em 27/10 às 18h; revisão Iohan. Não bloqueia a demo. A issue #46 registra o escopo; nenhuma nova medição de custo ou otimização é declarada por este cadastro. Definir ensaio isolado e critérios antes de alterar implementação. https://github.com/Solution-Explores/SigmaTI/issues/46

### https://trello.com/c/
YGVH2Pg9
[Certo] Atualização de 21/10/2026 (UTC−4). Como equipe, quero integrar somente o que teve revisão e aceite para apresentar um SHA verificável. Responsável: Vinny; revisor: Iohan. #43 em 22/10; #44 e aceite em 23/10; congelar SHA às 18h; demo em 24/10 às 9h. Release v1.0.0, #5, #13 e #25 físico propostos até 03/11, sujeitos ao orientador; aceite da release em 31/10–01/11. Não confundir aptidão do candidato em VM com merge e aceite final. Joyce começa após a demo, proposta de 26/10. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
WzIvGyKq
[Certo] Atualização de 21/10/2026 (UTC−4). Como operador, quero impedir o envio de dados sensíveis para reduzir exposição no diagnóstico. Responsável: Vinny; revisão: Iohan. Próxima etapa proposta até 03/11 às 18h, sujeita ao orientador: conferir critérios completos e ampliar casos adversariais. O corpus E6 e o roteiro com dados fictícios têm evidências locais; as rodadas da VM validam regressão, não anonimização universal. Revisão completa dos critérios e dados reais não foram concluídas; IA da demo é simulada. https://github.com/Solution-Explores/SigmaTI/issues/5

### https://trello.com/c/
HMFmBFhp
[Certo] Atualização de 21/10/2026 (UTC−4). Como apresentador, quero um roteiro reproduzível e material coerente para demonstrar o que foi medido. Responsável: Vinny; revisor: Iohan. Até 23/10 às 18h: dados fictícios, dois ensaios, gravação de contingência, capturas e slides. Sete passos: arquitetura; perfis/403; coleta e incidente/SSE; SLO; aprovação/auditoria; IA simulada e generalização; resultados. Slides: 489/489 e carga 5/5 no candidato, atraso máximo 0,093 s, 0 erros. README definitivo e PRs #41/#42 ficam após a demo. Ensaios e gravação ainda sem execução confirmada. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
zOyTl0LP
[Certo] Atualização de 21/10/2026 (UTC−4). Como mantenedor, quero uma release com critérios completos e evidência para publicar uma versão reproduzível. Responsável: Vinny; revisor: Iohan. v1.0.0 proposta até 03/11 às 18h; aceite em 31/10–01/11, condicionado ao orientador. Depende de #5, #13 e restauração física #25. Não há release final nem todos esses critérios concluídos. O congelamento da demo em 23/10 não equivale à release na main. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
KfknLcok
[Certo] Atualização de 21/10/2026 (UTC−4). Como revisor, quero executar o roteiro no próprio computador a partir do SHA congelado, para descobrir dependências ocultas. Executor: Iohan, 23/10 após 22h; apoio/revisão: Vinny. A data nativa de 23/10 é preparação; a execução independente é noturna, depois do freeze das 18h. Registrar SHA, instalação, comandos, falhas e resultado. Esta execução ainda não foi confirmada e não substitui o critério de restauração física da #25. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
sTTArNVt
[Certo] Atualização de 21/10/2026 (UTC−4). Como integrador, quero CI e instruções reproduzíveis para testar o mesmo SHA da demo. Responsável: Vinny; revisor: Iohan. Conferir até 23/10 às 18h, após merges autorizados: CI, PostgreSQL de teste, painel e validadores API/coleta. CI verde nos heads #43/#44 não comprova automaticamente o SHA integrado. O aceite final e a instalação independente ainda estão pendentes. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
z1CLDzjj
[Certo] Atualização de 21/10/2026 (UTC−4). Como equipe, quero validar o conjunto integrado para não apresentar apenas resultados de branches. Responsável pelo aceite: Vinny; revisão independente: Iohan. Em 23/10 antes das 18h, registrar SHA integrado e resultados de pytest e validate_api_acceptance.py, validate_panel.py e validate_collection.py. Candidato ddd4840 validado em VM: 489/489 e carga 5/5, atraso 0,093 s e 0 erros. Rodada-2026-10-22b é evidência de candidato; aceite final em 23/10 ainda pendente. #4 encerrada não encerra #5/#6 automaticamente. https://github.com/Solution-Explores/SigmaTI/issues/31

### https://trello.com/c/
e7us28WV
[Certo] Atualização de 21/10/2026 (UTC−4). Como auditor, quero âncora externa, rotação HMAC e verificação agendada para detectar alterações além da cadeia local. Responsável: Vinny; revisor: Iohan. Próxima etapa proposta até 03/11 às 18h, sujeita ao orientador. A cadeia local demonstrável não comprova âncora externa nem rotação/agendamento. Esses critérios continuam pendentes; não marcar a issue concluída por associação à auditoria do #43. https://github.com/Solution-Explores/SigmaTI/issues/13

### https://trello.com/c/
9zGDTCQp
[Certo] Atualização de 21/10/2026 (UTC−4). Como mantenedor, quero restaurar em outra máquina física para comprovar portabilidade além do host atual. Responsável pela coordenação: Vinny; revisor: Iohan. Proposta até 03/11 às 18h, sujeita à disponibilidade da máquina e ao orientador. Evidência existente: 17 verificações de restauração aprovadas em VM no mesmo host. As rodadas-2026-10-22, -22b e -22c não repetiram a restauração. Falta outra máquina física; não declarar a #25 integralmente concluída. https://github.com/Solution-Explores/SigmaTI/issues/25

### https://trello.com/c/
tr4WuXPv
[Certo] Atualização de 21/10/2026 (UTC−4). Como mantenedor, quero testes determinísticos para distinguir regressão de instabilidade. Triagem por Vinny em 27/10 às 18h; revisão Iohan. Não bloqueia a demo. Rodada-2026-10-22c: provedor 9/10 e sonda 5/10 na baseline anterior aos PRs; sonda sem ajuste 26/30, com shutdown 30/30. Correção da sonda em branch local, sem PR confirmado. Provedor: timer atrasou até 1,263 s antes do TimeoutError; causa sistêmica exata não isolada. DNS também falhou na baseline. Não aumentar limites nem declarar correção integrada. https://github.com/Solution-Explores/SigmaTI/issues/45

### https://trello.com/c/
9tWbeAYN
[Certo] Atualização de 21/10/2026 (UTC−4). Como integrador, quero tratar achados de API e autenticação antes de integrar, para preservar autorização e auditoria. Responsável: Vinny; revisor: Iohan. #43/8662ea9 aberto e CI verde; tratar revisão em 22/10, aceite final em 23/10 até 18h. #4 está encerrada; #5 permanece etapa pós-demo. Não declarar todos os critérios da #5 entregues junto com o #43. https://github.com/Solution-Explores/SigmaTI/pull/43 https://github.com/Solution-Explores/SigmaTI/issues/6

### https://trello.com/c/
NRkslN8y
[Certo] Atualização de 21/10/2026 (UTC−4). Como revisor independente, quero conferir PR e evidência antes do merge para reduzir regressões. Responsável pela revisão: Iohan; integração: Vinny. Revisão #43 até 22/10 às 8h; #44 em 22/10 após 22h. #44 só muda para develop depois do merge #43. Aceite integrado em 23/10 antes das 18h; roteiro independente em 23/10 após 22h. #41/#42 são documentação e ficam após a demo. PR aberto não equivale a aprovado. https://github.com/Solution-Explores/SigmaTI/pull/43 https://github.com/Solution-Explores/SigmaTI/pull/44 https://github.com/Solution-Explores/SigmaTI/issues/31

## Novos marcos e dependências — prévia antes da publicação

### 
DEMO — Congelar e registrar SHA após aceite
Lista: A fazer; etiqueta: Demonstração 24/10; data UTC−4: 23/10/2026 18:00
Como apresentador, quero um SHA congelado e reproduzível para demonstrar exatamente a versão aceita. Responsável Vinny; revisor Iohan. Marco fixo: sexta 23/10 às 18h UTC−4. Depende dos merges #43/#44, CI e aceite integrado. Registrar SHA, resultados e contingência; não introduzir novas mudanças após o freeze. Pendente; candidato validado em VM não comprova congelamento.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
DEMO — Executar roteiro independente no SHA congelado
Lista: A fazer; etiqueta: Demonstração 24/10; data UTC−4: 23/10/2026 22:00
Como revisor, quero executar sozinho o roteiro no próprio computador para detectar dependências ocultas. Executor Iohan; apoio e revisão dos achados Vinny. Início previsto após 22h de 23/10; a data nativa marca início da janela, não término às 22h. Depende do SHA congelado às 18h. Registrar SHA, instalação, percurso e falhas. Relacionado ao cartão de instalação https://trello.com/c/KfknLcok . Execução ainda não confirmada.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
DEMO — Smoke de sábado às 7h30
Lista: A fazer; etiqueta: Demonstração 24/10; data UTC−4: 24/10/2026 07:30
Como apresentador, quero subir o ambiente e percorrer o smoke antes da reunião para detectar indisponibilidade. Executor Vinny; revisão prévia Iohan no ensaio da sexta. Marco fixo 24/10 às 7h30 UTC−4. Usar SHA congelado, dados fictícios e IA simulada. Conferir login, painel, coleta/SSE, incidente, aprovação, cadeia e diagnóstico. Se falhar, usar contingência e declarar limite; smoke ainda pendente.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
DEMO — Apresentar SigmaTI ao orientador às 9h
Lista: A fazer; etiqueta: Demonstração 24/10; data UTC−4: 24/10/2026 09:00
Como equipe, quero demonstrar evidências e limites para obter decisões do orientador. Responsável pela apresentação Vinny; revisão do roteiro Iohan. Marco fixo sábado 24/10 às 9h UTC−4, cerca de 15 min. Sete passos: arquitetura; perfis/403; coleta e incidente/SSE; SLO; aprovação/auditoria; IA simulada e generalização; resultados. Declarar loopback, dados fictícios, VM no mesmo host e margem curta do timer da IA. Pedir decisão sobre 03/11, trabalho futuro, máquina física #25 e licença. Não declarar homologação hospitalar.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
PÓS-DEMO — Organizar documentação e README em PR próprio
Lista: A fazer; etiqueta: Pós-demo; data UTC−4: 27/10/2026 18:00
Como visitante e mantenedor, quero README enxuto e documentação organizada para reproduzir o projeto. Responsável proposto Vinny; revisor Iohan. Começar depois da apresentação de 24/10. Data proposta 27/10 às 18h para revisão de planejamento/PR, não promessa anterior de conclusão. PR de documentação separado: organizar docs por assunto, selos, captura do ensaio, fluxo, início rápido, números atuais 489/489 e carga 5/5 com limites. Revisar #41/#42 após demo. Não afirmar integração nem encerrar critérios técnicos por documentação.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
PÓS-DEMO — Reorganizar diretórios em PR separado
Lista: A fazer; etiqueta: Pós-demo; data UTC−4: 27/10/2026 18:00
Como mantenedor, quero estrutura de diretórios clara sem alterar lógica para facilitar evolução. Responsável proposto Vinny; revisor Iohan. Iniciar após apresentação de 24/10 e PR documental. Meta do cronograma: integrar até terça 27/10 às 18h, condicionada a revisão e CI. Planejar backend/, frontend/ e deploy/, ajustar imports, scripts, CI e caminhos. Exige CI verde, regressão na VM e revisão independente. Nenhum movimento de código foi feito por este cadastro.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
API-01 — Planejar assunção concorrente [libera DS-35]
Lista: Backlog; etiqueta: Bloqueado · Integração; data UTC−4: 26/10/2026 18:00
Como operador, quero responsabilidade persistida e concorrência controlada para assumir um incidente sem sobrescrever outro operador. Executor proposto Vinny; revisor Iohan. Revisão de escopo em 26/10 às 18h; sem prazo de implementação pactuado. RASCUNHO: API nova/mudança de modelo; reconhecer não significa assumir. Pactuar versão, autoria da sessão, operação atômica, 409 e RBAC; dois operadores no aceite. Gate para DS-35: contrato aprovado, API, adaptador/mock, fixtures e teste real. Plano completo no DS-01. Não há endpoint aprovado por este cartão.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
API-02 — Planejar escalonamento auditado [libera DS-36]
Lista: Backlog; etiqueta: Bloqueado · Integração; data UTC−4: 26/10/2026 18:00
Como operador, quero encaminhar incidente com destino e motivo confirmados pelo servidor para rastrear atendimento. Executor proposto Vinny; revisor Iohan. Revisão em 26/10 às 18h, sem prazo de implementação. RASCUNHO de API nova: decidir perfis, responsável, versão/409, persistência e auditoria. Não mudar estado só no cliente. Gate DS-36 exige contrato aprovado, mock/adaptador e teste real. Detalhe e reabertura são escopos separados. Plano no DS-01.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
API-03 — Planejar IA contextual [libera DS-37]
Lista: Backlog; etiqueta: Bloqueado · Integração; data UTC−4: 26/10/2026 18:00
Como analista, quero diagnóstico contextual ao incidente com estados explícitos para consultar histórico sem inferir sucesso do texto. Executor proposto Vinny; revisor Iohan. Revisão de escopo em 26/10 às 18h; implementação sem prazo pactuado. RASCUNHO: alertas atual é avulso, não chat. Negociar acesso, persistência, conteúdo generalizado, cancelamento, orçamento, auditoria e IA simulada. Gate DS-37: contrato, adaptador/mock e teste real. #18 é referência de evolução, não prova deste contrato. Plano no DS-01.
https://github.com/Solution-Explores/SigmaTI/issues/18

### 
API-04 — Planejar relatórios reais [libera DS-38]
Lista: Backlog; etiqueta: Bloqueado · Integração; data UTC−4: 26/10/2026 18:00
Como gestor, quero catálogo e download autorizados para obter relatório real. Executor proposto Vinny; revisor Iohan. Revisão em 26/10 às 18h; não é entrega. RASCUNHO: catálogo atual vazio não comprova geração/exportação. Pactuar período, job, falhas, arquivo protegido e RBAC. Gate DS-38: contrato, cliente/mock, fixtures e aceite real. Agendamento/envio exigem fatias próprias; #16 é referência de evolução. Plano no DS-01.
https://github.com/Solution-Explores/SigmaTI/issues/16

### 
API-05 — Planejar credenciais seguras [libera DS-39]
Lista: Backlog; etiqueta: Bloqueado · Integração; data UTC−4: 26/10/2026 18:00
Como gestor, quero metadados e ciclo de credenciais reais para administrar acesso sem expor segredos. Executor proposto Vinny; revisor Iohan. Revisão em 26/10 às 18h; sem prazo de implementação. RASCUNHO de API nova: resposta textual de sucesso não comprova rotação. Pactuar armazenamento seguro, revogação efetiva, entrega única e auditoria sem chave. Gate DS-39 limita-se à lista de metadados após contrato, mock e teste real; formulários futuros separados. Referência #23; plano no DS-01.
https://github.com/Solution-Explores/SigmaTI/issues/23

### 
API-06 — Integrar alvos existentes ao cliente/mock [libera DS-40]
Lista: Backlog; etiqueta: Bloqueado · Integração; data UTC−4: 26/10/2026 18:00
Como operador, quero consultar alvos pelo contrato existente para não duplicar APIs. Executor proposto Vinny; revisor Iohan. Revisão em 26/10 às 18h; implementação ainda não combinada. Integração simples: listar alvos N1+, criar/ativar Analista+. Cliente/mock devem cobrir limites, 403 de escrita N1, vazio/lento/erro. PATCH atual não edita host/nome e detalhe individual não existe nessa base. Gate DS-40: adaptador pronto e teste de contrato real. Plano no DS-01.
https://github.com/Solution-Explores/SigmaTI/issues/31

### 
API-07 — Integrar coleta/status [libera DS-41]
Lista: Backlog; etiqueta: Bloqueado · Integração; data UTC−4: 26/10/2026 18:00
Como analista/gestor, quero estado global do coletor para distinguir coleta desabilitada de conexão SSE. Executor proposto Vinny; revisor Iohan. Revisão em 26/10 às 18h; não é entrega. Integração da rota existente coleta/status: habilitada=false e metricas vazias não são rede indisponível ou zero. Cobrir normal/desabilitado/erro e RBAC. Gate DS-41: cliente/mock, fixtures e teste real; saúde por origem é extensão separada. #8 já validada em VM não significa esta tela implementada. Plano no DS-01.
https://github.com/Solution-Explores/SigmaTI/issues/8

### 
API-08 — Integrar usuários e separar administração [libera DS-42]
Lista: Backlog; etiqueta: Bloqueado · Integração; data UTC−4: 26/10/2026 18:00
Como gestor, quero consultar usuários pelo contrato disponível para administrar sem ações fictícias. Executor proposto Vinny; revisor Iohan. Revisão em 26/10 às 18h; sem prazo de implementação. GET atual lista usernames; não inferir papel/estado. Listar/criar são integração existente; detalhe completo, desativar e reset exigem contratos próprios e revogação de sessões. Gate DS-42: cliente/mock, RBAC/403, fixtures e teste real; sem senha em captura/storage. #6 é referência de autenticação, não aceite de administração futura. Plano no DS-01.
https://github.com/Solution-Explores/SigmaTI/issues/6
