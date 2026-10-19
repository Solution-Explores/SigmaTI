# SIGMA · Núcleo de Engenharia

Funcionalidades inspiradas no Sentinel Vigilark (plataforma de monitoramento e segurança do mesmo autor), reescritas aqui, para transformar o SIGMA de um MVP de monitoramento em um **sistema de engenharia da computação**: com requisitos rastreáveis, métricas definidas, experimentos reproduzíveis e propriedades de segurança testadas.

Esta pasta é **autocontida**. Não altera o MVP existente (`main.py`, `sigma-frontend/`); a integração é opt-in (ver [guia](docs/02-guia-de-implementacao.md)).

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
cd engenharia
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q                          # 58 testes
python -m experimentos.exp_deteccao   # experimento E1 → resultados/e1_deteccao.{csv,md}
```

O núcleo (tudo exceto `api.py`) usa só a biblioteca padrão do Python 3.10+.

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
