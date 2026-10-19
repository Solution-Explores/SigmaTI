# Issue #9 — empacotamento e integração por import instalado

Entrega a partir da `dev@086129c`, após integração autorizada do PR #32.
Revisão técnica e execução pelo Codex; não se declara revisão independente.

## Resultado e decisões

- Distribuição `sigma-eng` 0.1.0, módulo `sigma_eng`, Python 3.12+.
- Núcleo sem dependências externas. Extra `api`: FastAPI; `dev`: dependências de
  API/testes. Versões alinhadas aos requisitos já fixados da aplicação.
- Backend de build setuptools 84.0.0 fixado; wheel inclui apenas o pacote e seus
  metadados. Nenhum arquivo de credenciais, resultado de execução ou teste é incluído.
- `requirements.txt` instala o pacote com o extra `api`; instalação editável
  de desenvolvimento explicitada no guia e no CI.
- Removidos o import `engenharia.sigma_eng`, seu fallback na auditoria e a
  alteração de `sys.path` no main. O pytest usa o pacote instalado.
- `sigma_eng.api` não importa `auth.py` nem cria trilha ao importar. A aplicação
  chama `create_router(exige_papel, auditoria=trilha)`. A política é obrigatória;
  a falta de argumento falha na construção do roteador.
- O main preserva o caminho padrão anterior de auditoria de engenharia; o pacote
  pode receber uma trilha em qualquer local gravável definido pela aplicação.

## Validação local

| Verificação | Resultado |
|---|---|
| Instalação por requirements e, em seguida, editável com extras | Aprovada |
| Regressão Python | 375 testes aprovados em 103,77 s; zero falhas/erros/ignorados |
| Autorização de engenharia | Cinco rotas recusam token ausente com 401 e perfil insuficiente com 403 |
| Aceite HTTP real com IA simulada | 20 verificações aprovadas, timeout 14,016 s |
| Chromium após import instalado | 3 cenários aprovados em 9,2 s |
| E6 | 53 identificadores em 59 mensagens; 25 negativos preservados; aprovado neste corpus |
| Dependências | `pip check` aprovado |
| Instalações isoladas de pacote | Cinco verificações aprovadas para editável, wheel e extras |

O runner `scripts/validate_package.py` cria venvs novos e executa imports com
`python -I` em pasta externa à raiz e a `engenharia`, sem `PYTHONPATH`.
Verifica núcleo editável sem FastAPI, extras de desenvolvimento/API com política
obrigatória, conteúdo da wheel, import da wheel regular sem o checkout e extra
`api` sem módulos da aplicação hospedeira. As wheels geradas ficam em diretório
ignorado; não há publicação em registro de pacotes.

Artefatos locais: `test-results/issue9-final.xml`, `issue9-http.json`, `issue9-e6.md`,
`browser.xml`, `issue9-package-final.json` e `issue9-package-final-wheels/`.
Esses testes descrevem o worktree da alteração; o CI do PR vincula a validação
ao commit publicado. A infraestrutura Docker não mudou nesta issue.

## Reprodução

Na raiz, com ambiente virtual Python 3.12+ ativo:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e "./engenharia[api,dev]"
python -m pip check
python -m pytest -q -p no:cacheprovider
python scripts/validate_package.py --output test-results/package.json
python scripts/validate_api_acceptance.py --output test-results/http.json --port 18001
```

Para reproduzir o comando do CI dentro de `engenharia/`:

```bash
python -m pip install -e ".[dev]"
```

O validador de pacote precisa de acesso ao PyPI para os ambientes novos. O núcleo
isolado usa somente a biblioteca padrão; importar a API exige o extra `api`.
As credenciais dos demais testes são temporárias e toda IA é simulada.

## Limites e próxima etapa

A issue #9 estará tecnicamente atendida quando o CI do commit confirmar as duas
instalações e a regressão; integração e fechamento continuam separados da implementação.
A próxima frente de fundação é concluir #6/#7 com usuários/sessões e estado
operacional em PostgreSQL, conforme o plano aprovado. A main não foi alterada.

Referências primárias consultadas para o empacotamento:
[setuptools e pyproject.toml](https://setuptools.pypa.io/en/stable/userguide/pyproject_config.html)
e [instalações locais do pip](https://pip.pypa.io/en/stable/topics/local-project-installs/).
