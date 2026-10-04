# SIGMA

Sistema de monitoramento ativo de rede com apoio de IA, desenvolvido como TCC para a equipe de TI de um hospital oncológico (fundação pública).

## Problema que resolve

A equipe de TI trabalha sem visibilidade em tempo real da rede. Descobre as falhas só quando os usuários reclamam, o que gera:

- Demora para detectar e consertar incidentes (MTTD e MTTR altos).
- Técnicos sobrecarregados com tarefas manuais.
- Ausência de histórico para prevenir falhas.

Em um hospital, a queda da rede afeta prontuários eletrônicos e equipamentos médicos. O SIGMA troca o suporte reativo por um monitoramento contínuo, com custo zero de licenças.

## Funcionalidades

- **Alertas em tempo real:** o painel exibe qualquer anomalia em até 5 segundos após a detecção (RF01).
- **Captura de tráfego e alertas:** integração com o firewall pfSense e com uma sonda própria de análise de pacotes (RF02).
- **Diagnóstico assistido por IA:** chat no painel, com resposta em até 15 segundos (RF03, RNF04).
- **Privacidade (LGPD):** logs e mensagens são generalizados antes de ir à IA. IPs viram sub-redes, equipamentos viram categorias, nomes e identificadores médicos são removidos. Se o filtro falhar, nada é enviado (RF05).
- **Histórico de incidentes:** PostgreSQL com volume persistente e backup diário (RF04, RNF06).
- **Relatórios automáticos:** o n8n calcula métricas como o MTTR e envia relatórios à coordenação (RF06).
- **Controle de acesso:** login com perfis (Suporte N1, Analista de Redes, Gestor de TI). O n8n só é acessível por VLAN de gerência ou VPN (RF07).
- **Segurança de origens:** cada sonda e o pfSense usam chave exclusiva, com HTTPS, revogação e rotação (RNF07).

## Tecnologias

| Camada | Tecnologia | Onde roda |
|---|---|---|
| Backend / API | Python (FastAPI recomendado) | Contêiner |
| Tempo real | SSE (alertas) + WebSocket (chat) | Contêiner (API) |
| Banco de dados | PostgreSQL | Contêiner |
| Frontend | Vue.js ou React | Contêiner |
| Automação e relatórios | n8n | Contêiner |
| Análise de pacotes | Analisador customizado + Wireshark (apoio) | Host |
| Firewall | pfSense | Rede |
| IA (LLM) | OpenRouter / Groq (camadas gratuitas) | Nuvem |
| Implantação | Docker e Docker Compose | Servidor on-premise |

## Arquitetura

```
pfSense ───────────┐  (chave + HTTPS)
                   ├──► API (Python) ──► PostgreSQL ──► Backup diário
Sonda de pacotes ──┘        │                │
(host, chave própria)       │                └──► n8n (VLAN de gerência / VPN) ──► Relatórios
                            │
                            ├──► Generalização ──► Groq / OpenRouter ──► sugestão genérica
                            │
                            │ SSE / WebSocket
                            ▼
Técnicos (login + perfil) ──► Frontend (alerta original + chat com IA)
```

Implantação híbrida: `frontend`, `api`, `db` e `n8n` em contêineres. A sonda roda no host, porque precisa de acesso à interface física de rede. O pfSense fica na rede.

## Como instalar

Pré-requisitos: Docker, Docker Compose e um servidor ou VM Linux com acesso à interface de rede a ser monitorada.

1. Clone o repositório:
   ```bash
   git clone [URL do repositório]
   cd [nome-da-pasta]
   ```
2. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
   Preencha no `.env`: credenciais do banco, chave de cada sonda, chave do pfSense e chaves da IA (Groq/OpenRouter). **Nunca versione o `.env`.**
3. Suba os serviços em contêiner:
   ```bash
   docker compose up -d
   ```
4. Inicie a sonda no host:
   ```bash
   [comando de execução da sonda]
   ```
5. Configure o pfSense para enviar logs à API, com a chave própria e por HTTPS.

## Como usar

1. Acesse o painel e faça login com o seu perfil.
2. Acompanhe alertas e o status da rede em tempo real.
3. Abra o chat com a IA para receber a sugestão de diagnóstico. A IA devolve uma resposta genérica, e o painel mostra o alerta original para você ligá-la ao equipamento exato.
4. O Gestor de TI acessa o n8n (VLAN de gerência ou VPN) para os relatórios e gerencia usuários e chaves.

### Permissões por perfil

| Função | Suporte N1 | Analista de Redes | Gestor de TI |
|---|---|---|---|
| Ver alertas e status da rede | Sim | Sim | Sim |
| Usar o chat com a IA | Sim | Sim | Sim |
| Ver histórico e detalhes de pacotes | Não | Sim | Sim |
| Ver relatórios gerenciais | Não | Não | Sim |
| Gerenciar usuários e chaves | Não | Não | Sim |
| Acessar o n8n | Não | Não | Sim |

## Estrutura do projeto

```
[frontend/]  -> painel e chat com a IA
[api/]       -> API, autenticação, generalização e integrações
[probe/]     -> sonda de análise de pacotes (roda no host)
[n8n/]       -> fluxos de relatórios
[docs/]      -> estudo de caso e documentação do TCC
docker-compose.yml -> orquestração dos contêineres
.env.example       -> modelo de variáveis de ambiente
```

> Ajuste os nomes das pastas para a estrutura real do repositório.

## Validação

| Requisito | Meta |
|---|---|
| RF01 | Alerta no painel em até 5 s |
| RNF04 | Diagnóstico da IA em até 15 s |
| RNF06 | Backup restaurável e sem perda de dados ao recriar contêineres |
| RNF07 | Requisição sem chave, inválida ou revogada é recusada (401/403) |
| RNF08 | Zero vazamentos de dados sensíveis para a IA |

A validação completa está no estudo de caso (seção 6).

## Segurança e privacidade

- Chaves e senhas ficam em variáveis de ambiente, nunca no código.
- Não há tabela de correspondência (de/para) entre dados originais e generalizados.
- O histórico bruto fica dentro da infraestrutura da instituição, protegido por login, chaves e backup com acesso restrito.
- Evidências e testes usam **somente dados fictícios**, nos blocos reservados `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (RFC 5737) e `2001:db8::/32` (RFC 3849).
- A premissa de conformidade com o art. 12 da LGPD depende de homologação do DPO ou do jurídico da instituição.

## Limitações conhecidas

- Sem disco ou local de rede separado, o backup fica no mesmo servidor e não protege contra falha física total.
- As metas de 5 s e 15 s dependem das camadas gratuitas de IA. Com a IA fora do ar, o alerta continua no painel, sem o diagnóstico.
- A generalização é baseada em regras: reduz o risco, mas não o elimina. Por isso existe a falha segura.
- Arredondar horários e mascarar sub-redes pode reduzir a precisão do diagnóstico. O RNF08 mede essa perda com dados fictícios.
- O servidor on-premise e a VLAN ou VPN de gerência ainda precisam ser confirmados pela instituição.

## Status

Em desenvolvimento (TCC).

## Autor

Vinicius – [LinkedIn ou e-mail]
