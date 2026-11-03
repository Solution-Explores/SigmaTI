# Roteiro: restauração da #25 em máquina física separada (terça, 03/11/2026)

Executa o primeiro critério da #25: restaurar o backup em outra máquina reproduz os incidentes e uma auditoria íntegra. Siga o guia [backup-restauracao.md](../operacao/backup-restauracao.md); este roteiro só ordena os passos e diz o que anotar. Resultado no registro [segunda-maquina.md](../specs/018-backup-restauracao/segunda-maquina.md).

**Ensaio feito em 02/11 no computador de casa, com as mesmas etapas das seções 2 a 4.7: todas passaram.** O que o ensaio mudou neste roteiro: volume nomeado desde o início, senha digitada no console e a conferência da porta no momento C.

**Dados fictícios apenas.** Não leve dados reais do hospital nem da empresa. Não publique no GitHub o pacote, a chave, a trilha bruta, tokens nem configurações reais.

## 0. Antes de ir para a máquina de destino (no seu computador)

1. Confirme o SHA que vai ser testado: o `develop` depois da integração dos PRs aprovados (anote o SHA completo).
2. Gere um pacote **novo** nesse SHA, em vez de reaproveitar `test-results/recovery-final`, que veio de um SHA antigo e pode ter outro `alembic_version`:

   ```bash
   git switch --detach <SHA>
   .venv/Scripts/python.exe scripts/validate_recovery.py --output test-results/recovery-2026-11-03
   ```

   Precisa de Docker ligado. Saem `bundle/` (dump, trilha e manifesto), `audit-key.txt` (a chave, **fora** do bundle) e `report.json`. Anote do `report.json` a imagem do PostgreSQL com o digest e a versão principal.
3. **Se o SHA ainda não está no GitHub** (candidato montado localmente, por exemplo `develop` mais PRs ainda não integrados), a máquina de destino não consegue baixá-lo. Gere um arquivo de git com o histórico e confira-o:

   ```bash
   git bundle create candidato-<SHA7>.bundle --all
   git bundle verify candidato-<SHA7>.bundle
   sha256sum candidato-<SHA7>.bundle        # anote o hash para conferir no destino
   ```

   Se o SHA já está na `develop` do GitHub, pule este passo e clone do GitHub (seção 2).
4. Leve em um pendrive: **o `bundle/`** do pacote de restauração, o `candidato-<SHA7>.bundle` (se gerado) e uma cópia de `scripts/verificar_ambiente_restauracao.py`, para conferir a máquina **antes** de clonar. Leve a **chave por outro canal** (por exemplo, digitada à mão ou enviada por mensagem). Nunca no mesmo pacote.
5. Guarde também o SHA e o digest da imagem do PostgreSQL.

## 1. Na máquina de destino: verificar se serve

| Item | Conferir | Se faltar |
|---|---|---|
| Docker | `docker version` e `docker run --rm hello-world` funcionam | Sem Docker não dá; ver "Se não der" |
| Python 3.12+ | `python --version` | Instalar só se permitido |
| Git | `git --version` | Idem |
| Disco/rede | 2 GB livres; acesso ao PyPI e Docker Hub | Pedir à TI ou usar o plano B |

Anote, sem identificar a empresa: sistema operacional, memória, versão do Docker e do Python. Descreva a máquina como "notebook Windows 11, 16 GB" ou similar.

**Prepare o ambiente completo antes de restaurar, em vez de ir instalando aos poucos.** Na rodada de testes da #45 em VM, a primeira tentativa perdeu 6 minutos porque faltavam o `docker compose` e o Chromium do Playwright, e só se descobriu no fim. O mesmo vale aqui: instale tudo o que o guia exige (Git, Python 3.12+, Docker com o plugin Compose, as dependências do `requirements-dev.txt`) e **confira com o script abaixo antes de tocar no pacote**. Ele só usa a biblioteca padrão, não imprime chave nem senha e sai com código diferente de zero se faltar algo.

A verificação roda em três momentos, sempre com o mesmo script, e cada um só passa se o anterior passou:

