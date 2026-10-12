# Quality Checklist: Resolver Marcadores de Conflito no docker-compose.yml

**Purpose**: Verificação de conformidade da Issue #2 contra os padrões arquiteturais, de segurança e de integração contínua do SIGMA.  
**Created**: 2026-10-12  
**Feature**: [spec.md](spec.md) | [plan.md](plan.md) | [tasks.md](tasks.md)

---

## 1. Integridade do Arquivo e Sintaxe

- [x] CHK001 O arquivo `docker-compose.yml` é YAML válido e não contém delimitadores de conflito (`<<<<<<<`, `=======`, `>>>>>>>`).
- [x] CHK002 O atributo obsoleto `version` foi removido para total conformidade com a especificação Docker Compose v2.

## 2. Segurança e Hardening (Critérios B1, B2 e B3)

- [x] CHK003 Nenhuma credencial ou senha padrão vulnerável está fixada em código puro no Compose.
- [x] CHK004 A porta `5432` do banco de dados da aplicação não está aberta publicamente na interface do host.
- [x] CHK005 Portas de interfaces web de gerência (`n8n` e `grafana`) realizam bind restrito a `127.0.0.1` por padrão.
- [x] CHK006 Nenhuma imagem de contêiner utiliza a tag mutável `:latest`.

## 3. Gestão de Configuração e CI/CD

- [x] CHK007 O arquivo `.env.example` está presente na raiz com documentação clara de todas as variáveis do sistema.
- [x] CHK008 A esteira de CI em `.github/workflows/ci.yml` valida tanto a stack básica quanto o perfil `--profile monitoring` e o template `.env.example`.

## 4. Coerência Documental e Rastreabilidade

- [x] CHK009 O `README.md` detalha com clareza o uso dos comandos do Compose e a distinção de perfis.
- [x] CHK010 O `doc/stack-de-tecnologia.md` reflete a organização de serviços mantidos.
- [x] CHK011 O arquivo `engenharia/docs/05-seguranca-e-pendencias.md` registra formalmente a resolução de B1 e a mitigação de B2 e B3.
