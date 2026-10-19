# Correções K11/K12 e revisão de privacidade — 19/10/2026

Base remota: `dev@001d30402a1c5900a8228111ac16301171c83083`.
Branch: `fix/sprint-aceite-autenticacao-privacidade`.
Checkout independente em `D:/sigma-dev/SigmaTI`; cópia anterior preservada.
Execução e revisão técnica do código nesta conversa: Codex. Não se declara
revisão independente, aprovação de outro integrante ou homologação hospitalar.

## O que mudou

- CORS restrito aceita GET/POST e Authorization; login/me/logout no painel, Bearer
  apenas em memória, erros de autenticação/permissão/rede distintos.
- Logout remove o jti da sessão ativa; outro token do mesmo usuário permanece
  válido. Reinício/configuração invalida sessões; usuário desativado ou com papel
  alterado perde acesso. Removidos fallback JWT, contas automáticas e bypass.
- `.env` é carregado antes de configurar a chave JWT; arquivo local obrigatório
  contém somente hashes. Criação manual usa getpass; testes geram credenciais.
- CPF válido sem rótulo, IPv6 abreviado e nomes/hostnames passaram a ter cobertura
  adicional; detecção residual verifica todas as classes implementadas. Eventos
  de bloqueio entram na AuditChain sem texto, nomes, IPs ou valores originais.
- E6 agora avalia cada ocorrência anotada, com bloqueio seguro separado. Um teste
  adversarial reproduz remoção de e-mail com CPF restante e exige recall de 50%,
  um vazamento e reprovação, em vez do falso 100% anterior.
- CI inclui aceite HTTP real, E6, instalação npm pelo lockfile, build/lint e três
  testes Chromium com IA simulada. Sem chamadas ao OpenRouter real.

## Resultados locais

| Verificação | Resultado |
|---|---|
| Python 3.12, ambiente virtual novo e pip check | Aprovado, dependências de requirements-dev.txt |
| Regressão final pytest | 362 aprovados; zero falhas, erros ou ignorados; 274,93 s |
| Histórico de coleta | Baseline 346; dois casos de rejeição CORS GET/Authorization foram substituídos pela política autenticada aceita; cenários de recusa de origem e cabeçalhos estranhos preservados |
| Aceite HTTP real/Uvicorn | 20 verificações aprovadas; timeout 14,031 s, cancelamento confirmado e token revogado retorna 401 |
| E6 | 56 mensagens, 50 identificadores anotados; 50 transformados, nenhum bloqueado/vazado neste corpus; 25 negativos sem alteração |
| npm ci --include=optional | Instalação Windows final aprovada, sem regenerar o lockfile; Playwright foi adicionado explicitamente |
| Frontend build/lint | Aprovados |
| Chromium | 3 cenários aprovados, incluindo rejeição real do token após logout |
| Instalação isolada | 21 verificações aprovadas e limpeza código 0 |
| Política Compose | 32 verificações de credenciais, 12 cenários de infraestrutura e quatro manifests oficiais aprovados |

Artefatos locais ignorados: `test-results/sprint-final.xml`,
`test-results/browser.xml`, `test-results/painel-diagnostico.png` e saídas do
aceite HTTP. Snapshot sanitizado em
[resultados/recuperacao-sprint-2026-10-19.json](../../resultados/recuperacao-sprint-2026-10-19.json).
As medições locais descrevem o worktree de correção; o CI da publicação fornece
validação vinculada ao commit remoto. Nenhum relatório local anterior foi sobrescrito.

## Instalação K09/K12

Docker Engine 29.8.2 iniciado nesta execução. O download dos mesmos digests
concluiu com TLS válido; a causa do erro TLS da execução anterior não foi
determinada. Serviços, versões e volumes do Compose de produção foram preservados.
Cada execução usa projeto, contêineres, portas de loopback e volumes exclusivos;
o runner remove somente seus próprios recursos ao finalizar.

Duas correções do teste foram necessárias: verificar senha PostgreSQL no endereço
bridge, porque o loopback da imagem usa trust; e aguardar prontidão do n8n, porque
`/healthz` é apenas liveness. Durante migrações, o n8n devolve HTML com HTTP 200,
o que não comprova cadastro ou autenticação. O runner exige JSON de cadastro e
aguarda `/healthz/readiness` e `/rest/settings` antes de prosseguir.
Fonte primária da imagem 1.80.0:
[AbstractServer](https://github.com/n8n-io/n8n/blob/n8n%401.80.0/packages/cli/src/abstract-server.ts).

Resultado final: **21 verificações aprovadas**, incluindo senha correta/incorreta
nos bancos e no n8n/Grafana; owner nativo, acesso autenticado e recusa sem sessão;
marcadores nos dois PostgreSQL, configuração/owner do n8n e preferência do Grafana
preservados após recriar os contêineres. Projeto `sigma-acceptance-8547f31c3d` encerrado e volumes
descartáveis removidos; limpeza retornou código 0. Os demais projetos/volumes foram
preservados. SQL foi testado pela rede bridge, sem publicar portas dos bancos.

As tentativas anteriores ficam como evidências de correção do runner, não como
aceites do produto. A última execução usa as esperas corretas antes/depois da
recriação e exige JSON nas respostas do cadastro. Nenhuma proteção de cookie,
TLS ou autenticação foi desativada.

## Matriz de rastreabilidade e pendências

| Issue/cartão | Requisito/evidência | Próximo passo |
|---|---|---|
| #2 / K01 | Compose sem conflito, base já integrada | Conferência da equipe para fechamento |
| #3 / K03/K04 | Credenciais/portas/digests; validadores aprovados | Conferência operacional e revisão da entrega |
| #4 / K07/K08/K10/K11 | Timeout, CORS autenticado, contrato e erros seguros | Conferir aceite HTTP e CI do commit, revisar e integrar |
| #5 | E6 corrigido e falha segura auditada | Revisão completa das regras/limites; manter issue aberta |
| #6 / K11 | Sessões revogáveis, painel, chave/usuários externos | PostgreSQL e Argon2id/bcrypt; manter issue aberta |
| K09/K12 | Instalação, autenticação e persistência isoladas aprovadas | Revisão da evidência; não equivale a homologação hospitalar |
| K13 | Branch de correção preparada | Outro integrante revisa; integrar somente após aprovação |
| K14/K15 | Roteiro atualizado e evidências | Conferir CI, registrar decisão e atualizar quadro |

A issue #31 acompanha o roadmap; #7–#30 não foram implementadas por este recorte.
Sessões/usuários ainda usam memória; uma instância de API, dados fictícios e IA
simulada são os limites desta demonstração. O relatório E6 não atesta anonimização
universal nem conformidade jurídica. A mensagem legada "Incidente Registrado"
não significa persistência de incidente no PostgreSQL.
