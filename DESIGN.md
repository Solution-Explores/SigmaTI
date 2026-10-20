---
name: SIGMA
description: Painel operacional de monitoramento de rede
colors:
  dark-bg: "#13131a"
  dark-surface: "#202632"
  dark-field: "#121722"
  dark-fg: "#eef2f8"
  dark-muted: "#c3cedd"
  dark-line: "#65748a"
  dark-accent: "#91caff"
  button: "#12568e"
  button-fg: "#ffffff"
  dark-focus: "#f5d773"
  dark-error: "#54202a"
  dark-error-fg: "#ffe0e4"
  dark-good: "#abebcf"
  dark-bad: "#ffabb6"
  light-bg: "#f2f5f9"
  light-surface: "#ffffff"
  light-field: "#f7f9fc"
  light-fg: "#17283c"
  light-muted: "#41536c"
  light-line: "#63758e"
  light-accent: "#12568e"
  light-focus: "#7b3e00"
  light-error: "#fff0f2"
  light-error-fg: "#7d172c"
  light-good: "#15563c"
  light-bad: "#8c1830"
typography:
  headline:
    fontFamily: "system-ui, sans-serif"
    fontSize: "clamp(1.4rem, 3vw, 2rem)"
    fontWeight: 700
    lineHeight: 1.2
  title:
    fontSize: "1.5rem"
    fontWeight: 700
  body:
    fontFamily: "system-ui, sans-serif"
    lineHeight: 1.5
  label:
    fontSize: ".85rem"
rounded:
  field: "5px"
  control: "6px"
  panel: "12px"
  badge: "16px"
spacing:
  small: "8px"
  field: "10px"
  medium: "16px"
  panel: "24px"
  metrics: "28px"
components:
  button-primary:
    backgroundColor: "{colors.button}"
    textColor: "{colors.button-fg}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
  button-secondary:
    backgroundColor: "{colors.dark-surface}"
    textColor: "{colors.dark-accent}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
  input:
    backgroundColor: "{colors.dark-field}"
    textColor: "{colors.dark-fg}"
    rounded: "{rounded.field}"
    padding: "10px"
  panel:
    backgroundColor: "{colors.dark-surface}"
    rounded: "{rounded.panel}"
    padding: "24px"
---

# Design System: SIGMA

## Overview

Registro factual da identidade existente: azul sobre fundo escuro, fonte de sistema e painéis planos com borda. O tema claro foi requerido pela issue #15. Metáfora criativa e adjetivos de marca não foram definidos; não se afirma aprovação humana de uma composição.

**Key Characteristics:**
- Painéis planos com borda.
- Tema escuro inicial e alternância para claro.
- Tabelas, formulários e estados em português.

Fonte normativa: `sigma-frontend/src/App.css` e `index.css`. O contrato da superfície está em `specs/017-painel-operacional/brief.md`.

## Colors

### Primary
Azul identifica títulos, ações e navegação ativa. Os tokens de acento variam por tema; a ação principal mantém o token button.

### Neutral
bg, surface e field distinguem página, painel e entrada; fg, muted e line sustentam leitura e contornos. Prefixos indicam tema. No tema claro button-fg é herdado. good, bad e error reforçam estados textuais; focus marca teclado.

**The Semantic State Rule.** Estados mantêm rótulos textuais; cor apenas reforça a informação.

## Typography

Fonte de sistema com fallback sans-serif, herdada pelos controles. O título principal usa headline, títulos de área usam title e subtítulos usam 1.1rem. O corpo herda tamanho do navegador e limita parágrafos a 75ch. Tabelas e métricas usam algarismos tabulares. Não há fonte de marca confirmada.

## Layout

Contêiner central com máximo de 1180px e margem lateral total de 32px. Cabeçalho e sessão usam flex; navegação quebra linhas. Diagnóstico tem duas colunas e métricas três. Até 720px ambos viram uma coluna, cabeçalho e sessão quebram, workspace usa preenchimento 18px 14px e margem lateral total passa a 24px. Tabelas usam regiões com rolagem horizontal e foco de teclado. Corpo tem mínimo de 320px.

## Elevation & Depth

Sem sombras definidas; fundos e bordas separam níveis. Botões mudam de cor sem transição temporal; a troca de tema aplica as cores finais diretamente.

## Shapes

Painéis usam panel, campos field, botões control e badges badge. Bordas contínuas de 1px separam painéis, controles e linhas de tabela.

## Components

### Buttons
Ação principal azul, altura mínima de 44px e borda de acento. Secundária usa superfície e texto de acento. Hover aumenta brilho em 1.12; desabilitado usa opacidade .65 e cursor not-allowed. Foco visível tem contorno de 3px afastado 3px.

### Inputs / Fields
Largura integral, fundo próprio, borda e fonte herdada. Formulários empilham rótulos e controles. Justificativa é obrigatória nas decisões; autoria, papel insuficiente e expiração têm explicações textuais.

### Navigation
Botões transparentes com borda; aria-current e fundo principal marcam área ativa. Em telas estreitas a base flexível é 130px. Trocar área transfere foco ao título.

### Chips
Badge de estado combina borda na cor do texto e rótulo de disponibilidade, ausência de dados ou desativação.

### Cards / Containers
Fundo de superfície, borda e preenchimento panel. Tabelas têm legendas, cabeçalhos e separadores. Erros usam cores próprias; carregamento, ausência de dados e falhas têm mensagens explícitas e atualização manual.

## Do's and Don'ts

- Do preserve os papéis semânticos nos dois temas.
- Do mantenha rótulos textuais para estados e foco visível.
- Do permita rolagem horizontal nas tabelas em telas estreitas.
- Don't apresente ausência de medição como disponibilidade.
- Don't use cor como único sinal de estado.
