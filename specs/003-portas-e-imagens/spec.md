# K04 — Portas restritas e imagens fixadas

**Issue:** [#3](https://github.com/Solution-Explores/SigmaTI/issues/3), parte K04.

**Base:** `dev@1586221f87afb48efb5f843374ebe7a639a0929b`, com K03 preservada.

**Estado:** Revisão e testes — aguardando outro integrante. A autorrevisão e os
testes do agente não são revisão independente, não autorizam `main` e não encerram a issue.

## Solução

- Bancos sem portas publicadas; n8n, Grafana e Zabbix em `127.0.0.1` por padrão.
- `ZABBIX_BIND_IP` acrescentado; binds em formato longo para aceitar IPv4/IPv6.
- Nenhuma configuração de coletor externo foi encontrada no repositório. Acesso
  externo passa a exigir configuração explícita de interface de gerência/VPN,
  firewall e homologação da instalação, sem presumir necessidade de acesso amplo.
- Todas as imagens possuem release explícita e digest SHA-256. O
  [lock](../../docker-images.lock.json) e o Compose devem corresponder.
- Releases/metadados verificados em endpoints oficiais do Docker Hub, sem baixar
  camadas: PostgreSQL 15.19/Alpine 3.24, n8n 1.80.0, Zabbix 6.4.21 e Grafana 10.4.0.
- Linhas/majors atuais preservadas. O Zabbix 6.4 continua não suportado; migração
  para uma linha suportada é tarefa separada, não uma alteração implícita da K04.
- [Política de atualização e portas](../../doc/politica-imagens-e-portas.md)
  documentada; o CI verifica configurações e manifests, sem atualizar hashes sozinho.

## Validação

- Repetir as 32 verificações K03 e os 61 testes K02.
- Conferir configuração padrão/monitoring/template com valores fictícios.
- Verificar loopback IPv4/IPv6 e IP de gerência fictício; recusar publicações
  amplas, bancos publicados, rede host, portas alteradas e imagens fora do lock.
- Consultar manifests de tag/digest e confirmar o SHA-256 e as plataformas
  Linux amd64/arm64 nos quatro publicadores oficiais.
- Conferir preservação de credenciais, volumes, serviços, perfis, autores/MVP e
  fluxo no README, sem reintroduzir o trecho removido de soluções dos desafios.

## Limites

Nenhum contêiner foi iniciado e nenhum volume/dado foi acessado ou migrado.
Não há homologação de runtime, firewall/VPN ou `.env` real do servidor. O validador
testa cenários controlados e não impede um operador de usar outro ambiente ao
executar o Compose diretamente. Fixar referências não comprova ausência de CVEs
nem resolve o fim de suporte do Zabbix 6.4.

Consulte [evidências](evidencias.md) e [atividades](tasks.md).
