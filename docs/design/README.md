# Design do painel: protótipo e referências

Material copiado em 21/10/2026 de `Desktop\sigma-teste`, só para consulta. Nada daqui está no Git nem no código da `develop`.

| Pasta | Conteúdo |
|---|---|
| `prototipo-figcraft/` | Protótipo navegável de baixa fidelidade: 106 quadros em 11 páginas, com fluxos de N1, analista e gestor. `MASTER.md` define o sistema visual. `figcraft/handoff.md` traz as regras de implementação. `figcraft/review.html` é uma galeria que abre no navegador. As prévias PNG ficam em `figcraft/previews/`. |
| `referencia-sigma-teste/frontend-src/` | Redesenho já implementado em React no `sigma-teste`, com `tokens.css`, `Dashboard.jsx` e `ui.jsx`. Usa **dados fictícios fixos** (`data/demo.js`), não a API. |
| `referencia-sigma-teste/specs/` | Validações de acessibilidade e layout desse redesenho, com capturas em 375 e 1440 px e temas claro e escuro. |

Não foi copiado: `.env`, `.venv`, `.runtime/` e o resto do `sigma-teste`.

## Comparação com o painel atual (`develop@8cb1e23`)

| Tema | Painel atual | Protótipo | Depende de backend novo? |
|---|---|---|---|
| Visual (tokens, tema claro/escuro, Segoe UI, foco de 3px) | CSS simples, 5 KB, sem tokens | Sistema completo em `MASTER.md` e `tokens.css` | Não |
| Navegação | Abas no topo | Menu lateral, trilha de navegação, indicador "Coleta conectada" e usuário com perfil | Não: SSE e `/api/auth` já existem |
| Visão geral | Não existe | Cartões (críticos, sem responsável, meus atendimentos), incidentes prioritários, saúde da coleta | Em parte: sai de `/incidentes/resumo` e `/saude`; "sem responsável" exige responsável |
| Incidente em detalhe | Linha com Reconhecer e Resolver | Estado, condição medida, responsável, linha do tempo, evidências, IA contextual | Sim: responsável, ações registradas, escalonamento, versão para concorrência |
| Saúde do sistema | Saúde por alvo e SLO | Tabela por serviço (API, coleta, IA, automação, backup) | Em parte |
| IA | Aba Diagnóstico separada | Painel dentro do incidente, "hipótese a verificar", conteúdo generalizado | Pequeno: o incidente precisa ir junto na chamada |
| Equipamentos, relatórios, usuários, origens, regras, agendamentos | Não existem | Telas completas | Sim: são os módulos das issues #16 a #22 e #30 |

## Proposta em etapas (depois da `v1.0.0`)

1. **Camada visual, só frontend e de baixo risco:**
   - `tokens.css` e o tema escuro;
   - menu lateral e cabeçalho com estado da coleta;
   - Visão geral com os dados que a API já entrega;
   - Saúde em formato de tabela.

   O redesenho de `referencia-sigma-teste/` serve de ponto de partida, trocando os dados fixos pela API.
2. **Detalhe do incidente:** linha do tempo a partir dos eventos operacionais e IA contextual. Exige pequenos ajustes de API.
3. **Atendimento completo** (assumir, registrar ação, escalar, validar, reabrir): exige modelo de dados novo. Vira trabalho futuro ou issue nova.
4. **Gestão e administração:** segue as issues de expansão já abertas.

Antes de sábado, nada disso entra: o código está congelado para a demonstração.
