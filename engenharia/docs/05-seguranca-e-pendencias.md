> Estado atual e limites: [revisão da sprint de 19/10](../../docs/specs/011-recuperacao-sprint/evidencias.md). Relatos de testes anteriores são históricos; anonimização por regras não garante anonimização universal.

# 05 · Segurança e pendências

## Bloqueadores do repositório

Achados registrados antes de portar o código. As mitigações posteriores são
identificadas na coluna de status; uma entrega parcial não encerra automaticamente
a issue nem substitui a revisão e a validação operacional.

| # | Achado | Local | Impacto / Status |
|---|---|---|---|
| B1 | Marcadores de conflito de merge no `docker-compose.yml` | `docker-compose.yml` | **Resolvido na Issue #2:** YAML corrigido, validado localmente e no CI com stack core e profile `monitoring` |
| B2 | Credenciais fixas e porta `5432` publicada no host | `docker-compose.yml` | **K03 / entrega parcial da issue #3:** credenciais obrigatórias sem fallback e template sem senhas; PostgreSQL já sem porta publicada. Revisão por outro integrante e rotação de credenciais existentes continuam pendentes. |
| B3 | Referências de imagens mutáveis | `docker-compose.yml` | **K04 / configuração para revisão:** todas as imagens têm release e digest verificados no registro oficial. Bancos sem publicação e Zabbix também em loopback por padrão. Zabbix 6.4 permanece sem suporte; migração, homologação operacional e revisão por outro integrante são pendências separadas. Issue #3 não encerrada. |
| B4 | `OPENROUTER_API_KEY` fixa no código (vazia no momento) | `main.py` | **K02 / regressão preservada na K06:** chave obrigatória pelo ambiente; ausência/valor inválido impede a inicialização. Revisão independente do conjunto pendente. |
| B5 | CORS com `allow_origins=["*"]` e `allow_credentials=True` | `main.py`, `api_errors.py` | **K06 / para revisão:** origens explícitas; Origin não permitido recusado antes da rota; preflight restrito a POST/Content-Type, sem compartilhamento de credenciais. Erros HTTP/validação/internos genéricos com log seguro. Clientes sem Origin continuam possíveis; autenticação permanece B9. Veja [solução e evidências](../../docs/specs/004-cors-erros-publicos/spec.md). |
| B6 | Anonimização cobre apenas IPv4 e o literal `dr.joao` | `sanitizer.py`, `main.py` | **Implementação parcial #5 / revisão de 19/10:** Módulo `sanitizer.py` implementado com regras determinísticas para IPv4 (/24), IPv6 (/64), MAC, hostnames para categorias, CPF, CNS, prontuários e nomes clínicos, sem tabela de/para (Art. 12 LGPD). Veja [spec.md](../../docs/specs/005-anonimizador-fail-closed/spec.md). |
| B7 | Se a anonimização falhar, o fluxo segue e envia o texto | `sanitizer.py`, `main.py` | **Implementação parcial #5 / revisão de 19/10:** Arquitetura two-pass com detecção residual e bloqueio fail-closed estrito; falha no filtro aborta o envio à IA e registra auditoria segura (`AUDIT_PRIVACY`), garantindo zero chamadas externas. Veja [evidencias.md](../../docs/specs/005-anonimizador-fail-closed/evidencias.md). |
| B8 | `requests.post` síncrono, sem *timeout*, dentro de `async def` | `main.py` | **K05 / implementação para revisão:** cliente HTTPX2 assíncrono compartilhado, timeouts HTTP e prazo global de 14 s, erro público genérico e log técnico sem payload/segredos. Validação com provedor simulado; revisão independente e homologação operacional pendentes. A issue #4 permanece aberta. Veja [solução e evidências](../../docs/specs/004-chamada-assincrona-timeout/spec.md). |
| B9 | Sem autenticação nas rotas | `main.py`, `routers/auth.py`, `auth.py` | **Implementação parcial #6 / revisão de 19/10:** Autenticação por JWT de sessão (HS256) com tempo de expiração curto, senhas em hash PBKDF2-HMAC-SHA256 com salt individual, RBAC estrito com 3 perfis (`suporte_n1`, `analista_redes`, `gestor_ti`) cobrindo a matriz do README e as rotas `/api/eng/*`, rate limiting contra força bruta (5 tentativas/lockout) e registro de login/logout/bloqueio na AuditChain. Veja [spec.md](../../docs/specs/006-autenticacao-jwt-rbac/spec.md). |

