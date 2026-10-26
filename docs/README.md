# Documentação do SIGMA

Índice dos documentos do projeto. Para uma visão geral e a instalação, comece pelo [README](../README.md).

## Guias

Como instalar, operar e trabalhar no projeto.

- [Instalação para desenvolvimento](guias/instalacao.md): ambiente, testes, configuração e primeira execução.
- [Backup, restauração e atualização](guias/backup-restauracao.md): backup offline, restore em banco novo e smoke test.
- [Portas e imagens](guias/politica-imagens-e-portas.md): portas publicadas, imagens aprovadas e política de atualização.
- [Migração do volume PostgreSQL](guias/migracao-volume-postgresql.md): roteiro para instalações com dados.
- [Git Flow](guias/gitflow.md): branches, PRs, releases e hotfixes.
- [Organização do repositório (23/10/2026)](guias/organizacao-repositorio-2026-10-23.md): diagnóstico das branches, limpeza executada e qual branch baixar em outro computador.
- [Fluxo de trabalho do TCC](guias/fluxo-de-trabalho-tcc.md): da issue ao fechamento, com modelos de comentário.

## Arquitetura

- [Documento de visão](visao-do-produto.md): problema, posicionamento, escopo, restrições e critérios de sucesso (rascunho).
- [Stack de tecnologia](arquitetura/stack-de-tecnologia.md): tecnologias, privacidade, infraestrutura e fluxo de dados.
- [Estudo de caso](arquitetura/estudo-de-caso.md): contexto, requisitos (RF e RNF) e validação.
- [Núcleo de engenharia](../engenharia/README.md): pacote `sigma_eng`, experimentos e documentos técnicos.

## Demonstração

- [Plano de demonstração](plano-demonstracao-2026-10-27.md)
- [Roteiro](roteiro-demonstracao.md)
- [Material de apoio](demo/)

## Design

- [Direção de design](design/README.md): protótipo, capturas do painel e validações.
- [DESIGN.md](../DESIGN.md): tokens e componentes extraídos do código.
- [PRODUCT.md](../PRODUCT.md): contexto do produto e verdade dos dados.

## Histórico

Registros datados. Mostram o que aconteceu, não o estado atual.

- [Diário de bordo](historico/diario-bordo/)
- [Plano de conclusão de 20/10/2026](historico/plano-conclusao-2026-10-20.md)
- [Relatório ao orientador de 21/10/2026](historico/relatorio-orientador-2026-10-21.md)
- [Postmortem da sprint de 15 a 20/10/2026](historico/postmortem-sprint-15-20-10-2026.md): sprint não cumprida e falha de carga da coleta (rascunho).
- [Trail, fase 1](historico/trail-fase1.md)
- [Rascunhos de trabalho](historico/rascunhos/): prévias da documentação e do quadro de 21/10/2026.

## Outras pastas

- [`specs/`](../specs/): especificações, evidências e revisões por tarefa.
- [`engenharia/docs/`](../engenharia/docs/): documentos 00 a 09 e ADRs do núcleo de engenharia.
