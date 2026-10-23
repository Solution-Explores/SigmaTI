## Situação em 21/10/2026
[Certo] #8 está **validado em VM; aceite final em 23/10**: PR #44 (`ddd4840`), aberto, CI verde e ainda com alvo `fix/base-issues`.
Evidências locais: `rodada-2026-10-22`, baseline `8cb1e23`: carga **0/5**; `rodada-2026-10-22b`, candidato: **5/5**, **489/489**, p95 queda→SSE **≤0,410 s**, atraso máximo **0,093396 s**, **0 erros** e **0 timeouts**. p95 mede as quedas sintéticas anteriores à janela da carga.
Próximo passo: @Vinny1313 altera o alvo após integrar #43 em **22/10**; @iohanjheremy revisa #44 na noite de 22/10; integração e aceite por @Vinny1313 em **23/10**, com SHA congelado às **18h (UTC−4)**.
Ainda faltam revisão independente, integração, aceite e ensaios finais. São 200 alvos lógicos em loopback, sem homologação de equipamentos físicos ou operação prolongada.
