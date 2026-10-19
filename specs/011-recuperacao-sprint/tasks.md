# Recuperação da sprint — execução

Base: dev@001d30402a1c5900a8228111ac16301171c83083.
Branch: fix/sprint-aceite-autenticacao-privacidade.
Escopo autorizado: demonstração controlada; roteiro futuro permanece separado.

- [x] Checkout novo e ambiente virtual independente; cópia original preservada.
- [x] K11: CORS autenticado, login/painel, erros HTTP e revogação de sessão.
- [x] #6 parcial: chave obrigatória após .env, arquivo de hashes, sem contas padrão/bypass.
- [x] #5 parcial: CPF livre, IPv6 abreviado, nomes/hostnames e auditoria sem texto bruto.
- [x] E6: métricas por identificador, bloqueio seguro separado e caso que prova falso sucesso anterior.
- [x] Build/lint e navegador com IA simulada.
- [x] CI inclui aceite HTTP, E6, build/lint e navegador.
- [x] K09/K12: validação isolada de prontidão, autenticação e persistência; recursos removidos.
- [ ] Revisão de outro integrante e integração aprovada na dev/main.
- [x] Conferir CI remoto da implementação e atualizar o quadro com PR #32 e links da entrega.

Não fechar #5/#6 por este escopo parcial. PostgreSQL de usuários/sessões,
Argon2id/bcrypt e homologação hospitalar permanecem fora desta demonstração.
