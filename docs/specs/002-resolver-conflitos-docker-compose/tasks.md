---
description: "Lista de tarefas da Issue #2 - Resolução de Conflitos no docker-compose.yml"
---

# Tasks: Resolver Marcadores de Conflito no docker-compose.yml

**Input**: Design documents from `docs/specs/002-resolver-conflitos-docker-compose/`  
**Prerequisites**: `spec.md`, `plan.md`

## Correções posteriores à revisão K01–K06

Revisor responsável: **Vinícius Lima**. Após apresentação dos resultados, autorizou
publicação e conclusão dos escopos validados, condicionadas à integração verificada.
A lista original abaixo registra a entrega inicial; os
resultados e limites atuais estão no [registro de validação](../revisao-k01-k06/validacao.md).

- [x] Substituir placeholders de clone pela URL real e selecionar `dev`.
- [x] Distinguir primeira instalação de atualização com dados.
- [x] Documentar migração lógica futura para `sigma-db-data`, preservando a origem.
- [x] Identificar ausência de máquina de implantação informada pela equipe.
- [ ] Executar e homologar migração quando houver ambiente e dados de origem.
- [x] Registrar autorização de Vinícius Lima após apresentação dos resultados.
- [x] Registrar a integração à main e os dois CIs aprovados no registro consolidado.

## Formato: `[ID] [P?] [Story] Descrição`

- **[P]**: Executável em paralelo
- **[Story]**: Mapeamento para Histórias de Usuário (US1, US2, US3)

---

## Phase 1: Setup (Template de Ambiente)

- [x] T001 [P] [US1] Criar arquivo de modelo de ambiente com todas as variáveis requeridas e documentadas em `.env.example`

---

## Phase 2: Foundational (Orquestração do Docker Compose)

- [x] T002 [US1] Remover marcadores de conflito (`<<<<<<<`, `=======`, `>>>>>>>`) e atributo obsoleto `version` em `docker-compose.yml`
- [x] T003 [US1] Estruturar os serviços principais (`db` PostgreSQL e `n8n`) na rede interna `sigma-net`, sem exposição da porta 5432 no host em `docker-compose.yml`
- [x] T004 [US2] Encapsular os serviços de observabilidade (`postgres-server`, `zabbix-server`, `grafana`) sob o perfil `monitoring` em `docker-compose.yml`
- [x] T005 [US1] Substituir tags `:latest` por versões LTS estáveis (`postgres:15-alpine`, `n8nio/n8n:1.80.0`, `grafana:10.4.0`) em `docker-compose.yml`

---

## Phase 3: CI/CD Pipeline

- [x] T006 [US3] Atualizar job `validate-compose` em `.github/workflows/ci.yml` para validar o Compose padrão, o perfil `monitoring` e a integridade de `.env.example`

---

## Phase 4: Documentação e Rastreabilidade

- [x] T007 [P] [US1] Atualizar `README.md` com comandos de inicialização (`docker compose up -d` e `--profile monitoring`)
- [x] T008 [P] [US2] Atualizar tabela de infraestrutura na Seção 6 e legenda do fluxo de dados em `doc/stack-de-tecnologia.md`
- [x] T009 [P] [US1] Registrar resolução do bloqueador B1 e mitigação de B2 e B3 em `engenharia/docs/05-seguranca-e-pendencias.md`

---

## Phase 5: Verificação de Aceite

- [x] T010 [US1] Validar que `docker compose config --quiet` roda localmente com código 0 e sem avisos
- [x] T011 [US2] Validar que `docker compose --profile monitoring config --quiet` roda localmente com código 0
- [x] T012 [US3] Validar que `docker compose --env-file .env.example --profile monitoring config --quiet` roda com código 0
- [x] T013 [US1] Validar via busca textual que nenhum marcador de conflito remanesce no repositório
