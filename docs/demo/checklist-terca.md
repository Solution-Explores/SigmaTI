# Checklist de terça, 27/10 (início às 16h, demonstração às 18h)

Pasta de trabalho: `C:\Users\Vinicius Lima\Desktop\sigmati-develop`, no SHA congelado na segunda, 26/10, às 18h.

## Antes de terça
- [ ] Segunda às 18h: SHA da entrega congelado e anotado aqui: `[SHA congelado]`.
- [ ] Segunda à noite: Iohan conferiu o SHA e rodou o smoke.
- [ ] Gravação de contingência pronta e aberta em um player.
- [ ] Slides com os números do aceite no SHA congelado.

## 16h00: máquina
- [ ] Até 16h: desligue normalmente a VM `sigma-restore-25` e confirme que está desligada para liberar memória.
- [ ] Feche o Codex, a VM e as abas que não vai usar. A memória do Windows já se esgotou uma vez.
- [ ] Abra o Docker Desktop e espere o status "Engine running".
- [ ] Confira o SHA: `git -C C:\Users\Vinicius Lima\Desktop\sigmati-develop log --oneline -1` mostra `[SHA congelado]`.

## 16h10: subir a demo (detalhes em `docs/roteiro-demonstracao.md`)
- [ ] Suba o banco: `docker compose -f docker-compose.yml -f deploy/db-host.yml up -d db`
- [ ] **Terminal A:** defina `$env:SIGMA_TEST_DATABASE_URL`, ative a `.venv` e rode `python ..\sigma-develop\docs\demo\subir_demo.py`. Anote a senha impressa.
- [ ] **Terminal B:** `cd sigma-frontend; $env:VITE_API_URL='http://127.0.0.1:18000'; npx vite --host 127.0.0.1 --port 5173`
- [ ] **Terminal C:** `. ..\sigma-develop\docs\demo\demo.ps1` e `$env:SIGMA_DEMO_SENHA='<senha>'`
- [ ] **Terminal D:** deixe digitado, sem executar: `python -m http.server 9099 --bind 127.0.0.1`

## 16h20: smoke
- [ ] `Show-Sigma403` mostra 403 para o N1 e 200 para o gestor.
- [ ] Faça login como `browser.manager` no painel. As cinco abas aparecem e o indicador "Tempo real ativo" está ligado.
- [ ] Na aba Saúde, o alvo "Portal de testes" aparece em risco.
- [ ] Na aba Diagnóstico, envie um texto de teste. O texto anonimizado aparece.
- [ ] Se algo falhar e não se resolver até as 17h, use a gravação de contingência.

## 17h00: apresentação
- [ ] Abra os slides (link do Artifact) em tela cheia.
- [ ] Prepare duas janelas do navegador, uma normal e uma anônima, na tela de login.
- [ ] Silencie as notificações do Windows. Desligue o descanso de tela.
- [ ] Deixe aberta a gravação de contingência, pronta para tocar.
- [ ] Tenha à mão a proposta ao orientador: `docs/demo/proposta-orientador.md`, impressa ou em PDF.

- [ ] Pedidos de aprovação expiram em 15 min. A subida das 16h10 não preserva o pedido pré-carregado até a apresentação: recrie os dados no máximo 10 min antes da etapa 5 ou crie um pedido novo durante essa etapa.

## 18h00: entrega
