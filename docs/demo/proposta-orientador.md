# SigmaTI: situação e proposta de cronograma

**Para:** professor orientador · **Data:** 27/10/2026 · **Equipe:** Vinícius Lima, Iohan, Joyce

## 1. Entregue até a demonstração
| Issue | Escopo | Evidência |
|---|---|---|
| #2, #3 | docker-compose: conflitos resolvidos, sem credenciais fixas, portas restritas e versões fixadas | Issues encerradas |
| #4 | API: chave por variável de ambiente, CORS restrito e chamada à IA com timeout | Issue encerrada |
| #7 | Persistência em PostgreSQL: alvos, medições, incidentes e aprovações | Issue encerrada |
| #9 | `sigma_eng` empacotado (`pyproject.toml`) | Issue encerrada |
| #14 | Sonda conecta ao IP já validado (mitiga DNS rebinding) | Issue encerrada |
| #15 | Painel: Saúde, Incidentes, Aprovações e Auditoria | PR #39 integrado |
| #6 | Autenticação JWT e RBAC, com auditoria compartilhada | PR #43 integrado; aceite de 23/10 na VM feito (abaixo), repetição no SHA congelado de 26/10; issue aberta até todos os critérios serem atendidos |
| #8 | Sondagem contínua com alertas por SSE e carga de 200 alvos | PR #44 integrado; aceite de 23/10 na VM feito (abaixo), repetição no SHA congelado de 26/10; issue aberta até todos os critérios serem atendidos |

**Evidência em VM (21/10, Ubuntu 24.04, 4 vCPU, 4 GiB, PostgreSQL 15):**

| Versão | Testes | Carga de 200 alvos (intervalo de 2 s, 32 trabalhos) |
|---|---|---|
| `develop` antes das correções | 464/467 | 0 de 5 |
| `develop` + #43 + #44 | **488/488** | **5 de 5**, mais o E2 e o validador explícito |

Com as correções: tempo entre a queda e o alerta no painel (SSE) com p50 de 0,20 a 0,27 s e p95 de 0,33 a 0,41 s; atraso máximo do calendário de 0,185 s, abaixo do limite de 0,5 s; 0 erros e 0 ciclos perdidos.

**Aceite na VM, na `develop` integrada (`75b1874`, com #43 e #44), em 22/10 à noite e 23/10:** em 22/10, API 20 de 20, painel 4 de 4 e pytest com 491 aprovados e 1 falha de ambiente (dependência do navegador ausente); em 23/10, o teste que falhou passou isolado (a suíte completa não foi repetida) e cinco cargas de 200 alvos deram p95 entre a queda e o alerta de 0,395 a 0,496 s, com 0 erros e 0 timeouts. Em 20 execuções isoladas do teste do provedor de IA, feitas em 23/10, houve uma falha por 25 ms acima do limite de 15 s (issue #45). Na carga equivalente no Windows, em 22/10, o p95 foi 0,806 s; hardware e método diferem, então os números não se comparam.

**Aceite no SHA congelado de 26/10 (`7851da6`, com #43, #44 e #47), no Windows do desenvolvedor, com PostgreSQL em contêiner:** pytest completo com 491 aprovados e 1 pulado, sem falhas; aceite da API 20 de 20; painel 4 de 4; coleta com 30 quedas, mediana de 0,73 s, p95 de 0,85 s e máximo de 1,07 s, todas em até 5 s, com 200 alvos lógicos, intervalo de 2 s e 0 erros. O CI do GitHub passou nesse SHA. O ensaio manual do painel, no mesmo SHA, percorreu perfis, coleta ao vivo, SLO, aprovação por dois analistas, auditoria íntegra e anonimização (MTTD 0,26 s, MTTA 15,06 s, MTTR 29,03 s). Na VM (Ubuntu, 4 vCPU, 4 GiB), a bateria completa nesse SHA deu: API 20 de 20, painel 4 de 4, infraestrutura aprovada, cinco cargas de 200 alvos com p95 entre a queda e o alerta de 0,31 a 0,40 s e 0 erros, e a segunda execução do pytest completo com 492 de 492. **Duas verificações de tempo falharam e não têm causa isolada:** na primeira execução do pytest completo, o teste de carga excedeu o limite de atraso do calendário (0,96 s contra 0,5 s; 491 de 492), e uma de dez execuções isoladas do teste do provedor de IA terminou em 15,5 s contra o limite de 15 s. Ambas já eram sensíveis a tempo antes do PR #47 (o código do coletor não mudou desde a rodada anterior) e passam a ser acompanhadas na issue #45.

O PR #47 (estabilização do teste da sonda) foi revisado pelo Iohan e integrado em 26/10. Os demais testes sensíveis a tempo (provedor de IA, DNS e agendador) seguem na issue #45.

## 2. Próximas etapas (sprints semanais, de quarta a terça)
A banca está marcada para 18/11/2026 e pode ser antecipada. Por isso o que era "tudo até 03/11" foi dividido em três sprints, com o código congelado em 11/11.

**Sprint 1, 28/10 a 03/11 (4 dias úteis, porque 02/11 é Finados):**
- **#5:** anonimização LGPD revisada contra os critérios completos, com novos casos adversariais.
- **#6 e #8:** aceite final com todos os critérios.
- **Reorganização do repositório** (documentação e estrutura do código, em PRs separados).
- **Release `v1.0.0`** na `main`, com aceite no fim de semana de 31/10 e 01/11. Reserva para o seu retorno sobre esta demonstração.

**Sprint 2, 04/11 a 10/11 (mudança proposta, depende da sua concordância):**
- **#13:** âncora externa da trilha de auditoria, rotação da chave HMAC e verificação agendada.
- **#25:** scripts de implantação, backup e smoke E2E. Falta a restauração em outra máquina física; na mesma máquina, em VM, já foi aprovada com 17 verificações.
- **#45 e #47:** testes sensíveis a tempo e CI. **#46:** custo da verificação da trilha de auditoria.

**Sprint 3, 11/11 a 17/11:** código congelado em 11/11, texto do TCC, slides e ensaio. Banca em 18/11.

#13 e #25 saem do prazo de 03/11 para 10/11 porque não cabem junto com a `v1.0.0` sem estourar a capacidade.

## 3. Trabalho futuro ou nova sprint
- **Expansão:** #10, #16 a #19, #21, #22 e #30.
- **Validações externas:** #11, #12, #20, #24 e #26 a #29. Elas dependem de hospital parceiro, de hardware ou de coleta prolongada.

## 4. Limites declarados
- O provedor de IA é simulado.
- Os testes usam loopback e dados fictícios.
- Os números de carga foram medidos em laboratório e não equivalem a homologação hospitalar.
- A anonimização vale para o corpus avaliado (E6), não para dados reais.
- O painel ainda não exibe MTTD nem burn rate; os dois são calculados pela API.
- O custo de verificação da trilha de auditoria cresce com o tamanho do arquivo: medido em VM, a verificação HMAC leva cerca de 3,0 s com 100 mil registros. A issue #46 acompanha o tema; a medição está em `validacao-vm/rodada-2026-10-22d`.

## 5. Decisões pedidas ao orientador
1. Podemos manter #5, o aceite de #6 e #8, a reorganização e a `v1.0.0` em 03/11 e mover #13 e #25 para 10/11?
2. Os itens da seção 3 podem ficar registrados como trabalho futuro no texto do TCC?
3. Para o resultado do #25, a restauração em VM na mesma máquina basta, ou a máquina física diferente é obrigatória?
4. A banca de 18/11 está confirmada, e há risco de antecipação? Que licença o repositório deve ter?
