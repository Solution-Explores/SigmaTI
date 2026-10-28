# Stack de tecnologia

Tecnologias do SIGMA, o papel de cada uma e as decisões de segurança e privacidade que moldam a arquitetura. Os códigos RF e RNF referem-se aos requisitos do [estudo de caso](estudo-de-caso.md).

## Visão geral

| Camada | Tecnologia | Função | Onde roda |
|---|---|---|---|
| Backend | Python e FastAPI | API central, autenticação, generalização e orquestração | Host (ver nota abaixo) |
| Tempo real | SSE | Alertas e métricas no painel | API |
| Banco de dados | PostgreSQL 15 | Histórico de incidentes, usuários e sessões | Contêiner |
| Frontend | React 19 e Vite | Painel com login e diagnóstico | Host (ver nota abaixo) |
| Automação | n8n | Fluxos periódicos, métricas e relatórios | Contêiner |
| Análise de tráfego | Analisador customizado, com Wireshark de apoio | Sonda ativa e investigação | Host |
| Firewall | pfSense | Proteção da rede e envio de alertas | Rede |
| IA | OpenRouter e Groq | Diagnósticos e relatórios | Nuvem |
| Implantação | Docker e Docker Compose | Empacotamento dos serviços | Servidor |

Hoje a API e o frontend rodam no host, e o Compose sobe só `db` e `n8n`. A conteinerização de `api` e `frontend` está planejada. O chat por WebSocket também está previsto e ainda não existe no código.

## Backend e banco de dados

### FastAPI

A API recebe os alertas, valida a chave de cada origem, autentica os usuários do painel e aplica as permissões de cada perfil. Também generaliza logs e mensagens antes de qualquer envio à IA e orquestra as integrações.

O FastAPI foi escolhido por ser assíncrono, o que atende o fluxo contínuo de alertas, e por gerar a documentação OpenAPI automaticamente.

### PostgreSQL

- Guarda o histórico estruturado de incidentes (alertas, tempo de detecção e de reparo), os usuários (login, hash e cargo) e as sessões.
- Não guarda tabela de correspondência (de/para) entre identificadores originais e generalizados (RF05).
- O histórico fica dentro da infraestrutura e pode conter dados brutos. Login, chaves e backup com acesso restrito o protegem.
- Usa volume persistente (RF04). Recriar contêineres não apaga o histórico.
- O n8n acessa um usuário somente leitura, limitado a dados agregados ou generalizados.

## Frontend e tempo real

O painel é leve e responsivo, exige login (RF07) e traz o diagnóstico da IA. Ele mostra o alerta original ao técnico, que liga a sugestão genérica da IA ao equipamento exato (RNF08).

| Mecanismo | Fluxo | Uso | Situação |
|---|---|---|---|
| SSE | Servidor para cliente | Alertas e métricas | Em uso, com reconexão automática |
| WebSocket | Bidirecional | Chat com a IA | Previsto |

Meta de desempenho (RF01): o alerta aparece no painel em até 5 segundos após a detecção.

## Monitoramento e rede

- **pfSense** envia os logs de anomalias para a API com chave e HTTPS (RNF07). Roda fora do servidor da aplicação.
- **Analisador customizado** é a sonda ativa que analisa pacotes. Roda no host, porque o isolamento de rede padrão do Docker impede a captura na interface física. Cada sonda usa uma chave exclusiva e HTTPS (RNF07).
- **Wireshark** é um apoio opcional para quando o diagnóstico automático não bastar.

## IA e privacidade

### OpenRouter e Groq

Camadas gratuitas de LLM, usadas em diagnósticos interativos no painel e em relatórios automáticos. Meta (RNF04): diagnóstico em até 15 segundos após a falha. Se a IA estiver fora do ar, o alerta continua no painel, sem o diagnóstico.

### Generalização (RF05)

| Dado original | O que a IA recebe |
|---|---|
| IP específico | Máscara de sub-rede |
| Equipamento exato | Categoria do equipamento |
| Nome de pessoa ou identificador médico | Removido ou mascarado |
| Combinação única de horário, setor e equipamento | Generalizada ou descartada (horário arredondado, por exemplo) |
| Mensagem digitada no chat | Mesmo tratamento dos logs |

- Não há pseudonimização nem tabela de/para.
- Se a generalização falhar, o envio à IA é bloqueado.
- A premissa de conformidade é que o provedor de IA não tem meios razoáveis de reidentificar os dados. A Fcecon guarda os logs brutos, então a reidentificação interna é possível em tese, por cruzamento de horários.
- A premissa frente ao art. 12 da LGPD precisa ser homologada pelo DPO ou pelo jurídico da instituição.

### Testes da generalização (RNF08)

**Etapa 1: vazamentos.** Injetar logs falsos complexos, com identificação contextual e texto livre do chat. O critério é zero vazamentos, repetido a cada mudança nas regras de filtro.

**Etapa 2: custo da generalização.** Arredondar horários e mascarar sub-redes prejudica a precisão do diagnóstico? Para medir:

1. Prepare o mesmo cenário fictício em duas versões, original e generalizada.
2. Envie as duas ao mesmo modelo, com os mesmos parâmetros.
3. Repita cada caso várias vezes, porque o LLM varia a resposta.
4. Compare os diagnósticos e registre a taxa de equivalência.

