# Relatório do Ensaio Independente da Demonstração (Ponto 2 do Guia)

**Data do Ensaio:** 25/10/2026  
**Operador:** Iohan  
**SHA Base Utilizado:** `75b1874ee5f83f55ab12837249a9c701fd67cef1` (`origin/develop`)  
**Ambiente de Execução:** Windows 11 Pro 64-bit, Python 3.14.6, Node.js v24.22.0, npm 11.19.1, Docker Desktop (PostgreSQL 15.19 Alpine), PowerShell 5.1  

---

## 1. Tabela de Execução por Etapa

| Etapa | Descrição | Resultado | O que foi feito / Ajuste necessário |
|---|---|---|---|
| **Prep.** | Subida de banco, API, painel e smoke | **Passou com ajuste** | Ajustadas variáveis do `.env` para o Compose; extraída pasta `docs/demo` da branch `feature/trail-fase1` (inexistente na `develop`). Smoke `Show-Sigma403` aprovado (403 N1 / 200 gestor). |
| **1** | Arquitetura (1 min) | **Passou** | Verificado fluxo alvo → sonda → PG → detector → SSE → painel. Execução 100% local com IA simulada. |
| **2** | Perfis de acesso (2 min) | **Passou** | `browser.demo` vê estritamente 2 abas ("Saúde dos serviços" e "Diagnóstico"). `browser.manager` vê as 5 abas. `Show-Sigma403` confirmou barramento na API. |
| **3** | Coleta ao vivo (4 min) | **Passou com ajuste** | Cadastrado "Switch UTI" (9099). Ficou "Disponível". Derrubada da porta gerou incidentes de disponibilidade e latência. Resolvido incidente de `availability`. `Get-SigmaMetricas` calculou MTTA e MTTR (ajustado escopo do timestamp para não virar nulo). |
| **4** | SLO (2 min) | **Passou** | "Portal de testes" exibiu 25h de histórico, estado "Disponível", **12 min** de orçamento restante. **Confirmado:** a expressão "em risco" não aparece no painel. `Get-SigmaBurnRate` devolveu status `at_risk` e alerta `page`. |
| **5** | Governança (2 min) | **Passou com ajuste** | "Nova solicitação" inicia recolhida (`<details>`). Autor não pode aprovar próprio pedido (HTTP 409). Pedido aprovado pelo `browser.reviewer` (necessário evitar diacríticos/acentos no `Invoke-RestMethod` no PS 5.1). Cadeia íntegra (`Test-SigmaAuditoria` = 23 entradas, `integra: true`). |
| **6** | IA e LGPD (2 min) | **Passou** | Enviado alerta com nome de paciente, CPF e switch. Dados enviados à nuvem sanitizados para `[NOME_REMOVIDO] [CPF_REMOVIDO] [SWITCH_REDE]`. Diagnóstico retornado: `"Diagnóstico K10 simulado"`. Falha fechada validada. |
| **7** | Resultados e Limites (2 min) | **Passou** | Roteiro repassa métricas de laboratório, p95 de entrega SSE < 0,5 s, ausência de MTTD/burn rate na interface web e isolamento por schema efêmero. |

---

## 2. Tropeços Encontrados (Para Correção pelo Vinícius)

### Tropeço 1: Arquivos da demo ausentes no checkout puro da `develop`
- **Problema:** O roteiro instrui a executar `python ..\sigma-develop\docs\demo\subir_demo.py` e `. ..\sigma-develop\docs\demo\demo.ps1` a partir da `develop` (`75b1874`). No entanto, na branch `develop`, o diretório `docs/demo/` **não existe** (a `develop` ainda usa `doc/`). Esses arquivos só foram criados na branch `origin/feature/trail-fase1`.
- **Impacto:** Um operador clonando a `develop` do zero não encontra nem o `subir_demo.py` nem o `demo.ps1`.
- **Ajuste feito no ensaio:** Extraída a pasta `docs/` pontualmente da branch `feature/trail-fase1` (`git checkout origin/feature/trail-fase1 -- docs`).
- **Recomendação:** Incorporar `docs/demo/` ou mergear a documentação de apoio na `develop` antes do congelamento de segunda-feira.

---

