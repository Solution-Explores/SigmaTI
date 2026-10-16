# Implementation Plan: Resolver Marcadores de Conflito no docker-compose.yml

**Branch**: `002-resolver-conflitos-docker-compose` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-resolver-conflitos-docker-compose/spec.md`

---

## Summary

Resolução definitiva de marcadores de conflito de mesclagem no `docker-compose.yml`, padronizando a arquitetura em duas camadas: **Core SIGMA** (`db` + `n8n`) como execução padrão e **Observabilidade** (`zabbix-server`, `postgres-server`, `grafana`) encapsulada sob o perfil `monitoring`. O plano inclui saneamento de vulnerabilidades (B1, B2, B3), criação do template `.env.example`, validação tripla no CI e sincronização de toda a documentação do projeto.

---

## Technical Context

**Language/Version**: YAML (Docker Compose Specification v2)  
**Primary Dependencies**: Docker Compose 2.x+, PostgreSQL 15-alpine, n8n 1.80.0, Zabbix 6.4-alpine, Grafana 10.4.0  
**Storage**: Volumes Docker nomeados persistentes (`sigma-db-data`, `n8n-data`, `zabbix-db-data`, `grafana-data`)  
**Testing**: `docker compose config --quiet` (modo padrão, com profile e com `.env.example`)  
**Target Platform**: Linux / Windows Docker Engine  
**Project Type**: Infraestrutura e orquestração de contêineres  
**Constraints**: Zero credenciais em texto puro; sem exposição pública da porta 5432; compatibilidade com `.github/workflows/ci.yml`.

---

## Constitution & Security Check (05-seguranca-e-pendencias.md)

| Bloqueador | Requisito do Plano | Decisão Arquitetural |
|:---|:---|:---|
| **B1** | YAML inválido por marcadores | Remoção completa dos delimitadores de conflito (`<<<<<<<`, `=======`, `>>>>>>>`). |
| **B2** | Credenciais fixas e porta 5432 exposta | Variáveis `${POSTGRES_USER}`, `${POSTGRES_PASSWORD}` e remoção de `ports: 5432:5432` no host. |
| **B3** | Imagens com `:latest` | Fixação de tags LTS (`postgres:15-alpine`, `n8nio/n8n:1.80.0`, `grafana:10.4.0`). |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-resolver-conflitos-docker-compose/
├── spec.md              # Especificação de Requisitos e Critérios de Aceite
├── plan.md              # Plano de Implementação e Arquitetura (este arquivo)
├── tasks.md             # Decomposição e acompanhamento de tarefas
└── checklist.md         # Checklist de Qualidade do Spec-Kit
```

### Source Code & Configurations (repository root)

```text
├── docker-compose.yml                          # Orquestração sanitizada e profiles
├── .env.example                                # Template de variáveis de ambiente
├── .github/workflows/ci.yml                    # Pipeline de CI com validação tripla
├── README.md                                   # Instruções de instalação e profiles
├── doc/stack-de-tecnologia.md                  # Especificação da stack e Seção 6
└── engenharia/docs/05-seguranca-e-pendencias.md # Atualização dos status B1, B2 e B3
```

---

## Complexity Tracking

| Decisão | Por que foi necessária | Alternativa Rejeitada |
|:---|:---|:---|
| Dois bancos de dados (`db` e `postgres-server`) | O Zabbix exige controle do schema próprio de telemetria; misturar com o banco da aplicação hospitalar violaria o isolamento de dados do TCC e a LGPD. | Usar um único banco compartilhado (rejeitado por acoplamento excessivo e risco de contaminação de dados). |
| Docker Compose Profiles (`monitoring`) | Permite manter Zabbix/Grafana sem obrigar máquinas de desenvolvimento e testes do hospital a rodarem 5 contêineres pesados simultaneamente. | Deletar Zabbix e Grafana do projeto (rejeitado para não perder o trabalho de observabilidade prévio). |
