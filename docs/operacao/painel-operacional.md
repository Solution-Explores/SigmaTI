# Painel operacional

Como executar e testar o painel em React. Parte do conteúdo que antes estava no README.

O frontend fica em `frontend/` e usa a API de `VITE_API_URL` (padrão `http://localhost:8000`). Rode `npm ci` e `npm run dev` nessa pasta. A API precisa de `SIGMA_DATABASE_URL`, das migrações aplicadas e de usuários cadastrados, conforme os guias de [identidades](../../engenharia/docs/07-persistencia-identidades.md) e de [coleta](../../engenharia/docs/09-coleta-eventos.md). Sem persistência operacional, as áreas mostram indisponibilidade (503), sem dados fictícios no lugar.

| Perfil | Áreas do painel |
|---|---|
| `suporte_n1` | Saúde dos serviços e diagnóstico |
| `analista_redes` | Áreas anteriores, incidentes e aprovações |
| `gestor_ti` | Todas as áreas, incluindo auditoria |

A API também aplica a autorização. Esconder a navegação não substitui o controle de acesso por perfil. O tema claro ou escuro muda no cabeçalho. Sessão e cursor SSE ficam em memória, então recarregar exige login. O SSE usa Bearer e `Last-Event-ID`, reconecta com espera progressiva e atualiza os dados ao conectar. Há uma consulta de recuperação a cada 15 segundos.

A área de saúde distingue dados ausentes ou desatualizados de disponibilidade. O orçamento parcial é um limite máximo, e a projeção exige cobertura integral da janela. O MTTD aparece sem amostras enquanto não houver um início real de falha registrado. Aprovar ou rejeitar exige justificativa na interface, outro operador e o papel mínimo. Essa página registra decisões e não executa comandos. A integridade JSONL mostrada na auditoria cobre a trilha de sondas, e os eventos do PostgreSQL aparecem à parte.

Testes:

```bash
npm test                      # componentes
npm run test:e2e              # diagnóstico, no navegador
python scripts/validate_postgres.py --tests "backend/tests/test_panel_api.py backend/tests/test_panel_e2e.py"
```

O último comando faz o ensaio completo com um banco descartável. Ele prepara um schema isolado e publica capturas em `test-results/`. Instale o Chromium com `npx playwright install chromium`. No Windows, `SIGMA_BROWSER_CHANNEL=chrome` usa o Chrome já instalado.

Validação e limites: [evidências do painel](../specs/017-painel-operacional/brief.md).
