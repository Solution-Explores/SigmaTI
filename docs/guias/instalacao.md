# Instalação para desenvolvimento

Guia para montar um ambiente de desenvolvimento do SIGMA do zero, validá-lo e subir os componentes. Os testes usam dados fictícios e IA simulada. Este guia não cobre implantação hospitalar nem a sonda e o pfSense, que seguem planejados.

Para atualizar uma instalação que já tem dados, use a [migração do volume PostgreSQL](migracao-volume-postgresql.md). Não aplique este guia sobre uma base existente.

## Pré-requisitos

- Git e Python 3.12 ou superior.
- Docker e Docker Compose. O Docker Engine só é necessário para subir os contêineres.
- Node.js 24 (versão do CI) ou 22.22 ou superior, e npm, para o frontend.

## 1. Clonar e instalar dependências

```bash
git clone --branch develop https://github.com/Solution-Explores/SigmaTI.git
cd SigmaTI
python -m venv .venv
```

Ative o ambiente e instale as dependências:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip install -e "./engenharia[api,dev]"
python -m pip check
```

```bash
# Linux/macOS
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install -e "./engenharia[api,dev]"
python -m pip check
```

Se o PowerShell bloquear a ativação, rode o Python direto: `.venv\Scripts\python.exe`. Não precisa mudar a política do sistema.

O núcleo `sigma_eng` é instalado por `pip`. Não configure `PYTHONPATH`.

## 2. Rodar os testes

Na raiz do repositório, antes de configurar credenciais reais:

```bash
python -m pytest -q -p no:cacheprovider --junitxml=test-results/api.xml
python scripts/validate_compose_credentials.py
python scripts/validate_infrastructure.py --verify-registry
```

Resultado esperado:

- Todas as suítes da API e de engenharia passam, sem testes ignorados.
- 32 verificações de credenciais e 12 cenários de infraestrutura passam.

`--verify-registry` precisa de acesso aos registros oficiais de imagens. Os validadores não iniciam contêineres e não leem o seu `.env`. Nenhum teste precisa de chave real da IA.

Para validar o empacotamento do `sigma_eng` (baixa dependências do PyPI e não publica nada):

```bash
python scripts/validate_package.py --output test-results/package.json
```

Um erro de ambiente, como pasta temporária inacessível no Windows, não conta como teste aprovado. Corrija o ambiente e repita. Não enfraqueça a autenticação nem remova testes para contornar o erro.

## 3. Configurar

```bash
cp .env.example .env          # PowerShell: Copy-Item .env.example .env
```

Preencha o `.env` e nunca o versione.

1. **Credenciais do Compose.** São seis variáveis, com valores novos e distintos. Veja [Credenciais da infraestrutura](../../README.md#credenciais-da-infraestrutura).
2. **API.** Preencha `OPENROUTER_API_KEY`, `SIGMA_LLM_MODEL`, `SIGMA_CORS_ORIGINS` e `SIGMA_JWT_SECRET`. Veja [Variáveis da API](../../README.md#executar-a-api-no-desenvolvimento).
3. **Usuários.** Escolha um dos dois modos.

### Usuários no PostgreSQL (recomendado)

Defina `SIGMA_DATABASE_URL` com uma URL `postgresql+psycopg`. Aplique as migrações e crie o primeiro usuário:

```bash
python -m alembic upgrade head
python -m scripts.manage_identity create gestor gestor_ti
```

O comando pede a senha duas vezes, com 12 a 128 caracteres. As sessões sobrevivem ao reinício enquanto a chave JWT for a mesma. Detalhes em [Identidades e sessões persistentes](../../engenharia/docs/07-persistencia-identidades.md).

### Usuários em arquivo (só laboratório)

Gere um segredo JWT e os usuários de demonstração:

```bash
export SIGMA_JWT_SECRET="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python scripts/create_demo_users.py
export SIGMA_USERS_FILE="$(pwd)/.local/users.json"
```

```powershell
$env:SIGMA_JWT_SECRET = python -c "import secrets; print(secrets.token_hex(32))"
python scripts/create_demo_users.py
$env:SIGMA_USERS_FILE = (Resolve-Path .local/users.json).Path
```

O script pede uma senha temporária por perfil e grava só os hashes em arquivo ignorado pelo Git. As variáveis também podem ficar no `.env`, com caminho absoluto.

Neste modo as sessões ficam em memória de um único processo. Reiniciar a API derruba todas elas, e os usuários criados pela API se perdem.

Ajustes opcionais, lidos após o `.env`. A expiração da sessão também aceita 1 a 86400 segundos.

| Variável | Faixa | Padrão |
|---|---|---|
| `SIGMA_MAX_LOGIN_ATTEMPTS` | 1 a 100 | 5 |
| `SIGMA_LOCKOUT_DURATION_SECONDS` | 1 a 86400 | 900 |

## 4. Subir os componentes

```bash
docker compose config --quiet
docker compose up -d
docker compose ps
```

Para incluir Zabbix e Grafana (opcionais):

```bash
docker compose --profile monitoring up -d
```

O Compose sobe o banco e o n8n. Ele não sobe a API nem o frontend. Os bancos não publicam portas no host. n8n, Grafana e Zabbix escutam só em loopback. Na primeira vez, abra `http://127.0.0.1:5678` e crie a conta owner do n8n.

Em um terminal, inicie a API:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Em outro, o frontend:

```bash
cd sigma-frontend
npm ci
npm run dev
```

Confira: `GET http://127.0.0.1:8000/api/status` sem token deve retornar 401. O painel pede login, envia o token por Bearer e guarda a sessão só em memória, então recarregar a página exige novo login. `VITE_API_URL` define o endereço da API (padrão `http://localhost:8000`).

## 5. Teste de aceite

Sem IA real, com credenciais geradas pelo próprio script:

```bash
python scripts/validate_api_acceptance.py --output test-results/aceite-novo.json --port 18001
python scripts/executar_experimento_e6.py --output test-results/e6.md
cd sigma-frontend
npm ci --include=optional
npm run build
npm run lint
npx playwright install chromium
npm run test:e2e
```

Use um caminho de saída novo a cada execução, para preservar evidências anteriores. O teste de navegador inicia a API e o Vite por conta própria. As portas 18000 e 5173 precisam estar livres.

Para validar a instalação em projeto e volumes descartáveis (exige Docker ativo):

```bash
python scripts/validate_installation.py --output test-results/instalacao-nova
```

O script baixa as imagens fixadas, testa autenticação e persistência após recriar os contêineres, e remove só o que criou. A pasta de saída contém credenciais fictícias e não deve ser publicada. Só o `report.json` serve como evidência.

## Encerrar

```bash
docker compose down        # acrescente --profile monitoring se usou
```

Preserve os volumes. Não use `down -v` em ambiente com dados.

## Registrar evidências

Anote sistema operacional, versões, commit, perfis iniciados, resultado dos checks e estado dos serviços. Registre só os nomes das variáveis, nunca senhas, tokens ou dados reais. `compose config` não prova que os contêineres iniciam. Isso exige o Docker Engine ativo.

Histórico das execuções de validação:

- [K07 e K08](../../specs/007-008-ci-provedor-simulado/evidencias.md)
- [K09 e K10](../../specs/009-010-instalacao-aceite/evidencias.md)
- [K11 e K12](../../specs/011-recuperacao-sprint/evidencias.md)
