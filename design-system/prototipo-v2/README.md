# Protótipo v2 do SigmaTI (visual da Joyce)

Protótipo **navegável** do painel, feito em HTML, com a identidade v4 (`../identidade-visual/decisoes.md`), tema claro e escuro e larguras de computador, 1024, tablet e celular.

## Como abrir

Abra `prototipo-v2/index.html` no navegador. Não precisa instalar nada nem ter outras pastas ao lado.

## O que é e o que não é

- É um **desenho navegável**. Não é o painel: não fala com a API, não grava nada e os dados são fictícios.
- **Fase 1:** 56 das 106 telas do protótipo do Vinícius (login, visão geral, fila, histórico, as 16 variações do incidente por perfil, estados e exceções, Saúde, Auditoria, celular, tablet, 1024 e tema escuro), mais a biblioteca de componentes e as telas que o painel tem e o protótipo dele não tem: **Aprovações** e **Diagnóstico**.
- **Fase 2 (não feita):** as 50 telas restantes. O **Mapa de telas** (`#/mapa`) lista as 106, diz qual já está aqui e qual fica para depois.
- Cada tela mostra a **situação na API**, conforme `design-system/exemplo/README.md`: "Só front", "Integração simples" ou "API nova". Telas de "API nova" são só desenho e não funcionam no painel real.

## Medido e não medido

- Pares de cor das etiquetas e do texto: todos acima de 4,5:1 nos dois temas (menor valor 5,19:1 no claro e 6,03:1 no escuro, calculado por script sobre os valores do arquivo; botões e texto de apoio entre eles).
- Foi aberta cada uma das 56 rotas num navegador automático: nenhuma ficou vazia e nenhuma deu erro de JavaScript.
- **Não verificado:** leitor de tela, ordem de foco do teclado, impressão, Safari e Firefox, e o contraste do que o navegador desenha sozinho.
- O símbolo está embutido no HTML, copiado dos SVGs da prancha v4. Os fundos suaves das etiquetas, do aviso e do campo não vêm da prancha v4: foram escolhidos aqui e dependem da aprovação do Vinícius.

Dados, nomes e IPs são fictícios.

## Navegação (revisão de 13/11, a pedido do Vinícius)

Feedback recebido: faltava botão de voltar e a navegação não era previsível. Mudanças:

- **Botão "← Voltar"** em todas as telas, exceto a Visão geral e o Login. Volta para a tela anterior; se a tela foi aberta direto por link, vai para a tela-pai.
- **Trilha de navegação clicável** (Início / Área / Tela). A última parte indica onde você está.
- **Logo clicável**: leva à Visão geral.
- **Menu lateral agrupado** (Operação, Monitoramento, Decisões, Ferramentas), com o item atual destacado.
- **Controles do protótipo separados do produto**: a barra escura no topo é só do protótipo (perfil, tema, largura, atalhos).
- **"Situação na API"** passou para uma linha própria sob o título.
- **Incidente**: as ações ficam no cartão "O que fazer agora", separado da linha do tempo.
- **Símbolo embutido** no HTML (da prancha v4): o arquivo abre sozinho, sem a pasta identidade-visual.

### Por que (Lei de Jakob)
Jakob Nielsen observou que as pessoas passam a maior parte do tempo em outros sites e aplicativos e esperam que o seu funcione como os que já conhecem. Por isso o protótipo segue convenções: voltar no canto superior esquerdo, trilha de navegação, logo que leva ao início, menu lateral com item ativo. Fonte: https://lawsofux.com/jakobs-law/

### Testado
56 rotas abertas sem erro de JavaScript; voltar e trilha testados; sem rolagem lateral em 375 px, claro e escuro. Não testado em leitor de tela nem em aparelho real.
