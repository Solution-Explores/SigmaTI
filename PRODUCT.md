# SIGMA — contexto do produto

SIGMA é um MVP de TCC de monitoramento ativo de rede com apoio de IA para a equipe de TI de um hospital oncológico de fundação pública. Busca reduzir a descoberta reativa de falhas e a falta de histórico. Metas do README são requisitos; não constituem garantia de operação hospitalar homologada.

## Extensão operacional #15

O painel preserva login, logout e diagnóstico e acrescenta quatro áreas alimentadas pela API: saúde dos serviços, incidentes, aprovações e auditoria. Saúde apresenta medições, cobertura e orçamento. Incidentes permitem reconhecer e resolver e mostram média, mediana e p95. Aprovações registram solicitações e decisões justificadas, com papel mínimo e outro operador; a página não executa comandos. Auditoria separa integridade da trilha de sondas e eventos operacionais.

| Perfil | Visibilidade |
|---|---|
| suporte_n1 | Saúde e diagnóstico |
| analista_redes | Anteriores, incidentes e aprovações |
| gestor_ti | Todas, incluindo auditoria |

A API também aplica autorização. SSE autenticado usa Bearer, cursor Last-Event-ID e reconexão progressiva; reconectar atualiza os dados e consultas de recuperação ocorrem a cada 15s. Sessão e cursor ficam em memória no navegador; recarregar exige login. API operacional indisponível produz erro explícito, sem dados fictícios substituindo a resposta.

## Direção vigente

Extensão da identidade existente: azul sobre fundo escuro, fonte de sistema e painéis planos com borda e raio de 12px. A issue requer alternância claro/escuro. Não houve redesign nem composição visual aprovada. Metáfora criativa, adjetivos de marca e referências subjetivas não foram definidos. DESIGN.md extrai o código; o [brief](specs/017-painel-operacional/brief.md) mantém o contrato específico da superfície.

## Verdade dos dados

Ausência de medição recente significa desconhecido, não disponibilidade. Orçamento de janela parcial é limite máximo; projeção finita exige cobertura integral. MTTD fica sem amostras (n=0) enquanto não existir início real de falha persistido. Integridade JSONL cobre a trilha de sondas e não atesta os eventos PostgreSQL, apresentados separadamente. Horários seguem o navegador e as listagens têm limites explícitos.

## Evidência e limites

O brief registra 16 testes de componentes/parser/sessão, 4 testes PostgreSQL da API (incluindo orçamento exatamente esgotado), um orquestrador com 4 histórias reais de navegador, 3 regressões do diagnóstico, build e lint aprovados. Axe encontrou zero violações nas capturas locais iniciais, mas a CI posterior detectou contraste de 2.1:1 na cor intermediária do botão Atualizar saúde após alternar para claro. A transição de cores foi removida; a nova verificação após essa correção ainda não está registrada aqui. Esses ensaios não certificam acessibilidade integral. A revisão visual recebeu seis capturas `.impeccable/review/panel-*.png` e apontou como pendência documental a ausência deste arquivo.

Execução local com Chrome e PostgreSQL 17 descartável; CI com Chromium e PostgreSQL 15 executou 458 testes aprovados e 1 falha de contraste antes da correção; não se afirma sucesso da reexecução após a correção. Dados e alvos sintéticos não homologam uma rede hospitalar real. Motor Impeccable 0.1.15 e detector indisponíveis: evidência por leitura direta, capturas e revisão técnica.

Fontes: [README](README.md), [brief](specs/017-painel-operacional/brief.md) e `sigma-frontend/src/{App.jsx,Operations.jsx,OperationalPages.jsx,App.css,index.css}`.
