# Portas e imagens

Este guia define quais portas o Compose publica, quais imagens estão aprovadas e como atualizá-las. Leia antes de mudar um bind ou uma versão de imagem.

## Portas publicadas

| Serviço | Publicação padrão no host | Perfil |
|---|---|---|
| Banco principal (`db`) | Nenhuma | Padrão |
| Banco Zabbix (`postgres-server`) | Nenhuma | `monitoring` |
| n8n | `127.0.0.1:5678` | Padrão |
| Grafana | `127.0.0.1:3000` | `monitoring` |
| Zabbix server | `127.0.0.1:10051` | `monitoring` |

O padrão é loopback. Nada no repositório pede que o Zabbix receba conexões externas na porta 10051. Isso não prova que uma instalação fora do repositório não use agentes externos.

### Acesso pela rede de gerência ou VPN

As variáveis `N8N_BIND_IP`, `GRAFANA_BIND_IP` e `ZABBIX_BIND_IP` trocam o IP de publicação. Para mudar o padrão:

1. Defina quem precisa do acesso e qual interface do host será usada.
2. Informe o IP dessa interface. Não use `0.0.0.0`, `::` nem hostname.
3. Configure firewall e VPN para liberar só as origens autorizadas.
4. Teste o acesso permitido e o negado, e registre a evidência antes de publicar a configuração.

Um bind específico não isola VLANs. Essas variáveis também não instalam controles de rede, e um `docker compose up` direto com outro ambiente não é bloqueado pelo validador. O formato longo das portas aceita loopback IPv6 (`::1`). Os IPs de documentação usados nos testes são fictícios.

Use Docker Engine 28 ou superior para o isolamento por loopback. Versões anteriores têm uma limitação de acesso pelo mesmo segmento L2, descrita na [documentação do Docker](https://docs.docker.com/engine/network/port-publishing/).

## Imagens aprovadas

| Publicador | Release fixada | Uso |
|---|---|---|
| `postgres` | `15.19-alpine3.24` | Os dois bancos |
| `n8nio/n8n` | `1.80.0` | Automação |
| `zabbix/zabbix-server-pgsql` | `alpine-6.4.21` | Observabilidade opcional |
| `grafana/grafana` | `10.4.0` | Painéis opcionais |

Os digests completos estão em [`docker-images.lock.json`](../../docker-images.lock.json) e no Compose. Os manifests oficiais foram conferidos, com SHA-256 correspondente e entradas para Linux amd64 e arm64. Nenhuma camada foi baixada e nenhum binário foi executado.

O digest da tag de release do Zabbix difere do alias anterior. São builds distintos da mesma release. Imagens em cache local não foram investigadas.

Limites conhecidos:

- Zabbix 6.4 [não tem suporte oficial](https://www.zabbix.com/documentation/6.4/en/manual). Fixar o digest resolve a referência flutuante, não o ciclo de suporte. A migração para uma linha suportada exige tarefa própria, com backup, testes e aprovação.
- As outras imagens também pedem a leitura de advisories antes do uso operacional. Este guia não declara ausência de CVEs.

## Atualizar uma imagem

O responsável pela infraestrutura revisa suporte e avisos oficiais antes de cada homologação, toda semana durante a sprint e a cada aviso crítico. Não há automação para isso.

| Componente | Fonte de avisos |
|---|---|
| PostgreSQL | [Security Information](https://www.postgresql.org/support/security/) |
| n8n | [Security advisories](https://github.com/n8n-io/n8n/security/advisories) |
| Zabbix | [Security Advisories](https://www.zabbix.com/security_advisories) |
| Grafana | [Security advisories](https://grafana.com/security/security-advisories/) |

Para cada atualização:

1. Registre a motivação, o suporte, as release notes, a arquitetura e a necessidade de migração. Mudança de major exige escopo e aprovação próprios.
2. Consulte o publicador oficial e confira release e digest. Não preencha hashes de memória.
3. Altere juntos o Compose, o lock e o registro da decisão em `docs/specs/`.
4. Rode as validações abaixo na `develop`. Depois homologue o runtime em ambiente aprovado, com dados fictícios.
5. Peça revisão de outro integrante antes de integrar à `main`. Se houver mudança de dados ou schema, prepare backup e reversão. Voltar o digest não desfaz migração.

O CI falha se a tag oficial deixar de corresponder ao digest aprovado, se faltarem manifests ou se faltarem plataformas. Investigue a falha. Indisponibilidade de rede ou limite do registro não é vulnerabilidade, e um rebuild da tag não autoriza trocar o lock sem revisão.

## Validar

```bash
python scripts/validate_compose_credentials.py
python scripts/validate_infrastructure.py --verify-registry
python -m pytest -q -p no:cacheprovider
```

Os validadores usam credenciais fictícias em memória e não leem o seu `.env`. A opção `--verify-registry` só consulta manifests públicos. Não baixa camadas, não cria contêineres e não acessa volumes.

Os testes recusam bancos publicados, binds amplos ou multicast, rede `host`, portas inesperadas e imagens diferentes do lock. A homologação da rede real é uma etapa separada.
