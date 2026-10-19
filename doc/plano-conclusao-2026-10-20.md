# Concluir a demonstração do SigmaTI e organizar o fechamento do projeto

Plano definido com o usuário em 19/10/2026. Registro de planejamento, não evidência
de implementação das funcionalidades futuras. Esta publicação não altera o código
executável nem autoriza novos merges em branches compartilhadas.

Atualização do fluxo: `dev` foi renomeada para `develop` e a branch deste
plano para `feature/pacote`. Referências anteriores descrevem o estado histórico.
A renomeação encerrou automaticamente o PR #33; o [PR #34](https://github.com/Solution-Explores/SigmaTI/pull/34) preserva o escopo.
Consulte [Git Flow](gitflow.md) para o fluxo vigente.

## 1. Objetivo e estado de partida

Entrega em **20/10/2026, às 18h, America/Manaus (22h UTC)**, priorizando o máximo
de funcionalidades verificadas no ambiente local. O prazo não equivale à conclusão
de todas as issues: coleta de 14 dias, hardware e validações externas têm fases próprias.

- PR #32 integrado à dev em `086129c9b8dd119d72877f493e1828ef2a46c949`, com aceite
  e CI aprovados. A dispensa de revisão independente autorizada pelo usuário foi
  específica dessa entrega; não se atribui revisão a outro integrante.
- PR #33 implementa #9: head `b7958c9d1b3fcb06f775a95f6b52ed7901988616`, três
  checks aprovados, 375 testes Python locais aprovados; aguarda revisão e integração.
- A main ainda não recebeu essa integração. PostgreSQL operacional, sondagem contínua
  e páginas de gestão permanecem como trabalho futuro.
- Recursos confirmados: esta máquina Windows com Docker, dados fictícios e IA
  simulada. Sem dependência confirmada de outras pessoas, hardware ou rede hospitalar.
- Preservar Python 3.12, React e o núcleo sigma_eng independente de banco/framework.

Prioridade: **cadastrar alvo → detectar falha → persistir incidente → atualizar
painel → reconhecer e resolver**. O planejamento prioriza esse fluxo completo.

## 2. Execução até a demonstração

Cada bloco termina com implementação, revisão técnica, testes e evidências.
Não iniciar um bloco dependente enquanto sua base estiver reprovada.

| Ordem | Entrega | Critério de conclusão |
|---|---|---|
| 1 | Base: #9 e K13/K14 | Revisar PR #33, obter aprovação, integrar à dev e conferir CI do commit resultante. |
| 2 | Persistência/acesso: #6/#7 | Argon2id, sessões revogáveis no PostgreSQL, migrações, alvos/incidentes e recuperação após reinício. |
| 3 | Sondagem segura: #14 e parte de #13 | Resolver uma vez, conectar ao IP validado, manter Host/SNI e centralizar auditoria concorrente. |
| 4 | Monitoramento: #8 | Scheduler limitado, medições persistidas, incidente sem duplicação e SSE autenticado. |
| 5 | Painel: #15 | Saúde, Incidentes, Aprovações e Auditoria com dados do banco e controles por perfil. |
| 6 | Recuperação local: parte de #25 | Inicialização documentada; backup restaurado em banco descartável novo com comparação de registros/auditoria. |
| 7 | Expansão funcional | Avançar na fila abaixo somente enquanto os blocos anteriores permanecerem aprovados. |

Fila de expansão, em ordem fixa:

1. #21/#22: cinco runbooks de laboratório, execução auditada, aprovação por outra
   identidade e reteste de resolução.
2. #18/#17: provedores simulados com fallback e postmortem baseado em eventos persistidos.
3. #16: fluxo n8n versionado, relatório local e histórico; envio externo desabilitado na demonstração.
4. #10/#30: CUSUM/Page-Hinkley e propriedades de aprovação/auditoria no CI.
5. #19/#20/#24: inventário defensivo com diff de snapshots, checklist de prontidão
   e matriz documental de evidências.

### Cortes de escopo — 20/10, horário de Manaus

- **10h:** se persistência, monitoramento ou painel estiverem reprovados, suspender
  a fila de expansão e concentrar trabalho nesses blocos.
- **14h:** congelar funcionalidades; depois disso, somente correções, testes e documentação.
- **14h–17h:** validação final e reprodução da demonstração.
- **17h–18h:** preparar entrega, roteiro, evidências e status das issues.

Funcionalidade incompleta fica em branch/PR próprio, fora da versão demonstrada.
Preservar uma referência Git da última versão aprovada. Os horários são limites
de priorização, não garantia de concluir todos os blocos.

## 3. Decisões técnicas e interfaces

### Persistência e autenticação

- PostgreSQL existente, SQLAlchemy 2.x, Psycopg 3 e Alembic; versões instaladas fixadas.
  Adaptadores de persistência fora do núcleo puro e interfaces Protocol para usuários,
  sessões, alvos, medições, incidentes, aprovações, execuções e SLOs.
- Timestamps UTC, índices nas relações e em `(alvo_id, ts)`, particionamento mensal
  de medições e unicidade de incidente ativo por alvo/tipo.
