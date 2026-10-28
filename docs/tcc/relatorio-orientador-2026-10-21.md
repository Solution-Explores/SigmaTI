# SigmaTI — situação para o orientador · 21/10/2026

[Certo] Entregues e encerradas no GitHub: **#2** (conflitos Compose), **#3** (credenciais/portas/versões), **#4** (configuração, CORS e timeout), **#7** (persistência), **#9** (pacote), **#14** (sondagem segura) e **#15** (painel). **#6/PR #43** e **#8/PR #44**: **validados em VM; aceite final em 23/10**, após revisão independente e integração. CI verde nos SHAs atuais. **#25**: 17 verificações de restauração em VM no mesmo host; outra máquina física pendente. **#5/#13**: critérios completos de anonimização e âncora/rotação da auditoria pendentes.

| Evidência de laboratório | develop `8cb1e23` | Candidato `ddd4840` |
|---|---:|---:|
| Regressão Python | 464/467 | **489/489** |
| Carga de 200 alvos | **0/5** | **5/5** |
| Atraso máximo / erros | aquecimento reprovado | **0,093396 s / 0** |

Fontes locais: `rodada-2026-10-22`, `rodada-2026-10-22b` e `rodada-2026-10-22c`. p95 queda→SSE ≤0,410 s nas quedas sintéticas anteriores à janela de carga. Os três testes instáveis já falhavam antes dos PRs; sonda corrigida em branch separado (30/30), sem PR. O timer da IA atrasou até 1,263 s antes do cancelamento; a causa específica do agendamento permanece inconclusiva.

**Demo: sábado, 24/10, às 9h (UTC−4); SHA congelado sexta, 23/10, às 18h.** Sete passos:
1. Arquitetura: alvo → sonda → PostgreSQL → detector → SSE → painel.
2. Perfis de acesso e recusa 403, com comando de apoio.
3. Queda TCP fictícia, incidente ao vivo, reconhecimento/resolução e métricas pela API.
4. SLO, orçamento de erros e burn rate pela API.
5. Aprovação e verificação da cadeia de auditoria.
6. Anonimização de identificadores fictícios antes da IA simulada.
7. Resultados dos testes, carga e limites do laboratório.

**Limites e riscos:** IA simulada, loopback e dados fictícios; VM no mesmo host, sem homologação externa ou operação prolongada. O prazo interno da IA é 14 s para uma meta de 15 s: a margem de 1 s pode ser excedida. Anonimização válida para o corpus avaliado. Integração, ensaios, contingência e aceite de sexta ainda pendentes. Estimativas do diário: demo **≈43%**, escopo do TCC **≈65%**.

**Decisões solicitadas:** confirmar **03/11** para #5, #13, #25 e release; autorizar expansão e validações externas como trabalho futuro; definir se #25 exige outra máquina física ou aceita VM no mesmo host; escolher a licença do repositório. #41/#42, de documentação, serão revisados após a demo.

**Mensagem sugerida**
Prezado professor,
Compartilhamos o estado do SigmaTI para a demonstração de sábado, 24/10, às 9h.
O candidato passou 489/489 testes e 5/5 cargas de 200 alvos em laboratório.
Revisão, integração e aceite final estão previstos até sexta, com congelamento às 18h.
Apresentaremos o fluxo completo com dados fictícios e IA simulada, declarando os limites.
Solicitamos sua orientação sobre o prazo de 03/11, trabalho futuro, validação da restauração e licença.
O resumo acima reúne as entregas, evidências e pendências.
Atenciosamente, equipe SigmaTI.

