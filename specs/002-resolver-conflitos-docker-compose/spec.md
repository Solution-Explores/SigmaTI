# Feature Specification: Resolver Marcadores de Conflito no docker-compose.yml

**Feature Branch**: `002-resolver-conflitos-docker-compose`

**Created**: 2026-10-12

**Status**: Implemented

**Input**: User description: "Resolver marcadores de conflito de merge no docker-compose.yml #2 - O docker-compose.yml na main contém <<<<<<< HEAD, ======= e >>>>>>> 9d05615. O arquivo é YAML inválido: docker compose up falha e o job validate-compose do CI também. Proposta: Decidir a arquitetura-alvo e manter um conjunto de serviços (PostgreSQL da aplicação + n8n; Zabbix/Grafana como perfil opcional via profiles:)."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Seguro do Núcleo SIGMA (Priority: P1) 🎯 MVP

Como desenvolvedor ou operador do hospital,  
Quero executar `docker compose up -d` sem flags adicionais,  
Para que os serviços centrais da aplicação (`db` PostgreSQL e `n8n` para automação/relatórios) subam de forma segura, com portas protegidas e sem falhas de sintaxe YAML.

**Why this priority**: É o núcleo obrigatório do sistema SIGMA. Sem um banco funcional e sem automação, o sistema não opera. Além disso, elimina o bloqueador B1 e mitiga B2/B3 da engenharia.

**Independent Test**:
Executar `docker compose config --quiet` em ambiente com as variáveis básicas definidas e verificar que apenas `db` e `n8n` são renderizados e validados com código de saída 0.

**Acceptance Scenarios**:
1. **Given** variáveis de ambiente configuradas no `.env` (ou defaults), **When** executar `docker compose config --quiet`, **Then** o comando retorna código `0` e renderiza os serviços `db` e `n8n`.
2. **Given** o serviço `db` (PostgreSQL) em execução, **When** verificar as portas publicadas, **Then** a porta `5432` não deve estar publicada na interface do host (`0.0.0.0`), ficando restrita à rede `sigma-net`.

---

### User Story 2 - Observabilidade Opcional via Perfil (Priority: P2)

Como administrador de redes/infraestrutura,  
Quero subir a stack de telemetria legada utilizando `docker compose --profile monitoring up -d`,  
Para que Zabbix e Grafana estejam disponíveis sob demanda sem onerar os recursos da máquina com a execução padrão do SIGMA.

**Why this priority**: Permite manter o histórico e as configurações de observabilidade avançada de branches anteriores sem degradar o setup mínimo do hospital.

**Independent Test**:
Executar `docker compose --profile monitoring config --quiet` e certificar que inclui `zabbix-server`, `postgres-server` e `grafana`.

**Acceptance Scenarios**:
1. **Given** a flag `--profile monitoring`, **When** inspecionar a configuração com `docker compose --profile monitoring config --quiet`, **Then** a saída retorna código `0` contendo todos os 5 serviços (`db`, `n8n`, `postgres-server`, `zabbix-server`, `grafana`).
2. **Given** a ausência da flag `--profile monitoring`, **When** rodar o Compose padrão, **Then** os serviços `zabbix-server`, `postgres-server` e `grafana` não são iniciados.

---

### User Story 3 - Validação Contínua na Esteira de CI (Priority: P3)

Como mantenedor do repositório,  
Quero que o GitHub Actions valide automaticamente o Compose padrão, o perfil de monitoramento e o `.env.example`,  
Para que regressões de sintaxe YAML ou variáveis ausentes sejam bloqueadas antes do merge na `main`.

**Why this priority**: Evita que futuros commits voltem a introduzir marcadores de conflito ou quebras de sintaxe no repositório.

**Independent Test**:
Disparo do workflow `.github/workflows/ci.yml` com sucesso em todos os três passos de validação.

**Acceptance Scenarios**:
1. **Given** um PR direcionado para `main`, **When** o job `validate-compose` rodar, **Then** as etapas de validação básica, com profile e com `.env.example` devem passar com sucesso.

---

### Edge Cases

- **Variáveis de ambiente ausentes no host**: O Compose fornece fallbacks seguros para desenvolvimento local (ex.: `${POSTGRES_USER:-sigma}`) evitando erros de variável indefinida durante a inicialização rápida.
- **Portas em conflito no host**: As portas dos painéis web (`n8n` na 5678 e `grafana` na 3000) utilizam binds parametrizáveis com padrão `127.0.0.1` (`${N8N_BIND_IP:-127.0.0.1}:5678:5678`), evitando colisão com outros serviços escutando em interfaces externas.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O arquivo `docker-compose.yml` MUST ser um YAML 100% válido e sem qualquer marcador de conflito do Git (`<<<<<<<`, `=======`, `>>>>>>>`).
- **FR-002**: O Compose padrão (sem profiles) MUST instanciar apenas o banco de dados da aplicação (`db` - PostgreSQL 15) e o serviço de automação (`n8n`).
- **FR-003**: Os serviços `zabbix-server`, `postgres-server` e `grafana` MUST ser condicionados ao perfil `monitoring`.
- **FR-004**: Todas as credenciais sensíveis e portas sensíveis MUST ser parametrizadas via variáveis de ambiente, sem valores fixos vulneráveis expostos no código.
- **FR-005**: As imagens dos serviços MUST utilizar tags estáveis e determinísticas, eliminando o uso da tag `:latest`.
- **FR-006**: O repositório MUST disponibilizar um template `.env.example` documentando todas as variáveis necessárias.

### Key Entities

- **Core Network (`sigma-net`)**: Rede bridge isolada interna do Docker para comunicação entre contêineres.
- **Application DB (`sigma-db-data`)**: Volume persistente para os dados de incidentes e usuários do SIGMA.
- **Automation Volume (`n8n-data`)**: Volume persistente para credenciais e fluxos do n8n.
- **Monitoring DB (`zabbix-db-data`)**: Volume dedicado e isolado para a base de dados interna do Zabbix.
- **Observability Volume (`grafana-data`)**: Volume para dashboards e configurações do Grafana.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docker compose config --quiet` executa localmente e no CI com código de saída 0 e zero avisos de depreciação.
- **SC-002**: `docker compose --profile monitoring config --quiet` valida com código de saída 0.
- **SC-003**: Zero credenciais *hardcoded* e zero portas internas abertas publicamente para o host.
- **SC-004**: 100% de coerência entre o `docker-compose.yml`, `.env.example`, `ci.yml`, `README.md`, `doc/stack-de-tecnologia.md` e `05-seguranca-e-pendencias.md`.

---

## Assumptions

- Os serviços `api` (FastAPI) e `frontend` (React/Vue) serão integrados ao Compose em issues futuras, assim que os respectivos `Dockerfile` forem consolidados.
- O Zabbix e Grafana utilizam um banco PostgreSQL próprio (`postgres-server`) separado do banco de produção da aplicação (`db`), preservando a segregação de responsabilidades.
