# Atividades da Joyce (plano do orientador, atualizado em 02/11/2026)

## Resumo em uma página

**O que você faz**
- Melhora o design do sistema que o Vinícius preparou (o protótipo em `design-system/exemplo/`).
- Programa o visual novo no front (telas, botões, cores, menu).
- Escreve o **diário de bordo** do que produziu em cada dia de trabalho. Assim o Vinícius acompanha o seu progresso lendo o diário, e você não precisa mandar mensagem toda vez. O modelo está na seção "Diário de bordo".

**O que você não faz**
- Não liga o front à API do servidor, não mexe nos arquivos de comunicação (`api.js`, `useResource.js`, `useEvents.js`, `useActionRequest.js`, `mockApi.js`) e não ajusta os testes que usam o sistema de verdade. Isso é do Vinícius e do Iohan.
- Não decide regras do sistema (quem pode ver o quê, tempo de expiração, confirmar antes de resolver incidente). Isso também é deles.

**Para quando**
- O **prazo final das suas atividades é 17/11**, o fim da Sprint 3. É até esse dia que o time produz.
- O orientador tinha marcado o congelamento do código para 11/11. O Vinícius vai pedir a ele que o design e o front da Joyce possam seguir até 17/11. **Enquanto o orientador não responder, a meta segura é entregar o essencial até 11/11** e o resto até 17/11.
- O Vinícius ajuda você no desenvolvimento quando for preciso.
- A banca é entre **01 e 10/12** (edital). Em **18/11** começa a preparação da apresentação.
- Não cabe tudo até 17/11. Veja a seção "O que entra até 17/11".

**Como o trabalho anda**
1. O Vinícius e o Iohan arrumam a base de trabalho (seção "Onde você trabalha").
2. Você faz uma tarefa por vez, em um PR pequeno (pedido de revisão no GitHub).
3. Você avisa o Vinícius e o Iohan quando um PR estiver pronto. Eles revisam, testam com o sistema de verdade e integram.
4. No fim de cada dia de trabalho, você escreve o seu diário de bordo. Uma vez por semana, você abre um PR só com os diários.

## Por onde começar

1. Leia este resumo e as 7 tarefas do grupo A.
2. Continue na sua branch atual até o Vinícius avisar que a base nova está pronta.
3. Faça a DS-01 e a DS-02, uma de cada vez, cada uma em um PR pequeno.
4. No fim de cada dia, escreva o diário de bordo.
5. Uma vez por semana, abra o PR dos diários.
6. Se tiver dúvida ou algo bloquear o seu trabalho, avise o Vinícius na hora.

## Quem faz o quê

| Tema | Joyce | Vinícius e Iohan |
|---|---|---|
| Desenho, marca, cores, fonte | Faz | Aprovam a marca |
| Programar o visual no front | Faz | Revisam |
| Testes pequenos do front (`npm test`) | Faz | Revisam |
| Testes que usam o sistema de verdade (E2E) e a verificação de acessibilidade (axe) | Lista o que pode quebrar | Ajustam e rodam |
| Arquivos de comunicação com a API e o mock | Não mexe | Fazem |
| Regras de perfil e de comportamento | Não mexe | Decidem |
| Base de trabalho, merge na `develop` | Não faz | Fazem |
| Ajuda no desenvolvimento do front | Recebe | O Vinícius ajuda quando for preciso |
| Diário de bordo do que a Joyce produziu | Escreve um por dia e abre um PR só dos diários, uma vez por semana | O Vinícius lê e usa para acompanhar e analisar |

## Onde você trabalha

Hoje a sua branch (`feature/front-design-system`) está bem atrás da `develop` (46 mudanças) e usa a pasta antiga `sigma-frontend/`. Na `develop` a pasta se chama `frontend/`. Por isso o guia de instalação antigo não funciona na `develop`: lá não existe o mock (`npm run dev:mock`) nem a pasta `design-system/`.

Decisão do Vinícius, em dois passos:
1. **Agora:** o Vinícius (ou o Iohan) coloca na sua branch o commit `8661916`. Isso faz o teste `validate-compose` voltar a ficar verde nos PRs #52 a #55.
2. **Depois:** o Vinícius cria uma base nova a partir da `develop`, com o mock e os seus documentos na pasta `frontend/`, e o Iohan revisa. **Você não resolve conflitos de pasta.**

Até a base nova ficar pronta, continue na sua branch atual. Quando o Vinícius avisar, troque para a nova.

## Prazos (plano do orientador)

