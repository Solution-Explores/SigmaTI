# SIGMA · Núcleo de Engenharia

Funcionalidades inspiradas no Sentinel Vigilark (plataforma de monitoramento e segurança do mesmo autor), reescritas aqui, para transformar o SIGMA de um MVP de monitoramento em um **sistema de engenharia da computação**: com requisitos rastreáveis, métricas definidas, experimentos reproduzíveis e propriedades de segurança testadas.

O núcleo está integrado ao `main.py` do SIGMA, com proteção por perfil nas rotas
`/api/eng/*`. Os módulos de cálculo usam a biblioteca padrão; a API e seus testes
usam os extras opcionais do pacote instalável `sigma-eng`, com as mesmas versões
fixadas usadas pela aplicação.

## O que tem aqui

| Módulo (`sigma_eng/`) | O que faz | Funcionalidade de referência | Requisito SIGMA |
|---|---|---|---|
| `probe.py` | Sonda TCP/HTTP/HTTPS: latência, perda, jitter, TLS; alvos restritos a redes autorizadas | vigilância de serviços | RF01, RF02, RNF07 |
| `slo.py` | SLO, orçamento de erros, burn rate em múltiplas janelas | SLO e orçamento de erros | RF01, RF06 |
| `incidents.py` | MTTD / MTTA / MTTR (média, mediana, p95) | gestão de incidentes | RF04, RF06 |
| `anomaly.py` | Detectores online EWMA e MAD + avaliação (precisão, revocação, atraso) | novo (base do TCC) | RF01 |
| `audit_chain.py` | Trilha de auditoria com cadeia de hash/HMAC | trilha de auditoria | RF07, RNF07 |
| `approvals.py` | Aprovação humana: máquina de estados, TTL, quatro olhos, papéis | aprovações humanas | RF07 |
| `runbooks.py` | Runbooks em Markdown, dry-run, allowlist, aprovação por passo, **sem shell** | runbooks | RF03, RF07 |
| `api.py` | Roteador FastAPI (`/api/eng/*`) para integrar ao `main.py` | API de operação | RF01 |

## Como rodar

```bash
# Na raiz do repositório, com Python 3.12+ e ambiente virtual ativo:
python -m pip install -r requirements-dev.txt
python -m pip install -e "./engenharia[api,dev]"
python -m pytest engenharia/tests -q -p no:cacheprovider

# Experimento E1 → engenharia/resultados/e1_deteccao.{csv,md}
cd engenharia
python -m experimentos.exp_deteccao
```

O pacote exige Python 3.12+, como o ambiente validado da aplicação. O núcleo
(tudo exceto `api.py`) usa somente a biblioteca padrão e pode ser instalado sem extras:

```bash
python -m pip install -e ./engenharia
# Importar de qualquer pasta com o mesmo interpretador/venv:
python -c "import sigma_eng; print(sigma_eng.__version__)"
```

Dentro de `engenharia/`, `python -m pip install -e ".[dev]"` instala os extras de
testes, inclusive FastAPI e o cliente HTTP. O CI usa esse comando. Não é necessário
configurar `PYTHONPATH` ou alterar `sys.path`.

Integração com a API da aplicação:

```python
from auth import exige_papel  # política da aplicação hospedeira
from sigma_eng.api import create_router

app.include_router(create_router(exige_papel))
```

A política de autorização é obrigatória; não há roteador global sem autenticação.
Importar `sigma_eng.api` não importa `auth.py` nem abre arquivos. A trilha padrão
é `resultados/audit.jsonl`, relativa ao diretório de execução, ou `SIGMA_AUDIT_PATH`.
Também é possível passar uma `AuditChain` explícita: `create_router(exige_papel,
auditoria=trilha)`. O `main.py` do SIGMA faz isso para preservar sua trilha existente
em `engenharia/resultados/audit.jsonl` quando `SIGMA_AUDIT_PATH` não é definida.
Veja o [roteiro de instalação K08](../doc/instalacao-desenvolvimento.md).

## Documentação

1. [Visão de engenharia](docs/00-visao-de-engenharia.md): problema, hipóteses, contribuições
2. [Mapeamento Vigilark → SIGMA](docs/01-mapeamento-vigilark-sigma.md): o que foi herdado, o que mudou e por quê
3. [Guia de implementação](docs/02-guia-de-implementacao.md): como integrar, passo a passo
4. [Metodologia experimental](docs/03-metodologia-experimental.md): experimentos E1–E5 e ameaças à validade
5. [Rastreabilidade](docs/04-rastreabilidade.md): requisito → módulo → teste
6. [Segurança e pendências](docs/05-seguranca-e-pendencias.md): riscos, inclusive os já existentes no repositório
7. [Roteiro do TCC](docs/06-roteiro-tcc.md): capítulos, trabalhos futuros
8. [ADRs](docs/adr/): decisões de arquitetura

## Resultado do experimento E1 (sintético, 30 repetições)

| cenário | detector | detecção | atraso (amostras) | falsos positivos/série | F1 |
|---|---|---|---|---|---|
| degrau | EWMA | 100% | 0 | 1,37 | 0,908 |
| degrau | MAD | 100% | 0 | 0,23 | 0,998 |
| pico | EWMA | 100% | 0 | 1,90 | 0,783 |
| pico | MAD | 100% | 0 | 0,20 | 0,971 |
| deriva lenta | EWMA | **20%** | 12,5 | 52,07 | 0,002 |
| deriva lenta | MAD | **17%** | 17,6 | 0,30 | 0,005 |

Dados sintéticos: indicam o comportamento dos algoritmos, **não** a rede do hospital. A deriva lenta é um limite conhecido de detectores por limiar (ver issue de CUSUM/Page-Hinkley).