| Quando | Comando | O que confere |
|---|---|---|
| **A. Antes de clonar** (cópia do script do pendrive) | `python verificar_ambiente_restauracao.py` | Python 3.12+, Git, Docker instalado, **em execução e com contêineres Linux**, Compose, porta livre, 2 GiB e rede (PyPI e Docker Hub). Se acusar `FALTA` em Docker, Python ou Git, pare e vá à seção 7 |
| **B. Depois do clone e do checkout** (seção 2), antes de subir o PostgreSQL | `python scripts\verificar_ambiente_restauracao.py --sha <SHA> --imagem <IMAGEM_COM_DIGEST_DO_REPORT>` | O mesmo, mais: SHA do clone, clone sem alterações, imagem do PostgreSQL com o digest e venv com as dependências |
| **C. Imediatamente antes do restore** (seção 3), com o PostgreSQL já no ar, o pacote copiado e a chave na sessão | `python scripts\verificar_ambiente_restauracao.py --sha <SHA> --imagem <IMAGEM_COM_DIGEST_DO_REPORT> --bundle C:\sigma-restore\bundle` | O mesmo, mais: os três arquivos do pacote, chave **fora** do pacote e `SIGMA_AUDIT_KEY` com 32 bytes ou mais. Aqui a porta precisa **responder** (é o PostgreSQL de destino) |

Só siga para o restore com "Ambiente completo" no momento C. O script só usa a biblioteca padrão e não imprime chave nem senha.

Se faltar acesso ao PyPI ou ao Docker Hub (proxy corporativo), o script diz qual. Nesse caso peça liberação à TI ou use o plano B da seção 7, em vez de contornar a política da empresa.

Anote no registro as versões de Python, Docker e Compose que a verificação encontrou.

## 2. Preparar o destino

```powershell
# SHA já na develop do GitHub:
git clone https://github.com/Solution-Explores/SigmaTI.git
# SHA candidato, só no arquivo de git do pendrive (confira antes o hash: Get-FileHash candidato-<SHA7>.bundle):
git clone candidato-<SHA7>.bundle SigmaTI

cd SigmaTI
git checkout <SHA>
git rev-parse HEAD            # deve ser igual ao SHA anotado
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Suba um PostgreSQL **vazio**, da **mesma versão principal e imagem** do `report.json`. Nome e credenciais podem ser diferentes da origem; não aplique migrações antes do restore. O **volume nomeado** (`-v sigma-dest-data:...`) é necessário desde já: a prova da seção 4.7 recria o contêiner com ele, e sem volume o teste teria de ser refeito:

```powershell
$senha = [guid]::NewGuid().ToString('N')       # não imprimir nem anotar
docker run -d --name sigma-db-recuperado -v sigma-dest-data:/var/lib/postgresql/data `
  -e POSTGRES_USER=sigma_dest -e POSTGRES_DB=sigma_dest `
  -e POSTGRES_PASSWORD=$senha -p 127.0.0.1:55432:5432 <IMAGEM_COM_DIGEST_DO_REPORT>
docker exec sigma-db-recuperado pg_isready -U sigma_dest -d sigma_dest
```

Copie o `bundle/` para uma pasta do destino (por exemplo, `C:\sigma-restore\bundle`). Em Windows não há `chmod`; mantenha a pasta fora de diretórios sincronizados na nuvem.

## 3. Verificar o pacote e restaurar

```powershell
$env:SIGMA_AUDIT_KEY = '<a chave recebida pelo canal separado>'     # ao menos 32 bytes
.venv\Scripts\python.exe scripts\recovery.py verify --bundle C:\sigma-restore\bundle
.venv\Scripts\python.exe scripts\recovery.py restore --container sigma-db-recuperado `
  --bundle C:\sigma-restore\bundle --audit C:\sigma-restore\audit-restaurado.jsonl --quiesced
echo $LASTEXITCODE
```