| Quando | O que acontece |
|---|---|
| 03/11 | Fim da Sprint 1 (v1.0.0) |
| 10/11 | Fim da Sprint 2 |
| 11/11 | Congelamento do código do produto marcado pelo orientador (só correção de bug urgente). O Vinícius vai pedir prorrogação do design e do front da Joyce |
| **17/11** | **Fim da Sprint 3 e prazo final das atividades da Joyce** (texto do TCC, ensaio) |
| 18/11 | Início da preparação da apresentação (banca entre 01 e 10/12) |

## O que entra até 17/11

Estimativa: as 34 tarefas do backlog somam cerca de 26 dias de trabalho. De 03/11 a 17/11 há 11 dias úteis. Ainda não cabe tudo, e é preciso deixar folga para revisão e retoque. Por isso o recorte abaixo. Eu não sei a sua disponibilidade real; ajuste junto com o Vinícius.

| Grupo | Tarefas | Observação |
|---|---|---|
| **A. Essencial, meta até 11/11** (código) | DS-01 (versão curta), DS-02, DS-03 + DS-05, DS-06, DS-08, DS-09, DS-10 | Cerca de 5 a 6 dias de trabalho. É a parte que não pode ficar de fora |
| **B. Até 17/11** (código) | DS-07, DS-11, DS-12, DS-13 + DS-14 | Entram se o orientador aprovar a prorrogação até 17/11. Sem a aprovação, ficam na sua branch e entram depois da banca |
| **C. Até 17/11** (desenho e documentos) | DS-04, NOVA-1 (Aprovações), NOVA-2 (Diagnóstico, Saúde e Auditoria), capturas de tela parciais (DS-32 e DS-33), DS-34 (documento do que foi feito) | Andam em paralelo com o código. Não mexem no produto |
| **Depois da banca** | DS-15 a DS-31, e DS-32 e DS-33 completas | Não cabe até 17/11 |
| **Fora do seu escopo** | DS-35 a DS-42 | Dependem de API nova. Ficam como trabalho futuro de integração |

O tempo dos desenhos NOVA-1 e NOVA-2 é uma estimativa minha (cerca de 1 dia cada), porque o backlog não os tinha. Com a ajuda do Vinícius no desenvolvimento, é possível que parte do grupo B seja puxada para o prazo, mas isso depende da disponibilidade dele.

Sugestão de ritmo (só uma proposta, para combinar):
- Até 05/11: base nova pronta e DS-01 e DS-02 em revisão.
- 07/11: conversa rápida de acompanhamento.
- Até 11/11: DS-03 + DS-05, DS-06, DS-08, DS-09 e DS-10 prontas e em revisão (grupo A).
- 12 a 15/11: grupo B (DS-07, DS-11, DS-12, DS-13 + DS-14) e os desenhos NOVA-1 e NOVA-2.
- 16 e 17/11: DS-04, capturas parciais, DS-34 e ajustes de revisão. **17/11: prazo final.**

## Tarefas do grupo A (essencial, meta até 11/11)

### DS-01. Conhecer o sistema de exemplo e anotar o que cada perfil vê (pequena)
- **O que fazer:** abra o mock, entre com os três usuários (`suporte.joyce`, `analista.joyce`, `gestor.joyce`, qualquer senha) e anote as áreas que cada um vê. Tire as capturas.
- **Por que:** para saber o que cada perfil realmente pode ver antes de redesenhar.
- **Pronto quando:**
  - existe o documento `ambientacao.md` com as capturas;
  - as quatro situações do mock (`?cenario=vazio`, `erro`, `lento`, `falha-trilha`) estão registradas.
- **Situação:** PR #52, aberto e só com documentação.

### DS-02. Arrumar a ordem dos títulos na tela de Diagnóstico (pequena)
- **O que fazer:** deixar os títulos em ordem (1, 2, 3, 4), sem pular nível, para o leitor de tela entender a página.
- **Por que:** hoje "Enviar alerta" e "Resultado" continuam no nível 2 e os títulos de dentro passaram para o nível 4. Pula o nível 3.
- **Pronto quando:**
  - a ordem dos títulos está correta e o estilo (`App.css`) afeta os títulos certos;
  - o texto da descrição do PR bate com o que o código faz;
  - `npm run lint`, `npm test` e `npm run build` passam.
- **Situação:** PR #53. **Não integrar como está.** A descrição diz que mudou de nível 2 para 3, mas o código não faz isso.

