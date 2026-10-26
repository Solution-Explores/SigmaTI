# Teste rapido (smoke) da demonstracao, pela API. Confere o que a API garante; o painel
# (5 abas, "Tempo real ativo", 12 min do Portal de testes) continua sendo conferido a olho.
#
# Uso (com a API da demo no ar, subir_demo.py):
#   .\docs\demo\smoke.ps1 -Senha '<senha impressa por subir_demo.py>'
# ou defina $env:SIGMA_DEMO_SENHA antes. Sai com codigo 1 se algum item falhar.
param([string]$Senha = $env:SIGMA_DEMO_SENHA)

if (-not $Senha) { Write-Host 'Informe -Senha ou defina SIGMA_DEMO_SENHA.' -ForegroundColor Red; exit 2 }
$env:SIGMA_DEMO_SENHA = $Senha
. "$PSScriptRoot\demo.ps1"

$resultados = New-Object System.Collections.ArrayList
function Add-Resultado([string]$Item, [bool]$Ok, [string]$Detalhe) {
    [void]$resultados.Add([pscustomobject]@{ Item = $Item; Resultado = $(if ($Ok) { 'PASS' } else { 'FAIL' }); Detalhe = $Detalhe })
}
function Get-Status($Bloco) {
    try { & $Bloco | Out-Null; 200 } catch { [int]$_.Exception.Response.StatusCode }
}

# a) Controle de acesso: o N1 recebe 403 e o gestor 200 em GET /api/usuarios.
try {
    $n1 = Get-Status { Invoke-Sigma 'browser.demo' Get '/api/usuarios' }
    $n = @((Invoke-Sigma 'browser.manager' Get '/api/usuarios').usuarios).Count
    Add-Resultado 'a) N1 recebe 403 e gestor 200' (($n1 -eq 403) -and ($n -eq 4)) "N1=$n1; gestor viu $n usuarios (esperado 4)"
} catch { Add-Resultado 'a) N1 recebe 403 e gestor 200' $false $_.Exception.Message }

# b) O painel responde e o gestor consegue entrar.
try {
    $tok = Get-SigmaToken 'browser.manager'
    $painel = (Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:5173/').StatusCode
    Add-Resultado 'b) painel no ar e login do gestor' ([bool]$tok -and $painel -eq 200) "painel HTTP $painel; token $(if ($tok) {'recebido'} else {'ausente'})"
} catch { Add-Resultado 'b) painel no ar e login do gestor' $false $_.Exception.Message }

# c) SLO: burn rate do Portal de testes (orcamento de 12 min, at_risk, alerta page).
try {
    $b = Get-SigmaBurnRate | ConvertFrom-Json
    $ok = ($b.orcamento.status -eq 'at_risk') -and ([math]::Abs($b.orcamento.restante_min - 12) -lt 0.5) -and ($b.alertas[0].acao -eq 'page')
    Add-Resultado 'c) burn rate: at_risk, 12 min, alerta page' $ok "status=$($b.orcamento.status); restante=$($b.orcamento.restante_min) min; acao=$($b.alertas[0].acao)"
} catch { Add-Resultado 'c) burn rate: at_risk, 12 min, alerta page' $false $_.Exception.Message }

# d) IA e LGPD: nome e CPF fictícios saem anonimizados antes do provedor (simulado).
try {
    $corpo = @{ equipamento = 'sw-uti-01'; ip_origem = '10.0.0.5'; descricao_erro = 'Paciente Maria Silva CPF 529.982.247-25 relatou falha no sw-uti-01' }
    $r = Invoke-Sigma 'browser.demo' Post '/api/alertas' $corpo
    $enviado = [string]$r.dados_enviados_nuvem
    $ok = $enviado.Contains('[NOME_REMOVIDO]') -and $enviado.Contains('[CPF_REMOVIDO]') -and -not $enviado.Contains('529.982.247-25') -and -not $enviado.Contains('Maria Silva') -and ([string]$r.diagnostico_ia).Contains('K10 simulado')
    Add-Resultado 'd) nome e CPF anonimizados; IA simulada' $ok $enviado
} catch { Add-Resultado 'd) nome e CPF anonimizados; IA simulada' $false $_.Exception.Message }

# e) Auditoria: a cadeia de sondas esta integra.
try {
    $a = Test-SigmaAuditoria
    Add-Resultado 'e) cadeia de auditoria integra' ($a.integra -eq $true) "integra=$($a.integra)"
} catch { Add-Resultado 'e) cadeia de auditoria integra' $false $_.Exception.Message }

$resultados | Format-Table -AutoSize -Wrap | Out-String | Write-Host
$falhas = @($resultados | Where-Object { $_.Resultado -eq 'FAIL' }).Count
if ($falhas -eq 0) { Write-Host 'SMOKE DA API: TUDO PASS.' -ForegroundColor Green } else { Write-Host "SMOKE DA API: $falhas item(ns) com FAIL." -ForegroundColor Red }
Write-Host 'Ainda a olho no painel: 5 abas e "Tempo real ativo" (gestor); "Portal de testes" com 12 min na aba Saude.'
exit $(if ($falhas -eq 0) { 0 } else { 1 })
