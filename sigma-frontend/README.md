# Painel SIGMA

Use Node.js 24 e o lockfile versionado:

```bash
npm ci --include=optional
npm run dev -- --host 127.0.0.1
npm run build
npm run lint
```

Para trabalhar só no visual, sem backend, use a API simulada:

```bash
npm run dev:mock
```

Entre com um usuário iniciado por `suporte`, `analista` ou `gestor` e qualquer senha.
Detalhes e cenários (`?cenario=vazio|erro|lento|falha-trilha`) em
[design-system/01-instalacao-front.md](../design-system/01-instalacao-front.md).
O build de produção não inclui o mock.

A API é configurada por `VITE_API_URL` (padrão `http://localhost:8000`).
Não coloque segredo do servidor em variáveis `VITE_*`.
O login usa `/api/auth/login` e `/api/auth/me`; o token fica só em memória.
Logout revoga a sessão e recarregar a página exige nova autenticação.

Testes de navegador com API e provedor simulado:

```bash
npx playwright install chromium
npm run test:e2e
```

Prepare antes `.venv` na raiz com `requirements-dev.txt`. O Playwright cria
credenciais efêmeras e inicia API/Vite isolados em 18000/5173. Saídas e credenciais
ficam em `test-results/` ignorado; não publique arquivos `.users.json` ou `.browser.json`.
Veja [o roteiro completo](../doc/instalacao-desenvolvimento.md).
