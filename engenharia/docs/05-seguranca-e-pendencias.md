# 05 · Segurança e pendências

## Bloqueadores do repositório

Encontrados ao ler o repositório antes de portar o código. **Não foram alterados nesta branch** (fora do escopo da pasta `engenharia/`), mas bloqueiam a operação real e estão registrados como issues.

| # | Achado | Local | Impacto |
|---|---|---|---|
| B1 | `docker-compose.yml` contém marcadores de conflito de merge (`<<<<<<<`, `=======`, `>>>>>>>`) | `docker-compose.yml` | O arquivo é YAML inválido; `docker compose up` e o job de CI `validate-compose` falham |
| B2 | Credenciais fixas (`admin` / `adminpassword`) e porta `5432` publicada no host | `docker-compose.yml` (lado HEAD) | Banco acessível na rede com senha conhecida |
| B3 | Imagens com tag `:latest` (zabbix, grafana, n8n) | `docker-compose.yml` | Builds não reprodutíveis; atualização silenciosa |
| B4 | `OPENROUTER_API_KEY` fixa no código (vazia no momento) | `main.py` | Convida a commitar um segredo; deve vir de variável de ambiente |
| B5 | CORS com `allow_origins=["*"]` e `allow_credentials=True` | `main.py` | Qualquer origem pode chamar a API; restringir à origem do painel |
| B6 | Anonimização cobre apenas IPv4 e o literal `dr.joao` | `main.py::anonimizar_dados` | Contradiz o RF05 (nomes, MACs, hostnames, prontuários); risco LGPD |
| B7 | Se a anonimização falhar, o fluxo segue e envia o texto | `main.py` | O README promete "se o filtro falhar, nada é enviado" |
| B8 | `requests.post` síncrono, sem *timeout*, dentro de `async def` | `main.py` | Bloqueia o *event loop*; sem limite de espera (RNF04 ≤ 15 s não é garantido) |
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
