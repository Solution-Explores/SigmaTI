# Atividades — K08 e K07

## Implementação, validação e revisão nesta conversa

- [x] Conferir cartões, issue #4, `dev` remota e fluxo de trabalho do TCC.
- [x] Trabalhar no clone novo, preservando a cópia anterior em `sigma-teste`.
- [x] Preparar um ambiente virtual novo com as dependências fixadas.
- [x] Reproduzir os cinco erros de coleta do CI.
- [x] Configurar coleta e importações de API e engenharia com `pytest.ini`.
- [x] Retirar o skip incorreto dos testes HTTP de engenharia e usar JWT válido.
- [x] Corrigir as aspas do caminho Python no teste de runbook para Windows.
- [x] Conferir cobertura existente K02/K05/K06 e complementar a K07 autenticada.
- [x] Validar timeout real, cancelamento, erros genéricos e ausência de chamada sem token.
- [x] Executar 346 testes sem falhas, erros ou ignorados e 58 testes de engenharia isolados.
- [x] Revalidar 32 checks de credenciais, 12 cenários de infraestrutura e manifests oficiais.
- [x] Preparar o roteiro de instalação e registrar limites de K09/K10.
- [x] Revisar a alteração nesta conversa, conforme solicitado pelo usuário.
- [x] Reproduzir e registrar achados existentes de autenticação/CORS para K11.
- [x] Conferir diferenças e ausência de segredos ou arquivos locais na entrega.
- [x] Corrigir em branch separada a corrida do teste de porta fechada revelada no CI Linux.

## Publicação e entrega

- [x] Publicar a implementação inicial na `dev` e inspecionar os dois CIs.
- [x] Integrar a correção à `dev` e verificar os dois CIs remotos do conjunto corrigido.
- [x] Registrar referências de publicação e atualizar os cartões para Revisão e testes, com revisão técnica realizada.

O usuário dispensou a espera por revisão de outro integrante nesta execução;
a revisão registrada é do próprio Codex e está concluída. A integração do conjunto
na `main` pertence à K13, após aceite K10 e correções K11/K12. K09 e o aceite
integral das issues também permanecem tarefas separadas, com os limites em
[evidencias.md](evidencias.md).
