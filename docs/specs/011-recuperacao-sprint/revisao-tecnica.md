# Revisão técnica e novo aceite — 19/10/2026

Revisão executada pelo Codex sobre o PR #32, após solicitação de prosseguimento.
Base da revisão: `7489bf292ca3e754ac1d57b60bf132c40f0cc3c3`, comparada à
`dev@001d30402a1c5900a8228111ac16301171c83083`. Os testes locais abaixo incluem
as correções do worktree descritas neste registro. Não representam revisão
independente por outro integrante.

## Achados corrigidos

1. **Sobrenome preservado na sanitização.** `Dr. Joao Silva`, `dr.joao Silva` e
   `Dra.Maria Souza` eram transformados em `[USUARIO_MEDICO] Silva/Souza`.
   A substituição literal removia o contexto antes da regra de nomes completos.
   A regra contextual agora roda primeiro e reconhece abreviação sem espaço.
   Acrescentados três casos no corpus, com fragmentos proibidos, e três testes.
2. **Sessão antiga após recriar conta.** Substituir o usuário pelo mesmo nome e
   papel preservava o token anterior. A substituição no repositório ativo revoga
   as sessões daquele usuário. O teste exige 401 para o token anterior e permite
   novo login com a senha substituta.
3. **Limites de login ignoravam `.env`.** As constantes eram avaliadas durante a
   importação, antes do carregamento do arquivo. A configuração agora aplica os
   limites após o `.env`, valida inteiros positivos e rejeita valores inválidos.
   Expiração também deixa de converter valores durante a importação.
4. **Aceite Docker não conferia diretamente o Zabbix.** A presença de tabelas no
   PostgreSQL não comprova que o servidor aceita conexões. Adicionadas verificações
   TCP na porta publicada exclusivamente em loopback antes/depois da recriação.
   Elas comprovam escuta, não ingestão completa de telemetria.

## Resultado da validação

| Verificação | Resultado |
|---|---|
| Regressão Python completa | 369 aprovados em 140,14 s; zero falhas, erros ou ignorados |
| Aceite HTTP/Uvicorn | 20 verificações aprovadas; timeout 14,032 s; cancelamento confirmado |
| Privacidade E6 ampliada | 59 mensagens, 53 identificadores transformados; zero vazamentos/bloqueios observados no corpus; 25 negativos preservados |
| Frontend | Build e lint aprovados; dependências/lockfile preservados |
| Chromium | 3 cenários aprovados; execução final encerrou normalmente em 10,2 s |
| Dependências Python | `pip check` aprovado |
| Instalação isolada completa | 23 verificações aprovadas, incluindo escuta Zabbix antes/depois da recriação; limpeza código 0 |
| Política de infraestrutura | 32 verificações de credenciais, 12 cenários de portas/imagens e quatro manifests oficiais aprovados |
| Diff | Sem erros de whitespace |

Primeira repetição do navegador passou nos três cenários, mas seu encerramento
ficou preso às permissões do Windows. Foram identificados e encerrados somente
os processos API/Vite daquele teste. A repetição com permissão de encerramento
concluiu normalmente; nenhuma proteção do produto foi alterada.

Os testes chamaram somente IA simulada e usaram credenciais fictícias temporárias.
Docker Engine 29.8.2; instalação com os mesmos digests fixados no repositório,
novos nomes/portas/volumes. Não foram alterados dados de outros projetos.

Artefatos locais ignorados: `test-results/revisao-final.xml`, `revisao-http.json`,
`revisao-e6.md`, `browser.xml` e `revisao-instalacao-completa/report.json`.
O relatório E6 versionado foi regenerado com o corpus ampliado.

## Decisão e limites

As verificações técnicas do escopo de demonstração passaram após as correções.
O PR pode seguir para revisão da equipe quando o CI do novo commit confirmar
os resultados. Não há aprovação de integração nesta revisão técnica.

O [fluxo do repositório](../../processo/fluxo-de-trabalho-tcc.md) exige:
“Peça revisão a outro integrante” e “não dispensa os testes nem a aprovação do colega”.
A aprovação de outro integrante continua pendente; `dev` e `main` não foram alteradas.
Após aprovação, validar o conjunto integrado na `dev` antes da `main`.

Issues #5/#6 continuam parciais: nomes e hostnames fora das regras permanecem um
limite conhecido; usuários/sessões persistentes e Argon2id/bcrypt pertencem ao
roadmap. Não se declara homologação hospitalar, anonimização universal ou
persistência de incidentes. Nenhuma issue deve ser fechada com este registro.
