# Evidências da K03 — entrega parcial da issue #3

## Escopo e estado

Base de implementação: `dev@7f74e475c625ea4c69817d3fb79ef57089eb29f1`.
Estado: **Revisão e testes — aguardando outro integrante**. A autorrevisão do
agente e os resultados abaixo não substituem a revisão técnica do colega nem
autorizam integração à `main`. A issue #3 permanece aberta para K04 e para a
validação do pedido completo.

Foram alterados os blocos de credenciais do Compose, o template, o CI e as
instruções de operação. O [validador](../../../scripts/validate_compose_credentials.py)
gera valores fictícios durante a execução. Não há senha pronta no template nem
senha fixa no workflow ou no validador.

## Testes realizados

Ambiente local: Windows, Python 3.12.14 e Docker Compose v5.5.1.
Os testes não iniciaram contêineres e não acessaram dados de bancos ou volumes.

| Verificação | Resultado |
|---|---|
| `scripts/validate_compose_credentials.py` | **32 verificações aprovadas**, código 0 |
| Template: seis credenciais vazias, sem duplicatas ou fallback | Aprovado |
| `.env` ignorado pelo Git | Aprovado |
| Compose padrão com credenciais fictícias | Aprovado |
| Compose com `monitoring` e credenciais fictícias | Aprovado |
| `.env.example` preenchido por variáveis externas fictícias | Aprovado |
| Configuração renderizada: credenciais nos serviços esperados | Aprovado nos dois perfis |
| Template sem preenchimento | Recusado conforme esperado |
| Cada uma das seis credenciais ausente/vazia, nos dois perfis | **24 rejeições esperadas** confirmadas |
| Mensagens das rejeições | Identificam a variável e não expõem as senhas geradas |
| Regressão da K02: `tests/test_config.py` | **61 testes aprovados em 16,94 s**, sem avisos |
| Comparação da configuração renderizada com a base, removendo somente `environment` | Modelos idênticos: imagens, portas, redes e volumes preservados |
| README: fluxo, autores, MVP e ausência do trecho removido | Preservados |
| `python -m pip check` | Nenhuma incompatibilidade encontrada |
| `git diff --check` e seis links locais da documentação | Aprovados |

As três validações positivas do Compose usam somente `config`: padrão,
`monitoring` e template com valores externos. A renderização JSON adicional é
capturada em memória para inspeção, sem imprimir as credenciais.

## Como reproduzir

Em um checkout Git, com Python 3.12+ e Docker Compose disponíveis:

```bash
python scripts/validate_compose_credentials.py
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_config.py -q -p no:cacheprovider
git diff --check
```

O validador usa explicitamente um arquivo de ambiente temporário vazio ou o
template. Não lê implicitamente o `.env` do usuário, não grava senhas nos arquivos
temporários e não imprime a configuração renderizada. Gera credenciais distintas
em memória e não depende de chaves da IA ou da inicialização do Docker Engine.

No sandbox Windows usado na execução local, o runner ajustou a criação de
diretórios temporários para contornar ACLs de diretórios com modo 0700. Esse ajuste
é do runner local e não foi incorporado ao produto ou ao validador entregue.

## CI

O workflow de infraestrutura agora cobre pushes e PRs para `dev` e `main`, usando
o mesmo validador sem senhas literais. O workflow da API/K02 permanece inalterado.
O resultado remoto deve ser conferido em
[GitHub Actions](https://github.com/Solution-Explores/SigmaTI/actions) após a publicação;
os resultados acima são de execução local.

## Autorrevisão e limites

- As credenciais obrigatórias usam `${VAR:?mensagem}`, sem fallback; o nome do
  banco continua sendo uma configuração não secreta.
- A exigência de credenciais de perfis inativos foi documentada e testada. Não
  foi introduzido um segundo arquivo Compose ou outro modo de inicialização.
- O acesso ao n8n segue o fluxo nativo da conta owner, sem substituir sua imagem.
- Grafana e PostgreSQL usam credenciais de inicialização. Alterar o `.env` não
  rotaciona contas existentes; qualquer correção de credencial persistida exige
  procedimento operacional próprio e aprovado.
- A comparação de modelos confirmou que a K03 não implementa a K04. A exposição
  da porta Zabbix e as referências mutáveis de imagens permanecem pendentes.
- Não houve migração, renomeação ou leitura de volumes; nenhuma senha real ou
  dado do hospital foi utilizado. A pasta original do usuário foi preservada.
- Não foi identificado outro impedimento na autorrevisão dentro do escopo de
  configuração da K03. Não foi feita homologação operacional ou revisão independente.

## Pendências

1. Outro integrante revisar a alteração e reproduzir as verificações.
2. Implementar e validar K04: portas, referências de imagens e política de atualização.
3. Planejar separadamente qualquer migração de volume ou rotação de credenciais
   persistidas. A existência de uma instalação com dados não foi investigada.
4. Concluir os requisitos completos da issue #3 antes de considerar seu fechamento.
