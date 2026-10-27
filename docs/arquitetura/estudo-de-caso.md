# Estudo de Caso: Projeto SIGMA

**Instituição:** Fcecon (hospital oncológico, fundação pública)
**Tema:** Monitoramento ativo de rede com apoio de Inteligência Artificial

---

## 1. Problemática

### 1.1 Resumo

- **Alta dependência da tecnologia:** os hospitais dependem totalmente de sistemas e redes de computadores (prontuários eletrônicos, comunicação, aparelhos médicos e gestão) para funcionar corretamente no dia a dia.
- **Atuação "no escuro" (modelo reativo):** sem sistemas de monitoramento adequados, a equipe de TI só descobre que algo está errado depois que o problema já aconteceu e prejudicou o atendimento ou a operação do hospital.
- **Dificuldades extras no setor público:** a situação é mais crítica em fundações públicas brasileiras por três motivos:
  - Falta de orçamento adequado.
  - Dificuldade para contratar profissionais especializados.
  - Ausência de métodos organizados de gestão de TI.

### 1.2 Detalhamento

A Tecnologia da Informação tem papel fundamental e estrutural em ambientes de saúde de alta complexidade. Sistemas críticos, como prontuários eletrônicos, plataformas de comunicação, equipamentos médicos e ferramentas de gestão hospitalar, dependem diretamente da estabilidade e da disponibilidade contínua da rede de dados.

A ausência de sistemas adequados de monitoramento resulta em um modelo de suporte puramente reativo. A equipe de TI só toma conhecimento de falhas e incidentes depois que o problema se materializou e causou impacto nas operações diárias.

Essa vulnerabilidade é agravada no contexto das fundações públicas brasileiras por restrições orçamentárias, pela dificuldade na contratação de pessoal especializado e pela falta de frameworks estruturados de governança e gestão de TI.

### 1.3 Problema central na Fcecon

A equipe de TI trabalha sem visibilidade em tempo real da rede e descobre as falhas apenas quando os usuários as relatam informalmente. Consequências:

- Demora para detectar e consertar incidentes (aumento do tempo de resposta e reparo).
- Técnicos sobrecarregados com tarefas manuais.
- Ausência de dados históricos para prevenir falhas futuras.

> Em um hospital oncológico, onde a continuidade do atendimento aos pacientes é vital, essas falhas deixam de ser apenas um problema técnico e passam a representar um **risco crítico de responsabilidade ética e institucional**.

---

## 2. Solução

O projeto **SIGMA** promove a transição de um modelo de suporte puramente reativo para um **ecossistema de monitoramento ativo e inteligente**.

| Problema | Como o SIGMA resolve |
|---|---|
| Atuação "no escuro" | Substitui relatos informais por um sistema contínuo de detecção de anomalias, integrado via API e ferramentas próprias de análise de tráfego. |
| Dificuldade de contratar especialistas | Incorpora IA (modelos LLM via OpenRouter/Groq) de forma interativa no frontend. Diante de uma falha detectada pelo firewall (pfSense) ou pelo analisador de pacotes, a IA fornece diagnósticos assistidos em tempo real, reduzindo o **MTTD** (Mean Time to Detect) e o **MTTR** (Mean Time to Repair). |
| Ausência de gestão organizada e de histórico | Centraliza todos os eventos da rede no PostgreSQL, com volumes persistentes e backup diário. O n8n processa os dados periodicamente, calcula métricas como o MTTR e gera relatórios gerenciais automatizados. Isso libera a equipe de tarefas manuais para focar em manutenção preventiva. |
| Falta de orçamento | Usa exclusivamente tecnologias de código aberto (Python, PostgreSQL, n8n, pfSense, Docker) e camadas gratuitas de processamento em nuvem ("0$"). Entrega alta disponibilidade para a rede crítica sem ônus financeiro à instituição. |
| Servidores locais heterogêneos | A implantação híbrida (contêineres Docker e sonda no host) roda de forma uniforme, sem conflitos de dependência, no servidor on-premise da instituição, sem perder o acesso à interface física de rede. |
| Risco de alertas falsos, acesso indevido e vazamento de dados | Toda comunicação com a API é autenticada por chave exclusiva (RNF07). O painel exige login com perfis de acesso e o n8n fica restrito a uma rede de gerência ou VPN (RF07). Só dados generalizados vão à IA na nuvem (RF05), com testes de vazamento e medição do custo da generalização (RNF08). As evidências usam apenas dados fictícios, sem expor a topologia real (RNF09). Os backups têm acesso restrito (RNF06). O conjunto sustenta a conformidade com a LGPD, sujeito à homologação do DPO. |

