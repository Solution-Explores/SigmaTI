# Documento de visão do SIGMA

> **Rascunho de 24/10/2026.** Consolida o que já está escrito no [estudo de caso](arquitetura/estudo-de-caso.md), no [README](../README.md), no [PRODUCT.md](../PRODUCT.md) e na [visão de engenharia](../engenharia/docs/00-visao-de-engenharia.md). Não há modelo de referência: a estrutura segue o formato clássico de um documento de visão, adaptada a um TCC. Itens marcados **[a confirmar]** não têm fonte no repositório e precisam de validação da equipe ou da instituição.

## 1. Propósito

Este documento diz **o que o SIGMA é, para quem existe e que valor deve entregar**, em linguagem de produto. O detalhe dos requisitos (RF, RNF, RN) fica no estudo de caso, e o detalhe técnico fica nos documentos de arquitetura e engenharia. Aqui entram a visão, os limites e os critérios para dizer que o projeto deu certo.

## 2. Contexto e problema

A equipe de TI da Fcecon, um hospital oncológico de fundação pública, trabalha sem visibilidade em tempo real da rede. As falhas só chegam ao conhecimento da equipe quando os usuários reclamam. Prontuários eletrônicos, comunicação e equipamentos médicos dependem dessa rede, então uma queda deixa de ser só um problema técnico e vira risco para a continuidade do atendimento.

| Dor | Efeito |
|---|---|
| Suporte reativo, sem monitoramento contínuo | Incidentes detectados e reparados tarde (MTTD e MTTR altos) |
| Equipe pequena e sobrecarregada com tarefas manuais | Pouco tempo para manutenção preventiva |
| Sem histórico estruturado | Impossível analisar tendências e prevenir falhas |
| Orçamento restrito e dificuldade de contratar especialistas | Soluções comerciais e consultorias fora de alcance |
| Dados de um hospital sob a LGPD | Enviar logs brutos a uma IA na nuvem não é aceitável |

## 3. Declaração de posição

| | |
|---|---|
| **Para** | a equipe de TI de um hospital oncológico público, com pouco pessoal e sem verba para licenças |
| **Que** | descobre falhas de rede só depois que o atendimento foi afetado |
| **O SIGMA é** | um sistema de monitoramento ativo de rede com apoio de IA |
| **Que** | detecta anomalias, mostra o alerta em segundos, sugere um diagnóstico e guarda o histórico |
| **Diferente de** | ferramentas comerciais de observabilidade, que custam licença, e de enviar logs diretamente a um chatbot |
| **Nosso produto** | usa só componentes abertos ou gratuitos e generaliza os dados antes de qualquer envio à nuvem, com falha segura |

## 4. Visão

> Trocar o suporte reativo por um monitoramento contínuo, em que a equipe de TI vê a falha antes do usuário, recebe uma sugestão de diagnóstico sem expor dados do hospital e deixa um registro auditável de cada incidente e de cada decisão.

O SIGMA é um **MVP de TCC**. A visão descreve o produto que o projeto quer demonstrar, não uma operação hospitalar homologada.

## 5. Partes interessadas e usuários

### 5.1 Usuários do painel

| Perfil | Papel | O que precisa |
|---|---|---|
| Suporte N1 (`suporte_n1`) | Primeiro atendimento | Ver o estado dos serviços e pedir um diagnóstico |
| Analista de Redes (`analista_redes`) | Investigação e resposta | Incidentes, histórico, detalhes de pacotes e aprovações |
| Gestor de TI (`gestor_ti`) | Gestão e governança | Relatórios, auditoria, usuários, chaves e acesso ao n8n |

### 5.2 Outras partes interessadas

| Parte | Interesse |
|---|---|
| Coordenação do hospital | Receber relatórios gerenciais periódicos |
| DPO ou setor jurídico da Fcecon | Homologar a premissa de conformidade com o art. 12 da LGPD **[pendente]** |
| Orientador (Euler Azevedo) | Acompanhar a entrega, avaliar o aceite das issues e a demonstração de 27/10/2026 |
| Banca do TCC | Avaliar se o sistema funciona e se o resultado é reproduzível (prevista para 18/11/2026, podendo ser antecipada) |
| Equipe de desenvolvimento (Iohand Jheremy, Joyce Yasmin, Vinícius Gomes) | Entregar, documentar e revisar |

## 6. Visão geral do produto

### 6.1 Perspectiva

O SIGMA fica entre a rede monitorada e a equipe de TI.

```
pfSense ───────────┐  (chave + HTTPS)
                   ├──► API ──► PostgreSQL ──► Backup diário
Sonda de pacotes ──┘     │            └──► n8n (VLAN de gerência / VPN) ──► Relatórios
                         ├──► Generalização ──► IA na nuvem ──► sugestão genérica
                         │ SSE
                         ▼
Técnicos (login + perfil) ──► Painel (alerta original + diagnóstico)
```