- Recuperar aprovações, execuções waiting_approval e aquecimento dos detectores.
  Banco indisponível impede operações dependentes, sem fallback silencioso para memória.
- Bootstrap de usuários por comando administrativo com senha informada localmente.
  Importar hashes antigos somente por comando explícito; atualizar PBKDF2 para Argon2id
  após autenticação válida.
- No modo PostgreSQL, sessões válidas sobrevivem ao reinício até expirar/revogar.
  Desativação, troca de senha ou perfil invalidam as sessões correspondentes.

### Fluxo e APIs

- Preservar campos existentes de login/logout e `/api/alertas`; documentar adições.
  Adicionar operações em `/api/eng` para alvos, incidentes, aprovações e execuções.
- Persistir incidente antes do diagnóstico. Falha da IA não impede registro/exibição.
- `GET /api/eng/eventos`: SSE com identificadores e recuperação por Last-Event-ID.
  O painel usa fetch com Bearer no cabeçalho; sem tokens na URL. Expiração/revogação
  encerra a conexão.
- N1 consulta monitoramento e mantém envio manual; analista opera alvos, incidentes
  e runbooks; gestor administra usuários, chaves e auditoria. Solicitante e decisor
  de aprovação continuam sendo identidades diferentes.

### Execução e segurança

- API e banco na rede interna Docker; somente API publicada em loopback.
  Frontend pelo procedimento npm documentado. Alvos de teste explicitamente autorizados.
- Scheduler de laboratório: intervalo 2 s, jitter ±10%, até 64 sondas simultâneas,
  timeout 500 ms. Medir o comportamento; não extrapolar a configuração ao hospital.
- Auditoria transacional com as alterações e exportação JSONL verificável. Falhas
  de privacidade não registram senhas, tokens ou texto bruto.
- Prazo global de diagnóstico permanece 14 s, inclusive no fallback de provedores.
- Revisar #5 contra os critérios completos, ampliar casos adversariais e manter
  os resultados de anonimização restritos ao corpus avaliado.

## 4. Aceite e publicação

- Ambiente novo, migrações, inicialização e recuperação documentados.
- Login, 401/403, expiração/revogação e persistência após reinício.
- Alvo com falha → incidente persistido → painel → reconhecimento → resolução.
- Sem duplicação de incidente após reinício/reconexão SSE; recuperação de aprovações
  e execuções interrompidas.
- DNS alternando para IP não autorizado recusado; sanitização falha sem chamada externa.
- Teste com 200 alvos locais, atraso do scheduler e latência até o painel registrados.
  Declarar a meta de 5 s somente se medida.
- Backup restaurado em banco novo, com conferência de registros e auditoria.
- Regressão Python, PostgreSQL real, navegador, build/lint, instalação do pacote e CI aprovados.
- Cada módulo adicional precisa de seu cenário completo antes de entrar no roteiro.

Entregar SHA, reprodução, resultados e matriz issue → implementação → teste → pendência.
Main somente após aprovação do conjunto validado na dev. Fechar issues individualmente,
conforme seus requisitos; não transformar testes locais em homologação hospitalar.

## 5. Conclusão do backlog completo

| Frente | Issues | Condição de encerramento |
|---|---|---|
| Sprint | #2–#5/#9 e K07–K15 | Conferência individual, integração aprovada e evidências atualizadas. |
| Fundação | #6/#7 | Persistência integral, migrações, retenção/agregação e recuperação testadas. |
| Operação e funcionalidades | #8/#15–#22 | Concluir blocos que não passarem antes do congelamento. |
| Segurança/recuperação | #13/#14/#23/#25 | Chaves revogáveis, segredos protegidos, rotação verificável, âncora externa e restauração em outra máquina. |
| Experimentos locais | #10/#11/#28/#30 | Scripts reproduzíveis, resultados e limites; separar IA simulada de medições com provedor real. |
| Coleta/relógios | #12/#27 | Acesso autorizado, pelo menos 14 dias de coleta e medições entre máquinas com incerteza documentada. |
| Hardware/telemetria | #26/#29 | Primeiro protótipo Raspberry Pi, SNMPv3 de três métricas e comparação com latência; ensaio físico necessário. |
| Prontidão/conformidade | #20/#24 | Controles ligados a evidências e pendências institucionais/revisão externa registradas quando disponíveis. |

#31 só encerra com aceite das vinculadas ou redução de escopo aprovada e documentada.
Hospital, segunda máquina e hardware permanecem dependências externas; simuladores
preparam o software, mas não substituem esses ensaios.

## Referências

- [PR #32](https://github.com/Solution-Explores/SigmaTI/pull/32)
- [PR #33](https://github.com/Solution-Explores/SigmaTI/pull/33)
- [Integração na dev](../specs/011-recuperacao-sprint/integracao-dev.md)
- [Evidências do pacote](../specs/012-pacote-sigma-eng/evidencias.md)
- [Quadro SigmaTI](https://trello.com/b/vswV1j1T/sigmati)
