# Comandos de apoio da demonstração. Carregar no terminal da apresentação:
#   . .\docs\demo\demo.ps1
#   $env:SIGMA_DEMO_SENHA = '<senha impressa por subir_demo.py>'
# Todas as chamadas vão para a API local da demo (127.0.0.1:18000).
# Se o Ctrl+C deixar a porta 9099 presa (acontece no Windows): Stop-SigmaAlvoDemo.

$SigmaApi = 'http://127.0.0.1:18000'
# O início real da queda fica em arquivo, para valer também se Get-SigmaMetricas rodar em outra janela do PowerShell.
$SigmaQuedaArquivo = Join-Path ([System.IO.Path]::GetTempPath()) 'sigma_queda.txt'

function Get-SigmaToken([string]$Usuario) {
    $body = @{ username = $Usuario; password = $env:SIGMA_DEMO_SENHA } | ConvertTo-Json
    (Invoke-RestMethod -Method Post -Uri "$SigmaApi/api/auth/login" -ContentType 'application/json' -Body $body).access_token
}

function Invoke-Sigma([string]$Usuario, [string]$Metodo, [string]$Rota, $Corpo) {
    $p = @{ Method = $Metodo; Uri = "$SigmaApi$Rota"; Headers = @{ Authorization = "Bearer $(Get-SigmaToken $Usuario)" } }
    if ($null -ne $Corpo) {
        # No PowerShell 5.1 um corpo em texto sai em Windows-1252 e acento vira HTTP 400; por isso vão bytes UTF-8.
        $p.ContentType = 'application/json; charset=utf-8'
        $p.Body = [System.Text.Encoding]::UTF8.GetBytes((ConvertTo-Json -InputObject $Corpo -Depth 6))
    }
    Invoke-RestMethod @p
}

# Passo 2: suporte_n1 tenta listar usuários (só gestor_ti pode) e recebe 403.
function Show-Sigma403 {
    try { Invoke-Sigma 'browser.demo' Get '/api/usuarios' | Out-Null; 'ERRO: deveria ter recusado' }
    catch { "browser.demo (suporte_n1) -> GET /api/usuarios -> HTTP $([int]$_.Exception.Response.StatusCode)" }
    $n = @((Invoke-Sigma 'browser.manager' Get '/api/usuarios').usuarios).Count
    "browser.manager (gestor_ti) -> GET /api/usuarios -> HTTP 200 ($n usuários)"
}

# Passo 3: cadastra o alvo vigiado. Antes, em outro terminal:
#   python -m http.server 9099 --bind 127.0.0.1
# Depois de "Disponível" no painel, Ctrl+C nesse terminal derruba o serviço.
function New-SigmaAlvoDemo {
    Remove-Item -Path $SigmaQuedaArquivo -ErrorAction SilentlyContinue
    Invoke-Sigma 'browser.analyst' Post '/api/eng/alvos' @{ nome = 'Switch UTI'; host = '127.0.0.1'; porta = 9099; intervalo_s = 0.5; timeout_s = 0.3 }
}

# Encerra o http.server da porta 9099 quando o Ctrl+C o deixa órfão. Só encerra processo Python.
function Stop-SigmaAlvoDemo {
    $escuta = @(Get-NetTCPConnection -LocalPort 9099 -State Listen -ErrorAction SilentlyContinue)
    if ($escuta.Count -eq 0) { return 'Nada escutando na porta 9099.' }
    foreach ($c in $escuta) {
        $proc = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
        if ($proc -and $proc.ProcessName -like 'python*') { Stop-Process -Id $proc.Id -Force; "Encerrado: $($proc.ProcessName) (PID $($proc.Id))" }
        else { "Porta 9099 em uso por '$($proc.ProcessName)'; não encerrei." }
    }
}

# Chamar logo depois do Ctrl+C: registra o início real da falha para o MTTD.
function Set-SigmaQueda {
    $agora = (Get-Date).ToUniversalTime().ToString('o')
    Set-Content -Path $SigmaQuedaArquivo -Value $agora -Encoding ASCII
    "Queda registrada: $agora"
}

# Passo 3 (MTTD): o painel não mostra MTTD porque o incidente não guarda início real.
# Calcula MTTD, MTTA e MTTR do último incidente com o início registrado em Set-SigmaQueda.
function Get-SigmaMetricas {
    if (-not (Test-Path $SigmaQuedaArquivo)) { throw 'Sem início de queda registrado: rode Set-SigmaQueda logo depois do Ctrl+C.' }
    $queda = (Get-Content -Path $SigmaQuedaArquivo -Raw).Trim()
    # A API devolve { incidentes: [...] }, do mais recente para o mais antigo.
    # Se o serviço ainda estiver fora, resolver abre outro incidente na hora; por isso usamos o último já resolvido.
    $inc = @((Invoke-Sigma 'browser.analyst' Get '/api/eng/incidentes').incidentes) |
        Where-Object { $_.resolvido_em } | Select-Object -First 1
    $inc | Format-List | Out-String | Write-Host
    $corpo = @(@{ id = "$($inc.id)"; severidade = 'P2'; inicio_real = $queda
        detectado_em = $inc.detectado_em; reconhecido_em = $inc.reconhecido_em; resolvido_em = $inc.resolvido_em })
    Invoke-Sigma 'browser.analyst' Post '/api/eng/incidentes/metricas' $corpo
}

# Passo 4: burn rate do "Portal de testes" (SLO 95 % em 1 dia; a última hora falhou).
function Get-SigmaBurnRate {
    $agora = (Get-Date).ToUniversalTime()
    Invoke-Sigma 'browser.analyst' Post '/api/eng/slo/avaliar' @{ alvo_pct = 95; janela_dias = 1
        indisponibilidades = @(@{ inicio = $agora.AddHours(-1).ToString('o'); fim = $agora.ToString('o') }) } |
        ConvertTo-Json -Depth 6
}

# Passo 5: verificação da cadeia de auditoria (gestor_ti).
function Test-SigmaAuditoria { Invoke-Sigma 'browser.manager' Get '/api/eng/auditoria/verificar' }
