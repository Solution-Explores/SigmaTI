# Redesenho do SigmaTI — validação local

Data: 17/10/2026. Implementação local; sem publicação, commit ou alteração do backend. Alterações preexistentes no workspace foram preservadas.

## Entrega

Quatro seções em React: visão geral, incidentes, equipamentos e simulador conectado ao contrato existente. Temas claro/escuro, preferência de tema opcional no navegador, navegação por fragmentos, filtros e detalhes expansíveis. Base demonstrativa fixa: seis equipamentos e oito incidentes; indicadores derivados: seis equipamentos, quatro incidentes ativos, três ativos de severidade alta/crítica e quatro resolvidos.

Sistema visual em `design-system/MASTER.md`. Nenhum novo pacote de produção ou fonte remota foi adicionado.

## Evidências

- `npm run lint`: aprovado, sem erros. `npm run build`: aprovado, 21 módulos transformados e arquivos de produção gerados.
- `evidencias/layouts.json`: 32 combinações de seção, tema e largura (375, 768, 1024 e 1440 px), sem rolagem horizontal. Menu móvel também conferido.
- `evidencias/checks.json`: 20 verificações, nove requisições interceptadas, nenhum erro JavaScript de página.
- `evidencias/accessibility.json`: oito verificações de contraste e controles, com mínimo observado de 5,47:1 nos textos avaliados; detalhes expandidos conferidos nas quatro larguras e acionamento por teclado.
- Oito imagens PNG: visão geral e simulador, temas claro/escuro, desktop e celular. Inspeção visual confirma hierarquia, alinhamento e empilhamento dos painéis.

## Cenários exercitados

- Indicadores coerentes com a base fictícia; nenhuma chamada automática à API.
- Pesquisa por texto e acentos, combinação de filtros, resultados vazios e detalhes dos incidentes; pesquisa por IP/setor e incidentes relacionados dos equipamentos.
- Fragmentos de URL, recarregamento, voltar/avançar e foco no título após navegação.
- Campos obrigatórios e rejeição de conteúdo formado somente por espaços.
- Processamento, desabilitação do formulário e bloqueio de submissões duplicadas, preservando os três campos do contrato.
- Sucesso com resposta textual contendo HTML literal e sequência longa: sem execução de HTML e sem overflow nas quatro larguras.
- IA indisponível com HTTP 200, HTTP 422/500, conexão recusada, JSON inválido e formato de resposta inválido.
- Timeout real de 20 segundos, sem repetição automática; dados do formulário preservados.
- Formulário e resposta preservados ao mudar de seção; indicadores demonstrativos permanecem isolados.
- Preferência de tema após recarga, tema do sistema quando o armazenamento é bloqueado e alternância ainda funcional.
- Link para pular navegação, foco visível, detalhes acionáveis por Enter e alvos interativos com altura mínima de 44 px.
- Preferência por redução de movimento desativa a animação do processamento.

## Ambiente e limites

Testes com Chrome headless e Playwright do runtime local; Vite em `127.0.0.1:5174`, com a rota da API interceptada. Nenhuma chamada ao provedor de IA e nenhum dado real utilizado. Uma instância preexistente em `127.0.0.1:5173` foi identificada como o mesmo frontend atualizado; ela foi preservada.

O contrato foi comparado com a implementação atual de `main.py`. A disponibilidade do backend, autenticação, persistência e anonimização completa não fazem parte desta entrega. Para envio real de testes, a API deve estar ativa e autorizar a origem exata do frontend; a configuração de exemplo autoriza a porta 5173.

A auditoria cobre contraste calculado de textos visíveis sobre fundos sólidos e verificação de nomes de controles; não substitui avaliação completa com leitores de tela ou certificação de acessibilidade.

## Reproduzir

Na pasta `sigma-frontend`, executar `npm run lint`, `npm run build` e os dois scripts descritos no README do frontend. A compilação depende da permissão para criar subprocessos do Vite neste ambiente Windows; o primeiro bloqueio de sandbox foi resolvido executando a mesma compilação com autorização.
