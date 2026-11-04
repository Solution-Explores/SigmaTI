# 4. Fluxos de usuário

Fluxos levantados a partir do código atual (`App.jsx`, `Operations.jsx`, `OperationalPages.jsx`,
`Diagnostic.jsx`) e das regras da API. Cada fluxo indica as telas e mensagens envolvidas,
porque cada caixa é um estado que o design precisa cobrir.

## Perfis

| Perfil | Quem é | Áreas visíveis | Pode agir em |
|---|---|---|---|
| Suporte N1 (`suporte_n1`) | Técnico do primeiro atendimento | Saúde, Diagnóstico | Pedir diagnóstico à IA |
| Analista de Redes (`analista_redes`) | Responsável pela rede | + Incidentes, Aprovações | Reconhecer e resolver incidentes; solicitar e decidir aprovações |
| Gestor de TI (`gestor_ti`) | Coordenação de TI | + Auditoria | Tudo acima, decisões que exigem gestor e consulta à auditoria |

## F1. Entrar, navegar e sair

```mermaid
flowchart TD
  A([Abre o painel]) --> B[Tela de login]
  B -->|Usuário e senha| C{Credenciais válidas?}
  C -- não --> E1["Erro: Sessão ausente, expirada<br/>ou credenciais inválidas"] --> B
  C -- "muitas tentativas" --> E2["Erro: Muitas tentativas.<br/>Aguarde"] --> B
  C -- sim --> D[Carrega perfil]
  D --> F{Qual perfil?}
  F -- N1 --> G1[Saúde + Diagnóstico]
  F -- Analista --> G2[Saúde + Incidentes + Aprovações + Diagnóstico]
  F -- Gestor --> G3[Todas as áreas + Auditoria]
  G1 & G2 & G3 --> H[Área inicial: Saúde dos serviços]
  H --> I{Ação}
  I -- "Troca de aba" --> J[Foco vai para o título da área] --> I
  I -- Sair --> B
  I -- "Sessão expira ou é revogada" --> E1
  I -- "Recarrega a página" --> B
```

Observação: recarregar a página sempre volta ao login, porque o token fica só em memória.
Isso é uma decisão de segurança, não um defeito.

## F2. Acompanhar a saúde dos serviços (todos os perfis)

```mermaid
flowchart TD
  A[Abre Saúde dos serviços] --> B["Carregando dados…"]
  B --> C{Resposta}
  C -- erro --> D["Erro + Tentar novamente"] --> B
  C -- "lista vazia" --> E["Nenhum serviço cadastrado"]
  C -- ok --> F[Tabela de serviços]
  F --> G{Estado do serviço}
  G --> G1["Disponível"]
  G --> G2["Indisponível"]
  G --> G3["Sem dados recentes<br/>(nunca tratado como disponível)"]
  G --> G4["Desativado"]
  F --> H{Orçamento de disponibilidade}
  H --> H1["SLO não configurado"]
  H --> H2["Até X min · Observação parcial<br/>Sem projeção suficiente"]
  H --> H3["X min · Janela observada<br/>data de esgotamento ou Sem esgotamento"]
  H --> H4["Orçamento esgotado"]
  F -. "evento em tempo real ou a cada 15 s" .-> B
```

## F3. Tratar um incidente (Analista e Gestor)

```mermaid
flowchart TD
  A[Abre Incidentes] --> B[Métricas MTTD, MTTA, MTTR + histórico]
  B --> C{Estado do incidente}
  C -- Aberto --> D[Reconhecer] --> E["Incidente reconhecido."]
  C -- Aberto --> F[Resolver incidente]
  C -- Reconhecido --> F
  F --> G["Incidente resolvido."]
  C -- Resolvido --> H[Botões desabilitados]
  D & F --> X{"Alguém mudou antes?"}
  X -- "sim (409)" --> Y["O registro mudou… Atualize os dados"]
  E & G --> B
```

Ciclo de vida do incidente:

```mermaid
stateDiagram-v2
  [*] --> Aberto: coletor detecta falha
  Aberto --> Reconhecido: Reconhecer
  Aberto --> Resolvido: Resolver incidente
  Reconhecido --> Resolvido: Resolver incidente
  Resolvido --> [*]
```

## F4. Aprovação "quatro olhos" (Analista e Gestor)

Uma ação sensível, como reiniciar uma porta de switch, precisa da decisão de **outra pessoa**
com perfil suficiente. A página só registra a decisão e não executa nenhum comando.

```mermaid
sequenceDiagram
  actor A as Analista A
  participant P as Painel
  actor B as Analista ou Gestor B
  A->>P: Nova solicitação (ação + perfil mínimo)
  P-->>A: "Solicitação enviada para revisão por outro integrante."
  Note over A,P: Para A, os botões ficam desabilitados:<br/>"Você solicitou esta ação. Outro integrante precisa decidir."
  B->>P: Abre Aprovações e escreve a justificativa
  alt perfil de B abaixo do mínimo
    P-->>B: "Esta solicitação exige o perfil gestor_ti." (desabilitado)
  else passou 15 minutos
    P-->>B: "Solicitação expirada. Atualize a lista."
  else pode decidir
    B->>P: Aprovar ou Rejeitar
    P-->>B: "Solicitação aprovada." ou "Solicitação rejeitada."
  end
```

```mermaid
stateDiagram-v2
  [*] --> Pendente: solicitar
  Pendente --> Aprovada: outro integrante aprova com justificativa
  Pendente --> Rejeitada: outro integrante rejeita com justificativa
  Pendente --> Expirada: 15 minutos sem decisão
  Aprovada --> [*]
  Rejeitada --> [*]
  Expirada --> [*]
```

## F5. Diagnóstico com IA (todos os perfis)

```mermaid
flowchart TD
  A[Abre Diagnóstico] --> B[Preenche equipamento, IP e descrição]
  B --> C[Solicitar diagnóstico] --> D["Processando…"]
  D --> E{Resposta}
  E -- ok --> F["Mostra 'Dados enviados à IA' (já anonimizados)<br/>e 'Diagnóstico da IA'"]
  E -- "IA indisponível" --> G["Mensagem de indisponibilidade"]
  E -- erro --> H["Erro com texto"]
```

A seção "Dados enviados à IA" existe para mostrar ao usuário que IPs e nomes foram generalizados
antes de sair do hospital (LGPD). Ela é uma peça de confiança e não deve ser escondida.

## F6. Auditoria (Gestor)

```mermaid
flowchart TD
  A[Abre Auditoria] --> B{Trilha de sondas}
  B -- "0 registros" --> C["Trilha vazia: não há registros para verificar"]
  B -- íntegra --> D["Integridade consistente · N registros"]
  B -- adulterada --> E["Falha de integridade detectada (alerta)"]
  A --> F["Tabela: até 100 eventos operacionais<br/>horário, operador, ação, recurso"]
```

## F7. Tempo real

```mermaid
stateDiagram-v2
  [*] --> Conectando: login
  Conectando --> Ativo: fluxo aberto
  Ativo --> Reconectando: queda de rede ou API
  Reconectando --> Ativo: reconexão (espera 1s, 2s, 4s… até 15s)
  Ativo --> [*]: logout ou sessão expirada
```

Textos exibidos: "Conectando ao tempo real…", "Tempo real ativo" e "Reconectando ao tempo real;
dados atualizados também a cada 15 segundos." Mesmo sem tempo real, as telas se atualizam a cada 15 s.
