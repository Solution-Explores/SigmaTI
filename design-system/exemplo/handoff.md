# SIGMA — fluxos e telas

[Certo] Esta entrega implementa a modelagem visual em um documento FigCraft editável, com navegação entre estados de cenário. Não implementa o sistema operacional nem seus serviços.

## Abrir e revisar

1. Abra `sigma-fluxos.figcraft` no FigCraft.
2. Na página **01 · Comece aqui**, selecione o quadro e inicie a apresentação. Escolha a jornada de N1, analista ou gestor.
3. Para examinar o desenho sem o aplicativo, abra `review.html`. A galeria permite buscar telas e abrir as imagens em tamanho original; ela não reproduz as interações.
4. Os fluxos também possuem pontos de entrada nativos nas páginas de Acesso e Operação.

O incidente **INC-008** é o cenário principal. As demais linhas são contexto ilustrativo. Campos e filtros mostram valores previamente definidos. A navegação entre estados não persiste alterações nem aplica permissões de servidor.

## Conteúdo entregue

São 106 quadros em 11 páginas. O número inclui estados alternativos, confirmações, perfis e larguras; não representa 106 páginas distintas da aplicação.

| Página | Conteúdo |
| --- | --- |
| Biblioteca | Componentes de botão, tipografia, tokens e convenções de interação |
| Comece aqui | Entradas por perfil, escopo e acesso às referências |
| Acesso | Login, primeiro acesso, orientação e erro |
| Operação | Visão geral, fila ativa e histórico permitido por perfil |
| Atendimento | Assunção, registro, encaminhamento, validação, resolução, reabertura e IA contextual |
| Ações e evidências | Formulários, medições, captura fictícia e conteúdo generalizado |
| Equipamentos | Lista, detalhe e cadastro |
| Gestão e administração | Relatórios, usuários, origens, regras, saúde, auditoria, laboratório e agendamentos |
| Confirmações e conta | Ações sensíveis, resultados e contas por perfil |
| Estados e exceções | Vazio, erro, concorrência, sessão expirada, coleta atrasada e estados da IA |
| Responsivo e tema escuro | Referências em 375, 768, 1024 e 1440 px |

## Fluxos principais

- **N1:** login → visão geral → incidentes → INC-008 → assumir → registrar ação → escalar. A solicitação de validação encaminha o atendimento ao analista. Não há ação de encerramento ou reabertura na interface desse perfil.
- **Analista:** visão geral → incidente encaminhado → assumir → investigar → verificar recuperação → registrar resolução → encerrado → reabrir mediante motivo.
- **Gestor:** visão geral → relatórios → registros considerados ou agendamentos. Administração inclui confirmação de desativação, redefinição de acesso, rotação e revogação de credencial.
- **Celular:** resumo do incidente → registrar ação ou escalar → resultado. Resumo, atividade e IA ficam em abas para evitar comprimir os painéis de desktop.

As confirmações administrativas usam sobreposições nativas. Cancelar fecha a sobreposição. Os resultados são quadros de demonstração; voltar à lista não equivale a uma consulta a dados atualizados.

## Regras para a implementação

| Tema | Regra |
| --- | --- |
| Atendimento | Separar situação do fluxo, condição medida e responsabilidade. Uma recuperação medida não encerra automaticamente o atendimento. |
| N1 | Pode consultar ativos, assumir, registrar, escalar e solicitar validação. Não pode encerrar, reabrir ou consultar histórico e pacotes restritos. |
| Analista | Pode investigar evidências, registrar resolução, reabrir, consultar histórico e administrar equipamentos e regras. |
| Gestor | Possui capacidades operacionais e administra usuários, origens, credenciais, relatórios e auditoria. |
| IA | É uma hipótese a verificar; nunca executa a correção. Falha ou bloqueio do envio não impede o atendimento. |
| Coleta | Ausência de dados não significa operação normal. Mostrar o horário da última comunicação e a origem afetada. |
| Concorrência | A assunção exige versão do registro. Em conflito, apresentar quem assumiu e recuperar o estado confirmado. |
| Salvamento | Preservar o rascunho em memória quando houver erro. Mostrar sucesso somente após confirmação do servidor. Avisar antes de abandonar alterações. |
| Recorrência | Agrupar novas ocorrências enquanto o incidente estiver ativo. Após encerramento, criar um novo registro relacionado, preservando o histórico anterior. |
| Continuidade | Guardar consulta, filtros, página e posição da fila ao abrir e retornar do detalhe. |
| Administração | Bloquear a desativação do último gestor ativo. Registrar autoria, horário, alvo e resultado sem expor segredos. |
| Diagnóstico | Persistir o incidente antes de solicitar IA. Usar estados explícitos de processamento, falha e bloqueio; não inferir estado pelo texto da resposta. |
| Atualização | SSE para alertas, com nova consulta após reconexão. O canal da conversa deve seguir os contratos do projeto. |
| Privacidade | Generalizar conteúdo antes de enviar ao provedor; bloquear se a proteção falhar. Não persistir evidências sensíveis no armazenamento local do navegador. |

Todos os nomes e endereços mostrados são fictícios. Os horários devem usar o fuso da instituição e oferecer data completa nos detalhes. A instalação foi modelada para uma instituição, sem cadastro público e sem correção remota.

## Visual e adaptação

A identidade utiliza Segoe UI e azul institucional. Há 15 variáveis de cor com modos Claro/Escuro, 10 estilos tipográficos e componentes reutilizáveis de botão. `tokens.json` e `tokens.css` são exportações nativas para consulta durante a implementação.

Desktop prioriza fila e investigação lado a lado. Em 1024 px, a navegação fica mais estreita. Tablet e celular priorizam uma coluna e ações essenciais. Os quadros são referências de composição; o comportamento de redimensionamento contínuo precisa ser construído no frontend. As jornadas compactas usam os quadros de celular como destino de algumas ações.

Os estados usam texto além da cor. A biblioteca especifica foco visível e alvos de interação de pelo menos 44 px. Ordem de foco, leitores de tela, edição dos campos e comportamento real por teclado precisam de validação na aplicação.

## Verificação executada

[Certo] O arquivo salvo foi reaberto pelo motor FigCraft sem reparos. Foram exportadas 106 prévias. A inspeção percorreu 6.386 nós, sem texto excedendo os limites do respectivo contêiner e sem destinos ausentes nas interações inspecionadas. Cinco trajetos principais foram conferidos estruturalmente: N1, analista, relatórios/agendamentos, revogação e registro móvel. O relatório está em `validation.json`.

Foram inspecionadas visualmente amostras de atendimento, encerramento, relatórios, tema escuro e versões compactas. Essa conferência não equivale a um teste completo de reprodução das interações no aplicativo desktop nem a teste de usabilidade com usuários.

## Limites e sequência de desenvolvimento

[Certo] Autenticação, autorização, persistência, filtros, paginação, geração de arquivos, envio de relatórios, coleta e IA permanecem simulados. Estados distintos não mantêm uma sessão de dados compartilhada entre todos os quadros. As regras acima são requisitos para o sistema, não garantias implementadas pelo protótipo.

1. Fundação: autenticação, permissões e contratos persistentes.
2. Atendimento: fila, assunção concorrente, registros, encaminhamento e encerramento.
3. Investigação: equipamentos, evidências, IA contextual e eventos em tempo real.
4. Gestão: relatórios, agendamentos, administração e auditoria.

As metas de alerta em até 5 segundos e diagnóstico em até 15 segundos precisam de medição ponta a ponta. Nenhum tempo de resposta foi comprovado por esta entrega visual.
