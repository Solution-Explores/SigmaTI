# Mapa dos espaços do projeto

Onde fica cada coisa do SigmaTI e qual espaço vale quando houver divergência.

[Voltar ao índice do planejamento](README.md)

## Regra: o repositório vence

O repositório GitHub é a fonte da verdade. Issues, milestones e os documentos de `docs/planejamento/` definem escopo, responsáveis e prazos. Trello, Miro e Drive refletem o repositório. Se algo divergir, corrige-se o outro espaço; nada é apagado, o que não vale mais é arquivado.

## Espaços

| Espaço | Função | Link | Dono |
|---|---|---|---|
| GitHub | Código, issues, milestones, PRs e documentação | [Solution-Explores/SigmaTI](https://github.com/Solution-Explores/SigmaTI) | Equipe |
| Trello | Quadro de acompanhamento das tarefas (um cartão por issue e por marco) | [SigmaTI](https://trello.com/b/vswV1j1T/sigmati) | Vinícius |
| Miro | Arquitetura, fluxo do incidente e linha do tempo | [Board do Sigma](https://miro.com/app/board/uXjVG2r-Qbk=/) | Vinícius |
| Drive | Documentos do TCC: diário de bordo, projeto, orçamento, design e entrega final | [documentos-sigmati](https://drive.google.com/drive/folders/1KqGK1idsrPP1QwAmazULLcTq8Wo45E2n) | Vinícius |

## Como o Trello reflete o repositório

- Um cartão por issue aberta, com o link da issue, o milestone e o prazo do milestone.
- Sprint 1 (03/11): #56, #5, #25, #13, release `v1.0.0` e triagem. Sprint 2 (10/11): #45, #8, #46, #57 e validação final. Sprint 3 (17/11): congelamento em 11/11, ensaio em 13 e 14/11, checklist final e banca em 18/11.
- Sprint 4 (depois da banca): um cartão por grupo, sem data, com a etiqueta "Pós-banca".
- Cartões do design system (DS) e da API pertencem à Joyce e seguem os PRs #52 a #55; as datas só mudam com o aval dela e do orientador.

## Estrutura do Drive

| Pasta | Conteúdo |
|---|---|
| `01_desenvolvimento` | Atas de reunião, design (logotipo e sistema tipográfico) e diário de bordo |
| `02_documentação` | Projeto básico, plano e escopo, estudo de caso, orçamento e material do orientador |
| `03_entre_pacial` | Entregas parciais |
| `04_entrega_final` | Pitch, TCC, artigo e checklist da banca de 18/11 |

Versões antigas dos documentos ficam em `02_documentação/projeto/_arquivo`. O `00_LEIA-ME` na raiz da pasta aponta para os quatro espaços.

## Quando atualizar

Depois de cada mudança de issue, milestone ou plano no repositório, ajuste o cartão do Trello correspondente. O Miro e o Drive são revisados no congelamento (11/11) e antes da banca (17/11).