---

## 3. Requisitos Funcionais

*O que o sistema deve fazer.*

| ID | Requisito | Descrição |
|---|---|---|
| RF01 | Monitoramento em tempo real e mensurável | O sistema deve possuir um frontend que exiba o estado da infraestrutura de rede para a equipe de TI, eliminando o modelo de suporte "no escuro". A comunicação com a API (via WebSockets ou SSE) deve garantir que **qualquer alerta de falha ou anomalia seja exibido no painel em até 5 segundos após a detecção** pelo núcleo do sistema. |
| RF02 | Captura ativa de tráfego e alertas | A API (Python) integra-se ao firewall (pfSense) e à ferramenta própria de análise de pacotes para receber logs e alertas automáticos de anomalias, eliminando a dependência de chamados informais dos usuários. |
| RF03 | Diagnóstico interativo assistido por IA | Ao detectar um erro, a API processa o log e o envia, **já generalizado (RF05)**, a um LLM (Groq/OpenRouter) para obter sugestão de diagnóstico e resolução. O resultado é apresentado em um módulo de chat no painel, onde o técnico pode interagir com a IA. |
| RF04 | Registro estruturado de histórico | Armazena todo o histórico de incidentes em banco relacional (PostgreSQL), permitindo analisar tendências e prevenir falhas futuras. Esse histórico fica **dentro da infraestrutura da instituição** e pode conter dados brutos, por isso é protegido pelos RF07, RNF06 e RNF07. |
| RF05 | Anonimização, generalização e privacidade (LGPD) | Antes de enviar logs ou mensagens do chat à nuvem (Groq/OpenRouter), a API aplica **técnicas de generalização**: IPs específicos viram máscaras de sub-rede e equipamentos exatos viram categorias de equipamento. Nomes de pessoas, identificadores médicos e combinações que permitam identificar alguém (horário, setor, equipamento único) são mascarados ou descartados. O projeto **optou por não usar pseudonimização**: não existem tabelas de correspondência (de/para), para evitar a retenção de dados caracterizados como pessoais. Embora a Fcecon preserve os logs brutos no PostgreSQL (o que, em tese, permite reidentificação interna por cruzamento de horários), a **premissa de conformidade é que o provedor de IA não possui meios razoáveis de reidentificar os dados**. Se a anonimização falhar, o envio é bloqueado (falha segura). *Nota: a validação dessa premissa frente ao art. 12 da LGPD exige homologação formal do Encarregado de Dados (DPO) ou do setor jurídico da instituição.* |
| RF06 | Geração automatizada de relatórios analíticos | O n8n extrai os registros históricos do PostgreSQL, calcula métricas (como o MTTR) e envia ao LLM (OpenRouter) **somente dados agregados ou já generalizados**. Distribui automaticamente relatórios gerenciais sobre vulnerabilidades e tendências da rede. |
| RF07 | Controle de acesso e restrição de rede | O painel e o chat com a IA são protegidos por **login**, com usuários em tabela no banco, **senhas armazenadas com hash** (bcrypt ou Argon2) e **perfis restritos** (ex.: Analista de Redes, Suporte N1, Gestor de TI). O **n8n não fica exposto à rede hospitalar geral**. Para evitar o custo operacional do acesso apenas via servidor local, sua interface é disponibilizada **exclusivamente por rede restrita de gerência (VLAN isolada) ou túnel seguro (VPN)**, com **credenciais próprias e acesso limitado ao Gestor de TI**. |

---

## 4. Requisitos Não Funcionais

*Como o sistema deve operar.*

