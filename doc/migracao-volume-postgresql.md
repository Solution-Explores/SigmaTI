# PostgreSQL — primeira instalação e migração futura do volume

## Situação e decisão

A equipe informou que ainda não há máquina de implantação. Nenhuma instalação
com dados foi apresentada ou acessada nesta revisão. Na primeira instalação,
usar o volume lógico `sigma-db-data` do Compose atual. Não há migração a executar
nessa situação, e não é necessário criar uma imagem Docker diferente.

Caso uma instalação anterior venha a ser identificada, os dados do volume
legado `sigma_data` serão migrados por exportação/restauração lógica para o novo
volume. A origem será preservada para recuperação. Este documento é um roteiro
para preparar essa operação; não comprova migração nem restauração realizadas.

## Pré-requisitos antes de executar

O operador deve registrar ambiente, responsável, janela sem escrita e plano de
reversão. Identificar o contêiner, a versão do PostgreSQL, bases, proprietários,
extensões, imagem/digest usados e os nomes efetivos de projeto e volume.
`sigma_data` e `sigma-db-data` são nomes lógicos: o Compose normalmente acrescenta
o nome do projeto. Não adivinhar o prefixo nem mudar a pasta/projeto sem conferir
o efeito sobre todos os volumes, inclusive n8n, Zabbix e Grafana.

Este roteiro considera origem e destino PostgreSQL 15. Origem de outra versão,
extensões incompatíveis, dados de outra aplicação ou falta de espaço suficiente
exigem um plano próprio antes de prosseguir. Não monte o mesmo diretório de dados
em dois servidores PostgreSQL em execução. Não copie arquivos de um banco ativo
como se fossem um backup consistente.

Também devem estar disponíveis:

- Credenciais efetivamente persistidas, guardadas fora do Git e dos relatórios.
- Destino seguro de backup fora do checkout e do volume que será migrado, com
  permissões restritas e capacidade suficiente; backups podem conter dados e
  hashes de credenciais.
- Procedimento de restauração ensaiado em ambiente isolado com dados fictícios.
- Configuração anterior válida e sua imagem exata para recuperação. A main com
  conflitos de merge não constitui configuração de reversão utilizável.
- Aprovação operacional de **Vinícius Lima**, revisor responsável indicado.

## Sequência da migração quando houver ambiente

1. **Inventariar e congelar escritas.** Registrar identificação da origem,
   consumidores, volumes e versões. Suspender os produtores de escrita durante
   a captura final e o corte; impedir dois bancos recebendo alterações em paralelo.
2. **Exportar a origem.** Gerar backup lógico das bases com `pg_dump` e dos objetos
   globais necessários com `pg_dumpall --globals-only`, usando ferramentas
   compatíveis com PostgreSQL 15. Registrar bases, horário, tamanho e checksum
   dos arquivos, sem publicar conteúdo, senhas ou hashes de credenciais.
3. **Ensaiar a restauração.** Em instalação isolada, restaurar globais necessários
   e depois as bases, conferir erros, donos, permissões, extensões, sequências e
   tabelas. Resolver conflitos de roles de inicialização explicitamente. Um dump
   existente ou um checksum correto, sozinho, não prova restauração funcional.
4. **Preparar o destino vazio.** Com o nome de projeto escolhido e registrado,
   criar o destino `sigma-db-data` em ambiente de migração aprovado. Se o nome já
   contiver dados, interromper e investigar; não sobrescrever nem apagar. Validar
   imagem, credenciais e montagem antes da primeira inicialização.
5. **Restaurar e conferir.** Restaurar no destino os backups finais e verificar
   schema, contagens por tabela, amostras de dados, permissões e funcionamento dos
   consumidores. Realizar teste de escrita controlada e sequência/autoincremento
   em ambiente de ensaio. Registrar esperado e obtido, sem dados reais no TCC.
6. **Fazer o corte.** Somente após conferência e aprovação, iniciar os consumidores
   no destino e acompanhar erros e consistência. Registrar nomes efetivos de
   volume, referência do Compose e resultado. Renomear o volume não substitui
   essa migração lógica.
7. **Preservar a recuperação.** Manter volume antigo, backup e configuração
   anterior durante o período de retenção definido pela equipe. Não usar
   `docker compose down -v`, `docker volume rm` ou limpeza de volumes como parte
   deste roteiro. A remoção posterior é uma operação separada, autorizada após
   aceite e confirmação da retenção.

## Reversão e aceite

Antes de liberar escritas no destino, uma falha permite interromper o destino e
voltar à origem preservada com a configuração anterior válida. Depois de novas
escritas no destino, a origem fica desatualizada: suspender escritas e definir a
reconciliação/recuperação, pois voltar diretamente pode perder alterações novas.
Reverter imagem ou configuração não reverte os dados.

A migração será aceita apenas com backup restaurado com sucesso, conferência de
dados/permissões, teste dos consumidores, reversão ensaiada e aprovação registrada
de Vinícius Lima. Na ausência de máquina, todas essas verificações operacionais
continuam **não executadas**. Os testes `docker compose config` desta revisão
validam o modelo, sem acessar Engine ou volumes.

## Referências

- [Docker Compose: volumes e nomes efetivos](https://docs.docker.com/reference/compose-file/volumes/).
- [PostgreSQL 15: backup por SQL dump](https://www.postgresql.org/docs/15/backup-dump.html).
- [PostgreSQL 15: pg_dump](https://www.postgresql.org/docs/15/app-pgdump.html) e
  [pg_dumpall](https://www.postgresql.org/docs/15/app-pg-dumpall.html).

[Voltar às instruções de instalação](../README.md#como-instalar)
