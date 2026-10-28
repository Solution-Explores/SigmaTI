# Revisão do PR `fix/base-issues` (head `8662ea9`)

**Veredito sugerido: Request changes (leve).** São duas correções pequenas, de poucas linhas cada. O núcleo do lock está correto e dá para fazer o merge na quinta de manhã.

## Verificação local

- Worktree isolado em `../SigmaTI-review`. A sua branch `dev` não foi alterada.
- `tests/test_fail_closed.py`, `tests/test_session_auth.py`, `engenharia/tests/test_audit_shared.py` e `engenharia/tests/test_scheduler.py`: **92 aprovados em 18,5 s** (Windows, Python 3.14).
- Script de borda ([probe_edges.py](file:///C:/Users/iohan/.gemini/antigravity-ide/brain/31555448-f838-4ad6-9afd-d2cbcf245a04/scratch/probe_edges.py)):

| Cenário | Resultado |
|---|---|
| Exceção dentro do `with _coordenar()` | Lock liberado; mesma instância e outra instância voltam a gravar ✅ |
| Última linha JSON truncada (queda no meio da gravação) | `verificar()` = `(False, 1)` e `registrar()` recusa ✅ (falha fechado) |
| Byte UTF-8 inválido na trilha | `verificar()` e o construtor lançam `UnicodeDecodeError` ❌ |

## Checklist do roteiro

1. **`_coordenar()`**: o `finally` envolve a leitura e o `yield`, então exceções na leitura ou no corpo do `with` liberam o lock. Se a aquisição falhar ou estourar o tempo, o lock não chegou a ser obtido e o `with open` fecha o handle. Os errnos tratados (`EACCES`/`EAGAIN`/`EDEADLK`) cobrem `msvcrt` e `flock`. O `resolve()` faz caminhos por symlink usarem o mesmo `.lock`. ✅
2. **Releitura sob lock**: correta. Duas instâncias no mesmo processo também disputam o lock do SO, porque o `flock` vale por descritor e o `msvcrt` por handle. ✅
3. **`registrar()`** falha fechado, e a linha sem `\n` é tratada. ✅
4. **`resumo()`**: contagem e integridade saem da mesma leitura. ✅
5. **Auth falha fechado**: `obter_auditor()` lança `RuntimeError`; o login (em todos os ramos) e o logout dão 500. ✅
6. **Sanitizer**: `TimeoutError` é subclasse de `OSError`, e `UnicodeDecodeError` é subclasse de `ValueError`, então os dois viram `SanitizationError`. ✅

### Pergunta: existe caminho em que a IA é chamada sem a auditoria registrar?

**Sim.** No caminho de sucesso de `POST /api/alertas` ([main.py:163-181](file:///d:/iohan/Faculdade/TCC/SigmaTi/SigmaTI-review/main.py#L163-L181)), quando `anonimizar_dados` passa, `consultar_ia` é chamada e **nada** vai para a AuditChain. A auditoria só registra bloqueios (`privacy.sanitization_failed`). Isso **não foi introduzido por este PR**: é anterior a ele. O que este PR garante é que nenhum bloqueio deixa de ser auditado. Sugiro abrir uma issue (ex.: registrar `ai.request` com categoria e status, sem conteúdo) em vez de bloquear este PR.

## Achados a corrigir (Request changes)

### A. UTF-8 inválido derruba a verificação em vez de reportar adulteração
O arquivo é aberto em modo texto `utf-8` estrito ([audit_chain.py:79](file:///d:/iohan/Faculdade/TCC/SigmaTi/SigmaTI-review/engenharia/sigma_eng/audit_chain.py#L79)). Um byte inválido gera `UnicodeDecodeError`:
- `/api/eng/auditoria/verificar` responde 500 em vez de `{"integra": false, "primeira_invalida": i}`;
- `AuditChain(...)` em `main.py` falha no startup.

O `registrar()` continua falhando fechado, então não há buraco de segurança. O problema é que justamente o endpoint de detecção de adulteração para de funcionar. Correção sugerida: ler em binário e decodificar linha a linha, tratando a falha como linha inválida (`{}`), mais um teste.

### B. Espera do lock bloqueia o event loop
`receber_alerta` é `async def` e chama `anonimizar_dados`, que chama `registrar_auditoria_privacidade` de forma síncrona. Agora isso inclui `time.sleep` em laço por até **10 s**, mais a leitura O(n) e o `fsync`. Sob contenção, o loop inteiro congela: SSE, outras requisições e o **scheduler da coleta**, o que pesa justamente no diagnóstico da #8. Correção sugerida: `await asyncio.to_thread(anonimizar_dados, ...)` em `main.py`, ou transformar o endpoint em `def`.

## Não bloqueantes

- **C.** Trilha com última linha truncada (queda no meio do `write`) bloqueia login e logout até reparo manual. É o comportamento esperado de falha fechado, mas vale um parágrafo de procedimento de recuperação em `docs/historico/correcao-issues-base.md` (§ Limites operacionais).
- **D.** [api.py:79](file:///d:/iohan/Faculdade/TCC/SigmaTi/SigmaTI-review/engenharia/sigma_eng/api.py#L79) ainda usa como padrão o relativo `resultados/audit.jsonl` quando `auditoria` não é passada. Isso contradiz o doc ("Auth e engenharia passam a usar o mesmo caminho padrão"). Hoje o `main.py` sempre passa a instância, então é só um nit.
- **E.** O logout revoga o token antes de auditar. Se a auditoria falhar, o cliente recebe 500 com o logout já efetivado. Isso é aceitável (falha segura), mas vale um comentário no código.
- **F.** Se o unlock no `finally` lançar exceção, ele mascara a exceção original. O fechamento do arquivo libera o lock de qualquer forma. É só um nit.
- **G.** `scheduler.py`, `validate_*.py` e os docs estão OK. Os docs não prometem mais do que o código faz.

---

## Comentários prontos para colar no GitHub

**`engenharia/sigma_eng/audit_chain.py` L79** (Request changes)
> Com `encoding="utf-8"` estrito, um byte inválido na trilha lança `UnicodeDecodeError`: `verificar()`/`resumo()` e o construtor explodem, e o endpoint `/auditoria/verificar` responde 500 em vez de `integra: false`. O `registrar()` continua fechado (ValueError), mas a detecção de adulteração para de funcionar. Sugestão: abrir em `"rb"` e, por linha, `try: row = json.loads(line.decode("utf-8")) except ValueError: row = {}`. Vale também um teste com `b"\xff"` anexado.

**`sanitizer.py` L210** (Request changes)
> Esta chamada roda dentro de `async def receber_alerta` (via `anonimizar_dados`), e agora pode ficar até 10 s em `time.sleep` esperando o lock, mais a leitura O(n) e o `fsync`, tudo no event loop. Sob contenção isso congela o SSE e o scheduler da coleta. Sugestão: em `main.py`, `erro_anonimizado = await asyncio.to_thread(anonimizar_dados, alerta.descricao_erro)`, ou transformar o endpoint em `def`.

**`engenharia/sigma_eng/audit_chain.py` L91-96** (elogio/nit)
> `finally` cobre leitura e `yield` 👍. Nit: se o `LK_UNLCK`/`LOCK_UN` lançar exceção, ele mascara a exceção original. Dá para envolver em `try/except OSError: pass`, já que o `close()` libera o lock de qualquer forma.

**`routers/auth.py` L109-110** (nit)
> O token é revogado antes da auditoria. Se ela falhar, o cliente recebe 500 com o logout já efetivado. Está OK como falha segura; sugiro só um comentário explicando a ordem.

**`docs/historico/correcao-issues-base.md` L37-39** (sugestão)
> Vale descrever o caso da última linha truncada por queda no meio da gravação: a trilha passa a recusar gravações, e login/logout dão 500 até o reparo. Um passo a passo curto (preservar cópia, verificar, isolar a linha final) ajuda na demo.

**Comentário geral do review**
> Lock lateral, releitura sob lock, `resumo()` atômico e falha fechado em auth/sanitizer conferidos. Os 92 testes focados passaram localmente no Windows. Duas correções antes do merge: (A) UTF-8 inválido derruba `verificar()` e (B) a espera do lock no event loop em `/api/alertas`. Fora do escopo, para issue: o caminho de sucesso de `/api/alertas` chama a IA sem registrar nada na AuditChain (só bloqueios são auditados). Também abrir issue para o `api.py:79`, que ainda usa como padrão `resultados/audit.jsonl`.
