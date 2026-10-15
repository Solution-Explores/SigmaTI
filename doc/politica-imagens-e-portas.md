# Portas e atualização de imagens — K04

## Portas publicadas

| Serviço | Publicação padrão no host | Perfil |
|---|---|---|
| Banco principal (`db`) | Nenhuma | Padrão |
| Banco Zabbix (`postgres-server`) | Nenhuma | `monitoring` |
| n8n | `127.0.0.1:5678` TCP | Padrão |
| Grafana | `127.0.0.1:3000` TCP | `monitoring` |
| Zabbix server | `127.0.0.1:10051` TCP | `monitoring` |

A busca no README, documentação, engenharia, specs e workflows não encontrou
agentes/coletores externos configurados nem um requisito de recepção externa na
porta 10051. Isso não comprova que uma instalação fora do repositório não os use.
O padrão seguro é loopback, mantendo os serviços e o perfil existentes.

### Acesso por gerência ou VPN

As variáveis `N8N_BIND_IP`, `GRAFANA_BIND_IP` e `ZABBIX_BIND_IP` permitem selecionar
um IP específico da interface de gerência/VPN do host. Para mudar o padrão:

1. Identificar quem precisa acessar o serviço e qual interface do host será usada.
2. Informar o IP específico dessa interface, não `0.0.0.0`, `::` ou um hostname.
3. Configurar firewall e VPN para permitir somente as origens autorizadas.
4. Homologar alcance permitido/negado e registrar as evidências antes de publicar
   a configuração do ambiente. Um bind específico não comprova isolamento entre VLANs.

O formato longo das portas aceita também loopback IPv6 (`::1`) sem ambiguidades
de sintaxe. Os endereços de documentação usados nos testes são fictícios; não
são endereços reais do servidor e não devem ser copiados como configuração de rede.

Essas variáveis não instalam controles de rede. O Compose permite sobrescrever o
bind; o validador verifica a política em cenários de teste e não bloqueia por si só
um `docker compose up` executado diretamente com outro ambiente.

Usar Docker Engine suportado, versão 28 ou superior, para a homologação de
isolamento por loopback. O Docker registra uma limitação de acesso pelo mesmo
segmento L2 em versões anteriores. Ver
[documentação oficial de publicação de portas](https://docs.docker.com/engine/network/port-publishing/).
Nenhum Engine foi iniciado, consultado ou alterado na execução desta tarefa.

## Imagens aprovadas nesta configuração

| Publicador oficial | Release fixada | Uso |
|---|---|---|
| `postgres` | `15.19-alpine3.24` | Ambos os bancos |
| `n8nio/n8n` | `1.80.0` | Automação |
| `zabbix/zabbix-server-pgsql` | `alpine-6.4.21` | Observabilidade opcional |
| `grafana/grafana` | `10.4.0` | Painéis opcionais |

Os digests completos ficam no [lock de imagens](../docker-images.lock.json) e no
Compose. Foram conferidos os manifests oficiais de release e digest, com conteúdo
SHA-256 correspondente e entradas para Linux amd64 e arm64. Nenhuma camada foi
baixada e nenhum binário foi executado para homologar o runtime.

A escolha preserva as versões explícitas do n8n/Grafana e as linhas PostgreSQL 15
e Zabbix 6.4. PostgreSQL 15.19 é a release que a referência anterior resolvia na
consulta. O Zabbix também identificava versão de aplicação 6.4.21, mas o digest
da tag de release difere do alias anterior: são builds distintos da mesma release,
não imagens byte a byte idênticas. Instalações com imagens locais em cache não
foram investigadas. Compatibilidade operacional permanece sujeita à homologação.

**Limite conhecido:** Zabbix 6.4 consta como não suportado na
[documentação oficial](https://www.zabbix.com/documentation/6.4/en/manual).
Fixá-lo resolve a referência flutuante, não seu ciclo de suporte. Planejar migração
para uma linha suportada em tarefa própria, com backup, testes e aprovação.
Nenhuma atualização de major foi feita implicitamente. As outras imagens antigas
também exigem avaliação de advisories antes de uso operacional; esta entrega não
declara ausência de CVEs.

## Política de atualização

O responsável pela infraestrutura deve revisar suporte e avisos oficiais antes de
cada homologação, semanalmente durante a sprint e ao receber aviso crítico.
É um procedimento da equipe; esta documentação não cria automação ou agendamento.

| Componente | Fonte de avisos |
|---|---|
| PostgreSQL | [Security Information](https://www.postgresql.org/support/security/) |
| n8n | [Security advisories oficiais](https://github.com/n8n-io/n8n/security/advisories) |
| Zabbix | [Security Advisories](https://www.zabbix.com/security_advisories) |
| Grafana | [Security advisories oficiais](https://grafana.com/security/security-advisories/) |

Para cada atualização:

1. Registrar motivação, suporte, release notes, arquitetura e necessidade de
   migração. Mudanças de major exigem escopo e aprovação próprios.
2. Consultar o publicador oficial e verificar release e digest; não preencher
   hashes por memória nem substituir referências automaticamente.
3. Alterar conjuntamente Compose, lock e registro da decisão nas specs.
4. Executar validações de credenciais, portas, manifests e regressões da API na
   `dev`; depois homologar o runtime em ambiente aprovado, com dados fictícios.
5. Obter revisão de outro integrante antes de integrar à `main`. Em atualização
   de dados/schema, preparar backup e reversão próprios; voltar o digest não
   desfaz migração de dados.

O CI falha se a tag oficial deixar de corresponder ao digest aprovado, se os
manifests não estiverem disponíveis ou se as plataformas verificadas faltarem.
Não substitui hashes sozinho. Essa falha exige investigação: indisponibilidade
de rede/limite do registro não equivale a vulnerabilidade, e rebuild de uma tag
não autoriza trocar o lock sem revisão.

## Verificações reproduzíveis

```bash
python scripts/validate_compose_credentials.py
python scripts/validate_infrastructure.py --verify-registry
python -m pytest -q -p no:cacheprovider
```

As verificações de configuração usam credenciais fictícias em memória e não leem
o `.env` do usuário. A opção de registro faz somente consultas a manifests públicos,
sem pull de camadas, criação de contêineres ou acesso a volumes. Os testes de
política recusam bancos publicados, binds amplos/multicast, rede host, portas
inesperadas e imagens divergentes do lock. A homologação da rede real é separada.