| ID | Requisito | Descrição |
|---|---|---|
| RNF01 | Baixo custo e tecnologias abertas | Devido à restrição orçamentária ("0$"), o sistema é construído exclusivamente com ferramentas gratuitas ou de código aberto (Python, PostgreSQL, pfSense, n8n, Docker e Docker Compose) e IA em camadas gratuitas (Groq/OpenRouter). |
| RNF02 | Arquitetura desacoplada e escalável | Padrão de três camadas separadas: **Frontend**, **API (backend)** e **Banco de dados**, facilitando manutenção e expansões futuras. |
| RNF03 | Análise de pacotes integrada | O sistema incorpora nativamente o código de análise de pacotes fornecido, dispensando o uso manual de interfaces como o Wireshark no dia a dia. A arquitetura permite o uso do Wireshark em paralelo, como apoio opcional para investigações profundas quando o diagnóstico automático não for suficiente. |
| RNF04 | Desempenho e agilidade no diagnóstico | O processamento dos alertas e das respostas da IA deve ser rápido (favorecido pela velocidade do Groq), com o objetivo central de reduzir o MTTD e o MTTR. O sistema deve **retornar o diagnóstico da IA no painel em no máximo 15 segundos a partir do momento da falha**. |
| RNF05 | Implantação híbrida (contêineres e host) | O sistema adota um modelo de implantação híbrido para suprir restrições de rede. **Em contêineres Docker independentes** (orquestrados com Docker Compose): API, banco de dados (PostgreSQL), frontend e sistema de automação (n8n). **Nativamente no sistema operacional do host** (servidor ou máquina virtual): a sonda customizada de análise de tráfego, que precisa de acesso irrestrito à interface física para capturar pacotes. A sonda se conecta externamente à API, com autenticação (RNF07). O pfSense permanece fora do servidor, como firewall da rede. |
| RNF06 | Persistência, backup e controle de acesso (LGPD) | Para resguardar o registro estruturado de incidentes (RF04), o PostgreSQL e o n8n utilizam **volumes persistentes mapeados no disco físico do servidor**, evitando perda de dados caso os contêineres sejam recriados ou apagados. O sistema executa **backup diário automatizado** do banco, armazenado em disco ou local de rede **fisicamente separado do servidor principal**. Como os logs brutos podem conter IPs e identificadores antes da generalização, os arquivos de backup têm **controle estrito de acesso**. A ausência de um destino externo na Fcecon, se confirmada, é registrada como limitação conhecida (seção 7). |
| RNF07 | Segurança, autenticação e rotação de chaves | A comunicação entre a sonda (no host) e a API é **obrigatoriamente autenticada** por chave de segurança (API Key ou token) **exclusiva para cada sonda**, impedindo alertas falsos. A mesma regra vale para o envio de logs pelo pfSense, e o tráfego usa **HTTPS**. As chaves ficam **exclusivamente em variáveis de ambiente do servidor**, nunca no código-fonte. A API oferece **mecanismo administrativo de revogação e rotação** das credenciais, acessível apenas ao Gestor de TI (RF07). |
| RNF08 | Testes de vazamento e medição de degradação da IA | O mecanismo de anonimização (RF05) é submetido a baterias de testes controlados, em duas etapas. **Etapa 1, bloqueio de vazamentos:** injeção de logs falsos complexos (mocks), incluindo identificação contextual (combinação de horário, setor e equipamento único que permita deduzir quem operava o terminal) e texto livre do chat. O critério de aprovação é **zero vazamentos**, e os testes se repetem a cada alteração nas regras de filtro. **Etapa 2, custo da generalização:** mede-se se o **arredondamento de horários** ou o **mascaramento de sub-redes** degrada a capacidade do LLM de **correlacionar eventos e emitir diagnósticos técnicos precisos**. A medição compara, com o mesmo modelo e as mesmas entradas, o diagnóstico obtido com o log fictício original e com o log fictício generalizado, com repetições para absorver a variação natural do LLM. Os logs originais dessa comparação também são fictícios (RNF09). O objetivo é garantir o **equilíbrio entre privacidade e eficiência**. A nuvem recebe contexto estrutural generalizado e devolve uma sugestão técnica genérica, cabendo ao técnico de TI **correlacionar a recomendação ao equipamento exato** pelo alerta original exibido no painel. |
| RNF09 | Proteção de topologia e documentação acadêmica | Como medida **inegociável** de segurança institucional, todas as evidências (logs de entrada e saída) do Anexo do TCC usam **estritamente dados fictícios (mocks)**, com formato realista e valores inventados. É **terminantemente proibido** mimetizar as faixas de IP reais da Fcecon, inclusive as faixas privadas (RFC 1918), de modo que a banca não consiga inferir a topologia. Os mocks adotam **blocos oficialmente reservados para documentação**: `192.0.2.0/24`, `198.51.100.0/24` e `203.0.113.0/24` (RFC 5737) para IPv4 e `2001:db8::/32` (RFC 3849) para IPv6. A proteção vale também para **nomes de host, VLANs, setores, modelos de equipamento e padrões de nomenclatura**, que igualmente revelam a topologia. É proibida a publicação de logs verdadeiros no documento final. |