### Tropeço 2: Docker Compose bloqueia subida do `db` se `.env` tiver campos vazios
- **Problema:** Ao rodar `docker compose -f docker-compose.yml -f deploy/db-host.yml up -d db`, o Compose valida todas as variáveis do arquivo antes de subir qualquer serviço. Como o `.env.example` copiado para `.env` tinha as variáveis de monitoramento vazias (`ZABBIX_DB_USER`, `GF_SECURITY_ADMIN_USER`), o comando falhou com:
  `required variable ZABBIX_DB_USER is missing a value`.
- **Impacto:** O contêiner do banco não sobe mesmo pedindo apenas o serviço `db`.
- **Ajuste feito no ensaio:** Preenchidas as 6 credenciais no `.env`.
- **Recomendação:** Incluir no guia de preparação o lembrete explícito de preencher as 6 credenciais no `.env` antes do `docker compose`.

---

### Tropeço 3: `$script:SigmaQueda` volátil quebra `Get-SigmaMetricas`
- **Problema:** Em `docs/demo/demo.ps1`, a função `Set-SigmaQueda` grava a data em `$script:SigmaQueda`. Se o operador rodar `Set-SigmaQueda` e `Get-SigmaMetricas` em blocos ou janelas diferentes de PowerShell, `$script:SigmaQueda` fica nulo. Ao tentar executar `.ToString('o')`, o script lança `InvokeMethodOnNull` e envia um JSON inválido para a API, resultando em HTTP 422 ("Dados da requisição inválidos.").
- **Ajuste feito no ensaio:** Executar os comandos garantidamente na mesma sessão de terminal.
- **Recomendação:** Alterar `demo.ps1` para usar `$global:SigmaQueda` ou salvar o timestamp em `$env:TEMP/sigma_queda.txt`.

---

### Tropeço 4: Caracteres acentuados no PowerShell 5.1 causam HTTP 400 na API
- **Problema:** No PowerShell 5.1 (Windows), `Invoke-RestMethod` envia o payload no charset padrão ANSI (Windows-1252) quando `-ContentType 'application/json'` é usado sem `charset=utf-8`. Se a justificativa contiver acentos (ex.: `manutenção`), o parser UTF-8 do FastAPI falha e retorna HTTP 400 ("Requisição inválida.").
- **Ajuste feito no ensaio:** Enviar justificativa sem caracteres acentuados pelo terminal (`Janela aprovada`) ou via navegador.
- **Recomendação:** No `demo.ps1`, alterar a linha do `Invoke-Sigma` para:
  `$p.ContentType = 'application/json; charset=utf-8'`.

---

### Tropeço 5: Processo `http.server` pode ficar órfão no Windows após encerramento
- **Problema:** Ao encerrar o terminal D ou enviar Ctrl+C para derrubar o serviço de teste na porta 9099, o processo Python pode permanecer rodando em segundo plano no Windows, mantendo a porta 9099 em escuta e impedindo a detecção de queda pelo scheduler.
- **Ajuste feito no ensaio:** Matar o processo pelo PID associado à porta (`Stop-Process -Id (Get-NetTCPConnection -LocalPort 9099).OwningProcess -Force`).
- **Recomendação:** Adicionar uma função de apoio no `demo.ps1` (ex.: `Stop-SigmaAlvoDemo`).

---

## 3. Verificação dos Pontos de Atenção de 23/10

1. **Dois incidentes no mesmo alvo (`latency` e `availability`):**
   - **Confirmado.** Ao restabelecer o serviço, o scheduler registra o atraso gerando incidente de latência antes do restabelecimento completo. No painel, o incidente de `availability` deve ser o selecionado para reconhecimento/resolução.
2. **"Nova solicitação" inicia recolhida:**
   - **Confirmado.** A tag `<details className="request-details">` inicia fechada por padrão.
3. **F5 recarrega e derruba a sessão:**
   - **Confirmado.** O estado de autenticação reside unicamente em `useState(null)` no React; qualquer recarregamento da página força o retorno ao formulário de login.
4. **Expiração do pedido pré-carregado em 15 minutos:**
   - **Confirmado.** A requisição sintética gerada na subida expira após 900 s e sai da lista de pendências da API.
5. **Janela normal + anônima com duas sessões simultâneas:**
   - **Confirmado.** Como o token não é gravado em `localStorage` compartilhado, abas/janelas independentes operam simultaneamente com perfis distintos (`analyst` e `reviewer`) sem colisão.
6. **Aba Saúde não exibe "em risco":**
   - **Confirmado.** "Portal de testes" aparece como "Disponível", com "Até 12 min" de orçamento restante; o status `at_risk` é puramente interno da API.
