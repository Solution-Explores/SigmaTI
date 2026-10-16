# Correções da revisão K01–K06

Base revisada: `479a5386739310af485c73b696a24e07a03f6b0f`.
Branch de correção: `fix/revisao-k01-volumes-instalacao`.
Revisor responsável indicado pelo usuário: **Vinícius Lima**.
Execução das verificações automatizadas: Codex.
Situação: correções preparadas e validação automatizada aprovada em 15/10/2026.
Após apresentação dos resultados, **Vinícius Lima autorizou a publicação e a
conclusão dos escopos validados, condicionadas às verificações de integração**.
A autorização foi dada nesta conversa; não se alega reprodução manual dos testes
pelo revisor nem homologação de instalação ou migração de dados.

## Achados e solução

| Achado | Solução | Limite |
|---|---|---|
| A01 — volume legado sem transição documentada | Equipe informou ausência de máquina de implantação; nenhuma base de origem foi indicada. Primeira instalação mantém `sigma-db-data`; roteiro específico descreve migração lógica futura, backup, restauração, corte e reversão com origem preservada. | Nenhum dado migrado ou ambiente operacional homologado; instalação existente exige ensaio e aprovação antes da operação. |
| A02 — clone cai na main com Compose conflitante | README fornece URL real, `--branch dev --single-branch`, conferência de branch/SHA, validação antes de iniciar e passos separados para primeira instalação e atualização. | Correção preparada nesta branch; publicação/integração não é presumida. |

Imagens, digests, portas, credenciais, serviços e montagens do Compose são
preservados. API e frontend também não foram alterados. O fluxo da sonda/pfSense
foi identificado como pendente em vez de apresentar comandos de instalação
inexistentes. Não se criou uma imagem do SIGMA: a API/frontend ainda não estão
conteinerizados nesta entrega, e o Compose referencia as imagens dos serviços.

Consulte o [roteiro de migração](../../doc/migracao-volume-postgresql.md) e o
[fluxo da equipe](../../doc/fluxo-de-trabalho-tcc.md). A autorização registrada
abrange esta entrega com resultados apresentados, sem assinatura forjada ou
declaração de homologação operacional.

## Validação desta correção

Ambiente isolado: Windows, Python 3.12.14, Docker Compose v5.5.1; somente
credenciais/dados fictícios e provedor simulado. Nenhum contêiner iniciado,
nenhum volume acessado e nenhuma chamada real à IA.

| Verificação | Resultado |
|---|---|
| `python -m pip check` | Código 0; nenhuma dependência quebrada |
| `python scripts/validate_compose_credentials.py` | 32 verificações aprovadas; código 0 |
| `python scripts/validate_infrastructure.py --verify-registry` | 12 cenários e quatro imagens oficiais aprovados; código 0 |
| `python -m pytest -q -p no:cacheprovider --junitxml=...` | 180 testes aprovados em 32,89 s; sem falhas, erros ou ignorados |
| Orçamento real do provedor simulado | Caso aprovado em aproximadamente 14 s; asserção de resposta ≤15 s preservada |
| Links locais dos cinco documentos alterados | 16 links verificados; nenhum destino ausente |
| Conferência de URL/branch e remoção dos comandos fictícios | Aprovada |
| `git diff --check` | Código 0 |
| Comparação dos arquivos executáveis/Compose/lock/testes/workflows com a base | Sem alterações |

As saídas locais e o JUnit acompanham o pacote de correções. Os resultados desta
tabela são locais; a publicação e o CI remoto serão conferidos no GitHub antes
de concluir os escopos. A correção contém cinco alterações de documentação,
sem modificar os arquivos executáveis validados.
