# 5. Modelagem de baixo nível do front

Este documento mostra como as peças do front se ligam: quais componentes existem, quem busca dados
e quais estados cada tela pode assumir. Ele serve para a Joyce saber onde mexer sem quebrar a
integração e serve ao TCC como modelagem do frontend.

## 5.1 Árvore de componentes

```mermaid
flowchart TD
  main[main.jsx] --> App
  App["App.jsx<br/>sessão, tema, login/logout"] -->|sem sessão| Login[formulário de login]
  App -->|com sessão| Ops["Operations.jsx<br/>abas por perfil, tempo real, atualização a cada 15 s"]
  Ops --> HP[HealthPage] --> HC[HealthContent]
  Ops --> IP[IncidentsPage] --> IM[IncidentMetrics]
  Ops --> AP[ApprovalsPage] --> AI[ApprovalItem]
  Ops --> AU[AuditPage] --> AC[AuditContent]
  Ops --> DG[Diagnostic]
  HP & IP & AP & AU -.-> RS[ResourceState<br/>carregando / erro]
```

**Separação importante para o design system.** Os componentes `*Content`, `IncidentMetrics` e
`ApprovalItem` só recebem dados por props e desenham, sem chamar a API. Os componentes `*Page`
buscam os dados. A Joyce trabalha principalmente nos primeiros. Os testes de `OperationalPages.test.jsx`
renderizam esses componentes com dados fixos, e o mesmo padrão serve para novos componentes.

## 5.2 Camadas e responsabilidades

```mermaid
flowchart LR
  subgraph Apresentação["Apresentação (Joyce)"]
    CSS[App.css / tokens]
    UI["*Content, ApprovalItem,<br/>IncidentMetrics, futuros componentes"]
  end
  subgraph Estado["Estado e dados (integração)"]
    Pages["*Page, Operations, App"]
    Hooks["useResource · useActionRequest · useEvents"]
    API["api.js<br/>apiRequest · readEventStream"]
  end
  UI --> CSS
  Pages --> UI
  Pages --> Hooks --> API
  API -->|modo normal| Real[(API FastAPI)]
  API -->|"VITE_MOCK=1"| Mock[(src/mock/mockApi.js)]
```

| Peça | Responsabilidade |
|---|---|
| `api.js` | Monta a requisição com token Bearer, aplica tempo limite de 18 s e traduz códigos HTTP em mensagens em português |
| `useResource(path)` | Busca um recurso (GET) e devolve `{ data, error, loading, refresh }`; cancela ao sair da tela |
| `useActionRequest()` | Executa ações (POST) e cancela se o usuário sai da tela antes da resposta |
| `useEvents()` | Mantém o fluxo de tempo real (SSE), reconecta com espera progressiva e avisa as telas para recarregar |
| `src/mock/` | Substitui a API inteira quando `VITE_MOCK=1`; não entra no build de produção |

## 5.3 Estados de uma tela de dados

Toda tela que usa `useResource` passa pelos mesmos estados. O design precisa ter uma aparência
definida para cada um:

```mermaid
stateDiagram-v2
  [*] --> Carregando
  Carregando --> ComDados: 200 com itens
  Carregando --> Vazio: 200 com lista vazia
  Carregando --> Erro: falha de rede, 403, 5xx
  Carregando --> Login: 401 (sessão expirou)
  Erro --> Carregando: Tentar novamente
  ComDados --> Carregando: Atualizar, evento em tempo real ou 15 s
  Vazio --> Carregando: Atualizar
```

| Estado | Componente atual | Texto | Cenário mock |
|---|---|---|---|
| Carregando | `ResourceState` | "Carregando dados…" | `?cenario=lento` |
| Vazio | `.empty` | "Nenhum serviço cadastrado…", "Nenhum incidente registrado." | `?cenario=vazio` |
| Erro | `ResourceState` + `.error` | mensagem da API + "Tentar novamente" | `?cenario=erro` |
| Sem permissão | `.error` | "Seu perfil não tem permissão para esta operação." | — |
| Com dados | `*Content` | — | padrão |

## 5.4 Mensagens de erro (vêm de `api.js`)

| Código | Mensagem exibida |
|---|---|
| 401 | Sessão ausente, expirada ou credenciais inválidas. Entre novamente. |
| 403 | Seu perfil não tem permissão para esta operação. |
| 409 | O registro mudou ou a decisão não é permitida. Atualize os dados antes de tentar novamente. |
| 422 | Confira os dados informados. |
| 429 | Muitas tentativas. Aguarde antes de tentar novamente. |
| outros / rede | A API está indisponível no momento. / Não foi possível conectar à API. |

Os textos podem ser revisados pela Joyce; a regra é manter uma mensagem por código e nenhuma em inglês.

## 5.5 Sequência: abrir uma área e receber atualização em tempo real

```mermaid
sequenceDiagram
  actor U as Usuário
  participant O as Operations
  participant P as HealthPage
  participant R as useResource
  participant E as useEvents
  participant A as API
  U->>O: login concluído
  O->>E: abre /api/eng/eventos (SSE, Bearer)
  E-->>O: conectado ("Tempo real ativo")
  O->>P: render (revision)
  P->>R: useResource('/api/eng/saude')
  R->>A: GET /api/eng/saude
  A-->>R: { servicos, gerado_em, limite }
  R-->>P: data
  P-->>U: tabela
  A-)E: evento "incidente"
  E-->>O: revision + 1
  O->>P: render (nova revision)
  P->>R: busca de novo
  Note over O: sem eventos, um relógio de 15 s também incrementa revision
```

## 5.6 Sequência: ação com conflito (dois analistas no mesmo incidente)

```mermaid
sequenceDiagram
  actor X as Analista X
  actor Y as Analista Y
  participant A as API
  X->>A: POST /incidentes/{id}/resolver
  A-->>X: 200 → "Incidente resolvido."
  Y->>A: POST /incidentes/{id}/reconhecer (tela desatualizada)
  A-->>Y: 409 → "O registro mudou… Atualize os dados"
  Note over Y: a tela recarrega e os botões ficam desabilitados
```

## 5.7 Modelo de dados visto pelo front

```mermaid
classDiagram
  class Sessao {
    token: string
    usuario: string
    papel: suporte_n1 | analista_redes | gestor_ti
  }
  class Servico {
    id, nome, host, porta
    kind: tcp | http | https
    status: up | down | unknown | inactive
    ultima_em: data?
    latencia_ms: número?
    alvo_pct: número?
    janela_dias: número?
  }
  class Orcamento {
    completo: bool
    cobertura_pct, restante_max_min
    status: healthy | at_risk | partial | breaching
    esgota_em: data?
  }
  class Incidente {
    id, alvo_id, nome_alvo
    tipo, severidade: P1 | P2 | P3
    detectado_em, reconhecido_em?, resolvido_em?
  }
  class Metrica {
    n: amostras
    media_s, mediana_s, p95_s
  }
  class Aprovacao {
    id, acao, solicitante
    papel_minimo, estado
    criada_em, expira_em
  }
  class EventoAuditoria {
    id, ts, ator, acao, recurso
  }
  Servico "1" --> "0..1" Orcamento
  Servico "1" --> "*" Incidente : alvo_id
  Incidente ..> Metrica : MTTA / MTTR
```

O banco completo (tabelas `alvos`, `medicoes`, `slo`, `incidentes`, `eventos_operacionais`…) está em
`persistence/operational_models.py` e em `engenharia/docs/08-estado-operacional.md`. O front não acessa
o banco: só recebe o recorte acima pela API.
