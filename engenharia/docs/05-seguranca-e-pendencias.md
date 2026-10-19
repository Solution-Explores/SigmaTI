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
| B5 | CORS com `allow_origins=["*"]` e `allow_credentials=True` | `main.py`, `api_errors.py` | **K06 / para revisão:** origens explícitas; Origin não permitido recusado antes da rota; preflight restrito a POST/Content-Type, sem compartilhamento de credenciais. Erros HTTP/validação/internos genéricos com log seguro. Clientes sem Origin continuam possíveis; autenticação permanece B9. Veja [solução e evidências](../../specs/004-cors-erros-publicos/spec.md). |
| B6 | Anonimização cobre apenas IPv4 e o literal `dr.joao` | `sanitizer.py`, `main.py` | **Resolvido na Issue #5 (RF05):** Módulo `sanitizer.py` implementado com regras determinísticas para IPv4 (/24), IPv6 (/64), MAC, hostnames para categorias, CPF, CNS, prontuários e nomes clínicos, sem tabela de/para (Art. 12 LGPD). Veja [spec.md](../../specs/005-anonimizador-fail-closed/spec.md). |
| B7 | Se a anonimização falhar, o fluxo segue e envia o texto | `sanitizer.py`, `main.py` | **Resolvido na Issue #5 (RF05):** Arquitetura two-pass com detecção residual e bloqueio fail-closed estrito; falha no filtro aborta o envio à IA e registra auditoria segura (`AUDIT_PRIVACY`), garantindo zero chamadas externas. Veja [evidencias.md](../../specs/005-anonimizador-fail-closed/evidencias.md). |
| B8 | `requests.post` síncrono, sem *timeout*, dentro de `async def` | `main.py` | **K05 / implementação para revisão:** cliente HTTPX2 assíncrono compartilhado, timeouts HTTP e prazo global de 14 s, erro público genérico e log técnico sem payload/segredos. Validação com provedor simulado; revisão independente e homologação operacional pendentes. A issue #4 permanece aberta. Veja [solução e evidências](../../specs/004-chamada-assincrona-timeout/spec.md). |
| B9 | Sem autenticação nas rotas | `main.py` | RF07 não implementado |

## Riscos introduzidos por este núcleo e mitigações

| Risco | Mitigação |
|---|---|
| Sonda usada como proxy para varrer a rede (SSRF) | `is_target_allowed` exige que **todos** os IPs resolvidos estejam nas redes autorizadas; padrão = RFC 1918 + loopback |
| Troca de DNS entre a checagem e a conexão (TOCTOU/rebinding) | Limitação conhecida: a conexão resolve de novo. Mitigar conectando ao IP já validado (issue) |
| Execução de comandos via runbook | Sem shell, allowlist, validação de variáveis, dry-run padrão, aprovação por passo |
| Trilha de auditoria alterada por quem tem acesso ao arquivo | HMAC com `SIGMA_AUDIT_KEY` fora do disco da trilha; cópia periódica do último hash para outro host |
| Rotas `/api/eng/*` sem autenticação | **Pendente.** Não expor fora do laboratório antes de RF07 |
| Chave HMAC perdida invalida a verificação do histórico | Guardar a chave em cofre; documentar rotação (issue) |

## Limitações conhecidas do núcleo

- A cadeia de hash detecta adulteração, mas **não impede** que alguém com acesso total apague o arquivo inteiro e comece outro; é preciso ancorar o último hash fora da máquina.
- `ApprovalService` e `RunbookRunner` guardam estado em memória; reiniciar o processo perde pendências. Persistência em PostgreSQL está nas issues.
- A latência medida é a do *handshake* TCP, não a do serviço de aplicação.
- Um `EwmaDetector` por alvo é mantido em memória; o estado se perde ao reiniciar (re-aquecimento de 20 amostras).
