# K09 e K10 — instalação limpa e aceite integrado

Data: 19/10/2026. Base testada: `dev@142efd2`.

Referências: [K09](https://trello.com/c/KfknLcok),
[K10](https://trello.com/c/z1CLDzjj), [issue #4](https://github.com/Solution-Explores/SigmaTI/issues/4),
[roteiro K08](../../operacao/instalacao.md) e
[fluxo do TCC](../../processo/fluxo-de-trabalho-tcc.md).

## Objetivo e execução

- K09: outro checkout da `dev`, ambiente Python novo, frontend pelo lockfile e
  serviços em projeto Compose com volumes e portas de loopback exclusivos.
- K10: medir a API real em Uvicorn/HTTP, verificando autenticação, contrato,
  generalização, falhas do provedor, timeout, CORS e falha segura; conferir também
  o envio de alerta no painel pelo navegador.
- Usar dados fictícios e IA simulada; preservar dados e serviços dos outros projetos.
- Registrar reprovações para K11/K12 e repetir o aceite depois das correções.

## Resultado de aceite

**K09: bloqueada na inicialização Docker. K10: reprovada no fluxo integrado.**
Execução e revisão técnica realizadas pelo Codex nesta conversa, conforme
solicitação do usuário, sem esperar outro integrante. Não há homologação manual
atribuída a outra pessoa. Veja [evidências](evidencias.md).

O runner `scripts/validate_api_acceptance.py` usa o Python do checkout indicado,
inicia Uvicorn em loopback e injeta `httpx2.MockTransport` somente no processo de
aceite. Não altera `main.py`, não envia dados à IA real e retorna exit 1 quando
um critério falha. O campo `--keep-server` é somente para observar o painel;
o processo deve ser encerrado após as evidências.

API e frontend não são conteinerizados no Compose atual. Devolver "Incidente
Registrado" também não comprova persistência em banco. Homologação hospitalar,
migração de dados e provas com provedor real estão fora desta execução controlada.
