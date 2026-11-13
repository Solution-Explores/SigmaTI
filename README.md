<div align="center">

# SIGMA

**Monitoramento ativo de rede com apoio de IA para a equipe de TI de um hospital oncológico.**

[![CI](https://github.com/Solution-Explores/SigmaTI/actions/workflows/api-config.yml/badge.svg)](https://github.com/Solution-Explores/SigmaTI/actions/workflows/api-config.yml)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/status-MVP%20(TCC)-orange)
![Versão](https://img.shields.io/badge/vers%C3%A3o-v1.0.0-blue)

[Problema](#problema-que-resolve) ·
[Funcionalidades](#funcionalidades) ·
[Arquitetura](#arquitetura) ·
[Início rápido](#início-rápido) ·
[Versão entregue](#versão-entregue) ·
[Documentação](docs/README.md)

</div>

Trabalho de conclusão de curso (TCC) para a equipe de TI de uma fundação pública de saúde.

## Problema que resolve

A equipe de TI trabalha sem visibilidade em tempo real da rede e só descobre as falhas quando os usuários reclamam. Isso causa:

- demora para detectar e consertar incidentes (MTTD e MTTR altos);
- técnicos sobrecarregados com tarefas manuais;
- falta de histórico para prevenir falhas.

Em um hospital, a queda da rede afeta prontuários eletrônicos e equipamentos médicos. O SIGMA troca o suporte reativo por monitoramento contínuo, sem custo de licenças.

## Funcionalidades

- **Alertas em tempo real:** o painel exibe qualquer anomalia em até 5 segundos após a detecção (RF01).
- **Captura de tráfego e alertas:** integração com o firewall pfSense e com uma sonda própria de análise de pacotes (RF02).
- **Diagnóstico assistido por IA:** resposta no painel em até 15 segundos (RF03, RNF04).
- **Privacidade (LGPD):** logs e mensagens são generalizados antes de ir à IA. IPs viram sub-redes, equipamentos viram categorias, e nomes e identificadores médicos são removidos. Se o filtro falhar, nada é enviado (RF05).
- **Histórico de incidentes:** PostgreSQL com volume persistente e backup diário (RF04, RNF06).
- **Relatórios automáticos:** o n8n calcula métricas como o MTTR e envia relatórios à coordenação (RF06).
- **Controle de acesso:** login com perfis (Suporte N1, Analista de Redes e Gestor de TI). O n8n só é acessível pela VLAN de gerência ou por VPN (RF07).
- **Segurança de origens:** cada sonda e o pfSense usam chave exclusiva, com HTTPS, revogação e rotação (RNF07).

## Arquitetura

```mermaid
flowchart LR
    PF["pfSense"] -->|"chave + HTTPS"| API
    SO["Sonda de pacotes<br/>(host, chave própria)"] -->|"chave + HTTPS"| API
    API["API Python (FastAPI)"] --> DB[("PostgreSQL")]
    DB --> BK["Backup diário"]
    DB --> N8["n8n<br/>(VLAN de gerência / VPN)"] --> REL["Relatórios"]
    API --> GEN["Generalização (LGPD)"] --> IA["Groq / OpenRouter"] --> SUG["Sugestão genérica"]
    API -->|"SSE"| FE["Frontend React<br/>alerta original + diagnóstico com IA"]
    TEC["Técnicos<br/>(login + perfil)"] --> FE
```

A implantação é híbrida. O Docker Compose orquestra `db` (PostgreSQL) e `n8n`. A API e o frontend rodam no host por enquanto, e a conteinerização deles está planejada. Zabbix e Grafana, uma stack de observabilidade opcional, entram com `--profile monitoring`. A sonda roda no host, porque precisa da interface física de rede. O pfSense fica na rede.

### Tecnologias

| Camada | Tecnologia | Onde roda |
|---|---|---|
| Backend e API | Python e FastAPI | Host |
| Tempo real | SSE | API |
| Banco de dados | PostgreSQL | Contêiner |
| Frontend | React e Vite | Host |
| Automação e relatórios | n8n | Contêiner |
| Análise de pacotes | Analisador customizado, com Wireshark de apoio | Host |
| Firewall | pfSense | Rede |
| IA (LLM) | OpenRouter e Groq (camadas gratuitas) | Nuvem |
| Implantação | Docker e Docker Compose | Servidor on-premise |

Detalhes em [Stack de tecnologia](docs/arquitetura/stack-de-tecnologia.md).

## Início rápido

Pré-requisitos: Docker, Docker Compose, Python 3.12+ e Node.js. O MVP não é uma instalação hospitalar homologada, e a sonda e o pfSense continuam planejados, sem procedimento de instalação.

```bash
git clone --branch develop https://github.com/Solution-Explores/SigmaTI.git
cd SigmaTI
cp .env.example .env          # preencha as credenciais; nunca versione o .env
docker compose up -d          # banco de dados e n8n

python -m venv .venv          # Windows: .venv\Scripts\Activate.ps1 | Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn --app-dir backend main:app --host 127.0.0.1 --port 8000 --reload

cd frontend && npm ci && npm run dev
```

O Compose exige seis variáveis de credenciais e não tem senha padrão. A API exige `OPENROUTER_API_KEY`, `SIGMA_LLM_MODEL`, `SIGMA_CORS_ORIGINS` e `SIGMA_JWT_SECRET`, além de `SIGMA_DATABASE_URL` (PostgreSQL, recomendado) ou `SIGMA_USERS_FILE` (arquivo, só laboratório). Os detalhes estão em:

- [Instalação para desenvolvimento](docs/operacao/instalacao.md), com comandos de Windows e Linux;
- [Configuração e execução](docs/operacao/configuracao-e-execucao.md): credenciais, portas e versões, variáveis da API, origens, erros públicos e chamada à IA;
- [Painel operacional](docs/operacao/painel-operacional.md): execução e testes do frontend;
- [Backup, restauração e atualização](docs/operacao/backup-restauracao.md): `scripts/backup.sh`, `scripts/restore.sh` e `scripts/smoke.sh`.

Para rodar os testes sem chave real nem chamadas externas:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q -p no:cacheprovider
```

## Como usar

1. Acesse o painel e faça login com o seu perfil.
2. Acompanhe os alertas e o status da rede em tempo real.
3. Peça à IA uma sugestão de diagnóstico. Ela devolve uma resposta genérica, e o painel mostra o alerta original para você ligá-la ao equipamento exato.
4. O Gestor de TI acessa o n8n (VLAN de gerência ou VPN) para os relatórios e gerencia usuários e chaves.

### Permissões por perfil

| Função | Suporte N1 | Analista de Redes | Gestor de TI |
|---|---|---|---|
| Ver alertas e status da rede (`GET /api/alertas` planejado, 501) | Sim | Sim | Sim |
| Usar o diagnóstico com a IA (`POST /api/alertas`) | Sim | Sim | Sim |
| Ver histórico e detalhes de pacotes (`GET /api/pacotes`, planejado, 501) | Não | Sim | Sim |
| Ver relatórios gerenciais (`GET /api/relatorios` planejado #16, 501) | Não | Não | Sim |
| Gerenciar usuários e chaves (usuários em `/api/usuarios`; `POST /api/chaves/rotacao` planejado #23, 501) | Não | Não | Sim |
| Acessar o n8n (`GET /api/n8n/acesso`, requer `SIGMA_N8N_URL`) | Não | Não | Sim |

## Estado do desenvolvimento

- A demonstração controlada segue o [plano de demonstração](docs/planejamento/plano-demonstracao-2026-10-27.md). O [plano de conclusão de 20/10](docs/planejamento/plano-conclusao-2026-10-20.md) registra a ordem de implementação, os cortes de escopo e as dependências externas. Itens planejados não são funcionalidades entregues.
- Com `SIGMA_USERS_FILE`, sessões e usuários alterados ficam em memória. Com PostgreSQL, eles persistem ([identidades e sessões](engenharia/docs/07-persistencia-identidades.md)).
- O [estado operacional no PostgreSQL](engenharia/docs/08-estado-operacional.md) cobre esquema, recuperação de aprovações e execuções, medições, retenção e APIs. Veja também a [coleta de eventos e o SSE](engenharia/docs/09-coleta-eventos.md).
- O experimento E6 avalia cada identificador anotado, e seus resultados valem só para o corpus sintético.
- As issues #5 (anonimização) e #6 (autenticação e perfis) foram fechadas. Continuam abertas a #8 (sondagem contínua), a #11 (experimentos, falta o E5), a #45, a #46 e a #57.
- `POST /api/alertas` responde `status: "Diagnóstico gerado"` e não grava incidente no PostgreSQL (incidentes nascem da coleta de medições sobre alvos cadastrados). As rotas planejadas de rotação de chaves de origem (`POST /api/chaves/rotacao`, #23), relatórios gerenciais (`GET /api/relatorios`, #16), pacotes (`GET /api/pacotes`) e listagem legada de alertas (`GET /api/alertas`) respondem HTTP 501 (`Recurso ainda não disponível.`). `GET /api/status` continua registrado como débito técnico por responder `"operacional"` sem sondar dependências.
- As correções de sessão, painel e anonimização estão nas [evidências da recuperação da sprint](docs/specs/011-recuperacao-sprint/evidencias.md), integradas à `develop` pelo [PR #32](https://github.com/Solution-Explores/SigmaTI/pull/32).
- A #25 foi fechada: a restauração foi aceita em máquina física separada. A ativação do modelo systemd continua pendente.
- A [#57](https://github.com/Solution-Explores/SigmaTI/issues/57) eliminou as respostas `200` sem efeito nas rotas de rotação de chaves, relatórios, pacotes, listagem de alertas, incidentes sem banco (503) e URL fictícia do n8n.

## Versão entregue

**`v1.0.0`**, marcada em 04/11/2026 no commit `0379374`. O aceite completo foi executado no SHA `15568d3`, cuja árvore é idêntica à da tag: mesmo conteúdo, só a história difere.

Máquina física, loopback, PostgreSQL 15.19 descartável em contêiner com imagem presa por digest. Um validador de cada vez.

| Rodada | Resultado |
|---|---|
| `pytest` (suíte inteira) | 565 passaram, 1 pulado, **0 falharam** |
| `validate_api_acceptance` | 20 PASS, 0 FAIL |
| `validate_panel` | 4 de 4, em navegador real |
| `validate_collection` | 30 de 30 dentro de 5 s; mediana 0,758 s, p95 0,960 s, máx. 1,099 s |
| `validate_infrastructure` | 12 PASS; K04 aprovado sem iniciar contêiner |

Tempos medidos na versão entregue, 30 repetições em loopback:

| | média | p95 |
|---|---|---|
| MTTD | 0,684 s | 0,795 s |
| MTTA | 0,133 s | 0,216 s |
| MTTR | 0,164 s | 0,244 s |

**Estes números não são promessas de desempenho em rede hospitalar.** São de laboratório, numa máquina só, com alvos sintéticos. O MTTD variou entre 0,684 e 0,795 s em três execuções do mesmo código — a diferença entre execuções é maior que o desvio dentro de cada uma, então a faixa vale mais que qualquer valor único. O que cada medição não cobre está em [limitações do trabalho](docs/tcc/limitacoes.md).

## Segurança e privacidade

- Chaves e senhas ficam em variáveis de ambiente, nunca no código.
- Não há tabela de correspondência (de/para) entre dados originais e generalizados.
- O histórico bruto fica dentro da infraestrutura da instituição, protegido por login, chaves e backup com acesso restrito.
- Evidências e testes usam **só dados fictícios**, nos blocos reservados `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (RFC 5737) e `2001:db8::/32` (RFC 3849).
- A conformidade com o art. 12 da LGPD depende da homologação do DPO ou do jurídico da instituição.

## Validação

| Requisito | Meta | Medido na `v1.0.0` |
|---|---|---|
| RF01 | Alerta no painel em até 5 s | ✅ 30 de 30; mediana 0,758 s, máx. 1,099 s (loopback) |
| RNF04 | Diagnóstico da IA em até 15 s | ❌ sem nenhuma medição com provedor real |
| RNF06 | Backup restaurável e sem perda de dados ao recriar contêineres | ✅ aceito em máquina física separada (#25) |
| RNF07 | Requisição sem chave, inválida ou revogada é recusada (401 ou 403) | ✅ origem não confiável 403, payload inválido 422, sem chamada ao provedor |
| RNF08 | Zero vazamentos de dados sensíveis para a IA | ⚠️ 100% de proteção pelo bloqueio *fail-closed*; o recall de transformação ficou em 95,12% (n = 41), abaixo do critério original |

A validação completa está na seção 6 do [estudo de caso](docs/arquitetura/estudo-de-caso.md). O registro de testes e achados corrigidos está em [revisão K01 a K06](docs/specs/revisao-k01-k06/validacao.md).

## Limitações conhecidas

- Sem disco ou local de rede separado, o backup fica no mesmo servidor e não protege contra falha física total.
- As metas de 5 s e 15 s dependem das camadas gratuitas de IA. Com a IA fora do ar, o alerta continua no painel, sem diagnóstico.
- A generalização é feita por regras: reduz o risco, mas não o elimina. Por isso existe a falha segura.
- Arredondar horários e mascarar sub-redes pode reduzir a precisão do diagnóstico. O RNF08 mede essa perda com dados fictícios.
- O servidor on-premise e a VLAN ou VPN de gerência ainda precisam ser confirmados pela instituição.
- A cadeia de hash da auditoria **não detecta truncamento do fim** da trilha: 0 de 250 casos no experimento E4. Só a âncora guardada fora da máquina pega esse caso.
- O RNF04 (diagnóstico da IA em até 15 s) **não tem nenhuma medição** com provedor real e filtro de anonimização ativo.

A lista completa, com a medição que sustenta cada item, está em [limitações do trabalho](docs/tcc/limitacoes.md).

## Estrutura do projeto

```
backend/       API FastAPI: main.py, routers/, persistence/, migrations/ e tests/
frontend/      painel em React (Vite)
engenharia/    núcleo sigma_eng, testes, experimentos e resultados
scripts/       validação, backup, instalação e utilitários
deploy/        unidade systemd e overlays do Compose
docs/          documentação, specs e evidências (índice em docs/README.md)
docker-compose.yml, docker-images.lock.json, .env.example
```

## Para quem trabalha no TCC

Trello, Miro e Drive estão mapeados em [docs/planejamento/mapa-de-espacos.md](docs/planejamento/mapa-de-espacos.md); o repositório vence em caso de divergência.

O desenvolvimento segue o [Git Flow](docs/processo/gitflow.md): branches `feature/*` e `fix/*` entram na `develop` por PR, com testes, evidências e revisão, e uma `release/*` prepara a `main`. Comece pelo [fluxo de trabalho do TCC](docs/processo/fluxo-de-trabalho-tcc.md), que explica as etapas, as colunas do quadro e quando uma issue pode ser encerrada. Toda a documentação está indexada em [docs/README.md](docs/README.md).

## Licença

O código é publicado sob a [PolyForm Noncommercial License 1.0.0](LICENSE): pode ser lido, estudado e usado para fins não comerciais, inclusive pesquisa e ensino. O **uso comercial exige autorização dos autores**. Esta licença preserva o uso comercial futuro do SIGMA e não é uma licença de código aberto no sentido da OSI.

## Autores

Discentes:

- **Iohand Jheremy**: [LinkedIn](https://www.linkedin.com/in/iohan-jheremy/)
- **Joyce Yasmin**: LinkedIn pendente
- **Vinícius Gomes**: [LinkedIn](https://www.linkedin.com/in/viniciusgomesdev/)

Docente:

- **Euler Azevedo**: [LinkedIn](https://www.linkedin.com/in/eulerazevedo/)
