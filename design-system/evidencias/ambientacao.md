# DS-01 · Ambientação: perfis e cenários do mock

Registro de quem vê o quê no painel em modo mock (`npm run dev:mock`). Dados 100% fictícios.
Conferido em 29/10/2026. Tema escuro, desktop.

## 1. Perfis e áreas visíveis

Entrar com o usuário abaixo e qualquer senha não vazia.

| Usuário | Perfil | Áreas | Saúde dos serviços | Incidentes | Aprovações | Auditoria | Diagnóstico | Conferido |
|---|---|---|---|---|---|---|---|---|
| `suporte.joyce` | Suporte N1 | 2 | sim | não | não | não | sim | [x] |
| `analista.joyce` | Analista de Redes | 4 | sim | sim | sim | não | sim | [x] |
| `gestor.joyce` | Gestor de TI | 5 | sim | sim | sim | sim | sim | [x] |

Fonte: regras de perfil em `src/Operations.jsx`. O menu oculto não é uma tela de "sem permissão".

## 2. Cenários

Acrescentar o trecho ao endereço `http://localhost:5173/` e recarregar. Depois de recarregar, é preciso entrar de novo.

| Cenário | Endereço | O que aparece | Quem vê | Conferido |
|---|---|---|---|---|
| Normal | `/` | Dados completos | todos | [x] |
| Vazio | `/?cenario=vazio` | Saúde: "Nenhum serviço cadastrado."; Incidentes: "Nenhum incidente registrado."; Aprovações: "Nenhuma aprovação pendente."; Auditoria: "Trilha vazia" e "Nenhum evento operacional registrado." | cada área, pelo seu perfil | [x] |
| Erro | `/?cenario=erro` | "A API está indisponível no momento. Tente novamente." com o botão "Tentar novamente"; o login continua funcionando | todos | [x] |
| Lento | `/?cenario=lento` | "Carregando dados…" por cerca de 2,5 s | todos | [x] |
| Falha na trilha | `/?cenario=falha-trilha` | Auditoria com "Falha de integridade detectada" em alerta | só o Gestor de TI | [x] |

Fonte: `src/mock/mockApi.js` e `src/OperationalPages.jsx`.

## 3. Erro de login x erro operacional

- **Erro de login:** usuário que não começa por `suporte`, `analista` ou `gestor`, ou senha vazia. A tela de login mostra "Sessão ausente, expirada ou credenciais inválidas. Entre novamente."
- **Erro operacional:** cenário `erro`. O login funciona, e cada área mostra "A API está indisponível no momento. Tente novamente." com o botão "Tentar novamente". O tempo real (SSE) também falha e o aviso passa a "Reconectando ao tempo real".

## 4. Limites dos cenários

- Não existe URL para "sem permissão", sessão expirada, coleta atrasada, IA indisponível ou bloqueio LGPD. Esses estados não são alcançáveis no mock.
- No cenário `vazio`, a lista continua vazia mesmo depois de criar um pedido. O Diagnóstico não é uma lista.
- No cenário `lento`, cada requisição espera 2,5 s; o tempo real tem espera própria de 300 ms.
- Recarregar a página perde a sessão e as alterações feitas. Duas abas do navegador têm estados independentes.
- A regra de quatro olhos testa-se com `analista.a`, depois Sair, depois `gestor.b`, sem recarregar a página.

## 5. Estado dos três comandos

Executados em 29/10/2026 às 23:34, no computador da Joyce, em `sigma-frontend/`, com Node v24.22.1 e com as alterações da DS-02 já aplicadas:

| Comando | Resultado |
|---|---|
| `npm run lint` | sem erros |
| `npm test` | 4 arquivos de teste, 19 testes aprovados |
| `npm run build` | build gerado sem erros |

## 6. Capturas iniciais

Pasta: `design-system/evidencias/capturas-ds01/`. As 7 imagens foram geradas automaticamente (navegador Chromium sem interface, 1280 x 900, tema escuro) no mesmo mock, com dados fictícios. Nenhuma tem barra de favoritos ou dados pessoais.

| Arquivo | Perfil | Tela |
|---|---|---|
| `01-n1-saude-normal.png` | suporte.joyce | Saúde dos serviços, cenário normal |
| `02-analista-incidentes-normal.png` | analista.joyce | Incidentes, cenário normal |
| `03-gestor-auditoria-normal.png` | gestor.joyce | Auditoria, cenário normal |
| `04-vazio-saude.png` | gestor.joyce | Saúde dos serviços, cenário vazio |
| `05-erro-saude.png` | gestor.joyce | Saúde dos serviços, cenário erro |
| `06-lento-carregando.png` | gestor.joyce | Saúde dos serviços, cenário lento |
| `07-falha-trilha-auditoria.png` | gestor.joyce | Auditoria, cenário falha-trilha |

## 7. Diferenças encontradas

Nenhuma: as abas de cada perfil e as mensagens de cada cenário bateram com as tabelas acima.

## 8. Pendências

- Capturas em tema claro e a 390 px: aguardando orientação do Vinny.