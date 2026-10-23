# SIGMA: contexto do produto

SIGMA é um MVP de TCC de monitoramento ativo de rede com apoio de IA, para a equipe de TI de um hospital oncológico de fundação pública. O objetivo é reduzir a descoberta reativa de falhas e a falta de histórico. As metas do README são requisitos, não garantia de operação hospitalar homologada.

## Painel operacional

O painel mantém login, logout e diagnóstico, e acrescenta quatro áreas alimentadas pela API:

- **Saúde dos serviços:** medições, cobertura e orçamento de erros.
- **Incidentes:** reconhecer e resolver, com média, mediana e p95.
- **Aprovações:** solicitações e decisões justificadas, com papel mínimo e outro operador. A página não executa comandos.
- **Auditoria:** separa a integridade da trilha de sondas dos eventos operacionais.

| Perfil | Visibilidade |
|---|---|
| `suporte_n1` | Saúde e diagnóstico |
| `analista_redes` | Áreas anteriores, incidentes e aprovações |
| `gestor_ti` | Todas, incluindo auditoria |

A API também aplica a autorização. O SSE autenticado usa Bearer, cursor `Last-Event-ID` e reconexão progressiva. Ao reconectar, os dados são atualizados, e há uma consulta de recuperação a cada 15 s. Sessão e cursor ficam em memória no navegador, então recarregar exige login. Se a API operacional estiver indisponível, o painel mostra um erro explícito, sem dados fictícios no lugar.

## Direção visual

O painel estende a identidade existente: azul sobre fundo escuro, fonte de sistema e painéis planos com borda e raio de 12 px. A issue pede alternância entre tema claro e escuro. Não houve redesign nem composição visual aprovada, e não foram definidos metáfora criativa, adjetivos de marca nem referências subjetivas. O [DESIGN.md](DESIGN.md) extrai o código, e o [brief](specs/017-painel-operacional/brief.md) guarda o contrato da superfície.

## Verdade dos dados

- Sem medição recente, o estado é desconhecido, não disponível.
- O orçamento de uma janela parcial é um limite máximo. A projeção finita exige cobertura integral da janela.
- O MTTD fica sem amostras (n=0) enquanto não houver um início real de falha gravado.
- A integridade JSONL cobre a trilha de sondas. Ela não atesta os eventos do PostgreSQL, que aparecem à parte.
- Os horários seguem o navegador, e as listagens têm limites explícitos.

## Evidência e limites

O [brief](specs/017-painel-operacional/brief.md) registra:

- 16 testes de componentes, parser e sessão;
- 4 testes PostgreSQL da API, incluindo orçamento exatamente esgotado;
- um orquestrador com 4 histórias reais de navegador;
- 3 regressões do diagnóstico;
- build e lint aprovados.

O Axe não achou violações nas capturas locais iniciais. A CI depois apontou contraste de 2.1:1 na cor intermediária do botão Atualizar saúde ao alternar para o tema claro. A transição de cores foi removida, mas a nova verificação ainda não está registrada. Esses ensaios não certificam acessibilidade integral.

A revisão visual recebeu seis capturas `.impeccable/review/panel-*.png` e apontou a falta deste arquivo como pendência documental.

A execução local usou Chrome e PostgreSQL 17 descartável. A CI, com Chromium e PostgreSQL 15, teve 458 testes aprovados e 1 falha de contraste antes da correção. O sucesso da reexecução depois da correção não está afirmado. Dados e alvos sintéticos não homologam uma rede hospitalar real. O motor Impeccable 0.1.15 e o detector não estavam disponíveis, então a evidência vem de leitura direta, capturas e revisão técnica.

Fontes: [README](README.md), [brief](specs/017-painel-operacional/brief.md) e `sigma-frontend/src/{App.jsx,Operations.jsx,OperationalPages.jsx,App.css,index.css}`.
