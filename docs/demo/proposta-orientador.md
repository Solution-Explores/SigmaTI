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
| #6 | Autenticação JWT e RBAC, com auditoria compartilhada | PR #43; aprovado na VM, confirmação no aceite de 23/10 e no SHA congelado de 26/10 |
| #8 | Sondagem contínua com alertas por SSE e carga de 200 alvos | PR #44; aprovado na VM, confirmação no aceite de 23/10 e no SHA congelado de 26/10 |

**Evidência em VM (21/10, Ubuntu 24.04, 4 vCPU, 4 GiB, PostgreSQL 15):**

| Versão | Testes | Carga de 200 alvos (intervalo de 2 s, 32 trabalhos) |
|---|---|---|
| `develop` antes das correções | 464/467 | 0 de 5 |
| `develop` + #43 + #44 | **488/488** | **5 de 5**, mais o E2 e o validador explícito |

Com as correções: tempo entre a queda e o alerta no painel (SSE) com p50 de 0,20 a 0,27 s e p95 de 0,33 a 0,41 s; atraso máximo do calendário de 0,185 s, abaixo do limite de 0,5 s; 0 erros e 0 ciclos perdidos.

Aceite final, no SHA congelado de 26/10: [preencher].

## 2. Próxima etapa, até 03/11/2026
- **#13:** âncora externa da trilha de auditoria, rotação da chave HMAC e verificação agendada.
- **#5:** anonimização LGPD revisada contra os critérios completos, com novos casos adversariais.
- **#25:** scripts de implantação, backup e smoke E2E. Falta a restauração em outra máquina física; na mesma máquina, em VM, já foi aprovada com 17 verificações.
- **Release `v1.0.0`** na `main`, com aceite no fim de semana de 31/10 e 01/11.

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
1. O prazo de 03/11 para #13, #5 e #25 está aprovado?
2. Os itens da seção 3 podem ficar registrados como trabalho futuro no texto do TCC?
3. Para o resultado do #25, a restauração em VM na mesma máquina basta, ou a máquina física diferente é obrigatória?
