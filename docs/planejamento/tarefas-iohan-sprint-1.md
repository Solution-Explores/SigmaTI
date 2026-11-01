# Atividades do Iohan na Sprint 1 (prazo 03/11/2026)

Estamos seguindo as sprints e as orientações do orientador, registradas nos milestones e nos comentários das issues. A Sprint 1 fecha a `v1.0.0` em 03/11, e 02/11 é feriado. Você tem duas issues, em cerca de 5 pts (≈ 10 h). Cada um integra o próprio PR para a `develop` quando o CI estiver verde, como em [fluxo-de-trabalho-tcc.md](../processo/fluxo-de-trabalho-tcc.md). O plano completo está em [plano-pos-demo-issues-abertas.md](plano-pos-demo-issues-abertas.md).

A restauração em máquina física, a VM e os testes relacionados (#25) ficam com o Vinícius.

## 1. Issue #5: anonimização, regressão e conjunto cego (4 pts, comece por esta)

- **Por que:** o orientador testou o anonimizador com 14 casos fora do corpus e todos vazaram. O recall de 100% do E6 valia só para casos escritos por quem escreveu as regras. Ele pediu explicitamente que o conjunto de avaliação seja escrito por você, sem ver as regras (veja o último comentário da #5).
- **Regra importante:** você escreve os testes e os casos, e o Vinícius ajusta as regras em `backend/sanitizer.py`. Não leia as regras antes de fechar o conjunto cego. O Vinícius, por sua vez, não ajusta as regras olhando o seu conjunto.
- **Parte A, regressão (1 pt):** inclua os 14 casos do comentário do orientador em `tests/test_sanitizer.py` como regressão, sem relaxar as asserções. O arquivo existe em `backend/tests/test_sanitizer.py`. Eles ficam falhando até as regras do Vinícius serem corrigidas, e isso é esperado.
- **Parte B, conjunto cego (3 pts):**
  1. Escreva casos sintéticos com texto de incidente de rede e o resultado esperado de cada um. Cubra IPv4 e IPv6, MAC, hostname, e-mail, login, CPF e CNS (inclusive com espaços e pontos), prontuário e registro de atendimento, nomes (com e sem cargo, "Dr" sem ponto, após "Paciente:", "Sra."), telefone, RG, data de nascimento e endereço. Inclua casos negativos, que não devem ser alterados, para medir falsos positivos.
  2. Quando as regras estiverem corrigidas, rode o conjunto no `sanitizar_texto` e registre o recall e a precisão com intervalo de confiança. A meta é recall ≥ 99%.
  3. Escreva o relatório em `docs/historico/resultados/`, declarando as limitações, e comente o resultado na issue.
- **Dados:** somente fictícios, nunca dados reais do hospital.
- **Pronto quando:** a regressão, o conjunto cego, o teste que o executa e o relatório estão na `develop`, e o resultado está comentado na #5.

## 2. Issue #56: CI de infraestrutura vermelho (1 pt)

- **O que a issue diz:** o Docker Hub republicou a tag do PostgreSQL, e o CI falha em todas as branches. Ela propõe atualizar o digest no lock e no compose.
- **O que foi verificado:** o commit `8661916` (22/10) já faz a `main` checar só pelo digest fixado, e `python scripts/validate_infrastructure.py --verify-registry` passa na `main`. As branches vermelhas (PRs #52 a #55, da Joyce: `feature/ds-*` e `feature/front-design-system`) não têm esse commit.
- **O que fazer:**
  1. Comente na #56 a causa correta.
  2. Avise a Joyce nos PRs #52 a #55 para atualizar as branches com a `main`. Se ela autorizar, você mesmo atualiza. Confirme que o CI fica verde.
  3. Não troque o digest no lock nem no compose por conta própria. Se quiser propor a atualização, revise antes o changelog da imagem e faça num PR separado.
  4. Se couber, proponha a separação estrutural: checagem sem rede (compose × lock) bloqueante, e verificação de deriva do registry num job agendado e informativo.
- **Pronto quando:** o CI está verde nas branches abertas e a causa correta está registrada na issue.

## Ordem sugerida

1. Parte B da #5 (conjunto cego), porque não depende de ninguém.
2. Parte A da #5 (regressão dos 14 casos).
3. #56, que é rápida.

## Sprint 2 (04 a 10/11): issue #57, rotas com sucesso sem efeito (3 pts)

Sugerida para você. A auditoria encontrou rotas que passam pelo controle de acesso, mas respondem sucesso sem executar nada. Em `backend/main.py`:

- `POST /api/chaves/rotacao` responde `chaves_rotacionadas` sem rotacionar nada. Passa a responder `501 Not Implemented` com mensagem pública clara. A rotação real é da #23.
- `POST /api/alertas` responde "Incidente Registrado" sem gravar o incidente. Registre o incidente de fato (o armazenamento operacional já existe, #7) ou mude o texto para "Diagnóstico gerado".
- `/api/n8n/acesso` devolve uma URL fixa fictícia. Passa a ler `SIGMA_N8N_URL`, sem valor fictício.
- `GET /api/alertas`, `/api/pacotes` e `/api/relatorios` devolvem listas vazias fixas, indistinguíveis de "não há dados". Os relatórios são da #16.
- O painel não deve exibir uma rota 501 como sucesso.

**Pronto quando:** existe um teste por rota garantindo que nenhuma responde 2xx sem efeito correspondente, a matriz RBAC de `test_session_auth.py` continua verde, e o README deixa de afirmar que "Incidente Registrado" comprova a gravação.

Se sobrar tempo na Sprint 2, converse com o Vinícius sobre pegar parte do painel (MTTD e burn rate).

## Regras que valem para tudo

CI verde antes do merge, cada critério com teste ou comando, sem segredos, evidência comentada na issue. A issue só fecha se todos os critérios estiverem atendidos. Se não, deixe aberta e liste o que falta.
