# Atividades do Iohan: Sprints 1, 2 e 3 (plano do orientador, atualizado em 02/11/2026)

**Plano seguido.** A partir de 02/11/2026 vale o plano do orientador, e o planejamento pós-demo está descontinuado. A fonte são os três milestones do GitHub e a auditoria de 31/10 (`SigmaTI-auditoria-estabilizacao-2026-10-31.md`, seção 5):

| Sprint | Prazo | Issues do orientador |
|---|---|---|
| 1, Fechar a v1.0.0 | 03/11 | #5 (risco alto), #13, #25, #56 (bloqueador) |
| 2, Robustez e evidências | 10/11 | #8, #45, #46, #57 |
| 3, Congelamento e banca | 17/11 | Texto do TCC, ensaio e banca em 18/11. Código congelado em 11/11, só correção P0 |

O orientador ainda não decidiu mover a #13 e a #25 para 10/11. Até a resposta dele, os prazos continuam como estão no milestone.

02/11 é feriado. Cada um integra o próprio PR para a `develop` quando o CI estiver verde, como em [fluxo-de-trabalho-tcc.md](../processo/fluxo-de-trabalho-tcc.md). **Quem revisa não integra o PR de outro autor.** A restauração em máquina física, a VM e os testes de carga (#25, #8) ficam com o Vinícius. A estimativa anterior era de ≈ 10 h por semana para o Iohan; confirme a sua disponibilidade, porque as revisões abaixo somam horas.

Sem segredos e sem dados reais do hospital, em tudo.

## Resumo em poucas linhas

O que você já entregou ajudou bastante: o conjunto cego e a regressão da #5 (PR #64) e os avisos da #56. Falta pouco para fechar cada um. O resto deste documento tem o detalhe de cada item.

**Agora (Sprint 1, até 03/11)**
1. **Revisar os meus PRs** (#59, #60, #61, #62 e #65). Só revisar: cada um integra o próprio PR, então quem integra sou eu.
2. **Ajustar o PR #64** para ele ficar verde:
   - o teste que falha acontece porque o critério de aprovação do E6 mudou;
   - o ajuste é voltar ao critério original e mostrar o outro resultado ao lado, no relatório;
   - tirar o "Closes #5" do PR, porque a #5 ainda não está pronta.
3. **Fechar a #56:**
   - corrigir o número (digest) citado no seu comentário;
   - combinar com a Joyce como atualizar as branches dela;
   - fazer o PR que separa a checagem do CI (sem internet) da checagem agendada do Docker Hub.

**Depois (Sprint 2, até 10/11)**
4. **#57:** rotas que respondem "sucesso" sem fazer nada. Comece depois que o #60 e o #61 entrarem.

**Sprint 3 (até 17/11):** texto do TCC, ensaio e banca. Combinamos a divisão até 07/11.

## Situação em 02/11 (noite)

| Item | Situação |
|---|---|
| #5, regressão e conjunto cego | Entregue no PR #64. Está com CI vermelho e precisa de correções (seção 1) |
| #56, causa e aviso à Joyce | Comentários feitos na #56 e nos PRs #52 a #55. Faltam correções e o PR estrutural (seção 2) |
| Revisões dos PRs #59, #60, #61, #62 e #65 | Não feitas. Só o #65 tem revisão pedida a você |
| #57 | Não iniciada |

## Sprint 1 (prazo 03/11)

### 1. Issue #5: ajustar o PR #64 (prioridade)

O PR #64 traz a regressão dos 14 casos e o conjunto cego de 46 amostras. O Vinícius integra o #59 (regras); o #64 é seu. A revisão encontrou o que corrigir:

1. **Voltar o critério de aprovação do E6.** Em `scripts/executar_experimento_e6.py`, o `aprovado` passou de recall de transformação para recall de proteção. O orientador não autorizou essa troca e ela derruba `test_safe_block_is_not_counted_as_transformation`. Faça assim:
   - `aprovado` volta a usar o recall de transformação (≥ 99%).
   - Crie `aprovado_protecao` à parte (nenhum vazamento, recall de proteção ≥ 99% e taxa de falso positivo dentro do limite), com um teto para a taxa de bloqueio, para que "bloquear tudo" não passe.
   - O relatório mostra os dois resultados lado a lado. Com isso o teste vermelho passa sem ser alterado.
   - `TestConjuntoCegoE6` deixa de exigir `aprovado is True`. Passa a exigir `vazados == 0` e `aprovado_protecao`.
2. **Reverter** as mudanças em `engenharia/resultados/experimento-e6-anonimizacao.md` (relatório do corpus de desenvolvimento). O orientador pediu o recall só no conjunto cego.
3. **Tirar o "Closes #5"** do corpo do PR e desmarcar os critérios que ainda não valem.
4. **Apertar a regressão** em `backend/tests/test_sanitizer.py`:
   - Fixe o resultado esperado de cada caso: os 13 que devem ser transformados e o ADV-04 (`Maria Oliveira (leito 12)`), que deve ser bloqueado. Hoje o `else` aceita qualquer bloqueio.
   - No ADV-13, proíba também `Manaus` e `123`, e não só a rua.
   - Esclareça no teste que os "14 casos" são 13 linhas da tabela do orientador, com a linha do hostname virando duas entradas (`PACS-01` e `pacs01`).
5. **Falha injetada** (critério da #5): já existe `test_fail_closed.py:54`, mas ele troca a função inteira por um mock. Acrescente:
   - um teste do ramo `erro_execucao` dentro de `sanitizar_texto`;
   - um teste de ponta a ponta em que `/api/alertas`, com uma mensagem que o sanitizador bloqueia, mostre que o provedor não é chamado e que o evento entra na trilha de auditoria.
6. **Relatório.** Hoje o PR cria `docs/historico/resultados/`, que não existe na `develop`. Grave em `engenharia/resultados/`, onde está o E6, e comente o resultado na #5. O relatório precisa declarar:
   - quem escreveu o conjunto, quando e em que branch. O conjunto foi commitado depois das regras (11 horas), na mesma branch, e o campo `substituto` exige conhecer a saída do sanitizador. Escreva o que de fato aconteceu, sem afirmar mais do que o Git prova;
   - que 14 dos 26 positivos repetem o molde dos 14 casos do orientador, então medem cobertura dos casos conhecidos, não generalização;
   - **o tamanho amostral.** Com 41 identificadores, o limite inferior de Wilson de 41/41 é 91,43%. Provar ≥ 99% com 95% de confiança exigiria cerca de 380 identificadores sem erro. A meta só vale como estimativa pontual, e o texto não pode afirmar "≥ 99%" como demonstrado;
   - os dois recalls (transformação 95,12% e proteção 100%), a taxa de bloqueio e os falsos positivos (1/20, no limite de 5%);
   - o rodapé `APROVADO` precisa refletir o critério voltado ao original. Se o recall de transformação ficar abaixo de 99%, o conjunto aparece como não aprovado nesse critério, e isso é honesto.
7. **Ampliar o conjunto** com casos que hoje faltam e que podem expor limites reais:
   - nomes sem contexto **fora** da lista de prenomes, nomes compostos com partícula, acentuados, em caixa alta e em caixa baixa (suspeita: `MARIA OLIVEIRA` sem cargo passa; confirme);
   - `Dr.`, `Dra.`, `Enf.`, `Doutor`; CNS com pontos ou hífens; RG sem pontuação; telefone sem parênteses e celular sem DDD; data de nascimento em outros formatos (`nasc.`, `DN`, `12-03-84`);
   - IPv4 com porta ou CIDR; FQDN (`.local`); endereço com `Av.` ou `Travessa`; registro por `protocolo` ou `AIH`; mensagens com vários identificadores misturados;
   - negativos difíceis: datas de log, números de 11 dígitos, versões, nomes compostos comuns (`Rosa Maria`, `Vera Cruz`).
8. **Regra de independência daqui em diante.** O Vinícius não ajusta as regras olhando os casos novos. Se alguma regra for ajustada por causa de um caso do conjunto, esse caso passa a ser de desenvolvimento, e o recall cego é relatado só em casos novos que ninguém tenha usado para ajustar regra. Combine com o Vinícius antes de rodar.

**Pronto quando:** o #64 está verde e revisado, a regressão fixa o resultado esperado, a falha injetada tem teste de ponta a ponta, o relatório declara as limitações acima, e a #5 tem o comentário de evidência com o recall e o intervalo de confiança. A #5 só fecha com todos os critérios atendidos. Se o recall de transformação não alcançar a meta, a decisão do critério é do orientador, e a limitação fica declarada.

### 2. Issue #56: CI de infraestrutura (bloqueador da Sprint 1)

Você já comentou a causa na issue e nos PRs #52 a #55. Falta corrigir o que está errado e atender os critérios de aceite da issue.

1. **Corrigir o comentário na #56.** O digest que o comentário cita (`sha256:7824aa8a…e04f`) não existe no repositório nem no Docker Hub. O digest do `docker-images.lock.json` e do compose é `sha256:f7d23353e1b15400d22ebe31189f4d314b87a4c129cc400c8c2d8d4ca127bf81`. Registre também:
   - o último run da `main` é de 28/10, anterior à republicação. A prova de que a checagem por digest passa é o run da `develop` de 01/11. Dispare ou aguarde um run na `main` para ter evidência direta;
   - a proposta "agora" do corpo da #56 (atualizar o digest) foi superada, porque o digest antigo continua válido.
2. **Corrigir o aviso à Joyce.** Na base do #55 é a `feature/ds-03-marca-paleta`, não a `feature/front-design-system`. E "atualizar com a main" não é trivial: mesclar a `develop` na `feature/front-design-system` dá 5 conflitos pela renomeação `sigma-frontend/` para `frontend/`. O caminho mais curto é levar só o commit `8661916` (3 linhas em `scripts/validate_infrastructure.py`) para a `feature/front-design-system` com cherry-pick e propagar para ds-01, ds-02 e ds-03; o ds-04 herda do ds-03. O conflito da renomeação só aparece quando a branch for integrada na `develop`. Combine com a Joyce quem faz, e confirme que o CI fica verde nos PRs #52 a #55.
3. **PR estrutural (critérios 2 e 3 da #56).** Hoje não existe PR nem workflow agendado:
   - O `ci.yml` do PR deixa de depender do Docker Hub: fica só a coerência compose × lock e as regras de porta, sem rede.
   - Um workflow separado, com `schedule` (semanal) e `workflow_dispatch`, roda `--verify-registry` e compara a tag com o lock, para a deriva continuar visível. Ele avisa ou abre issue, sem reprovar PR de outras áreas.
   - Um teste com lock divergente simulado, para provar que a mudança de tag no registry não reprova PR que não toca em infraestrutura.
4. **Não troque o digest** no lock nem no compose.

**Pronto quando:** o CI está verde na `main` e nos PRs #52 a #55, a mudança de tag no Docker Hub não reprova PR que não toca em infraestrutura (com teste), e a deriva upstream continua visível por job agendado ou relatório. O aviso à Joyce sozinho não fecha a #56.

### 3. Revisões

Revisão formal no GitHub (pedido de alteração, aprovação ou comentário de revisão), **sem integrar**. O autor integra. Todos estão com CI verde:

| PR | Para que | O que conferir |
|---|---|---|
| #59 | Regras da #5 | Os 14 casos do orientador, o detector residual de nomes, falsos positivos |
| #60 | #13: âncora externa e rotação HMAC | Remoção total detectável pela âncora, rotação com histórico verificável, ADR 0002 |
| #61 | #45: timer de IA e teste de DNS | Você é o revisor independente nomeado na #45. Veja a justificativa de 14 s para 13 s e a espera por evento |
| #62 | Roteiro da restauração da #25 | Passos, verificação de ambiente e caminhos |
| #65 | #46: custo da auditoria | Você é o revisor independente nomeado na #46. Veja a recusa de gravação após adulteração e a brecha declarada no ADR |

Ordem: #60 antes do #65, porque o #65 depende dele.

## Sprint 2 (04 a 10/11)

### 4. Issue #57: rotas que respondem sucesso sem efeito

Comece depois que o #60 e o #61 entrarem na `develop`, porque eles também mexem em `backend/main.py` e na documentação de configuração. Rebaseie antes de abrir o PR. Atribua-se à issue.

**Decisão de escopo:** `POST /api/alertas` passa a responder `status: "Diagnóstico gerado"`. Registrar o incidente de fato fica fora desta tarefa: a tabela `incidentes` exige `alvo_id`, e incidentes nascem de medição. Se isso for necessário, abra uma issue própria.

Em `backend/main.py` (não há roteador para essas rotas):

- `POST /api/chaves/rotacao` (linha ≈ 249) passa a responder `501`. A mensagem pública é genérica, sem prometer data. A #23 trata do cofre de credenciais, não desta rota.
- `POST /api/alertas` (≈ 155): troque o texto de `status` e mantenha o conjunto de chaves da resposta.
- `GET /api/n8n/acesso` (≈ 255): ler `SIGMA_N8N_URL`, sem URL fictícia. Sem a variável, responda 501 ou 503 (escolha e registre). Valide o esquema (`http` ou `https`) e recuse credenciais embutidas. Remova o status `autorizado_vlan_gerencia`, que não verifica nada. Acrescente `SIGMA_N8N_URL` ao `.env.example`, em ponto distante do bloco que o #60 altera, e à documentação de configuração.
- `GET /api/alertas`, `/api/pacotes` e `/api/relatorios` (≈ 203, 209 e 221): listas vazias fixas, indistinguíveis de "sem dados". Responda 501 ou remova a rota. Os relatórios são da #16.
- `GET /api/incidentes` (≈ 215): sem banco devolve `[]` com 200. Passe a responder 503, como já faz `routers/operational.py`. Não está na #57, mas é o mesmo defeito.
- `GET /api/status` (≈ 197) afirma "operacional" sem checar nada. Registre como débito técnico, sem corrigir agora.

**Testes**
- Um teste por rota garantindo que nenhuma responde 2xx sem efeito. Cada teste deve conferir o **corpo** da resposta do 501, porque `api_errors.py` pode reescrever o `detail`.
- A matriz RBAC (`backend/tests/test_session_auth.py`, `ROTAS_MATRIZ`) continua cobrindo 401 e 403. O esperado do perfil autorizado nas rotas que passam a responder 501 muda para 501 (campo `esperado`). Casos afetados: `/api/chaves/rotacao`; `GET /api/alertas`, `/api/pacotes`, `/api/relatorios` para os perfis autorizados; `/api/n8n/acesso` sem a variável. A fixture `temporary_identity` força `SIGMA_DATABASE_URL=""`, então o `operational_store` é `None` na matriz.
- Atualize os testes que fixam o texto antigo: `backend/tests/test_provider.py` (linhas 24, 54, 77), `test_config.py:237`, `test_fail_closed.py:159`, `test_public_errors.py:218` e `scripts/validate_api_acceptance.py:157`. O conjunto de chaves da resposta de `/api/alertas` não pode mudar.
- Documentação: `docs/operacao/configuracao-e-execucao.md:156`, `docs/specs/006-autenticacao-jwt-rbac/spec.md:90-96` e `docs/demo/smoke.ps1:45`. O README (linha 134) já diz que "Incidente Registrado" não comprova a gravação; reescreva essa linha depois da mudança e marque chaves, relatórios e pacotes como "planejado".

**Painel.** Só `POST /api/alertas` é consumida (`frontend/src/Diagnostic.jsx`), e o campo `status` não é lido. Mapeie `501` em `frontend/src/api.js` para uma mensagem própria ("Recurso ainda não disponível"), com teste no Vitest, porque hoje o 501 cai no texto genérico de indisponibilidade.

**Pronto quando:** cada rota tem teste, a matriz RBAC está atualizada e verde, os testes e a documentação acima estão ajustados, e o PR foi rebaseado depois do #60 e do #61. Estimativa: 8 a 11 h.

### 5. Revisor independente da #45 e da #46

Você já é o revisor independente nomeado nas duas issues. Depois da revisão dos PRs #61 e #65, confirme na issue que a revisão foi feita. Isso conta para o critério "PR da correção revisado" da #45.

## Sprint 3 (11 a 17/11)

O código fica congelado em 11/11, e só entra correção de bug P0. O trabalho é o texto do TCC, os slides, o ensaio e a banca em 18/11. O orientador ainda não confirmou a banca. A divisão entre você e o Vinícius ainda não foi definida; combinem na revisão de 07/11, antes do congelamento. Itens candidatos:

- Roteiro de demonstração (`docs/demo/roteiro-demonstracao.md`) e ensaio.
- Seção do TCC sobre anonimização, com as limitações da #5 (conjunto cego, tamanho amostral, nomes fora da lista).
- Seção sobre o CI hermético e a deriva do registry (#56).

## Ordem sugerida

1. Corrigir o #64 (critério do E6, relatório, testes) e abrir a revisão com o Vinícius.
2. Revisar #60, #59, #61, #62 e #65, nessa ordem.
3. Corrigir o comentário da #56, combinar com a Joyce o cherry-pick do `8661916` e abrir o PR estrutural.
4. #57, depois que o #60 e o #61 estiverem na `develop`.

## Regras que valem para tudo

CI verde antes do merge. Cada critério tem teste ou comando. Sem segredos. Evidência comentada na issue. A issue só fecha se todos os critérios estiverem atendidos; se não, deixe aberta e liste o que falta. Depois do congelamento de 11/11, só entra correção de bug P0. Atribua-se às issues que assumir (#5, #56, #57), como pede o fluxo de trabalho.
