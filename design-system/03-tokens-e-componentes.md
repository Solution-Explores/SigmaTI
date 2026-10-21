# 3. Tokens e componentes atuais

Fonte de verdade hoje: `sigma-frontend/src/App.css`. Os tokens são variáveis CSS definidas em
`.app-surface`; o tema claro sobrescreve as mesmas variáveis em `.app-surface[data-theme="light"]`.
Para trocar uma cor no sistema inteiro, troque a variável, nunca a cor dentro de um componente.

## Cores

| Token (`var(--…)`) | Papel | Escuro | Claro | Contraste sobre `surface` (escuro / claro) |
|---|---|---|---|---|
| `--bg` | Fundo da página | `#13131a` | `#f2f5f9` | — |
| `--surface` | Fundo de painel e cartão | `#202632` | `#ffffff` | — |
| `--field` | Fundo de campo, `pre` e diagnóstico | `#121722` | `#f7f9fc` | — |
| `--fg` | Texto principal | `#eef2f8` | `#17283c` | 13,5 / 14,9 |
| `--muted` | Texto secundário | `#c3cedd` | `#41536c` | 9,5 / 7,8 |
| `--line` | Bordas e separadores | `#65748a` | `#63758e` | 3,2 / 4,7 (mínimo de 3:1 para bordas) |
| `--accent` | Título, link, foco de ação | `#91caff` | `#12568e` | 8,7 / 7,6 |
| `--button` | Fundo do botão principal | `#12568e` | `#12568e` | branco sobre ele: 7,6 |
| `--button-fg` | Texto do botão principal | `#ffffff` | herdado | — |
| `--focus` | Contorno de foco do teclado | `#f5d773` | `#7b3e00` | 10,7 / 8,3 |
| `--good` | Estado positivo ("Disponível") | `#abebcf` | `#15563c` | 11,2 / 8,7 |
| `--bad` | Estado negativo ("Indisponível") | `#ffabb6` | `#8c1830` | 8,5 / 9,2 |
| `--error` / `--error-fg` | Caixa de erro (fundo / texto) | `#54202a` / `#ffe0e4` | `#fff0f2` / `#7d172c` | 10,5 / 9,4 entre si |

Os valores foram calculados pela fórmula WCAG 2.1. Texto exige ≥ 4,5:1 e bordas/ícones ≥ 3:1.
Não há cor de **alerta** (amarelo/laranja) para "em risco": hoje `at_risk` não tem badge próprio.
Se for criada, precisa de texto junto e de contraste conferido nos dois temas.

## Tipografia, forma e espaço

| Categoria | Valores atuais |
|---|---|
| Fonte | `system-ui, sans-serif` (sem fonte de marca) |
| Tamanhos | `h1` `clamp(1.4rem, 3vw, 2rem)` · `h2` 1.5rem · `h3` 1.1rem · corpo 1rem · rótulo/badge .85rem |
| Peso | títulos 700, cabeçalho de tabela 600 |
| Números | `font-variant-numeric: tabular-nums` em tabelas e métricas |
| Largura de texto | parágrafos com no máximo 75ch |
| Raio | campo 5px · botão 6px · painel 12px · badge 16px |
| Espaço | 8 · 10 · 16 · 24 · 28 px (não há escala formal) |
| Layout | contêiner de no máximo 1180px; quebra única em 720px (duas e três colunas viram uma) |
| Sombra | nenhuma; profundidade só por fundo e borda |

## Componentes (classes CSS)

| Componente | Classe / elemento | Onde é usado | Variações |
|---|---|---|---|
| Botão principal | `.sigma-panel button` | Entrar, Reconhecer, Aprovar | `:hover` brilho 1.12 · `:disabled` opacidade .65 |
| Botão secundário | `button.secondary` | Atualizar…, Rejeitar | — |
| Navegação | `nav button[aria-current="page"]` | Abas das áreas | ativa / inativa |
| Campo | `input`, `textarea`, `select` | Login, aprovações, diagnóstico | desabilitado |
| Painel | `.card`, `.workspace` | Login e área principal | — |
| Badge de estado | `.badge.up` · `.down` · `.unknown` · `.inactive` | Saúde | sempre com texto |
| Tabela | `.table-scroll > table` | Saúde, incidentes, auditoria | rolagem horizontal com foco |
| Métrica | `.metric-grid section dl` | MTTD/MTTA/MTTR | com amostras / sem amostras |
| Item de aprovação | `.approval-item` | Aprovações | própria / perfil insuficiente / expirada |
| Mensagens | `.error`, `.notice`, `.empty`, `.muted`, `.stream-state` | Todas | erro com `role="alert"` |
| Expansível | `details.request-details` | Nova solicitação | aberto / fechado |

## Regras de acessibilidade já cobradas

- `:focus-visible` com contorno de 3px e afastamento de 3px em toda a superfície;
- alvo de toque mínimo de 44px nos botões;
- ao trocar de área, o foco vai para o título (`h2` com `tabIndex=-1`);
- erros com `role="alert"` e feedback com `role="status"`;
- sem transição de cor ao trocar o tema. Uma transição já reprovou o CI por contraste intermediário de 2,1:1.
  Se quiser animar algo, anime opacidade ou posição, nunca as cores de texto e fundo.

## Sugestão de evolução (decisão da Joyce)

1. Mover os tokens para `src/styles/tokens.css` e nomeá-los por papel (`--color-text`, `--space-4`, `--radius-panel`).
2. Criar uma escala de espaçamento (4/8/12/16/24/32) e de tipografia.
3. Extrair componentes React reutilizáveis: `Button`, `Badge`, `DataTable`, `Panel`, `Alert`, `EmptyState`.
4. Definir os badges que faltam (severidade P1–P3, estado do incidente, orçamento em risco).
5. Atualizar `DESIGN.md` ao final, porque ele é a referência citada no TCC.
