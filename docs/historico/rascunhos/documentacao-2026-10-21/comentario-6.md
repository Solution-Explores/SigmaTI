## Situação em 21/10/2026
[Certo] #6 está **validado em VM; aceite final em 23/10**, com a correção de auditoria no PR #43 (`8662ea9`), aberto e com CI verde.
Evidência local: `rodada-2026-10-22b`: auditoria concorrente **7/7**; regressão do #43 **476/478**, com falhas no E2 de carga (depende do #44) e no teste temporal DNS. O candidato conjunto `ddd4840` passou **489/489**.
Próximo passo: revisão independente por @iohanjheremy até **22/10 às 8h (UTC−4)**; @Vinny1313 trata achados e integra em 22/10, conforme o plano.
Ainda não houve revisão aprovada, merge do #43 ou aceite final no SHA da demo. Âncora externa e rotação HMAC pertencem à #13 e seguem pendentes.
