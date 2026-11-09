# DS-08 · Contraste da identidade v4 no painel

**Situação:** medido em 09/11/2026. A identidade v4 (opção 1 de `decisoes.md`) foi aplicada aos tokens de `frontend/src/styles/tokens.css`. Este documento registra o que foi medido e o que não foi.

## Como foi medido

1. **Pares de tokens:** script com a fórmula WCAG 2.1, sobre os valores de `tokens.css`.
2. **Painel renderizado:** Chrome sem interface (Linux), com o painel em modo mock, perfil gestor, tema escuro e claro, 1440 px, cenários normal, `?cenario=erro` e `?cenario=falha-trilha`, em todas as áreas e na tela de login. O script leu a cor e o fundo de cada elemento com texto visível (de 22 a 86 textos por tela).
3. **Hover do botão:** calculado a partir do filtro `brightness(1.12)` do CSS. **Não** foi medido com o ponteiro sobre o botão.

Mínimos: texto 4,5:1; borda de campo e foco 3:1. Separadores decorativos não têm mínimo.

## Mapa de tokens

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `--bg` | `#0a1e30` | `#f3f6f8` | Fundo |
| `--surface` | `#11293d` | `#ffffff` | Cartões |
| `--field` | `#0a1e30` | `#ffffff` | Campos |
| `--fg` | `#e3eef6` | `#0a1e30` | Texto |
| `--muted` | `#9fb3c4` | `#4f6577` | Texto de apoio e "Desconhecido" |
| `--line` | `#4f7c9e` | `#4f6577` | Borda funcional (campos, botões) |
| `--separator` | `#2c4a63` | `#c5ced3` | Só decoração (cartões, linhas de tabela) |
| `--accent` e `--button` | `#a5b4fc` | `#3730a3` | Marca, links, botão |
| `--button-fg` | `#0a1e30` | `#ffffff` | Texto do botão |
| `--focus` | `#f5d773` | `#7b3e00` | Foco do teclado (mantido) |
| `--error` e `--error-fg` | `#3a1b1e` e `#ff9e94` | `#fdecea` e `#a82a20` | Aviso de erro |
| `--good`, `--bad`, `--warn` | `#abebcf`, `#ff9e94`, `#ffd479` | `#15563c`, `#a82a20`, `#7a4a00` | Estados |

`--error`, `--field` e `--separator` (no escuro) foram escolhidos aqui, porque a prancha v4 não os define. `--warn` ainda não é usado por nenhuma tela (a DS-10 cria as etiquetas).

## Pares de tokens

| Par | Escuro | Claro | Mínimo |
|---|---|---|---|
| Texto sobre fundo | 14,36 | 15,59 | 4,5 |
| Texto sobre cartão | 12,66 | 16,92 | 4,5 |
| Texto de apoio sobre fundo | 7,83 | 5,59 | 4,5 |
| Texto de apoio sobre cartão | 6,90 | 6,07 | 4,5 |
| Marca sobre fundo | 8,49 | 9,15 | 4,5 |
| Marca sobre cartão | 7,48 | 9,93 | 4,5 |
| Texto do botão | 8,49 | 9,93 | 4,5 |
| Disponível sobre cartão | 11,02 | 8,65 | 4,5 |
| Atenção sobre cartão | 10,61 | 7,48 | 4,5 |
| Erro sobre cartão | 7,51 | 6,96 | 4,5 |
| Texto do aviso de erro | 7,80 | 6,09 | 4,5 |
| Borda de campo sobre cartão | 3,34 | 6,07 | 3 |
| Borda de campo sobre fundo | 3,79 | 5,59 | 3 |
| Foco sobre cartão | 10,54 | 8,30 | 3 |
| Foco sobre fundo | 11,96 | 7,64 | 3 |
| Separador decorativo | 1,61 | 1,60 | sem mínimo |

## Painel renderizado

- **Textos com botão habilitado:** o menor valor foi **6,90:1 no escuro** e **5,59:1 no claro**. Nenhum ficou abaixo de 4,5:1.
- **Borda de campo (login e Diagnóstico):** o menor valor foi **3,34:1**.
- **Botão desabilitado:** **2,76:1 no escuro e 2,59:1 no claro (e 3,91:1 e 4,03:1 em "Rejeitar")**. Fica abaixo de 4,5:1 porque o estilo atual usa `opacity: .65`. O WCAG não exige contraste mínimo de componentes desabilitados, mas o plano pede que o desabilitado não dependa só de cor e transparência. **Fica para a DS-09 (botão com estados).** Hoje o estado só se distingue pelo esmaecimento e pelo cursor.
- **Hover do botão principal (cálculo):** 9,99:1 no escuro e 8,69:1 no claro, acima do mínimo.

## Não medido

- Hover dos botões das abas e do botão secundário.
- Foco renderizado sobre cada superfície (só o par de tokens foi medido).
- Larguras de 390 px e de 320 px (o contraste não depende da largura, mas a leitura não foi conferida).
- Perfis suporte e analista, cenários vazio e lento.
- A prancha v4 não define borda de campo nem aviso de erro: os valores acima são propostas desta tarefa.
- Nenhuma verificação com o axe (fica para o Vinícius e o Iohan, em marcos).

## Transições de cor

Nenhuma regra `transition` existe em `App.css`. O tema troca sem animação.
