# Tipografia (DS-05)

**Situação: ESCOLHA DA JOYCE, em 04/11/2026 (opção B, pilha Segoe UI).** Aguarda revisão do Vinícius no PR. Nada aqui foi aplicado ao painel: a aplicação é das tarefas DS-06 e DS-07. Este documento não altera `index.css` nem nenhum arquivo do painel.

## 1. Decisão

Pilha da interface (texto, rótulos, números):

```css
font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif;
```

Pesos permitidos:

| Peso | Uso |
| --- | --- |
| 400 | Texto corrido, tabelas, campos |
| 600 | Rótulos, títulos de seção, botões |
| 700 | Títulos principais e valores em destaque |

Qualquer outro peso deve ser registrado aqui antes de ser usado.

Números de métricas, horários, IPs e tabelas devem usar `font-variant-numeric: tabular-nums`, para os algarismos alinharem em coluna. O efeito real dessa regra na Segoe UI ainda precisa ser conferido na DS-07.

## 2. Estratégia local

- Nenhum arquivo de fonte entra no repositório e nenhuma fonte é carregada de servidor externo (sem Google Fonts, sem CDN).
- A Segoe UI vem instalada no Windows. O arquivo dela **não é redistribuído**, pois não é uma fonte livre.
- Sem a Segoe UI (outro sistema operacional), o navegador usa a fonte do sistema (`system-ui`) e as demais da pilha. Isso pode mudar o espaçamento e a largura dos textos. Esse caso não foi testado.

## 3. Como foi comparado

A comparação foi feita pela Joyce em uma página de amostra local (`amostra-fontes.html`, gerada para esta tarefa e **não versionada**), com três pilhas lado a lado nos dois temas:

- A: `system-ui, sans-serif`
- B: `"Segoe UI", system-ui, sans-serif`
- C: Atkinson Hyperlegible Next, com Segoe UI e system-ui de reserva

A amostra trazia acentos do português, números com vírgula e ponto, as frases "Sem dados recentes", "Até 15 min" e "Sem início real de falha registrado", caracteres parecidos (`Il1 O0 rn m`) e um nome de equipamento fictício comprido. Foi uma comparação visual, sem teste com usuários. Escolha: **B**.

Contraste do texto da amostra (calculado por script): `#0A1E30` sobre `#F3F6F8` = 15,59:1 no tema claro, e `#E3EEF6` sobre `#0A1E30` = 14,36:1 no tema escuro. Os dois passam de 4,5:1. O contraste das demais cores continua nas tabelas do `decisoes.md`.

## 4. Alternativa considerada: Atkinson Hyperlegible Next (não adotada)

Registrada para uso futuro:

- Licença **SIL Open Font License 1.1**, conferida em 31/10/2026 no arquivo `OFL.txt` do repositório oficial `googlefonts/atkinson-hyperlegible-next` (copyright 2020-2024 The Atkinson Hyperlegible Next Project Authors). Versão da fonte lida: 2.001.
- Tem glifos para os acentos do português testados e números tabulares (`tnum`). **Não** tem as setas (→ ↑ ↓), o ✓ nem o ●; esses caracteres cairiam na fonte de reserva.
- A versão original de 2020 teve uma licença própria do Braille Institute antes de migrar para a OFL. Se a fonte for adotada, registrar a versão exata e levar o `OFL.txt` junto dos arquivos.
- Se for adotada, entra em um PR próprio, com os arquivos de fonte locais (um `woff2` variável de 48 KB cobre os pesos 200 a 800).

## 5. IBM Plex Mono (não incluída)

A prancha da identidade sugeria essa fonte para texto monoespaçado. A licença **não foi verificada** no repositório oficial da IBM (só páginas de terceiros indicam OFL 1.1, com nome reservado "Plex"). Não é exigida por esta tarefa. Se IDs e IPs precisarem de monoespaçada, decidir depois, com a licença conferida.

## 6. Logotipos

O nome "SigmaTI" nos SVGs de `design-system/identidade-visual/` está em curvas (os arquivos não têm elemento de texto). Ele não depende da fonte da interface e não deve ser recomposto com ela.

## 7. O que ainda não foi verificado

- **A legibilidade medida vale para o Windows (Segoe UI).** Em Android, macOS, iOS e Linux a fonte será outra (system-ui ou Helvetica Neue/Arial) e a aparência nelas não foi medida; quais sistemas os usuários do painel usam também não foi verificado.
- Se os pesos 600 e 700 aparecem como Semibold e Bold em todas as versões do Windows usadas.
- Comportamento a 390 px e com zoom de 200% com a fonte aplicada: só dá para medir na DS-07, quando a fonte for aplicada ao painel.
- Nomes extensos reais do mock (`src/mock/data.js`): a amostra usou texto fictício. Conferir com `gestor.joyce` em `/`, Saúde e Incidentes.
- Revisão do Vinícius.

## 8. Próximos passos

1. Revisão do Vinícius neste PR.
2. Depois que o PR da identidade v4 for mesclado, acrescentar ao `README.md` desta pasta um bloco apontando para este arquivo (adiado para evitar conflito no mesmo arquivo).
3. DS-06 e DS-07: aplicar a pilha e as regras de peso e número ao painel.
