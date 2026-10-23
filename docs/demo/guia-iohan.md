# Guia do Iohan até a demonstração de 27/10

Três tarefas, nesta ordem. A regra do plano vale: quem revisa não é quem fez, por isso a revisão do #47 e a execução independente são suas. Base: [plano da demonstração](../plano-demonstracao-2026-10-27.md) e [roteiro](../roteiro-demonstracao.md).

## 1. Revisar o PR #47 (sexta, 23/10, à noite)

PR: [#47](https://github.com/Solution-Explores/SigmaTI/pull/47), `fix/teste-sonda-instavel`, head `0b372cb`, autor Vinícius. Pede **Approve** ou **Request changes** no GitHub (hoje não há nenhum dos dois).

Conferência prévia, só de leitura, feita em 23/10 (Claude, a pedido do Vinícius). Confirme por conta própria:

- O diff é só teste: `engenharia/tests/test_stats_probe.py`. Cria `_fechar(srv)`, que chama `shutdown(SHUT_RDWR)` antes de `close()`, e a usa nos quatro pontos em que o teste fechava o servidor com `close()`.
- A explicação do comentário confere com o que a VM mostrou: no Linux, `close()` não interrompe um `accept()` bloqueado em outra thread, e, sem o `shutdown()`, uma conexão ainda era aceita depois do fechamento (é o que o comentário do código afirma). O `except OSError` cobre o Windows, onde `shutdown` num socket que só escuta levanta erro.
- Nenhuma asserção foi afrouxada.
- CI do head: as cinco verificações aprovadas (`test-config`, `validate-compose`, `test-package`, `test-postgres`, `test-recovery`), inclusive `validate-compose`, que estava reprovado em 22/10.
- **Ressalva para a sua decisão:** a evidência de que a correção resolve é a da rodada 3 (`validacao-vm/rodada-2026-10-22c`, na base `8cb1e23`: 5/10 sem a correção, 30/30 com ela). Na rodada 7 de 23/10, o teste passou 10/10 **dos dois lados** (com e sem a correção), então essa rodada não distingue os dois. Isso não contradiz a rodada 3; só quer dizer que a prova de efeito vem dela.
- O #47 não mexe nos outros testes instáveis (provedor de IA, DNS, `scheduler`); eles seguem na [#45](https://github.com/Solution-Explores/SigmaTI/issues/45).

## 2. Executar o roteiro sozinho (sábado, 24/10, à tarde)

Objetivo: achar o que só aparece em outra máquina. Faça no seu computador, a partir da `develop` integrada (`75b1874`), sem pedir ajuda ao Vinícius durante a execução. Anote cada tropeço.

1. Clone ou atualize e confira o SHA: `git fetch origin && git checkout develop && git pull` e `git log --oneline -1` mostra `75b1874`.
2. Siga [docs/guias/instalacao.md](../guias/instalacao.md) até o ambiente (Python, `npm ci`, Docker, `.env`).
3. Suba a demonstração e percorra as sete etapas de [roteiro-demonstracao.md](../roteiro-demonstracao.md), usando `docs/demo/subir_demo.py` e `docs/demo/demo.ps1`. Se o seu sistema não for Windows, anote em quais passos o PowerShell fez falta (a rodada 4 já mostrou que o roteiro assume Windows).
4. Registre, para cada etapa, **passou**, **passou com ajuste** ou **falhou**, e o que você fez diferente do texto.

Pontos que o ensaio do Vinícius de 23/10 já mostrou e que você deve procurar de propósito:

- Subir o serviço de novo abre um segundo incidente (`latency`) no mesmo alvo; resolva o de `availability`, que fica em segundo na lista.
- **Nova solicitação** (aba Aprovações) começa recolhida.
- Recarregar a página derruba a sessão.
- O pedido de aprovação pré-carregado expira em 15 minutos.
- Tente a janela anônima com duas sessões ao mesmo tempo (o ensaio de 23/10 usou duas abas do navegador embutido). A visão do `browser.demo` (N1) já foi conferida: só Saúde e Diagnóstico.
- A aba Saúde não escreve "em risco": o "Portal de testes" aparece "Disponível", com 12 min de orçamento restante.

Devolva ao Vinícius até o domingo de manhã: a tabela por etapa, os tropeços e o SHA que você usou. Se houver correção, ele a faz no domingo e você repete só o que mudou.

## 3. Conferir o SHA congelado e rodar o smoke (segunda, 26/10, depois das 22h)

1. O Vinícius congela o SHA às 18h e o registra no [checklist de terça](checklist-terca.md). Confira que `git log --oneline -1` na `develop` mostra esse SHA.
2. Rode o smoke de 16h20 do checklist: `Show-Sigma403` (403 para o N1, 200 para o gestor), login do gestor com as cinco abas e "Tempo real ativo", alvo "Portal de testes" com 12 min de orçamento restante (o painel não escreve "em risco") e o diagnóstico com o texto anonimizado.
3. Responda ao Vinícius com o SHA conferido e o resultado de cada item. Se qualquer item falhar, avise na mesma noite: terça de manhã ainda dá para usar a gravação de contingência.

## O que fica de fora

Você não precisa mexer em #13, #5, #25 nem na reorganização do repositório; tudo isso começa em 28/10.
