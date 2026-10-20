# Issue #14 — conexão ao IP validado

## Implementação

Base independente: develop@27d2b55, sem incorporar o PR #36 aberto. Resolver uma vez por série, exigir todos os IPs dentro de SIGMA_PROBE_NETS, fixar o primeiro IP e conectar socket numérico IPv4/IPv6 sem segunda resolução. Host e SNI usam o nome original normalizado em IDNA. Host inclui porta não padrão e colchetes IPv6. Respostas mistas/vazias, falha DNS, scope e autoridades inválidas são recusadas antes da conexão. API conserva RBAC e responde 403 para destino recusado.

probe_service também aplica a política quando chamado diretamente; probe_many reutiliza o destino na série inteira. Não há fallback nem redirects. Conectores injetados recebem somente IP numérico. Nenhuma alteração na política de inspeção TLS, auditoria criptográfica ou persistência.

## Validação local — 19/10/2026 (UTC−4)

37 testes aprovados em 20,15 s:

```powershell
.venv/Scripts/python.exe -m pytest engenharia/tests/test_probe_pinning.py engenharia/tests/test_stats_probe.py engenharia/tests/test_api.py -q
```

Inclui DNS alternando IP permitido/externo nos protocolos TCP/HTTP/HTTPS; uma resolução para três amostras; recusa da resposta externa na operação seguinte; Host/SNI preservados; DNS misto/vazio/mapeado; entradas inválidas; socket numérico IPv4/IPv6; falha DNS; API autorizada e restrição de perfil; conexão HTTP real em loopback com nome fictício e redirect externo não seguido. HTTPS usa contexto/socket simulado para observar SNI, sem alegar validação de confiança TLS real. HTTP real usa socket real. Nenhuma conexão ao IP externo é executada.

pip check: sem dependências quebradas. git diff --check aprovado. CI completo será conferido no PR antes de registrar conclusão.

## Revisão técnica e limites

Conferidos os caminhos API → probe_many → probe_service → socket: não existe passagem de hostname ao conector padrão. Cada medição revalida o IP fixado sem DNS; um novo pedido faz nova resolução/política. Todos os IPs da resposta devem ser autorizados, sem escolher apenas um IP permitido de uma resposta mista. Documentação de riscos atualizada em engenharia/docs/05-seguranca-e-pendencias.md.

Revisão pelo Codex; não atribuída a integrante independente. Sem merge, fechamento de issue ou alteração no PR #36. Scheduler/prazo global (#8), confiança PKI e âncora/rotação da auditoria (#13) permanecem fora deste bloco. A indisponibilidade do primeiro IP retorna falha, sem tentativa automática em outro destino.