---

## 5. Requisitos de Negócio

*O valor que o sistema entrega.*

| ID | Requisito | Descrição |
|---|---|---|
| RN01 | Garantia de continuidade assistencial | Protege a estabilidade da rede que sustenta sistemas vitais (prontuários eletrônicos e aparelhos médicos), mitigando riscos éticos e institucionais de paradas não programadas no hospital oncológico. |
| RN02 | Compensação da escassez de pessoal | A IA atua como multiplicador de forças, compensando a dificuldade da fundação pública em contratar e reter profissionais altamente especializados na triagem de problemas complexos. |
| RN03 | Redução de sobrecarga e burocracia | A automação de alertas (API) e a emissão automática de relatórios (n8n) desoneram a equipe técnica de tarefas repetitivas, liberando tempo para a infraestrutura preventiva. |

---

## 6. Métricas de Validação

*Como a banca pode comprovar que o sistema funciona.*

| Requisito | Métrica | Como testar |
|---|---|---|
| RF01 | Alerta no painel em ≤ 5 s após a detecção | Simular uma falha e cronometrar entre o registro na API e a exibição na tela |
| RNF04 | Diagnóstico da IA no painel em ≤ 15 s após a falha | Simular uma falha e cronometrar até a resposta aparecer no chat |
| RNF05 | Serviços em contêiner sobem com um comando e a sonda no host envia dados à API | Executar `docker compose up`, verificar que os serviços ficam saudáveis e que a sonda registra tráfego na API |
| RNF06 | Nenhum dado perdido ao recriar contêineres | Recriar os contêineres (sem apagar os volumes) e confirmar que o histórico continua no painel |
| RNF06 | Backup restaurável | Restaurar o último backup em ambiente limpo e conferir a contagem de incidentes |
| RNF06 | Backup protegido | Tentar ler o backup com um usuário sem permissão e confirmar que o acesso é negado |
| RNF07 | Requisição sem chave é recusada | Enviar um alerta falso sem chave (ou com chave inválida) e confirmar a recusa (HTTP 401/403) |
| RNF07 | Chave revogada deixa de funcionar | Revogar a chave de uma sonda e confirmar que ela não envia mais dados |
| RNF07 | Rotação de chave funciona | Rotacionar a chave e confirmar que a antiga é recusada e a nova é aceita |
| RNF07 | Chaves fora do código-fonte | Buscar chaves no repositório e confirmar que não existem |
| RF05 | Generalização aplicada | Enviar logs com IPs e equipamentos e confirmar que a saída traz sub-rede e categoria, não os valores exatos |
| RF05 | Sem tabela de correspondência | Inspecionar o esquema do banco e o código e confirmar que não existe mapeamento de/para |
| RF05 | Provedor não reidentifica | Tentar reidentificar pessoas ou equipamentos apenas com a saída enviada à IA, sem acesso ao banco, e confirmar que nenhum é identificado |
| RF05 | Falha segura | Forçar um erro no filtro e confirmar que nada é enviado à IA |
| RNF08 (etapa 1) | Zero vazamentos em padrões óbvios | Injetar logs e mensagens de chat fictícios com nomes, IPs e identificadores médicos em formatos variados e confirmar que nada sensível chega à IA |
| RNF08 (etapa 1) | Zero vazamentos contextuais | Injetar combinações de horário, setor e equipamento único e confirmar que a saída não permite deduzir a pessoa |
| RNF08 (etapa 1) | Testes repetidos após mudança | Alterar uma regra de filtro e confirmar que a bateria é executada de novo, com resultado registrado |
| RNF08 (etapa 2) | Arredondamento de horário não degrada a correlação | Comparar, nos mocks, o diagnóstico com horário exato e com horário arredondado, com repetições, e registrar a taxa de diagnósticos equivalentes (meta a definir) |
| RNF08 (etapa 2) | Máscara de sub-rede não degrada o diagnóstico | Comparar, nos mocks, o diagnóstico com IP completo e com sub-rede, com repetições, e registrar a taxa de diagnósticos equivalentes (meta a definir) |
| RNF08 (etapa 2) | Comparação sem dados reais | Confirmar que nenhum log real foi enviado à nuvem para servir de referência |
| RNF09 | Mocks só com blocos reservados | Varrer o Anexo A e confirmar que todo IPv4 está em `192.0.2.0/24`, `198.51.100.0/24` ou `203.0.113.0/24`, e todo IPv6 em `2001:db8::/32` |
| RNF09 | Nenhuma faixa real | Comparar o Anexo A com o plano de endereçamento da Fcecon e confirmar que não há coincidência de faixa, host, VLAN, setor ou modelo |
| RNF09 | Nenhum log real no documento | Revisão do Anexo A por uma segunda pessoa, antes da entrega |
| RF06 | n8n não envia dados brutos | Inspecionar o que o n8n envia ao OpenRouter e confirmar que só há dados agregados ou generalizados |
| RF07 | Acesso sem login é negado | Abrir o painel e o chat sem autenticar e confirmar redirecionamento ao login ou HTTP 401 |
| RF07 | Perfil sem permissão é barrado | Entrar como Suporte N1 e tentar usar função de Gestor de TI e confirmar a negação |
| RF07 | Senhas não legíveis | Inspecionar a tabela de usuários e confirmar que só existem hashes |
| RF07 | n8n inacessível pela rede hospitalar geral | Tentar abrir o n8n de um computador da rede geral e confirmar que a conexão é recusada |
| RF07 | n8n acessível pela VLAN de gerência ou VPN | Acessar o n8n pela VLAN ou VPN com as credenciais do Gestor de TI e confirmar o acesso |
| RF07 | n8n exige credenciais do Gestor de TI | Tentar entrar com credenciais de outros perfis e confirmar a negação |

