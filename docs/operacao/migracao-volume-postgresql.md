# Migração do volume PostgreSQL

Roteiro para migrar os dados de uma instalação antiga (volume `sigma_data`) para o volume atual (`sigma-db-data`), por exportação e restauração lógica. A origem é preservada para recuperação.

Este roteiro é um plano. Nenhuma migração foi executada, porque nenhuma instalação com dados foi identificada.

## Quando usar

- **Primeira instalação:** não há o que migrar. Use o volume `sigma-db-data` do Compose, sem imagem Docker diferente. Siga a [instalação](instalacao.md).
- **Instalação com dados:** siga este roteiro. Renomear o volume ou apontar outra imagem para os dados não basta.

## Antes de começar

Registre o ambiente, o responsável, a janela sem escrita e o plano de reversão. Identifique:

- o contêiner, a versão do PostgreSQL, as bases, os donos, as extensões e a imagem com digest;
- os nomes efetivos do projeto e do volume. O Compose costuma acrescentar o nome do projeto a `sigma_data` e `sigma-db-data`. Não adivinhe o prefixo e não mude a pasta ou o projeto sem checar o efeito nos volumes de n8n, Zabbix e Grafana.

Origem e destino precisam ser PostgreSQL 15. Outra versão, extensões incompatíveis, dados de outra aplicação ou falta de espaço exigem um plano próprio.

Nunca monte o mesmo diretório de dados em dois servidores ativos. Nunca copie arquivos de um banco ativo como se fossem um backup consistente.

Tenha à mão:

- as credenciais realmente gravadas, guardadas fora do Git e dos relatórios;
- um destino de backup fora do checkout e do volume migrado, com permissões restritas e espaço suficiente. O backup pode conter dados e hashes de senha;
- um ensaio de restauração em ambiente isolado, com dados fictícios;
- a configuração anterior válida e sua imagem exata. Uma `main` com conflitos de merge não serve para reverter;
- a aprovação operacional de Vinícius Lima, revisor responsável.

## Passos

1. **Inventariar e congelar escritas.** Registre origem, consumidores, volumes e versões. Pare os produtores de escrita durante a captura final e o corte. Dois bancos não podem receber escrita ao mesmo tempo.
2. **Exportar a origem.** Gere o backup das bases com `pg_dump` e dos objetos globais com `pg_dumpall --globals-only`, com ferramentas do PostgreSQL 15. Registre bases, horário, tamanho e checksum, sem publicar conteúdo, senhas ou hashes.
3. **Ensaiar a restauração.** Em instalação isolada, restaure os globais e depois as bases. Confira erros, donos, permissões, extensões, sequências e tabelas. Resolva explicitamente os conflitos de roles de inicialização. Um dump existente ou um checksum correto não prova uma restauração funcional.
4. **Preparar o destino vazio.** Crie `sigma-db-data` com o nome de projeto registrado. Se o volume já tiver dados, pare e investigue. Não sobrescreva nem apague. Valide imagem, credenciais e montagem antes da primeira inicialização.
5. **Restaurar e conferir.** Restaure os backups finais no destino. Verifique schema, contagem por tabela, amostras, permissões e os consumidores. Faça uma escrita controlada e confira as sequências no ambiente de ensaio. Registre esperado e obtido, sem dados reais.
6. **Fazer o corte.** Só depois da conferência e da aprovação, inicie os consumidores no destino. Acompanhe erros e consistência. Registre os nomes efetivos do volume, a referência do Compose e o resultado.
7. **Preservar a recuperação.** Mantenha o volume antigo, o backup e a configuração anterior pelo período de retenção definido pela equipe. Não use `docker compose down -v`, `docker volume rm` nem limpeza de volumes neste roteiro. A remoção é uma operação separada, autorizada depois do aceite.

## Reversão

Antes de liberar escritas no destino, uma falha permite parar o destino e voltar à origem com a configuração anterior.

Depois de escritas novas no destino, a origem fica desatualizada. Suspenda as escritas e defina como reconciliar, porque voltar direto pode perder dados. Reverter imagem ou configuração não reverte os dados.

## Aceite

A migração só é aceita com:

- backup restaurado com sucesso;
- dados e permissões conferidos;
- consumidores testados;
- reversão ensaiada;
- aprovação registrada de Vinícius Lima.

Hoje nenhuma dessas verificações foi executada. Os testes de `docker compose config` validam só o modelo, sem acessar o Engine ou os volumes.

## Referências

- [Docker Compose: volumes e nomes efetivos](https://docs.docker.com/reference/compose-file/volumes/)
- [PostgreSQL 15: backup por SQL dump](https://www.postgresql.org/docs/15/backup-dump.html)
- [pg_dump](https://www.postgresql.org/docs/15/app-pgdump.html) e [pg_dumpall](https://www.postgresql.org/docs/15/app-pg-dumpall.html)
