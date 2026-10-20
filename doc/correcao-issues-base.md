# Correção das issues de base

Branch `fix/base-issues`, baseada em `develop@8cb1e23`. Trabalho de 20/10/2026.
Os achados anteriores constam na [revisão](revisao-achados-base-2026-10-20.md).

## #6 — auditoria compartilhada

A trilha JSONL usa bloqueio lateral estável do sistema operacional, com espera
limitada a 10 segundos: `msvcrt.locking` no Windows e `flock` no Linux. Escritores
cooperantes leem e verificam a cadeia corrente antes de derivar sequência/hash e
anexar com fsync. Exceções liberam o bloqueio. A trilha inválida recusa append;
a correção não reescreve nem “conserta” registros antigos automaticamente.

O byte bloqueado pode ficar além do EOF; não há inicialização de conteúdo fora
do lock. Referência: [Microsoft CRT `_locking`](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/locking?view=msvc-170).

`resumo()` verifica integridade e contagem no mesmo snapshot protegido e é usado
pelo endpoint existente. Leitores duradouros enxergam gravações novas de outras
instâncias/processos e adulterações posteriores ao startup. O contrato JSON e
as dependências RBAC foram preservados.

Auth e engenharia passam a usar o mesmo caminho padrão existente de engenharia,
ou o `SIGMA_AUDIT_PATH` explícito. A inicialização malsucedida da trilha impede
continuar login silenciosamente sem auditoria. A resposta continua sendo erro
público genérico, sem copiar detalhes da exceção.

### Limites operacionais

- Lock coordena processos cooperantes no mesmo filesystem local. Não valida
  coordenação distribuída em NFS/SMB nem impede editores não cooperantes.
- Não apagar/substituir `.lock` enquanto houver processos ativos. Em implantação,
  parar todos os escritores antigos antes de iniciar a versão corrigida.
- Se `SIGMA_AUDIT_PATH` não era definido, auth podia gravar em
  `resultados/audit.jsonl` enquanto engenharia usava `engenharia/resultados/audit.jsonl`.
  Preservar ambas as trilhas antigas, verificá-las separadamente e configurar
  explicitamente a trilha canônica futura; não concatenar duas cadeias HMAC.
- Com diretório sem permissão, lock expirado ou I/O indisponível, a operação
  falha; verificar logs seguros e permissões. Não apagar a auditoria para liberar
  o login. Preservar uma cópia e investigar a integridade.
- As leituras e validações percorrem a trilha; não é uma solução de rotação ou
  armazenamento de longo prazo. HMAC, âncora e rotação seguem escopos distintos.
- Se a confirmação da gravação falhar após bytes terem sido escritos, o cliente
  recebe erro; não se promete exatamente uma vez de eventos sob falha de I/O.
- O JSONL e os eventos operacionais transacionais PostgreSQL são trilhas distintas.

## #7 e #14

Não foi identificada implementação adicional exigida pelos critérios originais.
Os testes de persistência/reinício e de pinning foram mantidos. O aceite deve
usar os resultados efetivos, distinguindo implementação integrada, ensaio local
e revisão de encerramento. Não concluir o cartão conjunto #14/#13 apenas por #14.

## #8

A carga reprovou também no host local, sem VirtualBox. No primeiro ensaio desta
branch, com a carga original de 200 alvos/2 s/32 trabalhos, `missed` aumentou de
1.272 para 1.612 durante a janela. Havia 81 timeouts acumulados, sem novos
timeouts nessa janela; `errors` permaneceu zero. A causa não foi isolada.
Não foi alterado o executor nem relaxado o critério para anunciar aprovação.

O runner PostgreSQL passou a usar um diretório temporário exclusivo por execução,
evitando depender de temporários herdados entre contextos de permissão do Windows.
Isso corrige a preparação do ensaio, não o desempenho do produto.

## Evidências

- Sessão/RBAC: 69 testes locais aprovados em 51,59 s.
- Auditoria/aprovações/pinning: primeira rodada de 29 testes aprovada em 10,64 s.
- Linux Python 3.12, contêiner sem rede e código somente leitura: quatro processos,
  120 eventos íntegros, leitura atualizada, corrupção recusada e lock liberado.
  Imagem `python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1`.
- Relatórios locais em `test-results/revisao-issues-base/`. Logs brutos podem
  conter credenciais efêmeras de bancos descartáveis: não publicá-los.

### Resultados posteriores

Primeira regressão completa local: **473 testes, 470 aprovados, duas falhas e um
ignorado em 629,45 s**. Falhas: carga E2 e navegador sem `npm.cmd`. O ignorado é
`test_backup_private_permissions_on_posix`, explicitamente específico de Linux.
Não apresentar essa rodada como regressão aprovada.

Após preparar npm local e instalar com `npm ci --include=optional`, o ensaio de
navegador real/API/PostgreSQL passou em 85,99 s. Não houve alteração do lockfile.
O teste de navegador encapsula as histórias Playwright; sua unidade pytest é uma.
Persistência/identidades/coleta PostgreSQL tiveram respectivamente 18/17/6 testes
aprovados na regressão completa. Testes focados posteriores: 44 aprovados em
49,42 s; após remover a inicialização não coordenada do byte de lock, as sete
regressões finais da auditoria passaram em 15,88 s no Windows.

A tentativa intermediária de integração também encontrou dependência ausente
`@axe-core/playwright` e timeout no aquecimento dos 200 alvos; não foi aceite de
carga. O runner agora arquiva resumos antigos e grava métricas de aquecimento
quando essa etapa reprova. Cada E2 usa arquivo de auditoria próprio, evitando
mistura de trilhas entre execuções.

O experimento que baixou temporariamente o intervalo do GIL somente no Uvicorn
para 1 ms **reprovou**: `missed` de 1.792 para 2.243. Pelos deltas da janela,
persistência com espera no executor teve média de 813 ms por future concluído;
sondas tiveram média de 87 ms. Havia 24 gravações pendentes. Esse ajuste não foi
incluído no produto. As métricas de duração foram adicionadas para diagnóstico,
sem mudar concorrência nem critérios de aceite.

Microbenchmark separado, sem sondas: `SELECT 1` médio de 1,89 ms; 600 medições
por variante produziram 19,34 gravações/s com um trabalhador, 63,66/s com quatro
e 56,74/s com doze. Portanto, mudar apenas o tamanho do executor não sustenta
os 100 registros/s médios exigidos por 200 alvos a cada 2 s nesse ambiente.
O ensaio não homologa outras máquinas. Próxima investigação: reduzir o custo
transacional/idas ao banco, avaliando persistência em lotes limitados e mantendo
idempotência, ordem por alvo, estado do detector e atomicidade com incidentes.
Não introduzir fila ilimitada nem confirmar medição antes do commit.

`npm audit` apontou Vite na faixa vulnerável 8.3.0–8.3.2, incluindo o aviso
GHSA-587h-7wmj-h5pm. É uma pendência de dependência do frontend a tratar em
entrega separada; não foi executado `npm audit fix` nesta branch. Servidores de
teste foram configurados apenas em loopback.

Nenhuma issue é encerrada automaticamente por este documento.
