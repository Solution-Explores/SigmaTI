# Painel SIGMA

Frontend em React e Vite. O guia completo de ambiente está em [Instalação para desenvolvimento](../docs/operacao/instalacao.md).

## Rodar

Use Node.js 24 (versão do CI) e o lockfile versionado:

```bash
npm ci --include=optional
npm run dev -- --host 127.0.0.1
npm run build
npm run lint
```

## Configuração

- `VITE_API_URL` define o endereço da API. O padrão é `http://localhost:8000`.
- Não coloque segredos do servidor em variáveis `VITE_*`.
- O login usa `/api/auth/login` e `/api/auth/me`. O token fica só em memória, o logout revoga a sessão e recarregar a página exige novo login.

## Testes de navegador

Rodam com a API e um provedor de IA simulados:

```bash
npx playwright install chromium
npm run test:e2e
```

Antes, crie o `.venv` na raiz e instale `requirements-dev.txt`. O Playwright gera credenciais temporárias e inicia a API e o Vite isolados nas portas 18000 e 5173. Saídas e credenciais ficam em `test-results/`, que o Git ignora. Não publique arquivos `.users.json` ou `.browser.json`.