---

## 7. Limitações Conhecidas

- **Destino do backup:** se a Fcecon não dispuser de disco ou local de rede fisicamente separado, o backup ficará no mesmo equipamento e não protege contra falha física total do servidor.
- **Dependência de IA gratuita:** as metas de 5 s e 15 s dependem das camadas gratuitas de Groq/OpenRouter. Com a IA indisponível, o alerta continua no painel, sem o diagnóstico.
- **Reidentificação interna:** como os logs brutos ficam no PostgreSQL, a Fcecon pode, em tese, relacionar a saída generalizada ao original por cruzamento de horários. A premissa de conformidade se apoia em o **provedor de IA** não ter meios razoáveis de reidentificar. A validação depende do DPO ou do jurídico (art. 12 da LGPD).
- **Generalização baseada em regras:** o filtro reduz o risco, mas não o elimina. Por isso há falha segura (RF05) e validação contínua (RNF08).
- **Custo da generalização:** arredondar horários e mascarar sub-redes pode reduzir a precisão do diagnóstico. O RNF08 mede essa perda, mas a medição com mocks pode não representar toda a variedade dos logs reais.
- **Variação do LLM:** o mesmo log pode gerar diagnósticos diferentes em execuções distintas. Por isso a comparação do RNF08 usa repetições.
- **Diagnóstico genérico:** sem tabela de/para, a IA não cita o equipamento exato. O técnico faz essa correlação pelo alerta original.
- **Mocks com poucos blocos de IP:** só existem três blocos /24 de documentação em IPv4. Para testar várias sub-redes, os blocos são subdivididos em sub-redes menores.
- **Servidor on-premise e rede de gerência:** o servidor e a VLAN ou VPN de gerência ainda precisam ser confirmados pela instituição.