Os diagramas completos estão no [README](../README.md) e na [stack de tecnologia](arquitetura/stack-de-tecnologia.md).

### 6.2 Capacidades

| # | Capacidade | Valor para o usuário | Requisito |
|---|---|---|---|
| 1 | Alertas em tempo real no painel, em até 5 s após a detecção | Saber da falha antes do chamado | RF01 |
| 2 | Captura de alertas do pfSense e de uma sonda própria de pacotes | Deixar de depender de relatos informais | RF02 |
| 3 | Diagnóstico assistido por IA, em até 15 s | Apoio à triagem sem especialista disponível | RF03, RNF04 |
| 4 | Generalização dos dados antes da nuvem, com bloqueio se o filtro falhar | Usar IA sem expor dados do hospital | RF05, RNF08 |
| 5 | Histórico estruturado de incidentes | Analisar tendências e prevenir falhas | RF04 |
| 6 | Relatórios automáticos (MTTR e outras métricas) | Menos trabalho manual e informação para a gestão | RF06 |
| 7 | Controle de acesso por perfil e n8n restrito à gerência | Cada pessoa vê só o que precisa | RF07 |
| 8 | Autenticação por chave exclusiva em cada origem, com revogação e rotação | Impedir alertas falsos | RNF07 |
| 9 | Painel operacional: saúde dos serviços, incidentes, aprovações e auditoria | Acompanhar e decidir no mesmo lugar | [PRODUCT.md](../PRODUCT.md) |
| 10 | Trilha de auditoria com cadeia de hash e runbooks com aprovação humana | Rastrear ações e detectar adulteração | [Visão de engenharia](../engenharia/docs/00-visao-de-engenharia.md) |

### 6.3 Princípios do produto

- **Custo zero de licença.** Só tecnologia aberta ou gratuita (RNF01).
- **Privacidade primeiro.** Generalização, sem tabela de correspondência (de/para), com falha segura (RF05).
- **Verdade dos dados.** Sem medição recente, o estado é "desconhecido", não "disponível". O painel nunca mostra dados fictícios no lugar de uma API indisponível.
- **Humano no controle.** A IA sugere de forma genérica, e o técnico liga a sugestão ao equipamento exato. Aprovações exigem justificativa e outro operador, e o painel não executa comandos.
- **Medir, não afirmar.** Cada meta tem métrica, instrumento e teste (seção 9).

## 7. Escopo

### 7.1 Dentro do escopo do MVP

- Painel web com login e perfis, alertas por SSE, diagnóstico com IA e áreas operacionais.
- API em Python (FastAPI) com autenticação, generalização e integração com a IA.
- Histórico em PostgreSQL, com volume persistente e backup restaurável.
- Núcleo de engenharia `sigma_eng`: detectores estatísticos, SLO e orçamento de erros, MTTD, MTTA e MTTR, auditoria com hash e runbooks.
- Validação com dados sintéticos e experimentos reproduzíveis.

### 7.2 Fora do escopo ou planejado

