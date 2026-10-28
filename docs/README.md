# Documentação do SIGMA

Índice dos documentos do projeto. Para uma visão geral e a instalação, comece pelo [README](../README.md).

## Operação (`operacao/`)

Como instalar e operar o sistema.

- [Instalação para desenvolvimento](operacao/instalacao.md): ambiente, testes, configuração e primeira execução.
- [Backup, restauração e atualização](operacao/backup-restauracao.md): backup offline, restore em banco novo e smoke test.
- [Portas e imagens](operacao/politica-imagens-e-portas.md): portas publicadas, imagens aprovadas e política de atualização.
- [Migração do volume PostgreSQL](operacao/migracao-volume-postgresql.md): roteiro para instalações com dados.

## Processo (`processo/`)

Como a equipe trabalha.

- [Git Flow](processo/gitflow.md): branches, PRs, releases e hotfixes.
- [Organização do repositório (23/10/2026)](processo/organizacao-repositorio-2026-10-23.md): diagnóstico das branches, limpeza executada e qual branch baixar em outro computador.
- [Fluxo de trabalho do TCC](processo/fluxo-de-trabalho-tcc.md): da issue ao fechamento, com modelos de comentário.

## Arquitetura (`arquitetura/`)

- [Documento de visão](visao-do-produto.md): problema, posicionamento, escopo, restrições e critérios de sucesso (rascunho).
- [Stack de tecnologia](arquitetura/stack-de-tecnologia.md): tecnologias, privacidade, infraestrutura e fluxo de dados.
- [Estudo de caso](arquitetura/estudo-de-caso.md): contexto, requisitos (RF e RNF) e validação.
- [Núcleo de engenharia](../engenharia/README.md): pacote `sigma_eng`, experimentos e documentos técnicos.

## Planejamento (`planejamento/`)

- [Plano de demonstração](planejamento/plano-demonstracao-2026-10-27.md)
- [Plano de sprints pós-demo](planejamento/plano-sprints-pos-demo.md)
- [Pauta de 28/10: pós-congelamento](planejamento/pauta-pos-congelamento-2026-10-28.md)
- [Plano de conclusão de 20/10/2026](planejamento/plano-conclusao-2026-10-20.md)

## Demonstração (`demo/`)

- [Roteiro](demo/roteiro-demonstracao.md)
- [Material de apoio](demo/): checklist, scripts, perguntas prováveis e guia do Iohan.

## TCC (`tcc/`)

Material de acompanhamento com o orientador.

- [Diário de bordo](tcc/diario-bordo/)
- [Relatório ao orientador de 21/10/2026](tcc/relatorio-orientador-2026-10-21.md)
- [Proposta ao orientador](tcc/proposta-orientador.md)

## Design (`design/`)

- [Direção de design](design/README.md): protótipo, capturas do painel e validações.
- [DESIGN.md](../DESIGN.md): tokens e componentes extraídos do código.
- [PRODUCT.md](../PRODUCT.md): contexto do produto e verdade dos dados.

## Especificações (`specs/`)

- [`specs/`](specs/): especificações, evidências e revisões por tarefa.

## Histórico (`historico/`)

Registros datados. Mostram o que aconteceu, não o estado atual.

- [Postmortem da sprint de 15 a 20/10/2026](historico/postmortem-sprint-15-20-10-2026.md): sprint não cumprida e falha de carga da coleta (rascunho).
- [Ensaio independente de 25/10/2026](historico/ensaio-independente-2026-10-25.md): roteiro executado pelo Iohan na `develop` `75b1874`, com cinco tropeços.
- [Trail, fase 1](historico/trail-fase1.md)
- [Rascunhos de trabalho](historico/rascunhos/): prévias da documentação e do quadro de 21/10/2026.

## Outras pastas

- [`engenharia/docs/`](../engenharia/docs/): documentos 00 a 09 e ADRs do núcleo de engenharia.
- [`engenharia/resultados/`](../engenharia/resultados/): relatórios dos experimentos (E1, E6) e evidências de aceite e recuperação.