---

## Anexo A: Evidências de Validação (RNF08 e RNF09)

*Todos os dados deste anexo são **fictícios**. Os mocks imitam o formato real, mas os valores são inventados. Não pode constar nenhum log real, faixa de IP real, nome de host real, VLAN, setor ou modelo de equipamento da Fcecon.*

**Blocos permitidos para IP:** `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (IPv4, RFC 5737) e `2001:db8::/32` (IPv6, RFC 3849).

### A.1 Etapa 1: bloqueio de vazamentos

| ID do caso | Tipo | Entrada (fictícia) | Saída enviada à IA | Dado sensível na saída? | Resultado |
|---|---|---|---|---|---|
| C01 | Óbvio (nome) | *(a preencher)* | *(a preencher)* | *(Sim/Não)* | *(Aprovado/Reprovado)* |
| C02 | Óbvio (IP) | *(a preencher)* | *(a preencher)* | *(Sim/Não)* | *(Aprovado/Reprovado)* |
| C03 | Óbvio (identificador médico) | *(a preencher)* | *(a preencher)* | *(Sim/Não)* | *(Aprovado/Reprovado)* |
| C04 | Chat (texto livre com nome e IP) | *(a preencher)* | *(a preencher)* | *(Sim/Não)* | *(Aprovado/Reprovado)* |
| C05 | Contextual (horário + setor + equipamento único) | *(a preencher)* | *(a preencher)* | *(Sim/Não)* | *(Aprovado/Reprovado)* |
| C06 | Formato imprevisto | *(a preencher)* | *(a preencher)* | *(Sim/Não)* | *(Aprovado/Reprovado)* |

### A.2 Etapa 2: custo da generalização

| ID do caso | Variável testada | Diagnóstico com mock original | Diagnóstico com mock generalizado | Equivalentes? (por repetição) | Observação |
|---|---|---|---|---|---|
| U01 | Horário exato × arredondado | *(a preencher)* | *(a preencher)* | *(x de N)* | *(a preencher)* |
| U02 | IP completo × sub-rede | *(a preencher)* | *(a preencher)* | *(x de N)* | *(a preencher)* |
| U03 | Equipamento exato × categoria | *(a preencher)* | *(a preencher)* | *(x de N)* | *(a preencher)* |
| U04 | Correlação de eventos em sequência | *(a preencher)* | *(a preencher)* | *(x de N)* | *(a preencher)* |

**Parâmetros fixos:** modelo, versão, temperatura e número de repetições por caso.
**Registro de execução:** data, versão das regras de filtro e responsável por cada rodada.

---

## Anexo B: Stack Tecnológica

| Camada | Tecnologia | Onde roda |
|---|---|---|
| Frontend | Vue.js ou React (definido pela familiaridade da equipe), com login e perfis | Contêiner |
| Backend/API | Python (FastAPI recomendado; Django REST como alternativa), com autenticação por chave, login de usuários e módulo de generalização | Contêiner |
| Comunicação em tempo real | SSE (alertas e métricas) + WebSocket (chat com IA) | Contêiner (API) |
| Banco de dados | PostgreSQL, com volume persistente, tabela de usuários e backup diário | Contêiner |
| Automação e relatórios | n8n, com volume persistente, acessível só por VLAN de gerência ou VPN | Contêiner |
| Análise de pacotes | Analisador customizado (padrão) + Wireshark (apoio opcional) | Host |
| Firewall | pfSense | Rede (fora do servidor) |
| IA (LLM) | Groq / OpenRouter | Nuvem |
| Implantação | Docker e Docker Compose | Servidor on-premise |