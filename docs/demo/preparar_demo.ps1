# Prepara a demonstracao em um comando (substitui os terminais A e B do checklist de terca):
# confere o SHA, liga o Docker e o banco, sobe a API com dados ficticios e o painel, e roda o smoke.
#
#   .\docs\demo\preparar_demo.ps1
#
# Abre duas janelas do PowerShell (API e painel); feche-as com Ctrl+C ao terminar. O Ctrl+C na janela
# da API apaga o schema da demo. O terminal C (comandos de apoio) e o D (http.server) continuam manuais.
param(
    [string]$Repo = 'C:\Users\Vinicius Lima\Desktop\sigmati-develop',
    [string]$Docs = 'C:\Users\Vinicius Lima\Desktop\sigma-develop',
    [string]$ShaEsperado = '7851da6',
    [switch]$SemSmoke
)
$ErrorActionPreference = 'Stop'
function Passo([string]$t) { Write-Host "==> $t" -ForegroundColor Cyan }
function Esperar([scriptblock]$Cond, [int]$Segundos, [string]$Msg) {
    $fim = (Get-Date).AddSeconds($Segundos)
    while ((Get-Date) -lt $fim) { if (& $Cond) { return }; Start-Sleep 2 }
    throw "Tempo esgotado: $Msg"
}
function PortaAberta([int]$p) { (Test-NetConnection 127.0.0.1 -Port $p -WarningAction SilentlyContinue).TcpTestSucceeded }
# No PowerShell 5.1, stderr de comando nativo vira erro fatal com 'Stop'; por isso comandos nativos rodam sem ele.
function Nativo([scriptblock]$Bloco) {
    $antes = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { & $Bloco 2>&1 | ForEach-Object { "$_" } | Out-Host } finally { $ErrorActionPreference = $antes }
    $global:LASTEXITCODE
}
function DockerPronto { $antes = $ErrorActionPreference; $ErrorActionPreference = 'Continue'; try { docker info *> $null; $global:LASTEXITCODE -eq 0 } finally { $ErrorActionPreference = $antes } }

Passo "SHA em $Repo"
$head = (git -C $Repo log --oneline -1)
Write-Host $head
if (-not $head.StartsWith($ShaEsperado)) { throw "SHA diferente do congelado ($ShaEsperado). Nao continue sem falar com o Vinicius." }
if (git -C $Repo status --porcelain --untracked-files=no) { Write-Warning 'Ha arquivos rastreados alterados no worktree.' }

Passo 'Docker'
if (-not (DockerPronto)) {
    $exe = "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe"
    if (-not (Test-Path $exe)) { throw 'Docker Desktop nao encontrado; abra-o manualmente.' }
    Start-Process $exe
    Esperar { DockerPronto } 240 'Docker Desktop nao ficou pronto'
}

Passo 'Banco (PostgreSQL em loopback)'
Push-Location $Repo
try { $rc = Nativo { docker compose -f docker-compose.yml -f deploy/db-host.yml up -d db }; if ($rc -ne 0) { throw "docker compose saiu com $rc" } } finally { Pop-Location }
Esperar { PortaAberta 5432 } 120 'PostgreSQL nao respondeu na porta 5432'
Start-Sleep 5

Passo 'Portas livres'
foreach ($p in 18000, 5173, 9099) { if (PortaAberta $p) { throw "A porta $p ja esta em uso. Encerre o processo antigo da demo e rode de novo." } }

Passo 'API com dados ficticios (janela nova)'
$e = @{}
Get-Content "$Repo\.env" | ForEach-Object { if ($_ -match '^\s*(POSTGRES_USER|POSTGRES_PASSWORD|POSTGRES_DB)=(.*)$') { $e[$matches[1]] = $matches[2].Trim().Trim('"') } }
$env:SIGMA_TEST_DATABASE_URL = "postgresql+psycopg://$($e['POSTGRES_USER']):$($e['POSTGRES_PASSWORD'])@127.0.0.1:5432/$($e['POSTGRES_DB'])"
$env:SIGMA_REPO = $Repo
$log = Join-Path $env:TEMP 'sigma-demo-api.log'
Remove-Item $log -ErrorAction SilentlyContinue
$cmdApi = "Set-Location '$Repo'; & '$Repo\.venv\Scripts\python.exe' -u '$Docs\docs\demo\subir_demo.py' 2>&1 | Tee-Object -FilePath '$log'"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $cmdApi | Out-Null
Esperar { (Test-Path $log) -and (Select-String -Path $log -Pattern 'Senha comum' -Quiet) } 180 'a API nao imprimiu a senha'
$senha = ((Select-String -Path $log -Pattern 'Senha comum: (.+)$').Matches[0].Groups[1].Value).Trim()
Esperar { PortaAberta 18000 } 60 'API nao abriu a porta 18000'

Passo 'Painel (janela nova)'
$cmdVite = "Set-Location '$Repo\sigma-frontend'; `$env:VITE_API_URL='http://127.0.0.1:18000'; npx vite --host 127.0.0.1 --port 5173"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $cmdVite | Out-Null
Esperar { PortaAberta 5173 } 120 'painel nao abriu a porta 5173'

$env:SIGMA_DEMO_SENHA = $senha
Write-Host ''
Write-Host "Demo no ar. API http://127.0.0.1:18000 | painel http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "Senha comum dos 4 usuarios: $senha"
Write-Host "Terminal C: . '$Docs\docs\demo\demo.ps1'; `$env:SIGMA_DEMO_SENHA = '$senha'"
Write-Host 'Terminal D (deixe digitado, sem executar): python -m http.server 9099 --bind 127.0.0.1'
Write-Host 'Pedidos de aprovacao expiram em 15 min: recrie os dados no maximo 10 min antes da etapa 5.'

if (-not $SemSmoke) {
    Passo 'Smoke pela API'
    & "$Docs\docs\demo\smoke.ps1" -Senha $senha
}
