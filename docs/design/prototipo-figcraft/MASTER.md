# SigmaTI — sistema visual

Painel operacional demonstrativo para equipes de TI hospitalar. Baseado no fluxo da skill ui-ux-pro-max, adaptado para uma aplicação de trabalho, sem elementos de landing page ou alegações de certificação.

## Fundamentos

Fonte: Segoe UI, system-ui, -apple-system, sans-serif; corpo 16px/1.5. Título principal 32px (26px no celular), seções 18px, formulários 14px. Metadados compactos 10–12px, com contraste validado. Sem fontes remotas.

Tokens em `sigma-frontend/src/tokens.css`. Escala de espaçamento: 4, 8, 12, 16, 24, 32, 48px. Cartões: raio 12px; controles: 8px. Alvos interativos: pelo menos 44px de altura. Ícones SVG locais, traço consistente, decorativos com aria-hidden.

| Função | Claro | Escuro |
|---|---|---|
| Fundo | #F8FAFC | #0B1220 |
| Superfície | #FFFFFF | #111C2E |
| Texto | #0F172A | #F1F5F9 |
| Texto secundário | #526176 | #A7B6CB |
| Destaque | #1D4ED8 | #60A5FA |
| Texto sobre destaque | #FFFFFF | #0B1220 |
| Sucesso / fundo | #166534 / #F0FDF4 | #86EFAC / #123227 |
| Atenção / fundo | #92400E / #FFFBEB | #FCD34D / #352A17 |
| Erro / fundo | #B91C1C / #FEF2F2 | #FCA5A5 / #3B1E2A |
| Informação / fundo | #1E40AF / #EFF6FF | #93C5FD / #172D4A |

## Comportamentos

- Tema inicial do sistema; preferência explícita em `sigma-theme-v1`. Armazenamento indisponível não bloqueia o aplicativo. Nenhum dado de incidente é persistido no navegador.
- Menu lateral a partir de 1024px; abaixo disso, menu expansível no fluxo. Tabelas tornam-se cartões abaixo de 768px. Navegação por fragmentos com foco no título da página.
- Estados sempre incluem texto e ícone. Indicadores e distribuição derivados da mesma base fictícia de seis equipamentos e oito incidentes.
- Três seções demonstrativas identificadas; simulador separado, sem chamadas automáticas. Não sugerir disponibilidade real da rede ou conformidade LGPD.
- Foco visível de 3px; link para pular navegação; formulários rotulados; avisos em regiões vivas; redução de movimento respeitada. Texto da API renderizado sem HTML e com quebra de palavras longas.
- Transições de cor/fundo de 180ms. Sem movimentos que alterem o layout no hover.

## Validação

Verificar ambos os temas em 375, 768, 1024 e 1440px, contraste de texto >=4.5:1, teclado, filtros vazios, detalhes, retorno/avanço, preferência de tema e falhas de API. Ver registro de validação da entrega em `specs/redesenho-interface/validacao.md`.

## Investigação de incidentes

A visão geral prioriza incidentes ativos críticos/altos; distribuição por severidade vem depois no fluxo de leitura. Em desktop acima de 1100px, lista e distribuição aparecem lado a lado, com mais espaço para a lista. Em telas menores, os incidentes vêm primeiro. A simulação permanece no menu e em um link secundário ao final da visão geral.

Indicadores e severidades são botões que aplicam um conjunto de filtros em memória e navegam para o fragmento correspondente. Não representam URLs compartilháveis de consultas. Equipamentos abre o inventário completo; Ativos abre abertos/em análise; Criticidade alta combina críticos e altos ativos; Resolvidos abre encerrados; cada severidade abre o subconjunto ativo correspondente, mesmo vazio.

O menu mostra a quantidade de ativos explicitamente. A primeira entrada em Incidentes usa Ativos; retornar pelo menu conserva a investigação anterior. Situação oferece Ativos, Todos, Abertos, Em análise e Resolvidos; Severidade inclui Crítica e alta. Limpar filtros remove busca/severidade e seleciona Todos. Busca aceita ID, equipamento, título e descrição, sem distinção de acentos ou maiúsculas.

Busca, filtros e registros expandidos pertencem ao estado de App, em memória. Identificadores controlam a expansão compartilhada entre desktop e celular. Recarregar volta ao padrão; voltar/avançar preserva o último estado da seção na sessão, sem histórico de cada mudança de filtro. Nome acessível de cada expansão identifica o incidente ou equipamento.

Evidências atuais e revisão heurística: `docs/specs/ajustes-investigacao/validacao.md`. O registro do redesenho inicial permanece como histórico.
