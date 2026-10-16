# Evidências da K04

Validação em 15/10/2026 sobre `dev@1586221`, usando credenciais fictícias.
Estado: implementação preparada para revisão de outro integrante; issue #3 aberta.

| Verificação | Resultado |
|---|---|
| Regressão de credenciais K03 | 32 verificações aprovadas |
| Pytest completo, Python 3.12.14 | 86 testes aprovados em 14,21 s: 61 K02 + 25 política K04 |
| Configuração K04 | 6 cenários positivos: padrão/monitoring com loopback IPv4, IPv6 e IP de documentação |
| Configuração K04 negativa | 6 binds amplos recusados: três serviços, duas famílias IP |
| Registro oficial | 4 imagens confirmadas por tag e digest, SHA-256 do conteúdo e Linux amd64/arm64 |
| Dependências Python | `pip check`: nenhuma dependência quebrada |

Comandos reproduzíveis:

```bash
python scripts/validate_compose_credentials.py
python scripts/validate_infrastructure.py --verify-registry
python -m pytest tests -q -p no:cacheprovider
python -m pip check
git diff --check
```

No ambiente Windows restrito, os testes usaram diretório temporário local e um
ajuste de permissão de criação de diretórios somente no processo de execução.
Esse ajuste não integra código ou CI. As verificações não imprimem credenciais.

## Imagens e exposição

Os quatro publicadores oficiais, releases e digests completos estão no
[lock](../../docker-images.lock.json). Foram consultados os endpoints de
autenticação pública e manifests de `registry-1.docker.io`; tokens ficaram em
memória. Nenhuma camada foi baixada.

PostgreSQL 15.19/Alpine 3.24 corresponde ao digest resolvido pelo alias anterior
na consulta. n8n 1.80.0 e Grafana 10.4.0 mantêm as releases explícitas existentes.
Zabbix mantém aplicação 6.4.21, porém a tag estável selecionada tem digest/build
diferente do alias anterior. Não se afirma identidade binária ou compatibilidade
de uma imagem antiga em cache, que não foi investigada.

Bancos continuam sem publicação. n8n, Grafana e Zabbix usam loopback por padrão.
A busca em README, docs, engenharia, specs e workflows não encontrou configuração
de coletores externos ou requisito de publicação externa da porta 10051. Isso
não descreve instalações externas ao repositório.

## Autorrevisão

- Comparação dos modelos Compose da base e da implementação, retirando somente
  imagens e portas, confirmou igualdade dos demais campos: credenciais, serviços,
  volumes, redes, dependências e perfis preservados.
- README conserva autores, MVP e destaque do fluxo; trecho removido de soluções
  dos desafios não foi reintroduzido.
- Testes de política cobrem bancos publicados, wildcard IPv4/IPv6 e mapeado,
  multicast mapeado, rede host, portas/protocolo alterados, portas extras,
  imagem divergente e lock com release flutuante/major/publicador inválido.
- Corrigida na autorrevisão a recusa de wildcard/multicast IPv4 mapeado em IPv6;
  credenciais foram retiradas da representação da fixture de testes de política.
  Os 86 testes passaram após as correções.
- O CI conserva as verificações K03 e acrescenta política/manifests oficiais.
  Nenhum hash é atualizado automaticamente quando o registro diverge.

## Limites e pendências

Zabbix 6.4 está sem suporte; planejar migração separada. Fixar imagens não
comprova ausência de CVEs. Consultar avisos oficiais e a
[política](../../doc/politica-imagens-e-portas.md) antes da homologação.

Não foram iniciados contêineres, consultado o Engine, acessados volumes/dados,
rotacionadas credenciais ou homologados runtime, firewall, VPN e `.env` real.
O validador usa cenários fictícios e não impede execução direta do Compose com
outro ambiente. Revisão de outro integrante e homologação operacional permanecem
pendentes. Sem integração à `main` ou encerramento da issue #3 nesta entrega.
