# Registro preparado para a issue #4

**Rascunho não publicado.** O conector recusou a escrita com HTTP 403; a sessão
do navegador está sem login. Texto abaixo pronto para a equipe publicar em
https://github.com/Solution-Explores/SigmaTI/issues/4.

---

## Entrega parcial — K05: chamada assíncrona à IA com timeout

Responsável: Vinícius (Pessoa 1). Sprint: 15–20/10/2026; prazo: 16/10/2026.
Implementação publicada na `dev`: [d7a3e0d](https://github.com/Solution-Explores/SigmaTI/commit/d7a3e0d1b965128426424f399d9005de158bdb32).

Requests foi substituído por cliente HTTPX2 assíncrono compartilhado, aberto e
fechado no lifespan da API. Timeouts HTTP e prazo global de 14 s limitam a espera,
sem retentativas automáticas. Timeout, erro de transporte/HTTP e resposta inválida
produzem mensagem pública genérica, com categoria, classe, status e duração no log,
sem chave, prompt, corpo bruto ou texto arbitrário de exceção.

Mantidos HTTP 200 e os três campos usados pelo painel, configuração K02,
anonimização e frontend. #2/#3 não bloqueiam os testes isolados; infraestrutura
e seus validadores foram preservados.

**Validação local:** 119 testes aprovados em 20,87 s, sem avisos; `pip check` e
`git diff --check` aprovados; 32 verificações K03 e 12 cenários K04 aprovados.
Somente dados fictícios e provedor simulado. O teste com orçamento real retornou
em 14,031 s e confirmou cancelamento do provedor que aguardaria 20 s. Concorrência,
leitura contínua lenta, erros, logs seguros, reuso e fechamento também foram testados.

**CI remoto do commit da implementação: ambos aprovados.**

- [API e relatório JUnit `api-test-results`](https://github.com/Solution-Explores/SigmaTI/actions/runs/38794814488).
- [Infraestrutura](https://github.com/Solution-Explores/SigmaTI/actions/runs/38794814430).
- [Solução, decisões e limites](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/004-chamada-assincrona-timeout/spec.md).
- [Evidências e reprodução](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/004-chamada-assincrona-timeout/evidencias.md).
- [Atividades e pendências](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/004-chamada-assincrona-timeout/tasks.md).

**Estado: pronta para Revisão e testes.** Revisor independente a definir pela equipe;
aprovação pendente. A autorrevisão do agente não substitui a revisão de outro
integrante. A movimentação do cartão ainda precisa ser feita no quadro da equipe.

Aceites demonstrados no escopo K05: chamada assíncrona, espera limitada a menos
de 15 s no cenário simulado, erro público genérico, log técnico seguro e contrato
preservado. Configuração obrigatória e preflights CORS da K02 passaram na regressão.
CORS não é autenticação nem bloqueio universal de clientes HTTP.

**A issue #4 permanece aberta.** Demais atividades K06/K07, revisão independente
e conferência de todos os requisitos continuam pendentes. Sem integração à `main`
ou PR de integração nesta etapa. Vincular o PR quando existir após aprovação e
validação do conjunto. A simulação não comprova a latência da IA real em produção.