| Item | Situação |
|---|---|
| Operação hospitalar homologada | Fora. Nenhuma instalação real foi identificada ou homologada |
| Integração operacional com o pfSense e instalação da sonda | Planejadas, sem procedimento de instalação |
| Chat interativo por WebSocket | Previsto, ainda não existe no código |
| Conteinerização da API e do frontend | Planejada. Hoje rodam no host |
| Âncora externa da auditoria e rotação da chave HMAC (#13) | Depois da demonstração. Pode virar trabalho futuro |
| Restauração em segunda máquina física (#25) | Pendente |
| Detecção de deriva lenta (CUSUM, Page-Hinkley) | Trabalho futuro, motivado pelo resultado negativo do experimento E1 |
| Expansão de funcionalidades (#10, #16 a #19, #21, #22, #23, #30) | Não entra antes da banca. Vira capítulo de trabalho futuro |

## 8. Restrições

| Tipo | Restrição |
|---|---|
| Orçamento | Sem verba. Camadas gratuitas de IA e software aberto |
| Legal | LGPD. Premissa: o provedor de IA não tem meios razoáveis de reidentificar os dados. Depende de homologação do DPO ou do jurídico |
| Segurança institucional | Evidências só com dados fictícios nos blocos RFC 5737 e RFC 3849. Nenhuma faixa, host, VLAN, setor ou modelo real (RNF09) |
| Técnica | A sonda roda no host, porque precisa da interface física de rede (RNF05). O n8n só é acessível pela VLAN de gerência ou VPN |
| Dependência externa | As metas de 5 s e 15 s dependem das camadas gratuitas de IA. Com a IA fora do ar, o alerta continua no painel, sem diagnóstico |
| Infraestrutura | Servidor on-premise e VLAN ou VPN de gerência ainda precisam ser confirmados pela instituição |
| Equipe e prazo | Duas pessoas ativas no desenvolvimento. Demonstração em 27/10/2026, congelamento de código previsto para 11/11 e banca em 18/11/2026 |

## 9. Critérios de sucesso

O projeto é bem-sucedido se a banca puder comprovar o que segue. A lista completa de testes está na seção 6 do estudo de caso.

| Resultado esperado | Meta | Requisito |
|---|---|---|
| Alerta visível rapidamente | Até 5 s após a detecção | RF01 |
| Diagnóstico da IA rápido | Até 15 s após a falha | RNF04 |
| Nenhum dado sensível na nuvem | Zero vazamentos na bateria de testes | RNF08 |
| Custo da privacidade conhecido | Perda de precisão medida com dados fictícios. Meta de equivalência **[a definir]** | RNF08 |
| Dados protegidos contra perda | Backup restaurável e sem perda ao recriar contêineres | RNF06 |
| Origens confiáveis | Requisição sem chave, inválida ou revogada é recusada (401 ou 403) | RNF07 |
| Acesso controlado | Sem login ou sem perfil adequado, o acesso é negado | RF07 |
| Resultado reproduzível | Experimentos com semente fixa e saída em CSV | Visão de engenharia |

**Pergunta de pesquisa.** Em uma rede hospitalar com equipe de TI reduzida, é possível reduzir o MTTD e dar rastreabilidade às ações de resposta usando só componentes sem custo de licença, preservando a LGPD? As hipóteses H1 a H4 estão na [visão de engenharia](../engenharia/docs/00-visao-de-engenharia.md).

## 10. Estado atual (24/10/2026)

O SIGMA está em **MVP**. Esta seção resume o estado e envelhece rápido, então confira o [README](../README.md) e o [plano de demonstração](plano-demonstracao-2026-10-27.md) antes de citá-la.

- Existem a API com JWT e RBAC, a generalização com falha segura, o painel operacional, o estado operacional no PostgreSQL, o SSE, o backup com restauração local e o núcleo `sigma_eng`.
- O aceite das issues #5, #6 e #8 e a restauração em outra máquina (#25) continuam pendentes.
- Sonda, integração com o pfSense e implantação hospitalar são itens planejados, não entregues.
- Dados e alvos sintéticos não homologam uma rede hospitalar real.

## 11. Riscos principais

| Risco | Efeito | Resposta |
|---|---|---|
| Generalização por regras deixa passar um dado | Vazamento para a nuvem | Falha segura e testes repetidos a cada mudança nas regras (RNF08) |
| Generalização reduz a utilidade do diagnóstico | IA menos útil | Medir a perda na etapa 2 do RNF08 e registrar como limitação |
| IA gratuita lenta ou indisponível | Metas de 5 s e 15 s não cumpridas | O alerta segue no painel sem diagnóstico. Registrar a limitação |
| Premissa da LGPD não homologada | Conformidade sem aval formal | Levar ao DPO ou ao jurídico e declarar a pendência no TCC |
| Backup no mesmo servidor | Não protege contra falha física total | Registrar a limitação até haver destino separado |
| Backlog maior que o tempo até a banca | Entregas incompletas | Cortar para trabalho futuro e priorizar a `v1.0.0` |
| Zabbix 6.4 sem suporte | Componente opcional desatualizado | Tarefa de migração própria, fora do núcleo |

## 12. Perguntas em aberto

1. **[a confirmar]** Quem assina o aceite da visão? O orientador, a coordenação do hospital ou os dois?
2. **[a confirmar]** O DPO ou o jurídico da Fcecon já foi acionado sobre o art. 12 da LGPD?
3. **[a confirmar]** Qual a meta de equivalência entre o diagnóstico original e o generalizado?
4. **[a confirmar]** Há servidor on-premise, VLAN ou VPN de gerência e destino de backup separado na Fcecon?
5. **[a confirmar]** O que o orientador espera do documento de visão: formato, nível de detalhe e momento de entrega?
6. **[a confirmar]** O texto de posicionamento (seção 3) representa como a equipe quer apresentar o SIGMA à banca?

## 13. Referências

- [Estudo de caso](arquitetura/estudo-de-caso.md): problemática, solução, RF, RNF, RN e métricas de validação.
- [Stack de tecnologia](arquitetura/stack-de-tecnologia.md): tecnologias, privacidade e fluxo de dados.
- [README](../README.md): funcionalidades, arquitetura e estado do desenvolvimento.
- [PRODUCT.md](../PRODUCT.md): painel operacional e verdade dos dados.
- [Visão de engenharia](../engenharia/docs/00-visao-de-engenharia.md): problema de pesquisa, hipóteses e contribuições.
- [Plano de demonstração](plano-demonstracao-2026-10-27.md) e [plano de sprints pós-demo](plano-sprints-pos-demo.md): prazos e escopo até a banca.