### DS-03 + DS-05. Escolher a marca, a paleta e a fonte (média + pequena, juntas)
- **O que fazer:** escolher uma variante da marca e uma paleta oficial, e escolher a fonte conferindo a licença de uso.
- **Por que:** definir uma identidade clara, sem confundir a marca com "serviço disponível", e sem depender de uma fonte baixada da internet.
- **Pronto quando:**
  - existe um documento com a decisão (hoje o PR #54 está com esse registro em branco);
  - a decisão foi aprovada pelo Vinícius.
- **Atenção:** nenhuma cor do painel muda antes dessa aprovação.

### DS-06. Reunir as cores e medidas em um único lugar (pequena)
- **O que fazer:** juntar as cores, fontes e espaços do sistema em um arquivo só, **sem mudar a aparência**.
- **Por que:** para a equipe ajustar o visual em um lugar só.
- **Pronto quando:**
  - a tela fica igual à de antes (confira com as capturas);
  - os três comandos do front passam.

### DS-08. Criar os dois temas e medir a legibilidade (média)
- **O que fazer:** aplicar a paleta aprovada nos temas claro e escuro e medir se o texto fica fácil de ler.
- **Por que:** manter a leitura e os estados confiáveis nos dois temas.
- **Pronto quando:**
  - existe `contraste.md` com as medidas;
  - os itens abaixo estão resolvidos (veja "Cores que faltam").
- **Cores que faltam definir (resumo):**
  - uma borda de campo mais forte, separada da linha suave decorativa;
  - cor do foco do teclado;
  - fundo dos campos;
  - cor de "sem dado" que não pareça verde;
  - botão desabilitado que não dependa só de cor e de transparência.

### DS-09. Botão com todos os estados (média)
- **O que fazer:** botão principal, secundário, de perigo, ocupado e desabilitado.
- **Por que:** distinguir os estados sem depender só de transparência.
- **Pronto quando:** cada estado tem texto ou forma diferente, nos dois temas.
- **Atenção:** a confirmação antes de "Resolver incidente" não entra aqui. Documente só uma proposta visual. A decisão é do Vinícius e do Iohan.

### DS-10. Etiquetas de estado e prioridade (pequena)
- **O que fazer:** padronizar as etiquetas de disponibilidade, prioridade e orçamento.
- **Por que:** a pessoa deve entender o estado sem depender só da cor.
- **Pronto quando:** toda etiqueta tem texto, em claro e escuro.

## Tarefas do grupo B (código, até 17/11 se o orientador aprovar)

- **DS-07. Escalas de espaço e de texto aprovadas (pequena):** melhora o ritmo de leitura, inclusive com nomes longos.
- **DS-11. Painéis e títulos (pequena):** organiza os grupos de conteúdo com o mesmo contorno e a mesma hierarquia.
- **DS-12. Tabela acessível (média):** tabela com legenda, cabeçalhos e rolagem só dentro dela, sem perder a leitura por teclado.
- **DS-13 + DS-14. Alertas, mensagens e estados vazio e carregando (pequenas, juntas):** deixar claro o que é erro, informação, sucesso, carregamento e lista vazia.

## Tarefas do grupo C (desenho e documentos, até 17/11)

- **DS-04. Logotipo em vetor para os dois temas (média):** já existe o PR #55 com 9 SVGs. Depende da decisão da marca.
- **DS-34. Documento do que foi feito e do que falta (média):** escreva só o que foi entregue, sem misturar protótipo com produto.
- **Capturas parciais (DS-32 e DS-33):** das telas que ficarem prontas.
- **NOVA-1. Desenhar a tela de Aprovações ("quatro olhos"):**
  - O protótipo não tem essa tela, mas ela é obrigatória no painel.
  - Desenhe nos dois temas: aprovação própria (bloqueada), perfil insuficiente e solicitação expirada.
  - Mostre sempre a justificativa, o autor e a expiração.
  - Cuide só do visual. A regra (quem pode aprovar) continua igual.
- **NOVA-2. Desenhar Diagnóstico, Saúde por serviço e Auditoria nos dois temas:**
  - Diagnóstico atual (enviar alerta, resultado, o que vai para a nuvem) não existe no protótipo.
  - A Saúde precisa mostrar "Até X min", orçamento e "Sem dados recentes".
  - A Auditoria precisa mostrar se a trilha está íntegra e separar isso dos eventos.

## Todas as tarefas

A coluna **Tipo** diz o que é: **D** = desenho ou documento, **F** = programar o visual no front, **I** = integração (não é sua). A coluna **Quando** usa os grupos da seção "O que entra até 17/11" (A, B e C). Tarefas "juntas" são feitas em um PR só, para economizar tempo.

| Id | O que fazer | Tipo | Quando |
|---|---|---|---|
| DS-01 | Conhecer o mock e anotar o que cada perfil vê | D | A: meta 11/11 |
| DS-02 | Arrumar a ordem dos títulos no Diagnóstico | F | A: meta 11/11 |
| DS-03 | Escolher marca e paleta | D | A: meta 11/11 (com DS-05) |
| DS-04 | Logotipo em vetor para os dois temas | D | C: até 17/11 |
| DS-05 | Escolher fonte e direitos de uso | D | A: meta 11/11 (com DS-03) |
| DS-06 | Reunir cores e medidas em um lugar | F | A: meta 11/11 |
| DS-07 | Escalas de espaço e de texto | F | B: até 17/11 |
| DS-08 | Dois temas e medida de legibilidade | D + F | A: meta 11/11 |
| DS-09 | Botão com todos os estados | F | A: meta 11/11 |
| DS-10 | Etiquetas de estado e prioridade | F | A: meta 11/11 |
| DS-11 | Painéis e títulos | F | B: até 17/11 |
| DS-12 | Tabela acessível | F | B: até 17/11 |
| DS-13 e DS-14 | Alertas, mensagens, estados vazio e carregando | F | B: até 17/11 (juntas) |
| DS-15 | Campos e mensagens de formulário | F | Depois da banca |
| DS-16 | Cabeçalho com marca e papel por extenso | F | Depois da banca |
| DS-17 | Menu lateral no computador | F | Depois da banca |
| DS-18 | Menu no celular | F | Depois da banca |
| DS-19 | Avisos compactos | F | Depois da banca |
| DS-20 | Login | F | Depois da banca |
| DS-21 e DS-22 | Saúde (computador e celular) | F | Depois da banca (juntas) |
| DS-23 | Tipos e durações dos incidentes | F | Depois da banca |
| DS-24 e DS-25 | Incidentes (computador e celular) | F | Depois da banca (juntas) |
| DS-26 | Pedir aprovação | F | Depois da banca |
| DS-27 | Cartões de decisão (só o visual) | F | Depois da banca. Risco alto |
| DS-28 e DS-29 | Auditoria (computador e celular) | F | Depois da banca (juntas) |
| DS-30 e DS-31 | Diagnóstico: formulário e resultado | F | Depois da banca (juntas) |
| DS-32 e DS-33 | Capturas de todas as telas | D | C: parciais até 17/11, completas depois |
| DS-34 | Documento do que foi feito | D | C: até 17/11, só com o que foi entregue |
| NOVA-1 | Desenhar Aprovações | D | C: até 17/11 |
| NOVA-2 | Desenhar Diagnóstico, Saúde e Auditoria | D | C: até 17/11 |
| DS-35 a DS-42 | Telas que dependem de API nova | I | Fora do seu escopo |

**Sobre a ordem.** Várias tarefas mexem nos mesmos arquivos, por isso a ordem sugerida evita conflito. Mas só estas dependências são reais: DS-08 precisa da paleta (DS-03), DS-16 precisa do logotipo (DS-04) e as telas precisam dos componentes que usam. Escolher a paleta (DS-03) não depende de arrumar os títulos (DS-02).

**DS-27, cuidado.** O cartão de decisão mistura visual com regra de negócio (quatro olhos, expiração, perfil). Você só muda o visual. Quem valida a regra é o Vinícius e o Iohan.

## Regras de cada tarefa

**Para tarefas com código (F):**
1. Mostre os dois temas (claro e escuro), a tela de computador (1440 px) e a de celular (390 px), sem texto cortado. Tire uma captura antes e outra depois.
2. O texto precisa ficar bem legível sobre o fundo, e o foco do teclado precisa aparecer.
3. Todo estado tem texto, não só cor. Falta de dado não é "disponível" nem zero. Mantenha "Sem dados recentes", "Até X min" e "Sem início real de falha registrado".
4. O teclado funciona (Tab, Shift+Tab, Enter e Espaço), há o link "Ir para o conteúdo", os alvos de toque têm pelo menos 44 x 44 px e tudo está em português.
5. Rode `npm run lint`, `npm test` e `npm run build` e anote o resultado no PR.
6. Se mudar um texto visível: liste o texto antes e depois, ajuste os testes pequenos do front (`npm test`) e **liste no PR** quais testes que usam o sistema de verdade podem quebrar. Vinícius e Iohan ajustam esses.
7. Não mexa nos arquivos de comunicação (`api.js`, `useResource.js`, `useEvents.js`, `useActionRequest.js`, `mockApi.js`). Pode alterar os dados de exemplo de campos que já existem em `src/mock/data.js`, rodando também o teste do mock (`mockApi.test.js`). A sua branch já alterou `api.js` e `App.jsx` para o mock; a regra vale daqui para frente.
8. Mexa só no visual. Não refatore regra de perfil, tempos nem login.
9. Para cada tela tocada, confira dados normais, carregando, vazio, erro e sem permissão, nos dois temas e no celular.

**Para tarefas só de documento ou desenho (D):** português claro, capturas quando houver tela, e nada de comandos do front.

**Em todos os dias de trabalho:** escreva o diário de bordo antes de encerrar o dia, e abra o PR dos diários uma vez por semana (veja a seção a seguir).

**Verificação com o sistema de verdade e a acessibilidade automática (axe):** o Vinícius e o Iohan rodam em marcos, não em todo PR: depois da DS-10 e antes do congelamento.

## Diário de bordo

**Para que serve.** É o registro do que você fez em cada dia. Ele ajuda o Vinícius a acompanhar o seu trabalho e a fazer a análise sem depender de mensagens. Ele também é material para o texto do TCC.

**Em resumo.**
- Um arquivo por dia de trabalho.
- Um PR por semana, só com os diários. Não misture com o PR das tarefas.

**Onde guardar.** Na pasta `docs/tcc/diario-bordo/joyce/`, com o nome `AAAA-MM-DD.md` (por exemplo, `2026-11-05.md`). Há um modelo pronto em `docs/tcc/diario-bordo/joyce/_modelo.md`.

**Passo a passo do dia**
1. Copie `_modelo.md` e dê o nome da data de hoje (por exemplo, `2026-11-05.md`).
2. Preencha no fim do dia. Pode ser rápido.
3. Salve o arquivo e faça o commit com a mensagem `docs: diário de DD/MM`.

**Passo a passo da semana (abrir o PR do diário)**
1. Na sexta-feira, ou no último dia de trabalho da semana, crie uma branch nova a partir da `develop`.
2. Coloque nela os diários da semana.
3. Abra um PR com o nome `docs: diário de bordo da Joyce (semana de DD/MM)`.
4. Marque o Vinícius como revisor. Quando ele ler, você integra.

Os comandos, se quiser copiar:

```bash
git switch develop
git pull
git switch -c docs/diario-joyce-AAAA-MM-DD
git add docs/tcc/diario-bordo/joyce
git commit -m "docs: diário de bordo da Joyce (semana de DD/MM)"
git push -u origin HEAD
```

Depois é só abrir o PR no GitHub, com a base na `develop`. Se tiver qualquer dificuldade, o Vinícius mostra uma vez com você.

**Como escrever.**
- Frases curtas e simples. Conte o que aconteceu, na ordem em que aconteceu.
- Divida o dia em turnos: manhã, tarde e noite. Se não trabalhou em um turno, escreva "Sem trabalho neste turno".
- Os horários podem ser aproximados. Diga quando forem.
- Conte só o que está pronto como feito. O que ainda está em andamento vai em "Pendências".
- Sempre que puder, coloque o lugar onde está o resultado: o número do PR, o commit, o arquivo ou a captura de tela.
- Se rodou `npm run lint`, `npm test` ou `npm run build`, escreva o resultado.
- Conte também o que deu errado e o que ficou difícil. Isso ajuda o Vinícius a ajudar você.
- Use só dados fictícios. Nunca escreva senhas nem dados reais de ninguém.

**Modelo.**

```markdown
# Diário de bordo da Joyce: DD/MM/AAAA

## Cabeçalho

| Item | Registro |
|---|---|
| Data | dia da semana, DD/MM/AAAA |
| Turnos em que trabalhei | manhã, tarde, noite |
| Horário de cada turno | início e fim, aproximados |
| Onde trabalhei | computador, local |
| Quem ajudou | nomes, ou "ninguém" |

## Contexto e objetivo

**O que eu planejava fazer hoje.** Tarefas do dia (por exemplo, DS-01 e DS-02).

**Meta do dia.**
1. Primeira meta.
2. Segunda meta.

**Materiais que usei.** Arquivos, programas, links e capturas.

## Descrição da atividade

### Turno da manhã
1. O que eu fiz, em ordem. Onde está o resultado (PR, commit, arquivo). Como eu conferi.

### Turno da tarde
1. O que eu fiz.

### Turno da noite
1. O que eu fiz. Se não trabalhei, escrever "Sem trabalho neste turno".

## O que eu produzi hoje

| O que | Onde está | Situação |
|---|---|---|
| Exemplo: capturas da tela de Saúde | PR #52 | Pronto para revisão |

## Pontos de atenção

**Deu certo**
- O que funcionou bem.

**Deu errado ou ficou incompleto**
- O que não saiu como esperado, e por quê.

**Dúvidas e o que preciso do Vinícius ou do Iohan**
- Perguntas, decisões que dependem deles, algo que bloqueou o meu trabalho.

## Pendências para o próximo dia
- O que fica para continuar.
```

**Como o Vinícius usa.** Ele lê o diário no PR da semana, vê o que foi produzido e onde está, e responde as dúvidas sem precisar de uma mensagem à parte. Se algo for urgente ou estiver bloqueando o seu trabalho, avise também por mensagem, sem esperar o PR da semana.

## PRs que você já abriu (situação em 02/11)

| PR | O que é | Situação |
|---|---|---|
| #52 | DS-01, documento e 7 capturas | Aberto, pronto para revisão. Ninguém revisou ainda |
| #53 | DS-02, ordem dos títulos | Aberto, **precisa de correção** (veja DS-02) |
| #54 | DS-03, marca e paleta | Rascunho. Aguarda a decisão do Vinícius |
| #55 | DS-04, 9 logotipos em SVG | Rascunho, depende do #54. Se a equipe escolher outra marca, fecha sem integrar. Atenção: a base dele é a branch do #54, não a `front-design-system` |

Nos quatro, só o teste `validate-compose` está vermelho. A causa não é o seu trabalho: a base da sua branch é anterior ao commit `8661916`, e o Docker Hub republicou uma imagem. O Iohan comentou isso nos quatro PRs em 02/11.

Ordem sugerida de integração: `8661916` na sua branch, depois #52, depois #53 corrigido, depois a base nova, depois a decisão da marca e só então #54 e #55.

## O protótipo e o FigCraft

**O que você pode seguir direto**
- As cores em `tokens.json` (claro e escuro).
- As imagens em `previews/` e os fluxos por perfil (analista, gestor, N1) em `handoff.md`.
- A tabela do `README.md` que separa o que é "só front" do que depende de API nova.

**O que você não deve copiar**
- O `tokens.css` como está. Ele usa `data-sigma="Escuro"`, e o painel usa `data-theme=light`. Copie os valores, não o arquivo.
- O `MASTER.md`. É uma versão experimental antiga (os caminhos que ele cita não existem).
- A linha suave `--line` como borda de campo. Ela fica fraca demais (veja os detalhes no fim).

**Como abrir o `sigma-fluxos.figcraft`**
1. Abra o arquivo no FigCraft.
2. Na página "01 · Comece aqui", escolha o quadro e inicie a apresentação. Escolha a jornada do perfil (N1, analista ou gestor).
3. **Sem o FigCraft:** baixe a pasta `design-system/exemplo/` inteira (cerca de 15 MB) e abra o `review.html` no navegador. A galeria precisa da pasta `previews/` ao lado. Se você abrir o HTML direto no GitHub ou baixar só o HTML, as imagens não aparecem.
4. O nome do arquivo é `sigma-fluxos.figcraft` (com "s"). O programa se chama FigCraft.
5. O FigCraft é opcional. O backlog não depende dele.

**Pendência do Vinícius:** o repositório não diz onde baixar o FigCraft, qual é a versão exata e qual sistema usar. Hoje só diz "peça o instalador ao Vinny". Vale registrar isso em um guia curto.

**O que o protótipo não tem** (por isso aparecem como desenho novo): Aprovações, o Diagnóstico atual, a Saúde por serviço com orçamento, a Auditoria com integridade da trilha, e o tema escuro de Login, Saúde, Auditoria e Aprovações. Só 5 telas têm versão escura.

## Perguntas que só o Vinícius responde

1. Qual marca e paleta serão usadas (PR #54 e #55)?
2. Onde está o instalador do FigCraft e qual versão?
3. Haverá confirmação antes de "Resolver incidente"? Se sim, quando?
4. Quem altera a lista de áreas por perfil em `Operations.jsx`?
5. **Prorrogação até 17/11:** o Vinícius vai conversar com o orientador para o design e o front da Joyce poderem seguir até 17/11, e vai ajudar no desenvolvimento. Resposta pendente. Se o orientador aprovar, o grupo B entra no produto até 17/11. Se não aprovar, o grupo B fica na branch e entra depois da banca, e só desenhos e documentos seguem até 17/11.

## Glossário

- **Diário de bordo:** o registro do que você fez em cada dia, com o que produziu e onde está.
- **Design system:** o conjunto de cores, fontes, espaços e componentes (botão, tabela, etiqueta) que o sistema usa.
- **Tokens:** as cores, fontes e espaços do sistema, guardados em um lugar só.
- **Mock:** um sistema de mentira com dados de exemplo, para ver as telas sem o servidor.
- **Teste pequeno (de unidade):** teste rápido do front, com `npm test`.
- **Teste de verdade (E2E):** teste que abre o navegador e usa o sistema inteiro, com o servidor.
- **axe:** verificação automática de acessibilidade.
- **Contraste:** o quanto o texto se destaca do fundo. Precisa ser bem legível.
- **PR:** pedido de revisão no GitHub.
- **Congelamento:** a data a partir da qual só entra correção de bug urgente.
- **Integração:** ligar o front ao servidor e juntar tudo na `develop`.

---

# Detalhes para Vinícius e Iohan

Esta parte é técnica e a Joyce não precisa ler.

## Fontes

- Backlog completo: `design-system/tarefas-joyce.md` na branch `feature/tarefas-joyce` (commit `afac415`), escrito em 21/10/2026. A branch `feature/front-design-system` aponta para o mesmo conteúdo.
- Estado do GitHub em 02/11/2026 (PRs #52 a #55 e issue #56); `origin/develop` em `6e616bc`.
- Protótipo: `design-system/exemplo/` (115 arquivos, 106 telas em 11 páginas; há 107 PNG, o `account.png` é extra).
- Conferência feita só por leitura. Não foi rodado o aplicativo, os testes nem o CI.

## O que mudou em relação ao backlog

1. A divisão de papéis ficou explícita e com um termo único ("Vinícius e Iohan").
2. A regra C0.6 separa teste pequeno (Joyce) de teste de verdade (Vinícius e Iohan).
3. O aceite real e o axe passam a ser por marcos, para cada PR não depender de vocês.
4. DS-35 a DS-42 e API-01 a API-08 saem do escopo dela. Para o gate: vocês confirmam rota, campos e autorização, implementam, estendem `api.js`, o mock e os hooks, e entregam fixtures (normal, vazio, lento, erro, 403). Só depois a Joyce consome.
5. DS-39 contradizia a regra de não criar dados novos no mock (pedia fixtures de credencial, que o contrato não tem).
6. As dependências artificiais foram trocadas por uma ordem sugerida.
7. O prazo e o recorte seguem o plano do orientador.

## Pontos para vocês

- **`Operations.jsx`** guarda a política de perfil (`pages/level`). As tarefas DS-38 a DS-42 dizem que a entrada nova só entra "depois de liberada", sem dizer quem altera a lista.
- **Conflito 409 no incidente:** a tela não recarrega (ao contrário de Aprovações). Não corrigir dentro da DS-24; é decisão de vocês.
- **Resolver incidente não tem confirmação.** Aplicar confirmação muda a interação e fica com vocês.
- **`ApprovalItem`** tem estado, relógio e `submitter`. Na DS-27 a Joyce só extrai o visual.
- **Mock:** logout devolve `{revogado:true}` (o real devolve `{status, mensagem}`; o front não lê). O mock aceita qualquer senha, não expira token, não emite eventos pelo `mockEventStream` e não tem 429, 501 nem 503. `/api/alertas` só generaliza IPv4 para /24.
- **Mock dentro de arquivos de produção:** a branch já alterou `api.js` (flag `MOCK`, `import()` dinâmico) e `App.jsx`. A afirmação "o build remove esse ramo" não foi verificada. A #57 do Iohan também mexe em `api.js`, então pode haver conflito.
- **CI:** o README dela diz que o CI roda o axe. Na `develop`, o axe fica no `test:e2e:operational`, que o CI não executa (só `scripts/validate_panel.py`).
- **Testes:** o PR #52 cita 19 testes de Vitest; a contagem estática dá cerca de 14. Não foi rodado.

## Base de trabalho: opções avaliadas

| Opção | O que faz | Resultado |
|---|---|---|
| Cherry-pick do `8661916` na `front-design-system` e propagar para ds-01, ds-02 e ds-03 (o ds-04 herda do ds-03) | Aplica sem conflito | Corrige só o CI. **Escolhida como primeiro passo** |
| Base nova a partir da `origin/develop`, levando os commits do mock (`3241071`, `afac415`) e os de documentação, com `-c merge.directoryRenames=true`, e reescrevendo à mão a seção `dev:mock` do `frontend/README.md` | Sobram só `sigma-frontend/README.md` e a seção do `dev:mock`; `package.json`, `App.jsx` e `api.js` migram sozinhos | **Escolhida como segundo passo.** Reaplicar o `f8420fb` (DS-02) depois que a Joyce corrigir os títulos |
| Merge direto da `develop` na `front-design-system` | 5 conflitos pela renomeação | Sem vantagem sobre a base nova |

Cuidados na base nova:
- O `design-system/exemplo` duplica o `docs/design/prototipo-figcraft/` que já está na `develop` (cópia idêntica do `.figcraft`). Decidir onde fica. O `docs/design/README.md` chama o protótipo de "baixa fidelidade" e diz que nada dele está no Git, enquanto o `exemplo/README.md` o chama de referência visual.
- Corrigir os caminhos dos documentos dela: `sigma-frontend/` para `frontend/`, `../doc/gitflow.md` para `docs/processo/gitflow.md`, `../doc/fluxo-de-trabalho-tcc.md` para `docs/processo/fluxo-de-trabalho-tcc.md`, `../doc/instalacao-desenvolvimento.md` para `docs/operacao/instalacao.md`.
- O guia `01-instalacao-front.md` manda `git switch develop` e `dev:mock`, que só existem na branch dela. Trocar a versão de Node: ele diz "22.12 ou mais nova" e o CI usa Node 24.
- O #55 não aplica sem o #54 (conflito em `identidade-visual/README.md`).

## Contraste calculado (WCAG)

| Par | Claro | Escuro |
|---|---|---|
| Linha suave `--line` sobre a superfície | 1,29:1 | 1,64:1 |
| Botão desabilitado | 1,23:1 | 1,64:1 |
| Texto sobre fundo | 17,06:1 | 17,09:1 |
| Texto de apoio (`muted`) sobre superfície | 6,31:1 | 8,29:1 |
| Azul sobre superfície | 6,70:1 | 6,72:1 |
| Azul sobre a mancha azul clara | 6,16:1 | 5,47:1 (o menor dos pares de texto) |

Cores vivas da marca:

| Par | Razão |
|---|---|
| Branco sobre `#0EA5E9` | 2,77:1 |
| Branco sobre `#1AB2FF` | 2,37:1 |
| Verdes `#10B981` e `#41BA50` sobre branco | 2,54:1 e 2,51:1 |
| `#0EA5E9` sobre `#0B1220` (escuro) | 6,76:1, passa |
| `#0F172A` sobre `#0EA5E9` | 6,44:1, passa |

Borda de campo precisa de 3:1. Candidatas: `#6B7C93` (4,26:1 sobre branco) e `#7A8CA5` (3,43:1 sobre branco) no claro; `#5B7089` (3,35:1 sobre a superfície) no escuro. Faltam tokens: foco, fundo de campo e "desconhecido". O `tokens.css` tem só 15 cores.

## Divergências já registradas

- O README do protótipo diz que sessão expirada e coleta atrasada são reproduzíveis com `?cenario=`. O mock só trata `vazio`, `erro`, `lento` e `falha-trilha`.
- O que funciona no mock não prova o servidor real: o mock não valida expiração de token.
- Usuários não ficam só em memória: com PostgreSQL, a identidade vem do `PostgresIdentityStore`, e `GET /api/usuarios` devolve só nomes.
- `PATCH /api/eng/alvos/{id}` aceita só `{ativo: boolean}` e não existe `GET /alvos/{id}`.
- O protótipo prevê fila, assunção e escalonamento para o N1; o painel permite só Saúde e Diagnóstico a esse perfil.
- Perfis: no protótipo o N1 vê Visão geral, Incidentes e Equipamentos; no código o N1 vê 2 áreas, o analista 4 e o gestor 5.
- "Cinco URLs abaixo" na DS-01 deve ser "acima". Alguns textos do backlog perderam espaços (DS-23, DS-28, DS-35).
- Cada tarefa do backlog repete "C0 completo", inclusive as só de documento.
