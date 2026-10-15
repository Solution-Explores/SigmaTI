# Fluxo de trabalho do TCC — SIGMA

Este é o fluxo da equipe para desenvolver as tarefas do planejamento e atender
às issues do GitHub. O trabalho acontece diretamente na `dev`; uma branch
separada é criada para corrigir erros identificados na revisão. A integração à
`main` ocorre depois da aprovação e da validação do conjunto na `dev`.

## Fluxo

```mermaid
flowchart TD
    inicio(["INÍCIO"])
    leitura["1. Ler a issue no GitHub<br/>Pedido, critérios, dependências e responsável"]
    desenvolvimento["2. Desenvolver na dev<br/>Alterações e commits"]
    testes["3. Testar e registrar resultados"]
    revisao["4. Outro integrante revisa e valida"]
    aprovado{"Foi aprovado?"}
    correcao["Criar branch de correção<br/>Corrigir, testar e integrar à dev"]
    integracao["5. Integrar à main<br/>Após validar o conjunto na dev"]
    evidencia["6. Comentar na issue<br/>O que foi feito, links e evidências"]
    conclusao["7. Concluir a tarefa<br/>Fechar a issue só com todos os requisitos atendidos"]
    fim(["FIM"])

    inicio --> leitura --> desenvolvimento --> testes --> revisao --> aprovado
    aprovado -->|Não| correcao
    correcao --> revisao
    aprovado -->|Sim| integracao
    integracao --> evidencia --> conclusao --> fim
```

Durante todo o processo, documente **o que mudou, por que mudou, as decisões
tomadas, como foi testado, os resultados e as pendências**. Use comentários na
issue, mensagens de commit e a documentação do repositório; o registro final
consolida as evidências produzidas durante o trabalho.

## Como trabalhar uma issue

1. **Entenda o pedido completo.** Leia título, corpo, critérios de aceite,
   comentários e especificações vinculadas. O checklist resume o pedido, mas
   não elimina requisitos descritos no corpo. Confira as dependências e registre
   um responsável pela tarefa e um colega que fará a revisão.
2. **Relacione issue e planejamento.** Identifique qual cartão da sprint atende
   a qual parte da issue. Uma issue pode exigir várias tarefas; concluir um cartão
   não significa cumprir a issue inteira. Registre o escopo e as pendências antes
   de começar e mova o cartão para **Em andamento**.
3. **Desenvolva na `dev`.** Atualize a base antes de começar, coordene mudanças
   simultâneas com a equipe e preserve alterações de outros integrantes. Faça
   commits com uma descrição do resultado e referência à issue. Não é necessário
   criar uma branch por tarefa.
4. **Teste e produza evidências.** Execute as verificações dos critérios de aceite
   e as verificações afetadas pela mudança. Registre comandos, ambiente, resultado
   esperado, resultado obtido e links para commits, testes ou arquivos. Use dados
   fictícios; não inclua chaves, senhas ou dados reais do hospital nas evidências.
5. **Peça revisão a outro integrante.** Mova o cartão para **Revisão e testes**.
   O colega compara a alteração ao pedido completo e valida os resultados.
   Se houver reprovação, registre os achados, crie uma branch de correção a partir
   da `dev`, corrija e teste. Integre a correção à `dev` e retorne à revisão.
6. **Integre o conjunto aprovado à `main`.** Valide na `dev` o funcionamento das
   mudanças em conjunto antes da integração. Atualize a documentação conforme o
   comportamento entregue. A etapa do diagrama descreve o processo da equipe;
   não dispensa os testes nem a aprovação do colega.
7. **Registre a entrega e atualize o quadro.** Comente na issue o que foi feito,
   os links, a revisão e as evidências. Marque os critérios realmente atendidos.
   Mova a tarefa para **Concluído** quando seu escopo estiver aprovado e entregue.
   Feche a issue somente quando todos os seus requisitos estiverem atendidos;
   se a entrega for parcial, deixe-a aberta e identifique as tarefas restantes.

## Colunas do quadro

| Coluna | Quando usar |
|---|---|
| A fazer | Tarefa identificada, com escopo, responsável e dependências registrados. |
| Em andamento | Desenvolvimento na `dev` ou correção dos achados em execução. |
| Revisão e testes | Alteração pronta para validação e revisão por outro integrante, com evidências disponíveis. |
| Concluído | Escopo da tarefa aprovado e entregue; a issue só fecha se seus requisitos completos também estiverem atendidos. |

## Exemplos de comentários

Os modelos abaixo são exemplos para a equipe preencher. Publicar este documento
não cria comentários nas issues.

**Comentário inicial:**

```text
Iniciando a tarefa [Kxx], vinculada à issue #[número].
Responsável: [nome]. Revisor: [outro integrante].
Escopo desta entrega: [parte do pedido que será atendida].
Critérios a validar: [critérios do corpo e do checklist].
Dependências e pendências: [listar ou indicar nenhuma].
Trabalho na dev; evidências serão registradas nesta issue e na documentação.
```

**Comentário final:**

```text
Entrega da tarefa [Kxx] vinculada à issue #[número].
O que mudou e por quê: [resumo e decisões].
Commits / integração / documentação: [links].
Testes: [comandos, ambiente e resultados].
Evidências: [links].
Revisão: [nome do colega e registro da aprovação].
Critérios atendidos: [listar].
Pendências: [listar ou indicar nenhuma].
Situação da issue: [manter aberta por entrega parcial / fechar após atender tudo].
```

## Aplicação às issues atuais

Esta tabela orienta a conferência do pedido; **não declara que os critérios já
foram implementados ou validados**. A descrição atual de cada issue no GitHub
continua sendo a referência para a entrega.

| Issue | Conferências necessárias |
|---|---|
| [#2 — Docker Compose](https://github.com/Solution-Explores/SigmaTI/issues/2) | `docker compose config --quiet` aprovado localmente e no CI; arquivo sem marcadores de conflito; README e documentação da stack coerentes com os serviços mantidos. |
| [#3 — Credenciais, portas e imagens](https://github.com/Solution-Explores/SigmaTI/issues/3) | `.env.example` presente e `.env` ignorado; nenhuma senha literal versionada; imagens com versões fixadas e sem tags `latest`; conferir também o corpo: banco na rede interna, portas restritas, n8n acessível pela gerência/VPN e política de atualização documentada. |
| [#4 — Configuração e chamada à IA](https://github.com/Solution-Explores/SigmaTI/issues/4) | Sem segredo no código e API falhando ao iniciar sem chave; origem não autorizada recusada; teste com provedor simulado demonstrando timeout de até 15 s e erro público genérico; conferir também chamada assíncrona, modelo e origens por ambiente e registro dos detalhes de falha em log. |

Por exemplo, a K02 cobre a configuração por ambiente da issue #4. Só essa entrega
não permite fechar a issue: ainda é necessário validar os demais critérios,
incluindo chamada assíncrona, timeout e tratamento de erros.

[Voltar ao README](../README.md)