(`restore.sh` só chama esse mesmo `recovery.py`; no Windows rode direto o Python.) **Anote:** o código de saída (esperado 0) e o JSON final (`status`, `tables`, `audit_entries`). `verify` e `restore` recusam chave errada, pacote alterado e banco ocupado: se recusar, **não force**, anote a mensagem e pare.

## 4. Conferir que reproduziu incidentes e auditoria

O `restore` já compara todas as tabelas, contagens e fingerprints com o manifesto e só então grava a trilha. Confirme isso e faça as conferências pela API:

1. **Auditoria íntegra pela chave** (sem depender da API):

   ```powershell
   $env:PYTHONPATH = "engenharia"
   .venv\Scripts\python.exe -c "import os; from sigma_eng.audit_chain import AuditChain; c=AuditChain(r'C:\sigma-restore\audit-restaurado.jsonl', chave=os.environ['SIGMA_AUDIT_KEY'].encode()); print(c.resumo())"
   ```

   Esperado: `integra: True`, `primeira_invalida: None` e `entradas` igual ao `audit_entries` do restore.

2. **Subir a API no banco restaurado** (coleta desligada). Configure por variável de ambiente, **sem gravar em arquivo versionado**:

   ```powershell
   $env:SIGMA_DATABASE_URL = "postgresql+psycopg://sigma_dest:$senha@127.0.0.1:55432/sigma_dest"
   $env:SIGMA_COLLECTION_ENABLED = "0"
   $env:SIGMA_AUDIT_PATH = "C:\sigma-restore\audit-restaurado.jsonl"
   $env:SIGMA_JWT_SECRET = -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
   $env:OPENROUTER_API_KEY = "fake-restauracao-apenas"
   $env:SIGMA_LLM_MODEL = "test/model"
   $env:SIGMA_CORS_ORIGINS = "http://localhost:5173"
   $env:PYTHON_DOTENV_DISABLED = "1"
   .venv\Scripts\python.exe -m uvicorn --app-dir backend main:app --host 127.0.0.1 --port 8000
   ```

