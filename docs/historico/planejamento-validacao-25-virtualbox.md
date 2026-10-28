# Task #25 — validação de restauração em outra máquina (VirtualBox)

Planejamento para executar em outro local. Preparado em 20/10/2026 (UTC−4). **Não é um registro de execução.** Código de referência já integrado: `8cb1e23b0e83066e52d3f81dd7ef05ce82dfc93c` (PR #40). Issue #25 permanece aberta; smoke no CI aprovado, aceite externo pendente.

## 1. O que será comprovado

Transferir um backup criado na origem para uma instalação Linux nova, restaurar em PostgreSQL vazio, reproduzir os incidentes e verificar a trilha de auditoria. Depois, recriar o contêiner com o mesmo volume e confirmar persistência e novas escritas.

Uma VM instalada do zero é um sistema convidado separado. Se origem e VM estiverem no mesmo computador físico, registre **validação em VM no mesmo host**; isso não comprova resistência à perda do computador/disco. Para comprovar também independência física, execute a VM no outro computador/local e transfira o pacote. Não clone o disco/volume PostgreSQL da origem nem importe snapshot dela como evidência de restauração do backup.

Não é necessário instalar n8n, Grafana, Zabbix, frontend, IA real ou captura de pacotes para este aceite. Instalação/ativação systemd e atualização entre versões são ensaios complementares; não fazem parte deste roteiro principal.

## 2. Especificações da VM

[Provável] Dimensionamento proposto para os dados sintéticos desta sessão, não benchmark de produção.

| Item | Recomendado | Mínimo para este ensaio pequeno |
|---|---|---|
| Sistema | **Ubuntu Server 24.04 LTS, amd64**, instalação nova | Mesmo sistema, sem interface gráfica |
| CPU | **4 vCPU** | 2 vCPU |
| RAM | **8 GiB** | 4 GiB |
| Disco | **VDI60 GiB**, alocação dinâmica, SATA, ext4 | 40 GiB, desde que haja espaço para imagem/dados/dump |
| Rede | **NAT**, cabo conectado | NAT |
| Acesso | OpenSSH; redirecionamento host 127.0.0.1:2222→guest 22 | Console da VM também serve |
| Firmware | Padrão sugerido pelo VirtualBox para a ISO | Não mudar depois da instalação |
| Outros | 1 monitor, vídeo padrão; áudio/USB dispensáveis | Sem Guest Additions obrigatórias |

No computador hospedeiro, recomendo16 GiB de RAM e pelo menos100 GiB livres para uma VM de8 GiB, imagens e snapshots. Se tiver somente8 GiB, use VM de4 GiB e encerre programas pesados. Para duas VMs simultâneas de8 GiB, planeje24–32 GiB no host. O espaço real depende do backup: reserve, além do SO/imagens, pelo menos3 vezes o volume dos dados restaurados e margem para logs/snapshots.

Alternativa: **Debian 13 amd64**, Python 3.13 padrão; o projeto exige Python>=3.12 e foi validado no CI com 3.12. Verifique instalação das dependências antes do aceite. Debian 12/Python 3.11 e Ubuntu 22.04/Python 3.10 não são o caminho deste guia. Prefira Ubuntu 24.04 para reduzir diferença da versão Python do CI. Se quiser desktop, use Ubuntu Desktop 24.04 com 8 GiB e 80 GiB de disco; a interface gráfica é opcional.

Docker Engine funciona dentro do Linux convidado; não é necessário Docker Desktop na VM nem habilitar virtualização aninhada só para contêineres Linux. VT-x/AMD-V deve estar disponível ao VirtualBox no host. Se não conseguir criar uma VM 64 bits, resolver essa configuração antes de continuar.

## 3. Preparar antes de sair do local atual

- [ ] Copiar este guia e o roteiro de evidências [segunda-maquina.md](../specs/018-backup-restauracao/segunda-maquina.md).
- [ ] Levar o diretório de backup com **database.dump, audit.jsonl e manifest.json**.
- [ ] Levar a chave HMAC original em meio/canal separado do pacote. Não gerar outra chave no destino.
- [ ] Registrar SHA do código, versão principal PostgreSQL, contagens esperadas e pelo menos um ID fictício de incidente, quando disponível na origem.
- [ ] Confirmar acesso ao GitHub, registro Docker e repositório apt no destino, ou preparar as imagens/pacotes offline antes.

Pacote fictício já preparado nesta sessão (não versionado):

```text
C:\Users\Vinicius Lima\Desktop\sigma-mvp\test-results\recovery-final\bundle\
C:\Users\Vinicius Lima\Desktop\sigma-mvp\test-results\recovery-final\audit-key.txt
C:\Users\Vinicius Lima\Desktop\sigma-mvp\test-results\recovery-final\report.json
```

O bundle está dentro de test-results ignorado pelo Git: **clonar o repositório em outro local não o transfere**. Sua chave deve seguir separada. O dump contém hashes e dados; use transferência/armazenamento protegido e não publique esses arquivos em PR, Trello ou CI.

Esse pacote local foi criado com **PostgreSQL17**, não15. O CI usou15 em outro pacote. O script restore recusa versões principais diferentes. Consulte `postgres_major` no manifesto para cada pacote; não escolha a imagem apenas pelo número usado no CI.

As credenciais do usuário fictício `smoke.manager` eram efêmeras e não foram guardadas pelo runner. Após validar a reprodução do conteúdo, crie um gestor **novo** no destino para a consulta pela API. Isso não comprova login da identidade antiga; a reprodução dos hashes/identidades é conferida pelo inventário. Se usar outro backup e conhecer a senha original, poderá também testar essa conta.

## 4. Criar a VM no VirtualBox

1. Baixar ISO oficial: [Ubuntu 24.04](https://releases.ubuntu.com/24.04/) ou [Debian 13](https://www.debian.org/releases/trixie/debian-installer/); conferir checksum publicado pela distribuição.
2. Criar `sigma-restore-25`, Linux 64 bits, com os recursos da tabela. Instalar em **disco virtual novo**, sem conectar discos do host. Criar usuário administrativo próprio e habilitar OpenSSH.
3. Adaptador 1 em NAT. Em Avançado→Redirecionamento de portas, cadastrar TCP: IP do host 127.0.0.1, porta 2222, IP convidado vazio, porta 22. Não precisa de bridge nem de portas PostgreSQL abertas na LAN.
4. Instalar o SO, atualizar e reiniciar. Um snapshot opcional `SO-limpo` ajuda a repetir; snapshot não substitui backup e não é evidência deste aceite.
5. No host Windows, acessar `ssh -p2222 USUARIO_VM@127.0.0.1`. Se houver conflito em 2222, escolher outra porta do host e ajustar os comandos. Pode fazer tudo pelo console da VM.

## 5. Preparar Linux e Docker

Comandos seguintes são **dentro da VM**, no Bash, como usuário administrativo. Use um terminal reservado ao ensaio, sem `set -x` nem gravação de tela enquanto digitar chaves/senhas.

```bash
sudo apt update
sudo apt install -y git curl ca-certificates python3 python3-venv openssh-server
python3 -c 'import sys; assert sys.version_info >= (3,12); print(sys.version.split()[0])'
sudo systemctl enable --now ssh
```

Instalar Docker pelo [repositório oficial Ubuntu](https://docs.docker.com/engine/install/ubuntu/) ou [Debian](https://docs.docker.com/engine/install/debian/). Na VM nova sem pacotes Docker prévios:

```bash
DISTRO=$(. /etc/os-release; printf '%s' "$ID")
case "$DISTRO" in ubuntu|debian) ;; *) echo 'Distribuição fora deste roteiro'; exit 1;; esac
sudo install -m0755 -d /etc/apt/keyrings
sudo curl -fsSL "https://download.docker.com/linux/$DISTRO/gpg" -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
CODENAME=$(. /etc/os-release; printf '%s' "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
ARCH=$(dpkg --print-architecture)
printf 'Types: deb\nURIs: https://download.docker.com/linux/%s\nSuites: %s\nComponents: stable\nArchitectures: %s\nSigned-By: /etc/apt/keyrings/docker.asc\n' "$DISTRO" "$CODENAME" "$ARCH" | sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Sair da sessão e entrar novamente para aplicar o grupo. Esse grupo concede acesso administrativo ao Docker; use somente a conta autorizada do laboratório. Conferir:

```bash
docker version
docker compose version
free -h
df -h /
```

## 6. Obter o código e receber o pacote

```bash
umask 077
mkdir -p "$HOME/sigma-25/recebido" "$HOME/sigma-25/segredos" "$HOME/sigma-25/estado" "$HOME/sigma-25/evidencias"
chmod 700 "$HOME/sigma-25" "$HOME/sigma-25/segredos" "$HOME/sigma-25/recebido"
cd "$HOME/sigma-25"
git clone https://github.com/Solution-Explores/SigmaTI.git codigo
cd codigo
git checkout --detach 8cb1e23b0e83066e52d3f81dd7ef05ce82dfc93c
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

**Não executar install.sh nem alembic upgrade head no banco destino antes do restore.** O dump contém esquema e controle de migrações. Este roteiro usa só instalação de dependências nesse ponto.

Transferir `bundle/` para `~/sigma-25/recebido/bundle/` (por SCP/SFTP ou mídia protegida) e a chave, separadamente, para `~/sigma-25/segredos/audit-key.txt`. Pelo Windows, o formato é `scp -P2222 -r CAMINHO_BUNDLE USUARIO_VM@127.0.0.1:sigma-25/recebido/`. Não colocar a chave dentro do bundle, no histórico ou no repositório.

```bash
BASE="$HOME/sigma-25"
BUNDLE="$BASE/recebido/bundle"
chmod 700 "$BUNDLE"
chmod 600 "$BUNDLE"/* "$BASE/segredos/audit-key.txt"
export SIGMA_AUDIT_KEY="$(cat "$BASE/segredos/audit-key.txt")"
.venv/bin/python scripts/recovery.py verify --bundle "$BUNDLE" | tee "$BASE/evidencias/verificacao-pacote.json"
```

Deve retornar status ok. Em chave/checksum inválido, **parar** e recuperar o pacote correto. Não alterar manifesto nem recalcular HMAC para fazer passar.

## 7. Criar PostgreSQL vazio e restaurar

Ainda em `~/sigma-25/codigo`, no mesmo terminal:

```bash
MAJOR=$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["manifest"]["postgres_major"])' "$BUNDLE/manifest.json")
case "$MAJOR" in
  17) IMAGE='postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826' ;;
  15) IMAGE='postgres:15.19-alpine3.24@sha256:f7d23353e1b15400d22ebe31189f4d314b87a4c129cc400c8c2d8d4ca127bf81' ;;
  *) echo 'Versão fora das imagens deste ensaio; parar e planejar imagem compatível'; exit 1 ;;
esac
export POSTGRES_PASSWORD="$(.venv/bin/python -c 'import secrets; print(secrets.token_hex(24))')"
printf 'POSTGRES_USER=sigma_vm\nPOSTGRES_DB=sigma_vm\nPOSTGRES_PASSWORD=%s\n' "$POSTGRES_PASSWORD" > "$BASE/segredos/postgres.env"
chmod 600 "$BASE/segredos/postgres.env"
docker pull "$IMAGE"
docker volume create sigma25-destino-dados
docker run -d --name sigma25-destino --env-file "$BASE/segredos/postgres.env" \
  -p127.0.0.1:55432:5432 -v sigma25-destino-dados:/var/lib/postgresql/data "$IMAGE"
```

Usar esses nomes somente em VM nova, sem volume/contêiner homônimo. Se já existirem de outra tentativa, parar e conferir; não apagar automaticamente. Esperar `docker exec sigma25-destino pg_isready -h127.0.0.1 -Usigma_vm -dsigma_vm` retornar código 0 antes de continuar. Não iniciar API/coleta ainda.

```bash
set -o pipefail
bash scripts/restore.sh --container sigma25-destino --bundle "$BUNDLE" \
  --audit "$BASE/estado/audit-restaurado.jsonl" --quiesced \
  | tee "$BASE/evidencias/restauracao.json"
```

Esperado: saída0/status ok, mesma contagem de tabelas e de entradas do manifesto. O comando já compara fingerprints e contagens de **todas as tabelas públicas** e autentica a trilha. Em qualquer erro, guardar apenas a mensagem/resumo, manter destino offline e investigar. Não retomar em banco parcialmente restaurado nem usar `--clean` para contornar recusa.

## 8. Conferir incidentes e auditoria pela API

Primeiro registrar inventário restaurado, antes de criar o gestor novo:

```bash
export SIGMA_DATABASE_URL="postgresql+psycopg://sigma_vm:${POSTGRES_PASSWORD}@127.0.0.1:55432/sigma_vm"
export SIGMA_AUDIT_PATH="$BASE/estado/audit-restaurado.jsonl"
export SIGMA_JWT_SECRET="$(.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))')"
export SIGMA_CORS_ORIGINS='http://localhost:5173'
export SIGMA_COLLECTION_ENABLED=0
export PYTHON_DOTENV_DISABLED=1
export OPENROUTER_API_KEY='fake-only-restauracao-sem-ia'
export SIGMA_LLM_MODEL='test/model'
.venv/bin/python - <<'PY'
import os, json
from sigma_eng.audit_chain import AuditChain
from scripts.recovery import fingerprint
from pathlib import Path
base=Path.home()/"sigma-25"
chain=AuditChain(os.environ["SIGMA_AUDIT_PATH"], chave=os.environ["SIGMA_AUDIT_KEY"].encode())
assert chain.verificar()[0]
manifest=json.loads((base/"recebido/bundle/manifest.json").read_text())["manifest"]
assert fingerprint("sigma25-destino")==manifest["tables"]
report={"tables_equal":True,"audit_integrity":True,"audit_entries":len(chain)}
(base/"evidencias/conteudo-restaurado.json").write_text(json.dumps(report,indent=2))
PY
.venv/bin/python -m scripts.manage_identity create vm.validator gestor_ti
```

Escolher senha nova, de 12–128 caracteres, no prompt. Não alterar usuários antigos. O novo segredo JWT invalida tokens antigos; sessões previamente revogadas não devem ser reativadas. A coleta fica desligada para não sondar endereços restaurados. A chave de IA é fictícia: não testar `/api/alertas` neste aceite.

Iniciar a API em segundo plano e guardar seu PID neste terminal:

```bash
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --no-access-log > "$BASE/estado/api.log" 2>&1 &
API_PID=$!
```

Se a API encerrar, conferir api.log antes de continuar. Executar a consulta abaixo quando ela estiver pronta:

```bash
.venv/bin/python - <<'PY'
import getpass,json,urllib.request
from pathlib import Path
base="http://127.0.0.1:8000"
def call(path,data=None,token=None):
    headers={"Content-Type":"application/json"}
    if token:headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers=headers)
    with urllib.request.urlopen(req,timeout=15) as response:return json.load(response)
login=call("/api/auth/login",{"username":"vm.validator","password":getpass.getpass("Senha do gestor de teste: ")})
token=login["access_token"]
rows=call("/api/eng/incidentes",token=token)["incidentes"]
audit=call("/api/eng/auditoria/verificar",token=token)
assert audit["integra"]
report={"incident_count":len(rows),"incident_ids":sorted(r["id"] for r in rows),"audit_integrity":audit["integra"],"audit_entries":audit["entradas"]}
assert rows,"Pacote de aceite deve conter ao menos um incidente fictício"
out=Path.home()/"sigma-25/evidencias/api-restaurada.json"
out.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
PY
```

Se o terminal não aceitar senha em getpass com esse formato, salve o bloco Python em `~/sigma-25/consulta-api.py` e execute `.venv/bin/python ~/sigma-25/consulta-api.py` (senha lida do terminal). Nunca passar senha/token na linha de comando. Conferir o ID de referência da origem, quando registrado. O inventário completo já comprovou igualdade mesmo que o pacote antigo não tenha uma lista de IDs exportada.

## 9. Recriar o contêiner sem perder os dados

Copiar o resumo antes da recriação com `cp "$BASE/evidencias/api-restaurada.json" "$BASE/evidencias/api-antes-recriacao.json"`. Parar API com `kill "$API_PID"` e `wait "$API_PID"`; se wait retornar 143 após SIGTERM, confirmar encerramento antes de continuar. Guardar fingerprint de referência após o novo usuário/login:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path
from scripts.recovery import fingerprint
(Path.home()/"sigma-25/evidencias/antes-recriacao.json").write_text(json.dumps(fingerprint("sigma25-destino"),sort_keys=True))
PY
docker stop sigma25-destino
docker rm sigma25-destino
docker run -d --name sigma25-destino --env-file "$BASE/segredos/postgres.env" \
  -p127.0.0.1:55432:5432 -v sigma25-destino-dados:/var/lib/postgresql/data "$IMAGE"
```

Esperar pg_isready por TCP novamente. **Não remover o volume.** Depois:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path
from scripts.recovery import fingerprint
base=Path.home()/"sigma-25/evidencias"
assert fingerprint("sigma25-destino")==json.loads((base/"antes-recriacao.json").read_text())
(base/"recriacao.json").write_text(json.dumps({"all_tables_equal":True}))
PY
```

Reiniciar API como na etapa 8 e repetir a consulta. Depois comparar os resumos:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path
base=Path.home()/"sigma-25/evidencias"
a=json.loads((base/"api-antes-recriacao.json").read_text())
b=json.loads((base/"api-restaurada.json").read_text())
assert a["incident_ids"]==b["incident_ids"] and a["incident_count"]==b["incident_count"]
assert b["audit_integrity"] and b["audit_entries"]>=a["audit_entries"]
print("PASS: incidentes preservados e auditoria íntegra após recriação")
PY
```

Opcional complementar: criar uma aprovação fictícia via API e conferir novo evento/ID sem colisão, sem executar comandos/runbooks. Encerrar API ao terminar; deixar o volume preservado até revisar as evidências.

## 10. Evidências e condição de encerramento

Preencher [segunda-maquina.md](../specs/018-backup-restauracao/segunda-maquina.md) com:

- local/data(UTC−4), operador e identificação fictícia de origem/destino;
- computador físico diferente ou VM no mesmo host, declarado explicitamente;
- distro/versão, VirtualBox,4 vCPU/8 GiB/60 GiB efetivamente usados (ou a configuração real);
- SHA `8cb1e23...`, versão/digest PostgreSQL e formato do manifesto;
- código 0 do verify/restore, igualdade de tabelas e auditoria íntegra;
- IDs/contagem de incidentes na API e confirmação após recriar o contêiner;
- resultado final, falhas encontradas e limites.

Anexar apenas resumos JSON de `evidencias/` revisados, sem segredos/dados reais. Não publicar bundle, chave, postgres.env, JWT, senha ou logs brutos. Não usar o smoke em dois contêineres no destino como substituto da transferência/restauração acima.

**Encerrar a #25 somente após executar e revisar esse aceite**, marcar o primeiro critério e registrar o resultado na issue/Trello. Este documento não atesta que a VM foi criada ou que o teste externo passou. Se faltar evidência, manter a issue aberta.

## Fontes de preparação

- [VirtualBox 7.2 — redes NAT e encaminhamento](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html).
- [Docker Engine — Ubuntu](https://docs.docker.com/engine/install/ubuntu/) e [Debian](https://docs.docker.com/engine/install/debian/).
- [Python3 do Debian 13](https://packages.debian.org/trixie/python3).
- [Guia operacional do projeto](../operacao/backup-restauracao.md).

As quantidades de RAM/CPU/disco são recomendações deste planejamento. Não são mínimos oficiais das distribuições nem garantia de capacidade para dados hospitalares.
