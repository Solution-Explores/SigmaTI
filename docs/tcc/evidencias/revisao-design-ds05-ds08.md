# Revisão de design dos PRs da Joyce (DS-05 a DS-08)

Revisão de **10/11/2026** dos PRs #86, #87, #95 e #96, feita por dois agentes de design do Claude (critérios das skills `design-critique`, `design-system` e `accessibility-review`) e conferida por Vinícius Lima. Os agentes só leram: nada foi postado nem alterado no repositório. Dados e telas são do modo mock, com dados fictícios.

Esta é uma conferência assistida por IA, **não** substitui a revisão humana nem o teste com leitor de tela.

## Resumo

| PR | Tarefa | Estado em 10/11 | Critérios do cartão | Veredito da revisão |
|---|---|---|---|---|
| [#86](https://github.com/Solution-Explores/SigmaTI/pull/86) | DS-05 · Fonte | Rascunho | Cumpridos (fonte, licença e motivo) | Integrar com ajuste |
| [#87](https://github.com/Solution-Explores/SigmaTI/pull/87) | DS-06 · Tokens | Rascunho | Cumpridos (tela igual, 3 comandos passam) | Pode integrar |
| [#95](https://github.com/Solution-Explores/SigmaTI/pull/95) | DS-07 · Escalas | Rascunho, base no #87 | Cumpridos (escala aplicada, sem texto cortado na página) | Pode integrar |
| [#96](https://github.com/Solution-Explores/SigmaTI/pull/96) | DS-08 · Paleta v4 | Rascunho, base no #95 | 5 de 6 (o botão desabilitado ficou para a DS-09) | Integrar com ajuste |

Nenhum achado bloqueia o merge. Ordem de integração: #87, #95, #96, com o #86 antes ou depois.

## #87 (DS-06, tokens em um arquivo)

- **Equivalência dos valores:** comparação por script das duas regras do `App.css` original contra o `tokens.css`: 14 variáveis no escuro e 13 no claro, **0 diferenças**.
- **Comandos em `frontend/`:** `npm ci`, `npm run lint`, `npm test` (20 passed) e `npm run build` passaram. O PR declara 19 testes; a diferença vem da base.
- **`@import` no Vite:** o CSS do build traz o bloco de variáveis inlinado, sem requisição extra.
- **Arquivos proibidos** (`api.js`, hooks, `mockApi.js`, `index.css`): nenhum alterado.
- **Navegador (Vinícius, 05/11):** painel da branch e da `develop` lado a lado, gestor, 5 abas, claro e escuro. Cor, fundo, borda, contorno, sombra, fonte e cursor idênticos, e o foco por teclado idêntico em todos os elementos focáveis.
- **Pendências sem bloqueio:** o cartão pede "cores, fontes e espaços" e o PR só moveu as cores (fontes e espaços ficam para a DS-07); o apontamento no `DESIGN.md` ficou de fora e deve entrar na DS-08; o comentário "único lugar para ajustar cores" é forte demais se houver cor fixa fora das variáveis (não foi varrido).

## #86 (DS-05, tipografia)

- **Cumpre o cartão:** o `tipografia.md` traz a fonte (pilha com Segoe UI), a licença e o motivo. Nenhum arquivo de fonte entra no repositório e nenhuma fonte vem de servidor externo. Coerente com o `MASTER.md` do protótipo.
- **Contrastes recalculados:** 15,588:1 no claro e 14,361:1 no escuro (o PR declara 15,59 e 14,36).
- **Ajustes recomendados:**
  1. A prancha da identidade v4, já na `develop`, mostra a Atkinson Hyperlegible como fonte principal, e o #86 escolhe a Segoe UI. Falta registrar no `decisoes.md` que a tipografia da v4 foi substituída: hoje há duas fontes de verdade.
  2. Depois da aprovação do Vinícius, o status "aguarda revisão" deve passar a "aprovada em dd/mm".
  3. Dizer de forma direta que a legibilidade validada vale para o Windows; em Android, macOS e Linux a fonte será outra.
- **Não conferido:** a licença da Atkinson no repositório oficial (sem acesso à rede), a afirmação de que setas e ✓ não existem na fonte, e a amostra visual da autora, que não está versionada.

## #95 (DS-07, escalas de espaço e de texto)

- Escala de espaço 4, 8, 12, 16, 24, 32, 48 e 64 px, coerente com a do protótipo (4 a 48 px). Os arredondamentos (10→12, 20→24, 28→32, 14→16, 6→8, 3→4, 60→64) não deixaram nada apertado nem folgado demais.
- Em 768, 1024 e 1440 px, nas 5 abas e no tema claro, a página não estoura na horizontal.
- **Sem ajuste novo.** O código do produto congela em 11/11: sem prorrogação aprovada, este trabalho fica na branch.

## #96 (DS-08, paleta v4 e contraste)

### O que passou

- **Foco por teclado (Tab real), gestor, 2 temas, 5 abas:** todo elemento focado tem `:focus-visible` e contorno de 3 px. Escuro `#f5d773`: 11,96:1 com a página e 10,54:1 com o cartão. Claro `#7b3e00`: 7,64:1 e 8,30:1. A ordem é lógica e os botões desabilitados são pulados.
- **Hover real (claro):** botão principal 8,73:1, secundário 8,73:1, aba inativa 16,26:1 e aba ativa 8,73:1. No escuro só foi calculado: 10,0:1, 8,6:1 e 16,2:1.
- **Perfis:** suporte (2 abas), analista (4 abas, sem Auditoria) e gestor (5 abas) têm estilização idêntica. A diferença é só de permissão.
- **Cenários do mock:** `?cenario=erro` (alerta com `role=alert`; 6,09:1 no claro e 7,80:1 no escuro), `?cenario=falha-trilha` ("Falha de integridade detectada", em texto, não só em cor) e `?cenario=vazio` (mensagens claras nas 4 abas).
- **Texto:** nenhum abaixo de 4,5:1; o menor é 5,59:1 no claro e 6,90:1 no escuro.

### Ajustes recomendados (não bloqueiam)

1. **Tabelas cortadas.** Em 768 px a tabela de Saúde tem 810 px dentro de 671 px, e a 6ª coluna fica escondida; no celular a 3ª coluna é cortada. Não há dica visual de rolagem. Já existia no #95 e na `develop`, então não é regressão. Em 1024 e 1440 px cabe tudo.
2. **Botões "Tema" e "Sair"** com o mesmo índigo cheio das ações principais: parecem principais e se confundem com a aba ativa. Usar a variante secundária (previsto na DS-09).
3. **Borda do cartão** com `--separator` de 1,6:1 (claro `#c5ced3`, escuro `#2c4a63`). É só decorativa e não reprova o WCAG 1.4.11, mas no #95 a borda era visível e no #96 enfraquece nos dois temas.
4. **Diferença em relação ao protótipo (`MASTER.md`):** o protótipo usa azul (`#1D4ED8` e `#60A5FA`) e raio de controles de 8 px; o #96 usa índigo (`#3730a3` e `#a5b4fc`) e raios de 5 a 6 px. **Direção combinada em 10/11/2026** entre Vinícius e Joyce: o protótipo é referência, e a evolução sobre o design atual do painel é esperada. A diferença não é problema.
5. Opcional: em `?cenario=erro` aparecem "Tentar novamente" e "Atualizar incidentes" no mesmo cartão, com função quase igual.

### Botão desabilitado: o número certo

O `contraste.md` do #96 declara **2,6 a 2,8:1** para o botão desabilitado principal. A conferência **não reproduziu** esse valor. Com `opacity: .65` sobre o fundo do cartão:

| Tema | Texto e botão | Contraste medido | Sem a opacidade |
|---|---|---|---|
| Claro | `#ffffff` sobre `#3730a3` | **3,9:1** | 9,93:1 |
| Escuro | `#0a1e30` sobre `#a5b4fc` | **4,4:1** | 8,49:1 |

Valores conferidos por dois métodos independentes (agente e cálculo próprio pela fórmula WCAG). O secundário "Rejeitar" bate com o que a autora declara (3,91:1 e 4,03:1). O WCAG não exige contraste mínimo de componente desabilitado, então não bloqueia, mas o número no `contraste.md` deve ser corrigido. O estado próprio do botão, sem depender de opacidade, é a DS-09.

## Capturas

Todas conferidas: o `data-theme` da página e o visual correspondem ao tema indicado. Gestor, modo mock.

| Arquivo | O que mostra |
|---|---|
| [pr95-claro-incidentes-1440-gestor.jpg](capturas-design-ds05-ds08/pr95-claro-incidentes-1440-gestor.jpg) | #95, claro, Incidentes (azul antigo, borda do cartão visível) |
| [pr96-claro-incidentes-1440-gestor.jpg](capturas-design-ds05-ds08/pr96-claro-incidentes-1440-gestor.jpg) | #96, claro, Incidentes (índigo) |
| [pr96-claro-saude-768-gestor.jpg](capturas-design-ds05-ds08/pr96-claro-saude-768-gestor.jpg) | #96, claro, Saúde a 768 px (tabela cortada) |
| [pr96-claro-erro-incidentes-1440-gestor.jpg](capturas-design-ds05-ds08/pr96-claro-erro-incidentes-1440-gestor.jpg) | #96, claro, `?cenario=erro` |
| [pr96-escuro-falha-trilha-1440-gestor.jpg](capturas-design-ds05-ds08/pr96-escuro-falha-trilha-1440-gestor.jpg) | #96, escuro, `?cenario=falha-trilha` |

As capturas são limitadas pela janela do navegador do painel (800×500 ou 768×1024), não 1440 px reais.

## Limites desta revisão

- Sem leitor de tela (NVDA, VoiceOver) e sem zoom de 200%.
- Hover com ponteiro real só no tema claro; no escuro foi calculado.
- Tab real só no perfil gestor; nos perfis suporte e analista foi conferido apenas quais abas e botões aparecem.
- Tab real só no #96 (as regras de foco do #95 são iguais, mas não foram percorridas).
- Cenário `?cenario=lento` não foi conferido.
- Fonte Segoe UI real em macOS, Linux e celular, e o `axe`, ficam para Vinícius e Iohan, em marcos.
- O #86 e o #87 não têm tela nova; para o #87, a aparência foi conferida pelo Vinícius em 05/11.

## Relação com os cartões do Trello

DS-05, DS-06, DS-07 e DS-08 permanecem em "Revisão e testes" até a integração. Cada cartão passa a "Concluído" só depois do merge na `develop`.
