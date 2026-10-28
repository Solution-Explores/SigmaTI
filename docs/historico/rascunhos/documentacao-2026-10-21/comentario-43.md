### Evidência da VM — atualização de 21/10/2026
[Certo] Resultados locais, sem links inventados para os artefatos:

| Versão | Regressão Python | Carga adicional de 200 alvos |
|---|---:|---:|
| `develop@8cb1e23` — `rodada-2026-10-22` | 464/467 | 0/5 |
| #43 `8662ea9` — `rodada-2026-10-22b` | 476/478; auditoria focada 7/7 | não repetida; E2 da suíte falhou |
| Candidato `ddd4840` (#43 + #44) — `rodada-2026-10-22b` | **489/489** | **5/5**, mais validador explícito aprovado |

No candidato: p95 queda→SSE **≤0,410 s**, atraso máximo **0,093396 s**, **0 erros**, **0 timeouts** e nenhum aumento de `missed_*` na janela. p95 vem de 30 quedas sintéticas anteriores à janela de carga; ensaio curto, 200 alvos lógicos em loopback.

Três instabilidades anteriores aos PRs, separadas do aceite:
- Provedor: baseline **9/10** na `rodada-2026-10-22c`; candidato **7/10** isolado na rodada 2. Timer de 14 s atrasou até **1,263 s** antes do cancelamento; não se isolou selector, scheduler ou hipervisor. Zero avisos de callback lento não descarta bloqueio.
- Sonda: baseline **5/10**; candidato **26/30**, variante com `shutdown` **30/30** na rodada 3. Causa confirmada no teardown; branch remoto `fix/teste-sonda-instavel@3cca38d`, ainda sem PR.
- DNS: falhou na suíte da baseline na rodada 1 e no #43 na rodada 2; candidato **10/10** isolado. Causa temporal ainda inconclusiva.

**Validado em VM; aceite final em 23/10.** A revisão independente e a integração permanecem pendentes. As rodadas não são homologação externa.

Próximo passo: @iohanjheremy revisa até **22/10 às 8h (UTC−4)**; @Vinny1313 trata achados e integra em 22/10. Esta tabela não atribui a correção da carga ao #43 isolado.
