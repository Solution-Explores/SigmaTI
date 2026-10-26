# Perguntas prováveis do orientador (demonstração de 27/10)

Cola de apoio, preparada em 26/10. Cada resposta usa só o que o repositório ou os registros provam, com a fonte. Onde algo **não foi medido**, a resposta diz isso. Números do SHA congelado `7851da6` (Windows) e da VM (`75b1874`, rodada 7) estão em [plano-demonstracao-2026-10-27.md](../plano-demonstracao-2026-10-27.md).

## Resultados e métodos

**1. Os números de carga valem para um hospital?**
Não. Foram medidos em laboratório, em loopback, com 200 alvos lógicos apontando para um serviço TCP local, sem rede hospitalar nem painel na medição de carga. Valem para dizer que o agendador e o caminho queda → SSE aguentam 200 alvos com intervalo de 2 s nesse cenário. Homologação em rede real é trabalho futuro (#11, #12).

**2. Por que há números diferentes no Windows e na VM?**
Hardware, sistema e método diferentes: Windows do desenvolvedor (p95 de 0,854 s, máximo de 1,065 s, 30 quedas) contra VM Ubuntu com 4 vCPU (p95 entre 0,314 e 0,402 s nas cinco cargas da rodada 8, no mesmo SHA; entre 0,395 e 0,496 s na rodada 7, em `75b1874`). Por isso não se comparam; cada um está rotulado com o seu SHA. O mesmo código, antes das correções de #43 e #44, reprovava a carga de 200 alvos em 0 de 5 repetições na VM.

**3. O que são `missed_overlap` e os timeouts nos resultados da carga?**
São contadores do agendador de ciclos perdidos (por sobreposição, por relógio ou por falta de capacidade), acumulados desde o início da execução. Nas execuções de 22/10 no Windows ficaram em torno de 187 e 60, acumulados antes e depois da janela, **sem aumento durante a janela medida**; `missed_capacity` ficou em 0 e `errors` em 0. A causa exata dos timeouts não foi isolada (**não medido**). Se perguntarem, dizer isso.

**4. O MTTD de 0,26 s é real?**
É o do ensaio: o tempo entre a hora real da queda, registrada pelo operador no comando de apoio, e a detecção. O painel **não** mostra MTTD porque o incidente não guarda a hora real da falha; o MTTD sai de `POST /api/eng/incidentes/metricas`. Os MTTA e MTTR da demo (segundos) dependem de quão rápido o operador clica; não representam uma operação real.

**5. Os testes passam sempre?**
Não sempre. No SHA congelado: no Windows, 491 aprovados e 1 pulado, e o CI do GitHub passou; na VM (rodada 8), a segunda execução do pytest completo deu 492/492, mas a **primeira** deu 491/492, porque o teste de carga com 200 alvos excedeu o limite de atraso do calendário (0,957 s contra 0,5 s; causa não isolada), e 1 de 10 execuções isoladas do teste do provedor ficou em 15,545 s contra 15 s. Existem **quatro testes sensíveis a tempo**, já presentes antes dos PRs (#45): provedor de IA (prazo interno de 14 s contra a meta de 15 s; 1 falha em 80 execuções isoladas na VM, 15,0248 s), sonda (corrigida no #47: 26/30 → 30/30 na VM), DNS e agendador (este com 28/30 na `develop` de 21/10). A margem do timer de IA será decidida na S2.

## Segurança, LGPD e governança

**6. A anonimização é confiável?**
Só dá para afirmar o que o corpus E6 mediu: 59 amostras sintéticas e 53 identificadores, com 100% de recall de transformação, 0 falsos positivos por mensagem negativa e 0 vazados (CPF, CNS, e-mail, hostname, IPv4, IPv6, MAC, nome, prontuário). **Não** demonstra anonimização universal nem conformidade jurídica; nomes sem contexto e hostnames fora dos padrões podem escapar. #5 amplia isso com casos adversariais (S1). Fonte: `resultados/experimento-e6-anonimizacao.md`.

**7. O que acontece se a anonimização falhar?**
Falha fechada: a chamada ao provedor não é feita e a API devolve erro (no aceite, `fail_closed` → HTTP 500 com 0 novas chamadas ao provedor). IPv4 é generalizado para /24 e IPv6 para /64.

**8. Por que a IA é simulada?**
Porque o objetivo da demonstração é mostrar o caminho dos dados (o que sai da rede e em que forma) sem custo, sem chave real e sem enviar nem dados fictícios a terceiros. No aceite, o provedor é um transporte simulado (`MockTransport`; nenhum provedor real é chamado). A API exige `OPENROUTER_API_KEY` e `SIGMA_LLM_MODEL` para iniciar, mas testes com um provedor real **não** foram feitos.

**9. Quem garante o controle de acesso: o painel ou a API?**
A API. O painel esconde abas, mas o N1 recebe HTTP 403 em `GET /api/usuarios` e o gestor recebe 200. Sessões JWT são revogáveis: no aceite, o mesmo token após o logout devolve 401.

**10. Como funciona a aprovação por dois analistas?**
Quem pediu não pode decidir (a API devolve 409 ao solicitante); outro integrante aprova ou rejeita com justificativa; o pedido expira em 15 minutos. O painel avisa que nenhum comando é executado: a decisão fica registrada, não dispara nada.

**11. A trilha de auditoria é à prova de adulteração?**
Ela é encadeada com HMAC e a verificação aponta inconsistências (a demo mostra "Integridade consistente · N registros"). **Limites:** a chave e o último hash ficam no mesmo host; a âncora externa, a rotação da chave e a verificação agendada são a issue #13 (S2). Os eventos operacionais (incidentes, aprovações) ficam em registro próprio, fora da cadeia das sondas. E o custo da verificação cresce com o tamanho: cerca de 37,8 ms com 1 mil registros, 355,9 ms com 10 mil e 3.001,5 ms com 100 mil (VM, rodada 4); a meta de 50 ms da #46 não é atendida pelo desenho atual.

## Escopo, prazo e processo

**12. O que o painel não mostra?**
MTTD e burn rate (só pela API; entram como stretch na S2) e o rótulo "em risco" do SLO (a API devolve `at_risk`, o painel mostra "Disponível" e o orçamento restante).

**13. O que falta para a v1.0.0?**
#5 (critérios completos), aceite final de #6 e #8 (as issues só fecham com todos os critérios), reorganização do repositório e aceite da release em 31/10 e 01/11. #13 e #25 (restauração em outra máquina física) são propostos para 10/11.

**14. Por que o #25 não foi concluído?**
A restauração e o smoke passam em VM na mesma máquina (17 verificações); falta uma máquina física diferente, que depende de acesso a ela. Pergunta ao orientador: a VM basta como evidência?

**15. Como vocês garantem que outra pessoa consegue rodar?**
O Iohan revisou os PRs #43, #44 e #47 (quem revisa não é quem fez); a instalação limpa está em `docs/guias/instalacao.md`; o CI roda cinco verificações (configuração, pacote, PostgreSQL, recuperação e compose); imagens e portas estão fixadas por digest e restritas ao loopback. O relatório da execução independente do Iohan de 24/10 **ainda não está registrado** (cobrar antes de afirmar).

## O que não afirmar
- "Homologado", "pronto para produção" ou "conforme a LGPD".
- "Testes estáveis" sem citar a #45.
- Que a VM da rodada 8 passou, enquanto não houver `RESULTADO.md`.
- Que o painel exibe MTTD ou burn rate.
- Que a anonimização funciona para dados reais.
