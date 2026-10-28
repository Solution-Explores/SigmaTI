# Roteiro da demonstração de 27/10/2026

Base: [plano da demonstração](plano-demonstracao-2026-10-27.md). Código: `develop`, no SHA congelado na segunda, 26/10, às 18h (hoje `7851da6`, com #43, #44 e #47 integrados; o #47 entrou em 26/10 e só alterou o teste da sonda. Os ensaios de 22 e 23/10 foram feitos em `75b1874`).

> **Situação:** Ensaio 1 feito em 22/10, à noite, no Windows, na `develop@75b1874`. Os passos de API (2 a 6) rodaram pelos comandos de apoio em [demo/](demo/); a interface do painel foi coberta só pelo `validate_panel.py` (4/4), não por um ensaio manual no navegador.
> Resultado: os dois itens ⚠ foram confirmados e o `demo.ps1` foi corrigido (veja "Achados do Ensaio 1").
>
> **Ensaio manual do painel feito em 23/10, entre 19h e 20h (UTC−4), no navegador embutido do Claude, na mesma `develop@75b1874`:** etapas 2 a 6 percorridas no painel, com `browser.analyst`, `browser.reviewer` e `browser.manager` (veja "Achados do ensaio manual do painel").

### Achados do Ensaio 1
- `/api/eng/incidentes` devolve `{ "incidentes": [...] }`, não uma lista. `Get-SigmaMetricas` e `Show-Sigma403` foram corrigidos (a contagem de usuários agora mostra 4).
- **Resolver com o serviço ainda fora abre outro incidente na hora.** Suba de novo o `http.server` no terminal D antes de clicar em **Resolver incidente**. `Get-SigmaMetricas` usa o último incidente já resolvido.
- Medido: incidente apareceu 0,7 s após a queda; MTTD 0,45 s com a hora real da queda; MTTA 29 s e MTTR 29 s (tempos do ensaio).
- **Os pedidos de aprovação expiram em 15 minutos** (`expira_em`). Suba a demo no máximo 10 min antes da etapa 5, ou o pedido pré-carregado "Revisar mudança sintética" já terá expirado.
- Anonimização confirmada: `Equipamento: [SWITCH_REDE] | Erro: [NOME_REMOVIDO] [CPF_REMOVIDO] relatou falha no [SWITCH_REDE]` e diagnóstico "Diagnóstico K10 simulado".
- No PowerShell 5.1, acentos de respostas JSON saem trocados no terminal (`DiagnÃ³stico`). É só exibição; o painel mostra certo.
- Quatro olhos: o solicitante recebe HTTP 409 ao decidir; o revisor aprova. Auditoria: `integra: true`, 42 entradas após o ensaio.

### Achados do ensaio manual do painel (23/10)
- Funcionou no navegador, sem recarregar a página: o incidente do "Switch UTI" apareceu 0,7 s depois da queda; **Reconhecer** e **Resolver incidente** atualizaram a tela. No painel: MTTA 17,07 s e MTTR 27,68 s. Pela API (`Get-SigmaMetricas`): MTTD 0,67 s, MTTA 17,07 s, MTTR 27,68 s. `Get-SigmaBurnRate`: `at_risk`, 12 min restantes, alerta `page` (burn 20,0 na janela longa).
- **Subir o serviço de novo pode abrir um incidente extra de latência no mesmo alvo.** Aconteceu uma vez no ensaio de 23/10 (P3, `latency`, logo depois do serviço voltar); a causa não foi confirmada e o ensaio de 22/10 não o registrou. Quando aparece, a lista tem dois incidentes "Switch UTI" e o mais recente (latência) fica em primeiro. **Leia o tipo na linha e resolva o de `availability`**, qualquer que seja a posição. Se quiser a lista limpa, reconheça o de latência também.
- A lista de incidentes se redesenha quando chegam eventos: se o clique falhar com "elemento removido", clique de novo olhando a linha certa.
- **Aprovações:** "Nova solicitação" começa recolhida; clique no título para abrir o formulário. O revisor vê os dois pedidos (o pré-carregado e o novo) com **Aprovar** liberado. Ao aprovar, a tela mostra "Solicitação aprovada." e recarrega a lista.
- **Auditoria** (`browser.manager`): "Integridade consistente · 11 registros", com `approvals.updated` do revisor, `approvals.created` do analista, `incident.resolve`, `incident.ack`, `incident.created` e `target.created` nas primeiras linhas.
- **Diagnóstico** (`browser.manager`): o quadro "Dados enviados à IA" mostra `Equipamento: [SWITCH_REDE] | Erro: [NOME_REMOVIDO] [CPF_REMOVIDO] relatou falha no [SWITCH_REDE]. Forneça um diagnóstico de rede curto e direto.` e a resposta "Diagnóstico K10 simulado". Fecha a pendência da etapa 6 ("a tela do painel não foi conferida à mão").
- **Recarregar a página (F5) encerra a sessão** e volta ao login. Não recarregue durante a demonstração.
- **N1 conferido à mão (23/10):** `browser.demo` vê só Saúde e Diagnóstico, com "Tempo real ativo".
- **Etapa 4:** o painel mostra "Disponível" e 12 min de orçamento para o "Portal de testes", sem a palavra "em risco" (ver etapa 4).
- Não conferido à mão: a janela anônima com duas sessões em navegador real; o ensaio usou duas abas do navegador embutido.

### Achados do Ensaio 2 (26/10)
Feito às 9h14–9h20 (UTC−4) no navegador embutido, na `develop@7851da6` (SHA congelado), com Docker Desktop e `sigma-db`; um painel por aba (analista, revisor e gestor ao mesmo tempo). **Etapas 2 a 6 passaram**, sem ajuste no texto.
- Perfis: `browser.demo` vê só Saúde e Diagnóstico; `Show-Sigma403` deu 403 para o N1 e 200 para o gestor (4 usuários); o gestor vê as cinco abas, com "Tempo real ativo".
- Coleta: o incidente de disponibilidade do "Switch UTI" apareceu na hora, sem recarregar (um marcador na aba sobreviveu). MTTA 15,06 s e MTTR 29,03 s no painel; `Get-SigmaMetricas`: **MTTD 0,26 s**.
- SLO: "Portal de testes" com 12 min restantes; `Get-SigmaBurnRate`: `at_risk`, alerta `page`, burn 20,0.
- Governança: o pedido do analista aparece com "Você solicitou esta ação"; o revisor aprovou com justificativa ("Solicitação aprovada."); a Auditoria mostrou "Integridade consistente · 13 registros", com `approvals.updated` e `approvals.created`.
- IA: `Equipamento: [SWITCH_REDE] | Erro: [NOME_REMOVIDO] [CPF_REMOVIDO] relatou falha no [SWITCH_REDE]` e "Diagnóstico K10 simulado".
- **Incidente extra de latência confirmado de novo:** 34 s depois da queda, logo depois de o serviço voltar, o agendador abriu mais um incidente (`incident.created`, 9h16:22). É a segunda vez que aparece (23/10 e 26/10); continua valendo a regra "leia o tipo na linha e resolva o de `availability`".
- Antes mesmo da queda a lista já tinha dois incidentes da própria demo: disponibilidade do "Portal de testes" (na subida) e latência do "Coletor SSE de teste" (cerca de 1 min depois). Com o "Switch UTI", são três linhas.
- Dois pedidos de aprovação ficam na lista (o pré-carregado e o novo). O pré-carregado expira 15 min depois da subida.

### Achados do Ensaio 3 (27/10, à noite)
Feito das 20h33 às 20h39 (UTC−4) por Claude, a pedido do Vinícius, na `develop@7851da6` (SHA congelado). O Docker Desktop estava desligado e foi ligado pelo `docs/demo/preparar_demo.ps1`, que subiu o banco `sigma-db`, a API e o painel. O painel foi percorrido no navegador embutido, uma aba por perfil (N1 antes; depois analista, revisor e gestor ao mesmo tempo). **Etapas 2 a 6 passaram**, sem ajuste no texto. É um ensaio no SHA congelado, depois do horário marcado para a apresentação; não é o registro da apresentação.
- **Smoke** (`smoke.ps1`): 5 de 5 PASS. N1 recebeu 403 e o gestor viu 4 usuários; painel HTTP 200 com login do gestor; `at_risk`, 12,0 min e alerta `page`; nome e CPF anonimizados; auditoria `integra=True`.
- Perfis: `browser.demo` viu só Saúde e Diagnóstico; `Show-Sigma403` deu 403 para o N1 e 200 para o gestor (4 usuários); o gestor viu as cinco abas, com "Tempo real ativo".
- Coleta: o "Switch UTI" apareceu como Disponível sem recarregar. Depois da queda (`Stop-SigmaAlvoDemo` e `Set-SigmaQueda`, 20h36:04), o incidente de disponibilidade apareceu na hora. No painel: MTTA 14,56 s e MTTR 28,63 s. `Get-SigmaMetricas`, rodado em outro processo do PowerShell: **MTTD 0,42 s**, MTTA 14,56 s e MTTR 28,63 s.
- SLO: "Portal de testes" Disponível, com 12 min restantes e meta de 95 % em 1 dia, sem a palavra "em risco". `Get-SigmaBurnRate`: `at_risk`, alerta `page`, burn 20,0 na janela longa.
- Governança: "Nova solicitação" começou recolhida. O pedido do analista mostrou "Você solicitou esta ação. Outro integrante precisa decidir."; o revisor aprovou com justificativa ("Solicitação aprovada."). A Auditoria mostrou "Integridade consistente · 18 registros", e `Test-SigmaAuditoria` deu `integra: true` com 19 entradas (a diferença de 1 não foi investigada).
- IA: `Equipamento: [SWITCH_REDE] | Erro: [NOME_REMOVIDO] [CPF_REMOVIDO] relatou falha no [SWITCH_REDE]` e "Diagnóstico K10 simulado".
- **O incidente extra de latência não apareceu desta vez.** Da volta do serviço (cerca de 20h36) até o fim do ensaio, a lista ficou com três incidentes: o do Switch UTI, resolvido, e os dois da própria demo, abertos. Ele tinha aparecido em 23/10 e 26/10 e não em 22/10; a regra "leia o tipo na linha e resolva o de `availability`" continua valendo.
- As correções do `demo.ps1` de 27/10 foram usadas na prática: `Stop-SigmaAlvoDemo` (duas vezes) e `Get-SigmaMetricas` em outra janela do PowerShell, lendo a queda de `%TEMP%\sigma_queda.txt`. A correção do UTF-8 não foi exercitada pela API: o pedido com acento foi digitado no navegador.
- Não conferido: a janela anônima de um navegador real (as sessões foram abas do navegador embutido, como no Ensaio 2), a gravação de contingência e as etapas 1 e 7 (fala e slides).

## Preparação (terça às 16h, cerca de 10 min; checklist em [demo/checklist-terca.md](demo/checklist-terca.md))

Faça tudo na raiz do worktree da `develop` (`C:\Users\Vinicius Lima\Desktop\sigmati-develop`).

1. **Banco.** Abra o Docker Desktop e suba o PostgreSQL publicado só em loopback:
   ```powershell
   docker compose -f docker-compose.yml -f deploy/db-host.yml up -d db
   $env:SIGMA_TEST_DATABASE_URL = 'postgresql+psycopg://<usuario>:<senha>@127.0.0.1:5432/sigmadb'
   ```
2. **Terminal A: API com dados fictícios.**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python ..\sigma-develop\docs\demo\subir_demo.py
   ```
   O script imprime a senha comum dos quatro usuários e deixa a API em `http://127.0.0.1:18000`. Ctrl+C encerra a API e apaga o schema da demo.
3. **Terminal B: painel.**
   ```powershell
   cd sigma-frontend; $env:VITE_API_URL = 'http://127.0.0.1:18000'
   npx vite --host 127.0.0.1 --port 5173
   ```
4. **Terminal C: comandos de apoio.**
   ```powershell
   . ..\sigma-develop\docs\demo\demo.ps1
   $env:SIGMA_DEMO_SENHA = '<senha impressa no terminal A>'
   ```
5. **Terminal D:** deixe pronto, sem executar, o comando `python -m http.server 9099 --bind 127.0.0.1`.
6. **Navegador:** abra duas janelas em `http://127.0.0.1:5173`. Use uma janela normal e uma anônima, para ter duas sessões ao mesmo tempo.
7. **Smoke.** Rode `Show-Sigma403` no terminal C. Ele deve mostrar 403 e depois 200. Se falhar, mude para a gravação de contingência.

### Usuários

| Usuário | Perfil | Uso na demo |
|---|---|---|
| `browser.demo` | `suporte_n1` | Visão restrita e o 403 |
| `browser.analyst` | `analista_redes` | Coleta, incidentes e pedido de aprovação |
| `browser.reviewer` | `analista_redes` | Segundo par de olhos na aprovação |
| `browser.manager` | `gestor_ti` | Visão completa e auditoria |

## Roteiro (cerca de 15 min)

### 1. Arquitetura (1 min)
- Mostre o fluxo: alvo, sonda, PostgreSQL, detector, SSE e painel.
- Diga que tudo roda localmente, com dados fictícios e provedor de IA simulado.

### 2. Perfis de acesso (2 min)
1. Entre como `browser.demo`. Mostre que o perfil N1 só vê as abas Saúde e Diagnóstico.
2. Saia e entre como `browser.manager`. Mostre as cinco abas.
3. No terminal C, rode `Show-Sigma403`:
   - o N1 recebe **HTTP 403** em `GET /api/usuarios`;
   - o gestor recebe 200.
4. Fala de apoio: "o painel esconde, mas quem garante é a API."

### 3. Coleta ao vivo (4 min)
1. No terminal D, suba o serviço de teste: `python -m http.server 9099 --bind 127.0.0.1`.
2. Faça login como `browser.analyst`. No terminal C, rode `New-SigmaAlvoDemo`, que cadastra o alvo "Switch UTI".
3. Na aba Saúde, espere o alvo ficar **Disponível**.
4. Abra a aba Incidentes. Mostre o indicador "Tempo real ativo".
5. **Ctrl+C no terminal D** e, logo em seguida, `Set-SigmaQueda` no terminal C. Se a porta 9099 ficar presa depois do Ctrl+C (acontece no Windows), `Stop-SigmaAlvoDemo` encerra o processo.
6. O incidente aparece **sem recarregar a página**, em até cerca de 5 s.
7. Clique em **Reconhecer**, depois em **Resolver incidente**.
8. Mostre os cards de MTTA e MTTR: média, mediana, p95 e n.
9. **MTTD:** o painel mostra "Sem início real de falha registrado", porque o incidente não guarda a hora real da queda. Rode `Get-SigmaMetricas`, que calcula MTTD, MTTA e MTTR com a hora registrada no passo 5 (ela fica em `%TEMP%\sigma_queda.txt`, então o comando também funciona em outra janela do PowerShell). Antes de **Resolver incidente**, suba o serviço de novo no terminal D (veja "Achados do Ensaio 1").

### 4. SLO (2 min)
1. Na aba Saúde, mostre o alvo **Portal de testes**:
   - SLO de 95 % em 1 dia;
   - 25 h de histórico, com a última hora em falha;
   - estado "Disponível" (a última medição está boa), com **12 min** de orçamento restante e a data da projeção de esgotamento. A palavra "em risco" não aparece no painel; o status `at_risk` vem da API e é mostrado no `Get-SigmaBurnRate`;
   - projeção de esgotamento.
2. No terminal C, rode `Get-SigmaBurnRate`. A resposta traz o orçamento e os alertas de burn rate calculados pela API. O painel ainda não exibe burn rate.

### 5. Governança (2 min)
1. Na aba Aprovações, como `browser.analyst`, crie um pedido. Os botões de decisão ficam bloqueados para quem pediu.
2. Na janela anônima, entre como `browser.reviewer` e **aprove** com uma justificativa. Há também o pedido pré-carregado "Revisar mudança sintética".
3. Entre como `browser.manager` e abra a aba Auditoria. Mostre:
   - "Integridade consistente · N registros";
   - os eventos recentes.
4. Opcional: rode `Test-SigmaAuditoria` para mostrar `integra: true`.
5. Explique que a cadeia HMAC cobre as sondagens e que os eventos operacionais ficam em registro próprio.

### 6. IA e LGPD (2 min)
1. Na aba Diagnóstico, envie:
   `Paciente Maria Silva CPF 529.982.247-25 relatou falha no sw-uti-01`
2. Mostre o quadro **Dados enviados à IA**. Saída esperada do `anonimizar_dados`, conferida em 21/10 na `8cb1e23`:
   `[NOME_REMOVIDO] [CPF_REMOVIDO] relatou falha no [SWITCH_REDE]`
   Confirmado no Ensaio 1 pela API (`dados_enviados_nuvem`) e, em 23/10, na tela do painel.
3. Mostre que o diagnóstico vem do provedor simulado: "Diagnóstico K10 simulado".
4. Explique que a sanitização falha fechada: se sobrar um dado pessoal, a chamada não é feita.

### 7. Resultados (2 min)
- CI aprovado nos PRs integrados.
- Rodada 7 na VM, em `75b1874` (`validacao-vm/rodada-2026-10-23a/RESULTADO.md`). Medido em 22/10 à noite: API 20/20, painel 4/4, infraestrutura PASS e pytest com 491 aprovados e 1 falha de ambiente. Medido em 23/10: cinco cargas de 200 alvos com p95 queda→SSE de 0,395 a 0,496 s, sem erros, e e2e do painel aprovado. No teste do provedor, 1 falha em 20 execuções (15,02 s contra o limite de 15 s; #45). Repetição no SHA congelado de segunda, 26/10; não apresentar testes futuros como executados. Windows de 22/10: painel 4/4, aceite HTTP PASS, p95 queda→SSE 0,806 s em loopback; 491 aprovados/1 pulado informados pelo Vinícius (log bruto não localizado nesta conferência). Não comparar com a VM antiga.
- Ensaio de carga, **#44 integrado em `75b1874`**: 200 alvos, intervalo de 2 s e 32 trabalhos.
  - Antes da correção: **0 de 5**. Depois: **5 de 5**, com 489/489 testes no candidato `ddd4840`. Números da VM em 21/10, a confirmar no aceite de sexta e no SHA congelado de segunda.
  - Mensagem central: **na VM e no candidato `ddd4840`, o cliente SSE recebeu os alertas em até 0,410 s (p95)**; não mede 30 renderizações do painel nem o SHA congelado.
  - Fonte: `validacao-vm/rodada-2026-10-22b/RESULTADO.md` (candidato `ddd4840`, 179 hashes conferidos) e `rodada-2026-10-22/RESULTADO.md` (linha de base).
- #44 já integrado; a confirmação no SHA final continua dependente da rodada 7 e da bateria no SHA congelado.

## Limites a declarar
- O provedor de IA é simulado.
- Os testes usam loopback e dados fictícios.
- Os números de carga do #44 foram medidos em laboratório. Não equivalem a homologação hospitalar.
- A anonimização vale para o corpus avaliado (E6), não para dados reais.
- O painel não exibe MTTD nem burn rate. Os dois são calculados pela API e mostrados no terminal.
- Os dados da demo são recriados a cada inicialização, e as sessões não sobrevivem a um reinício da API.
- Depois do #43, a trilha de auditoria é relida e verificada inteira a cada gravação, inclusive em cada login. Isso é seguro, mas o custo cresce com o tamanho do arquivo. Fica registrado como trabalho futuro (ver [demo/issue-custo-auditoria.md](demo/issue-custo-auditoria.md)).

## Contingência
- Use a gravação feita na segunda, 26/10.
- Se a API cair durante a demo: Ctrl+C no terminal A, rode `subir_demo.py` de novo, troque `SIGMA_DEMO_SENHA` pela nova senha e faça login de novo. Leva menos de 1 min.