A versão "original" também é fictícia. Enviar log real à nuvem como referência seria o vazamento que o projeto quer evitar. A meta de equivalência ainda não foi definida.

### Dados fictícios (RNF09)

As evidências do TCC usam só dados fictícios, em formato realista. É proibido imitar as faixas reais da Fcecon, inclusive as privadas (RFC 1918). Use apenas estes blocos:

| Tipo | Bloco | Norma |
|---|---|---|
| IPv4 | `192.0.2.0/24` | RFC 5737 |
| IPv4 | `198.51.100.0/24` | RFC 5737 |
| IPv4 | `203.0.113.0/24` | RFC 5737 |
| IPv6 | `2001:db8::/32` | RFC 3849 |

A regra vale também para nomes de host, VLANs, setores, modelos e padrões de nomenclatura. Para testar várias sub-redes, divida os blocos /24 em /26 ou /28. Logs reais nunca entram no TCC.

## Automação com n8n

O n8n roda com volume persistente. A interface não fica exposta na rede hospitalar geral: só a rede de gerência (VLAN isolada) ou uma VPN a alcança, com credenciais próprias do Gestor de TI (RF07).

O fluxo programado:

1. Extrai dados do PostgreSQL, com o usuário somente leitura.
2. Calcula métricas, como o MTTR.
3. Envia ao OpenRouter só dados agregados ou generalizados.
4. Dispara relatórios executivos (PDF ou e-mail) para a coordenação.

## Infraestrutura

### Onde cada parte roda

| Onde | Componentes | Motivo |
|---|---|---|
| Contêineres, núcleo | `db` (PostgreSQL), `n8n` | Portabilidade e isolamento |
| Contêineres, observabilidade | `zabbix-server`, `postgres-server`, `grafana` (perfil `monitoring`) | Telemetria sob demanda |
| Host (servidor ou VM) | API, frontend e sonda de pacotes | A sonda precisa da interface física |
| Rede | pfSense | Firewall da rede |

### Portas, imagens e credenciais

- O PostgreSQL não publica porta fora da rede interna do Docker.
- n8n (5678), Grafana (3000) e Zabbix (10051) escutam em loopback. O acesso remoto exige um IP de gerência ou VPN e o firewall da instalação.
- As imagens têm release e digest fixos em `docker-images.lock.json`. Veja [Portas e imagens](../operacao/politica-imagens-e-portas.md).
- As credenciais do PostgreSQL, do Zabbix e do Grafana vêm do ambiente ou do `.env`, sem senha padrão no Compose. Preencha todas antes de validar o Compose, inclusive as do perfil `monitoring`. Veja [Credenciais da infraestrutura](../../README.md#credenciais-da-infraestrutura).
- O n8n usa o cadastro nativo de owner na primeira abertura. As variáveis antigas de Basic Auth não fazem parte da configuração.
- Variáveis de inicialização não rotacionam credenciais já gravadas.

### Backup

- Backup diário do PostgreSQL, com cópia em disco ou local de rede fisicamente separado. Sem esse destino, registre a limitação.
- Os logs brutos podem conter IPs e identificadores, então o acesso aos backups é restrito.
- O teste de restauração faz parte da validação.

Procedimento completo em [Backup, restauração e atualização](../operacao/backup-restauracao.md).

## Autenticação de origens (RNF07)

| Item | Decisão |
|---|---|
| Quem se autentica | Cada sonda e o pfSense |
| Mecanismo | API key ou token, exclusivo por origem |
| Onde é validado | Na API, em toda requisição de entrada |
| Transporte | HTTPS |
| Onde ficam as chaves | Variáveis de ambiente do servidor, nunca no código |
| Revogação e rotação | Mecanismo administrativo na API, restrito ao Gestor de TI |
| Chave inválida ou revogada | Requisição recusada (HTTP 401 ou 403) |

## Acesso ao painel e ao backoffice (RF07)

- O login é obrigatório para o painel e o diagnóstico.
- Os usuários ficam no PostgreSQL, com hash de senha (Argon2id).
- As permissões por perfil estão em [Permissões por perfil](../../README.md#permissões-por-perfil).

## Fluxo de dados

```
pfSense (rede) ──────┐  (chave + HTTPS)
                     ├──► API (Python) ──► PostgreSQL ──► Backup diário
Sonda de pacotes ────┘        │                │          (local separado,
(host, chave própria)         │                │           acesso restrito)
                              │                │ leitura somente de dados
                              │                ▼ agregados ou generalizados
                              │          n8n (VLAN de gerência / VPN)
                              │             │
                              │             └──► Generalização ──► OpenRouter ──► Relatórios
                              │
                              ├──► Generalização (falha segura) ──► Groq / OpenRouter
                              │      (logs e chat, sem tabela de/para)       │
                              │                                              ▼
                              │                          sugestão genérica da IA
                              │ SSE                                          │
                              ▼                                              │
Técnicos (login + perfil) ──► Frontend (alerta original + diagnóstico) ◄─────┘
                              (o técnico liga a sugestão ao equipamento exato)
```

A validação (RNF08) fica fora do fluxo de produção: usa dados fictícios dos blocos RFC 5737 e RFC 3849, na etapa 1 (zero vazamentos) e na etapa 2 (custo da generalização), e o resultado vai para o Anexo A do estudo de caso.
