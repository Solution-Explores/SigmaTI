# Núcleo de engenharia

Pacote `sigma_eng`, que transforma o SIGMA de um MVP de monitoramento em um sistema de engenharia: requisitos rastreáveis, métricas definidas, experimentos reproduzíveis e propriedades de segurança testadas. Reescreve, para o SIGMA, funcionalidades do Sentinel Vigilark, plataforma de monitoramento do mesmo autor.

O núcleo está integrado ao `main.py`, com proteção por perfil nas rotas `/api/eng/*`. Os módulos de cálculo usam só a biblioteca padrão. A API e os testes usam os extras opcionais do pacote, com as versões fixadas da aplicação.

## Módulos

| Módulo (`sigma_eng/`) | O que faz | Requisito |
|---|---|---|
| `probe.py` | Sonda TCP, HTTP e HTTPS: latência, perda, jitter e TLS. Alvos restritos a redes autorizadas. | RF01, RF02, RNF07 |
| `slo.py` | SLO, orçamento de erros e burn rate em várias janelas. | RF01, RF06 |
| `incidents.py` | MTTD, MTTA e MTTR (média, mediana e p95). | RF04, RF06 |
| `anomaly.py` | Detectores online EWMA e MAD, com avaliação de precisão, revocação e atraso. | RF01 |
| `audit_chain.py` | Trilha de auditoria com cadeia de hash e HMAC. | RF07, RNF07 |
| `approvals.py` | Aprovação humana: máquina de estados, TTL, quatro olhos e papéis. | RF07 |
| `runbooks.py` | Runbooks em Markdown com dry-run, allowlist e aprovação por passo, sem shell. | RF03, RF07 |
| `api.py` | Roteador FastAPI (`/api/eng/*`) para integrar ao `main.py`. | RF01 |

## Instalar e testar

Na raiz do repositório, com Python 3.12+ e o ambiente virtual ativo:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e "./engenharia[api,dev]"
python -m pytest engenharia/tests -q -p no:cacheprovider
```

Não é necessário configurar `PYTHONPATH`. Para rodar o experimento E1, que grava `engenharia/resultados/e1_deteccao.{csv,md}`:

```bash
cd engenharia
python -m experimentos.exp_deteccao
```

O núcleo, que é tudo exceto `api.py`, também instala sem extras:

```bash
python -m pip install -e ./engenharia
python -c "import sigma_eng; print(sigma_eng.__version__)"
```

Dentro de `engenharia/`, `python -m pip install -e ".[dev]"` instala os extras de teste (FastAPI e cliente HTTP). O CI usa esse comando. O guia geral está em [Instalação para desenvolvimento](../docs/operacao/instalacao.md).

## Integrar à API

```python
from auth import exige_papel  # política da aplicação hospedeira
from sigma_eng.api import create_router

app.include_router(create_router(exige_papel))
```

A política de autorização é obrigatória. Não existe roteador global sem autenticação, e importar `sigma_eng.api` não importa `auth.py` nem abre arquivos.

A trilha de auditoria padrão é `resultados/audit.jsonl`, relativa ao diretório de execução, ou o caminho de `SIGMA_AUDIT_PATH`. Também dá para passar uma `AuditChain` explícita: `create_router(exige_papel, auditoria=trilha)`. O `main.py` faz isso para manter a trilha existente em `engenharia/resultados/audit.jsonl` quando `SIGMA_AUDIT_PATH` não está definida.

## Documentação

1. [Visão de engenharia](docs/00-visao-de-engenharia.md): problema, hipóteses e contribuições.
2. [Mapeamento Vigilark e SIGMA](docs/01-mapeamento-vigilark-sigma.md): o que foi herdado, o que mudou e por quê.
3. [Guia de implementação](docs/02-guia-de-implementacao.md): como integrar, passo a passo.
4. [Metodologia experimental](docs/03-metodologia-experimental.md): experimentos E1 a E5 e ameaças à validade.
5. [Rastreabilidade](docs/04-rastreabilidade.md): requisito, módulo e teste.
6. [Segurança e pendências](docs/05-seguranca-e-pendencias.md): riscos, inclusive os já existentes no repositório.
7. [Roteiro do TCC](docs/06-roteiro-tcc.md): capítulos e trabalhos futuros.
8. [Persistência de identidades](docs/07-persistencia-identidades.md).
9. [Estado operacional](docs/08-estado-operacional.md): esquema PostgreSQL, recuperação de aprovações e execuções, medições, retenção e APIs.
10. [Coleta de eventos](docs/09-coleta-eventos.md): coleta contínua, SSE autenticado, contratos e ensaio E2.
11. [ADRs](docs/adr/): decisões de arquitetura.

## Resultado do experimento E1

Dados sintéticos, 30 repetições por cenário:

| Cenário | Detector | Detecção | Atraso (amostras) | Falsos positivos por série | F1 |
|---|---|---|---|---|---|
| Degrau | EWMA | 100% | 0 | 1,37 | 0,908 |
| Degrau | MAD | 100% | 0 | 0,23 | 0,998 |
| Pico | EWMA | 100% | 0 | 1,90 | 0,783 |
| Pico | MAD | 100% | 0 | 0,20 | 0,971 |
| Deriva lenta | EWMA | **20%** | 12,5 | 52,07 | 0,002 |
| Deriva lenta | MAD | **17%** | 17,6 | 0,30 | 0,005 |

Os dados são sintéticos e mostram o comportamento dos algoritmos, não o da rede do hospital. A deriva lenta é um limite conhecido de detectores por limiar (veja a issue de CUSUM e Page-Hinkley).
