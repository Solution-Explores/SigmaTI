# Protótipo v2 do SigmaTI (visual da Joyce)

Protótipo **navegável** do painel, feito em HTML, com a identidade v4 (`../identidade-visual/decisoes.md`), tema claro e escuro e larguras de computador, 1024, tablet e celular.

## Como abrir

Abra `prototipo-v2/index.html` no navegador. Não precisa instalar nada nem ter outras pastas ao lado.

## O que é e o que não é

- É um **desenho navegável**. Não é o painel: não fala com a API, não grava nada e os dados são fictícios.
- **Fase 1:** 56 das 106 telas do protótipo do Vinícius (login, visão geral, fila, histórico, as 16 variações do incidente por perfil, estados e exceções, Saúde, Auditoria, celular, tablet, 1024 e tema escuro), mais a biblioteca de componentes e as telas que o painel tem e o protótipo dele não tem: **Aprovações** e **Diagnóstico**.
- **Fase 2 (não feita):** as 50 telas restantes. O **Mapa de telas** (`#/mapa`) lista as 106, diz qual já está aqui e qual fica para depois.
- A barra de controles do protótipo mostra, em **Esta tela**, a situação na API da tela aberta, conforme `design-system/exemplo/README.md`: "Só front", "Integração simples" ou "API nova". Telas de "API nova" são só desenho e não funcionam no painel real.

## Medido e não medido

- Pares de cor das etiquetas e do texto: todos acima de 4,5:1 nos dois temas (menor valor 5,19:1 no claro e 6,03:1 no escuro, calculado por script sobre os valores do arquivo; botões e texto de apoio entre eles). Esse cálculo foi feito na Fase 1 e não foi repetido depois das revisões de 14/11.
- Foi aberta cada uma das 56 rotas num navegador automático: nenhuma ficou vazia, nenhuma deu erro de JavaScript e nenhuma teve rolagem lateral a 375 px (tema inicial).
- **Não verificado:** tema escuro nas telas revisadas em 14/11, leitor de tela, ordem de foco do teclado, impressão, Safari e Firefox, aparelho real, e o contraste do que o navegador desenha sozinho.
- O símbolo está embutido no HTML, copiado dos SVGs da prancha v4. Os fundos suaves das etiquetas, do aviso e do campo não vêm da prancha v4: foram escolhidos aqui e dependem da aprovação do Vinícius.

Dados, nomes e IPs são fictícios.

## Navegação (revisões de 13/11 e 14/11)

Feedback recebido do Vinícius: faltava botão de voltar e a navegação não era previsível. Mudanças:

- **Botão "← Voltar"** em todas as telas, exceto a Visão geral e o Login. Volta para a tela anterior; se a tela foi aberta direto por link, vai para a tela-pai.
- **Trilha de navegação clicável** (Visão geral / Área / Tela), mostrada a partir do segundo nível. A raiz tem o mesmo nome do item do menu.
- **Logo clicável**: leva à Visão geral.
- **Menu lateral** só com itens e ícones, sem títulos de grupo, com o item atual destacado. Auditoria aparece apenas no perfil Gestor.
- **Controles do protótipo separados do produto**: a barra escura no topo é só do protótipo (perfil, tema, largura, situação da tela na API e atalhos).
- **Incidente**: abas **Resumo, Linha do tempo, Evidências** (não aparece para o Suporte N1) e **Diagnóstico**; os botões de ação ficam no cartão "Ações". Os estados de IA abrem direto na aba Diagnóstico.
- **Aprovações**: o seletor "Estado da solicitação (simulação do protótipo)" fica como título acima das quatro opções, e os dados do pedido aparecem em lista.
- **Diagnóstico**: o resultado aparece em lista (Causa provável, Verificações sugeridas, Dados enviados à IA), com a etiqueta "Hipótese · requer verificação".
- **Leitura**: mesmo espaçamento entre blocos em todas as telas, linhas de texto limitadas a cerca de 70 caracteres e cabeçalhos de tabela menores.
- **Símbolo embutido** no HTML (da prancha v4): o arquivo abre sozinho, sem a pasta identidade-visual.

### Por que (Lei de Jakob)
Jakob Nielsen observou que as pessoas passam a maior parte do tempo em outros sites e aplicativos e esperam que o seu funcione como os que já conhecem. Por isso o protótipo segue convenções: voltar no canto superior esquerdo, trilha de navegação, logo que leva ao início, menu lateral com item ativo. Fonte: https://lawsofux.com/jakobs-law/
