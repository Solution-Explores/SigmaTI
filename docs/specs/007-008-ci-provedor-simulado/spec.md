# K08 e K07 — CI reproduzível e API com provedor simulado

Data: 19/10/2026. Base: `dev@f4c2a5e`.

Referências: [K08](https://trello.com/c/sTTArNVt),
[K07](https://trello.com/c/D3LstOrT), [issue #4](https://github.com/Solution-Explores/SigmaTI/issues/4)
e [fluxo de trabalho do TCC](../../processo/fluxo-de-trabalho-tcc.md).

## Escopo e plano

1. Reproduzir os cinco erros de coleta `No module named sigma_eng` no checkout novo.
2. Configurar o pytest da raiz para coletar API e engenharia no mesmo comando do CI.
3. Reativar os testes HTTP de engenharia sem dependência opcional incorreta,
   usando JWT válido e autenticação ativa.
4. Reaproveitar cobertura K02/K05/K06 e complementar a K07 com login real,
   provedor simulado e recusa de tokens ausentes, inválidos ou expirados.
5. Documentar um roteiro executável de desenvolvimento, revisar a alteração e
   registrar resultados, limitações e achados para K09–K12.

Não há alteração do contrato público da API ou das dependências fixadas.
Empacotamento instalável de `sigma_eng` continua na issue #9; `pytest.ini`
resolve a execução dos testes no checkout, sem prometer instalação do pacote.

## Aceite

- O comando de CI coleta e executa ambas as suítes, sem pular os testes HTTP.
- Login e chamada autenticada ao provedor simulado funcionam; token recusado
  não causa nenhuma chamada ao provedor.
- Sucesso, falhas HTTP/transporte, JSON inválido, concorrência, cancelamento,
  CORS e anonimização são verificados pelas suítes existentes e complementares.
- O timeout real cancela o provedor e responde em até 15 s com mensagem genérica.
- Configuração de credenciais, portas e imagens permanece aprovada.
- Instalação limpa K09 e aceite integrado K10 não são declarados por testes unitários.

## Aplicação do fluxo e revisão

Implementação e testes executados pelo Codex na `dev`. O usuário solicitou nesta
conversa que a revisão também fosse feita aqui, dispensando a espera por outro
integrante nesta execução. A revisão técnica deve ser registrada como feita pelo
Codex, sem atribuir reprodução manual ou revisão independente a uma pessoa.

As etapas de evidências, atualização do quadro e conferência de integração
continuam aplicáveis. Os resultados e a situação de publicação/integração estão
no [registro de evidências](evidencias.md). Nenhuma issue deve ser encerrada
automaticamente pela conclusão parcial dessas duas tarefas.
