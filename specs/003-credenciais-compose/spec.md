# K03 — Credenciais obrigatórias do Compose

**Issue:** [#3](https://github.com/Solution-Explores/SigmaTI/issues/3), entrega parcial K03.

**Base:** `dev@7f74e475c625ea4c69817d3fb79ef57089eb29f1`.

**Estado no fluxo:** Revisão e testes — implementação validada localmente, aguardando revisão de outro
integrante antes de qualquer integração à `main`. A autorrevisão do agente não
equivale à aprovação do colega. A issue #3 continua aberta para K04 e demais
critérios de aceite.

## Objetivo e solução

- Bancos e Grafana exigem credenciais externas não vazias, sem fallback de usuário
  ou senha no Compose. O banco Zabbix e seu servidor consomem o mesmo par.
- As variáveis obrigatórias são `POSTGRES_USER`, `POSTGRES_PASSWORD`,
  `ZABBIX_DB_USER`, `ZABBIX_DB_PASS`, `GF_SECURITY_ADMIN_USER` e
  `GF_SECURITY_ADMIN_PASSWORD`. Nomes de bancos permanecem configurações não secretas.
- O `.env.example` mantém os seis campos vazios e documenta o preenchimento e a
  geração de senhas locais distintas. O `.env` permanece ignorado pelo Git.
- O n8n instalado usa a conta owner pelo fluxo nativo. As configurações legadas
  de Basic Auth foram removidas, sem trocar sua imagem ou alterar usuários existentes.
- O CI gera credenciais fictícias temporárias em memória, sem senhas fixas no
  workflow ou nos arquivos de teste e sem imprimir a configuração renderizada.
- Código e validações ficam nos locais próprios do projeto: Compose na raiz e
  [validador](../../scripts/validate_compose_credentials.py) em `scripts/`.
  Esta pasta contém a descrição da solução e suas evidências.

## Decisões e compatibilidade

1. Usar `${VAR:?mensagem}`: configuração ausente ou vazia deve falhar antes de
   iniciar contêineres. As mensagens citam variáveis, não seus valores.
2. Manter um único Compose e o perfil `monitoring`. A interpolação avalia também
   serviços de perfis inativos; por isso as seis credenciais são necessárias mesmo
   para validar o núcleo. Separar o perfil em outro arquivo fica fora desta entrega.
3. Preservar a K02. A API continua com seu carregamento/validação de ambiente;
   a configuração do Compose não inicia nem injeta variáveis no processo da API.
4. Preservar imagens, portas, redes, nomes e montagens dos volumes. A K04 e a
   migração do volume legado são tarefas distintas.
5. Variáveis de inicialização não rotacionam senhas já persistidas no PostgreSQL
   ou no Grafana. Em instalações existentes, informar os valores realmente usados
   e tratar qualquer rotação em procedimento separado e aprovado. A K03 não acessa
   bancos, não inicia contêineres e não altera os dados existentes.

## Critérios de aceite da K03

- As seis credenciais não têm fallback e são recusadas quando ausentes ou vazias.
- O template não oferece senhas prontas e o `.env` está ignorado.
- Com dados fictícios, o núcleo, o perfil monitoring e o template preenchido pelo
  ambiente passam na validação; o template não preenchido falha.
- A configuração renderizada utiliza os valores externos nos serviços corretos.
- O n8n não recebe variáveis de Basic Auth legadas.
- O CI não contém senhas fixas e executa as validações na `dev` e `main`.
- Os testes da K02 continuam aprovados e a documentação registra os limites.

## Validação e pendências

Consulte [atividades](tasks.md) e [evidências](evidencias.md).
Não estão incluídas restrição de portas, fixação de versões/digests, política de
atualização de imagens, migração de dados, rotação de credenciais existentes ou
homologação de instalação. Não encerrar a issue #3 nem declarar segurança
operacional completa somente por esta entrega.

## Referências oficiais

- [Docker Compose: valores obrigatórios e interpolação](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/).
- [n8n: gerenciamento nativo de usuários](https://docs.n8n.io/hosting/configuration/user-management-self-hosted/).
- [Grafana: configuração de usuário/senha iniciais](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#admin_password).
- [PostgreSQL: variáveis da imagem oficial](https://hub.docker.com/_/postgres).
