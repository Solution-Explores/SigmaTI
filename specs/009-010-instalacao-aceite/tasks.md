# Atividades — K09 / K10

## Execução e revisão realizadas

- [x] Ler cartões e aplicar o fluxo do TCC com revisão nesta conversa.
- [x] Criar checkout remoto independente e inicialmente limpo da `dev@142efd2`.
- [x] Criar outro ambiente virtual, instalar dependências fixadas e executar pip check.
- [x] Executar regressão no ambiente novo: 346 aprovados.
- [x] Executar npm ci, build e lint; investigar dependência nativa opcional omitida.
- [x] Repetir npm ci com cache preenchido e --include=optional, preservando o lockfile.
- [x] Iniciar Docker e preparar projeto Compose exclusivo com volumes novos.
- [x] Validar configuração e registrar falha TLS na tentativa de iniciar as imagens fixadas.
- [x] Executar 18 verificações por HTTP real: 16 aprovadas e duas reprovadas.
- [x] Testar o painel no navegador e registrar mensagem incorreta para a resposta 401.
- [x] Revisar o runner e classificar os achados para K11/K12.

## Critérios ainda não atendidos

- [ ] K09: concluir download, inicialização, prontidão e autenticação dos serviços.
- [ ] K09: verificar persistência após recriar contêineres com os mesmos volumes.
- [ ] K10: permitir preflight da origem autorizada com Authorization.
- [ ] K10: comprovar invalidação da sessão após logout.
- [ ] K10: concluir fluxo autenticado no painel e apresentar erros HTTP corretamente.
- [ ] Reexecutar o aceite depois das correções de K11/K12.

Testes executados não equivalem a aceite aprovado. Os cartões permanecem **Em
andamento**, com bloqueios documentados. Integração na main e conclusão das
issues continuam condicionadas ao aceite do conjunto.