3. **Entrar na API.** A senha do usuário de teste do pacote não é guardada pelo script de validação (ele a descarta). Crie um usuário novo no banco restaurado, em outro terminal. Defina nele as mesmas variáveis do passo 2 (`SIGMA_DATABASE_URL`, `SIGMA_AUDIT_PATH` e as demais):

   ```powershell
   $env:PYTHONPATH = "backend"
   .venv\Scripts\python.exe -m scripts.manage_identity create restauracao.gestor gestor_ti
   ```

   **O comando pede a senha digitada, duas vezes** (12 a 128 caracteres, e ela **não aparece na tela enquanto você digita**). Precisa de um console de verdade: não funciona com a senha vinda por pipe ou redirecionamento. Invente uma senha só para este teste e não a anote.

   Depois, login e as conferências 4 a 6 (testado em Windows, com o PostgreSQL em `127.0.0.1:55432`):

   ```powershell
   $b = "http://127.0.0.1:8000"
   $l = Invoke-RestMethod -Method Post -Uri "$b/api/auth/login" -ContentType "application/json" `
     -Body (@{username="restauracao.gestor"; password=(Read-Host "Senha do teste")} | ConvertTo-Json)
   $h = @{Authorization = "Bearer $($l.access_token)"}
   ```

4. **Incidente original:** `(Invoke-RestMethod "$b/api/eng/incidentes" -Headers $h).incidentes`. Esperado: o incidente do pacote (alvo `smoke.synthetic`, criado pela falha TCP injetada na origem) aparece na lista. Anote só a contagem e que o ID do incidente da origem consta.
5. **Auditoria pela API:** `(Invoke-RestMethod "$b/api/eng/auditoria/verificar" -Headers $h).integra`. Esperado: `True`.
6. **Nova escrita sem colisão de IDs.** Leia o maior ID, grave e leia de novo:

   ```powershell
   $q = "SELECT max(id) FROM eventos_operacionais;"
   docker exec sigma-db-recuperado psql -U sigma_dest -d sigma_dest -At -c $q      # antes (no ensaio: 4)
   Invoke-RestMethod -Method Post -Uri "$b/api/eng/aprovacoes" -Headers $h -ContentType "application/json" -Body '{"acao":"restauracao.pos"}'
   docker exec sigma-db-recuperado psql -U sigma_dest -d sigma_dest -At -c $q      # depois: precisa ser maior (no ensaio: 5)
   ```

7. **Recriar o contêiner com o mesmo volume** (o volume nomeado já foi criado no passo 2). Anote as contagens, recrie e compare:

   ```powershell
   $q = "SELECT 'incidentes='||count(*) FROM incidentes UNION ALL SELECT 'eventos='||count(*) FROM eventos_operacionais UNION ALL SELECT 'usuarios='||count(*) FROM usuarios;"
   docker exec sigma-db-recuperado psql -U sigma_dest -d sigma_dest -At -c $q       # ANTES
   # pare a API (Ctrl+C no terminal dela), depois:
   docker rm -f sigma-db-recuperado
   docker run -d --name sigma-db-recuperado -v sigma-dest-data:/var/lib/postgresql/data `
     -e POSTGRES_USER=sigma_dest -e POSTGRES_DB=sigma_dest -e POSTGRES_PASSWORD=$senha `
     -p 127.0.0.1:55432:5432 <IMAGEM_COM_DIGEST_DO_REPORT>
   docker exec sigma-db-recuperado pg_isready -U sigma_dest -d sigma_dest          # espere responder
   docker exec sigma-db-recuperado psql -U sigma_dest -d sigma_dest -At -c $q       # DEPOIS: iguais
   ```

   Se a sessão do PowerShell foi fechada, `$senha` se perdeu: o contêiner recriado precisa da **mesma** senha do original.

## 5. O que anotar em `segunda-maquina.md`

Preencha cada linha **sem segredos nem dados brutos**:

- Data, operador e identificação fictícia das máquinas de origem e destino (por exemplo, "origem: PC pessoal Windows 11; destino: notebook corporativo Windows 11, 16 GB").
- SHA completo do código, versão principal e imagem do PostgreSQL (com digest).
- Manifesto verificado com a chave recebida por canal separado: resultado do `verify`.
- Comando de restauração, código de saída e o resumo (`tables`, `audit_entries`).
- Inventário de tabelas conferido pelo restore.
- Incidente original visto pela API e `integra: true`.
- Recriação do contêiner com o mesmo volume sem perda.
- Nova escrita e IDs sem colisão.
- Evidência e resultado final: **aprovado** só se todos os itens passaram na máquina de destino.

## 6. Limpeza ao terminar

Pare a API, `docker rm -f` o contêiner, `docker volume rm` o volume, apague `C:\sigma-restore`, o `.venv` e o clone, e limpe as variáveis de ambiente da sessão. Não deixe chave, pacote nem trilha na máquina do estágio.

## 7. Se não der

- **Sem Docker ou sem permissão:** não dá para fazer aqui; use outra máquina física ou declare a limitação no TCC e mantenha a #25 na Sprint 2.
- **Plano B declarado:** a restauração em VM limpa, descrita em [planejamento-validacao-25-virtualbox.md](../historico/planejamento-validacao-25-virtualbox.md), só vale se a limitação (VM, não hardware distinto) for registrada.
- **Falha no restore:** não force nem use `--clean`. Anote a mensagem, descarte só o contêiner de destino e investigue com o guia.

## Comentário para a issue #25 (depois de preencher o registro)

> Restauração em máquina física separada em DD/11/2026. SHA `<SHA>`, PostgreSQL `<versão>`, origem e destino descritos de forma fictícia em `docs/specs/018-backup-restauracao/segunda-maquina.md`. `recovery.py verify` ok com a chave por canal separado; `restore` saiu com 0 (`tables=<n>`, `audit_entries=<n>`); trilha íntegra (`integra: true`); incidente original listado pela API; contêiner recriado com o mesmo volume sem perda; nova escrita sem colisão de IDs. Sem dump, trilha bruta, chaves nem configurações reais anexados. Critério 1 atendido, ou: o que falhou e por quê.