## Riscos introduzidos por este núcleo e mitigações

| Risco | Mitigação |
|---|---|
| Sonda usada como proxy para varrer a rede (SSRF) | `resolve_target` exige que **todos** os IPs resolvidos estejam nas redes autorizadas; padrão = RFC 1918 + loopback. Política aplicada também nas funções de sondagem; entrada inválida, falha DNS, resposta vazia/mista ou IP fora da política são recusados antes da conexão. |
| Troca de DNS entre a checagem e a conexão (TOCTOU/rebinding) | **Implementado para revisão — #14:** uma resolução por série, IP numérico fixado e socket direto, incluindo HTTPS, com Host/SNI original (IDNA para domínio internacional). Sem nova resolução/fallback durante a série; redirects não são seguidos. Regressões com resolvedor alternante e conexão HTTP real em `engenharia/tests/test_probe_pinning.py`. |
| Execução de comandos via runbook | Sem shell, allowlist, validação de variáveis, dry-run padrão, aprovação por passo |
| Trilha de auditoria alterada por quem tem acesso ao arquivo | HMAC com `SIGMA_AUDIT_KEY` fora do disco da trilha; cópia periódica do último hash para outro host |
| Rotas `/api/eng/*` sem autenticação | **Implementação parcial #6 / revisão de 19/10:** Rotas `/api/eng/*` protegidas via dependência FastAPI `exige_papel("analista_redes")` para operações de engenharia e `exige_papel("gestor_ti")` para auditoria. |
| Chave HMAC perdida invalida a verificação do histórico | Guardar a chave em cofre; documentar rotação (issue) |

## Limitações conhecidas do núcleo

- A cadeia de hash detecta adulteração, mas **não impede** que alguém com acesso total apague o arquivo inteiro e comece outro; é preciso ancorar o último hash fora da máquina.
- `ApprovalService` e `RunbookRunner` preservam estado em PostgreSQL quando configurados (#7/PR #36); o modo legado sem banco continua em memória. Ver [estado operacional](08-estado-operacional.md).
- A latência medida é a do *handshake* TCP, não a do serviço de aplicação.
- Na coleta persistente (#8), snapshots EWMA/MAD confirmam com a medição e são recuperados após reinício. Uso isolado sem repositório permanece em memória; parâmetros exigem calibração. Ver [coleta e eventos](09-coleta-eventos.md).


## Revisão das issues de base — 20/10/2026

Consulte [a revisão de #6/#7/#8/#14](../../docs/historico/revisao-achados-base-2026-10-20.md).
O pinning #14 foi integrado no PR #37; o texto “para revisão” acima é histórico.
Na branch de correção, a auditoria JSONL coordena escritores cooperantes por
arquivo lateral `.lock`, relê o arquivo sob esse bloqueio e recusa append em
cadeia inválida. A API verifica integridade e contagem no mesmo snapshot atual.
Não remover/substituir o arquivo de lock enquanto houver processos ativos.
Lock local não constitui coordenação distribuída em filesystem de rede, nem
substitui HMAC, âncora externa e rotação da #13. As leituras e validações são
lineares no tamanho da trilha; planejar rotação antes de uso prolongado.

## Limites da correção #14

- O primeiro IP da resposta autorizada é usado; indisponibilidade não dispara tentativa em outro endereço. Nova operação resolve e valida novamente.
- IPv6 usa socket AF_INET6 e autoridade HTTP entre colchetes. Endereços com scope/interface são recusados. Portas não padrão aparecem no Host.
- A sonda HTTPS continua sendo inspeção de certificado: não valida cadeia de confiança, não autentica o serviço e não envia credenciais. Preservar SNI não constitui validação PKI. Essa política não foi ampliada neste bloco.
- DNS e cada operação de socket não têm prazo global compartilhado; limites de coleta/scheduler permanecem na #8. Redes permitidas devem refletir a política do ambiente, incluindo o risco de acesso a serviços internos.
- A auditoria JSONL existente continua sem âncora externa/rotação (#13). A correção de destino não resolve essas pendências.
