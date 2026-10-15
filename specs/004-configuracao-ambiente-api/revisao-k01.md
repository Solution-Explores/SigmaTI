# Revisão da K01 — Docker Compose

Revisão feita após implementar e validar inicialmente a K02, antes da revisão
final da K02. Base revisada: `dev@b7ebe2c69bda6806fdbbfd4f16efd9bc7c3258b7`.
O Compose e o workflow original da K01 não foram alterados.

## Resultado

A correção de sintaxe e a separação dos serviços estão implementadas na `dev`.
As três verificações abaixo retornaram **0**, sem avisos, com Docker Compose
v5.5.1. São validações de configuração; não comprovam inicialização dos serviços,
autenticação, disponibilidade das imagens ou execução bem-sucedida no GitHub Actions.

```text
docker compose config --quiet
docker compose --profile monitoring config --quiet
docker compose --env-file .env.example --profile monitoring config --quiet
```

A configuração renderizada também confirmou:

- Padrão: `db`, `n8n`.
- Perfil monitoring: `db`, `n8n`, `postgres-server`, `zabbix-server`, `grafana`.
- Banco da aplicação sem portas publicadas.
- n8n e Grafana publicados em `127.0.0.1` por padrão.
- Ausência de marcadores de conflito no Compose da `dev`.

## Achados — somente relatados

### [P1] Senhas conhecidas continuam como fallback

**Local:** `docker-compose.yml:11`, `:27`, `:45`, `:61`; template `.env.example`.

Sem variáveis preenchidas, os bancos inicializam com senhas conhecidas presentes
no próprio código. Isso contradiz CHK003 e SC-003, marcados como concluídos na
especificação. O banco sem porta publicada reduz a exposição, mas as credenciais
permanecem utilizáveis por serviços na rede Docker. Retirar fallbacks de senhas e
exigir valores externos deve ser tratado na K03; este relatório não modifica a K01.

### [P1] A troca do volume não tem caminho de migração

**Local:** `docker-compose.yml:13-14`, declaração `:85`.

O Compose anterior usa `sigma_data`; a correção monta `sigma-db-data`. Se houver
dados de uma execução anterior, a nova configuração cria outro volume e inicia
um banco vazio, deixando os dados antigos fora do serviço. Não há migração ou
mapeamento do volume legado nas instruções. Os dados antigos não são apagados
por essa troca; o risco é a interrupção do acesso ao histórico. Antes de atualizar
uma instalação existente, identificar o volume, preservar backup e definir a
reutilização ou migração explícita. A presença de dados reais não foi investigada.

A [documentação do Docker sobre volumes](https://docs.docker.com/reference/compose-file/volumes/)
explica a criação de volumes pelo Compose e o uso de `name`/`external` para
referenciar um recurso existente.

### [P2] As variáveis de Basic Auth não configuram o login do n8n 1.80

**Local:** `docker-compose.yml:20`, `:24-27`; `.env.example:19-20`.

O serviço usa n8n 1.80.0, mas fornece `N8N_BASIC_AUTH_*`. Basic Auth foi removido
no n8n 1.0, portanto preencher `N8N_USER`/`N8N_PASS` não configura a conta de acesso
como o template sugere. O n8n possui seu próprio fluxo de criação da conta owner;
o achado não significa que o login próprio esteja desativado. O roteiro precisa
documentar esse fluxo ou uma proteção externa compatível com a versão escolhida.
Ver [documentação oficial de usuários do n8n](https://docs.n8n.io/hosting/configuration/user-management-self-hosted/).

### [P2] As tags ainda não garantem versões determinísticas

**Local:** `docker-compose.yml:7`, `:39`, `:54`.

`alpine-6.4-latest` continua móvel; `postgres:15-alpine` também não fixa patch nem
digest. Assim, os mesmos arquivos podem resolver imagens diferentes em execuções
posteriores, contrariando FR-005. Fixar releases/digests e definir a atualização
continua pendente para K04. n8n e Grafana já possuem tags de release explícitas.

## Integração e limites

Na consulta ao GitHub durante esta revisão, o
[Compose da main](https://github.com/Solution-Explores/SigmaTI/blob/main/docker-compose.yml)
ainda continha os marcadores de conflito. A implementação existente na `dev` não
equivale a integração concluída na `main`. Não foi efetuado merge.

A documentação já descreve os serviços padrão e opcionais; as afirmações sobre
ausência de senhas padrão e determinismo de imagens precisam ser reconciliadas
com os achados. Não foram iniciados contêineres, migrados volumes ou alteradas
credenciais. As verificações locais não substituem a homologação operacional.
