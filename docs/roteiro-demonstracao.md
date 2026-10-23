# Roteiro da demonstração de 27/10/2026

Base: [plano da demonstração](plano-demonstracao-2026-10-27.md). Código: `develop`, no SHA congelado na segunda, 26/10, às 18h (hoje `75b1874`, com #43 e #44 integrados).

> **Situação:** Ensaio 1 feito em 22/10, à noite, no Windows, na `develop@75b1874`. Os passos de API (2 a 6) rodaram pelos comandos de apoio em [demo/](demo/); a interface do painel foi coberta só pelo `validate_panel.py` (4/4), não por um ensaio manual no navegador.
> Resultado: os dois itens ⚠ foram confirmados e o `demo.ps1` foi corrigido (veja "Achados do Ensaio 1").

### Achados do Ensaio 1
- `/api/eng/incidentes` devolve `{ "incidentes": [...] }`, não uma lista. `Get-SigmaMetricas` e `Show-Sigma403` foram corrigidos (a contagem de usuários agora mostra 4).
- **Resolver com o serviço ainda fora abre outro incidente na hora.** Suba de novo o `http.server` no terminal D antes de clicar em **Resolver incidente**. `Get-SigmaMetricas` usa o último incidente já resolvido.
- Medido: incidente apareceu 0,7 s após a queda; MTTD 0,45 s com a hora real da queda; MTTA 29 s e MTTR 29 s (tempos do ensaio).
- **Os pedidos de aprovação expiram em 15 minutos** (`expira_em`). Suba a demo no máximo 10 min antes da etapa 5, ou o pedido pré-carregado "Revisar mudança sintética" já terá expirado.
- Anonimização confirmada: `Equipamento: [SWITCH_REDE] | Erro: [NOME_REMOVIDO] [CPF_REMOVIDO] relatou falha no [SWITCH_REDE]` e diagnóstico "Diagnóstico K10 simulado".
- No PowerShell 5.1, acentos de respostas JSON saem trocados no terminal (`DiagnÃ³stico`). É só exibição; o painel mostra certo.
- Quatro olhos: o solicitante recebe HTTP 409 ao decidir; o revisor aprova. Auditoria: `integra: true`, 42 entradas após o ensaio.

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
5. **Ctrl+C no terminal D** e, logo em seguida, `Set-SigmaQueda` no terminal C.
6. O incidente aparece **sem recarregar a página**, em até cerca de 5 s.
7. Clique em **Reconhecer**, depois em **Resolver incidente**.
8. Mostre os cards de MTTA e MTTR: média, mediana, p95 e n.
9. **MTTD:** o painel mostra "Sem início real de falha registrado", porque o incidente não guarda a hora real da queda. Rode `Get-SigmaMetricas`, que calcula MTTD, MTTA e MTTR com a hora registrada no passo 5. Antes de **Resolver incidente**, suba o serviço de novo no terminal D (veja "Achados do Ensaio 1").

### 4. SLO (2 min)
1. Na aba Saúde, mostre o alvo **Portal de testes**:
   - SLO de 95 % em 1 dia;
   - 25 h de histórico, com a última hora em falha;
   - status em risco e cerca de 12 min de orçamento restante;
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
   Confirmado no Ensaio 1 pela API (`dados_enviados_nuvem`). A tela do painel não foi conferida à mão.
3. Mostre que o diagnóstico vem do provedor simulado: "Diagnóstico K10 simulado".
4. Explique que a sanitização falha fechada: se sobrar um dado pessoal, a chamada não é feita.

### 7. Resultados (2 min)
- CI aprovado nos PRs integrados.
- Planejado: aceite na sexta, 23/10, e repetição no SHA congelado de segunda, 26/10. Rodada 7 pendente; não apresentar testes futuros como executados. Windows de 22/10: painel 4/4, aceite HTTP PASS, p95 queda→SSE 0,806 s em loopback; 491 aprovados/1 pulado informados pelo Vinícius (log bruto não localizado nesta conferência). Não comparar com a VM antiga.
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
