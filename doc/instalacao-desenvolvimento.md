# Roteiro de instalação e validação de desenvolvimento — K08

Este roteiro usa a `dev` e segue o [fluxo de trabalho do TCC](fluxo-de-trabalho-tcc.md).
Ele prepara o ambiente de desenvolvimento; a execução em uma máquina limpa e a
homologação dos serviços são a K09. Os testes usam dados fictícios e IA simulada.

## 1. Preparar um checkout novo

Pré-requisitos: Git, Python 3.12+ e Docker Compose. O Docker Engine é necessário
somente na etapa de inicialização dos contêineres. Para o frontend, use Node.js
22.12+ e npm, conforme o requisito do Vite registrado no `package-lock.json`.

```bash
git clone --branch dev https://github.com/Solution-Explores/SigmaTI.git
cd SigmaTI
git branch --show-current
git rev-parse HEAD
python -m venv .venv
```

Ative o ambiente e instale as dependências fixadas, sem reutilizar o ambiente
virtual ou o `.env` de outra cópia:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip check
```

```bash
# Linux/macOS
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
```

Se a política do PowerShell impedir a ativação, execute os comandos Python com
`.venv\Scripts\python.exe`; não é necessário mudar a política do sistema.

## 2. Validar antes de configurar credenciais reais

Execute da raiz, como no CI:

```bash
python -m pytest -q -p no:cacheprovider --junitxml=test-results/api.xml
python scripts/validate_compose_credentials.py
python scripts/validate_infrastructure.py --verify-registry
```

Resultado esperado: todas as suítes da API **e** de engenharia aprovadas, sem
testes ignorados; 32 verificações de credenciais e 12 cenários de infraestrutura
aprovados. A verificação de manifests precisa de acesso aos registros oficiais.
O JUnit fica em `test-results/api.xml`; essa pasta é ignorada pelo Git.

`pytest.ini` define os caminhos de importação e as duas suítes. Não é necessário
exportar `PYTHONPATH`, instalar outro cliente HTTP nem excluir os testes de
engenharia. Para executar apenas a K07:

```bash
python -m pytest tests/test_provider.py tests/test_config.py tests/test_public_errors.py tests/test_fail_closed.py -q -p no:cacheprovider --junitxml=test-results/k07.xml
```

Os validadores de Compose não iniciam contêineres e não carregam seu `.env`.
Os testes de sondas abrem servidores temporários somente em loopback. Nenhum
teste de diagnóstico precisa de uma chave real ou de acesso ao OpenRouter.

Se os diretórios temporários do Windows estiverem inacessíveis, use uma sessão
com acesso normal ao diretório temporário do usuário e repita a mesma verificação;
erros de preparação não constituem testes aprovados. Não enfraqueça a autenticação
nem remova testes para contornar um erro de ambiente.

## 3. Configurar a instalação nova

Copie `.env.example` para `.env` com `Copy-Item .env.example .env` no PowerShell
ou `cp .env.example .env` no Linux/macOS. Preencha as seis credenciais do Compose,
inclusive as do perfil opcional. Use valores novos e distintos para cada serviço.
O [README](../README.md#credenciais-da-infraestrutura) detalha cada variável.

Para iniciar a API, preencha também `OPENROUTER_API_KEY`, `SIGMA_LLM_MODEL` e
`SIGMA_CORS_ORIGINS`, com a origem exata do painel. Nunca publique esse arquivo.

A autenticação atual lê a chave JWT ao importar `auth.py`, antes de carregar o
`.env`. Por isso, defina `SIGMA_JWT_SECRET` **no ambiente do processo antes de
iniciar a API**, usando um segredo local gerado sem exibi-lo:

```powershell
$env:SIGMA_JWT_SECRET = python -c "import secrets; print(secrets.token_hex(32))"
```

```bash
export SIGMA_JWT_SECRET="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

A chave é efêmera nessa sessão; reiniciar com outra chave invalida os tokens
anteriores. Padronizar o carregamento e retirar o fallback é um achado para K11.
Mantenha a autenticação habilitada. Contas de demonstração, usuários em memória,
logout e integração do login ao painel ainda exigem tratamento na issue #6/K11.
Este roteiro não homologa o sistema para uso hospitalar.

## 4. Validar e iniciar os componentes

```bash
docker compose config --quiet
docker compose --profile monitoring config --quiet
docker compose up -d
docker compose ps
```

Para incluir a observabilidade opcional:

```bash
docker compose --profile monitoring up -d
docker compose --profile monitoring ps
```

Os bancos não publicam portas no host. n8n, Grafana e Zabbix ficam em loopback
por padrão. Abra o n8n local em `http://127.0.0.1:5678` e use o cadastro nativo de
owner na primeira instalação. O Compose não inicia API nem frontend.

Em um terminal com a configuração do passo 3:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Em outro terminal:

```bash
cd sigma-frontend
npm ci
npm run dev
```

Uma chamada sem token a `GET http://127.0.0.1:8000/api/status` deve receber 401.
A validação autenticada com IA simulada está nos testes da K07. O painel atual
ainda não implementa login, e o preflight CORS não permite `Authorization`;
o fluxo completo pelo navegador é um achado para K11/K10, não um aceite desta K08.

## 5. Evidências e recuperação

Na K09, registre sistema operacional, versões, commit, perfis iniciados, resultado
dos checks de configuração, estado dos serviços e testes de acesso. Registre
apenas nomes das variáveis, sem senhas, tokens ou dados reais. O Docker Engine
inativo impede validar a inicialização; `compose config` não substitui essa prova.

Para encerrar uma instalação nova de desenvolvimento, execute `docker compose
down` (com `--profile monitoring` se utilizado). Preserve os volumes. Uma instalação
com dados existentes deve seguir o [roteiro de migração](migracao-volume-postgresql.md).
Não use o procedimento de instalação nova como atualização de uma base existente.

Os resultados desta entrega e os achados encaminhados estão no
[registro K07/K08](../specs/007-008-ci-provedor-simulado/evidencias.md).

A [execução K09/K10 de 19/10/2026](../specs/009-010-instalacao-aceite/evidencias.md)
validou Python e build do frontend, mas encontrou falha TLS no download Docker,
falha de lint e reprovações no fluxo autenticado. Instalação e aceite integrado
continuam pendentes de correções K11/K12. O runner HTTP reproduzível é
`scripts/validate_api_acceptance.py`; ele usa IA simulada e retorna erro quando
um critério de aceite falha.
