# 1. Instalação só do front

Para trabalhar no visual basta **Git** e **Node.js 22.12 ou mais novo** (recomendado: 24 LTS).
Python, Docker, PostgreSQL e chave de IA não são necessários.

## Primeira vez

```bash
git clone https://github.com/Solution-Explores/SigmaTI.git
cd SigmaTI
git switch develop
cd sigma-frontend
npm ci
npm run dev:mock
```

Abra o endereço exibido no terminal (normalmente <http://localhost:5173>).
No Windows, use o PowerShell ou o terminal do VS Code; os comandos são os mesmos.

## Entrar no painel

O modo mock aceita **qualquer senha**. O perfil é escolhido pelo início do nome de usuário:

| Usuário (exemplo) | Perfil | O que aparece |
|---|---|---|
| `suporte.joyce` | Suporte N1 (`suporte_n1`) | Saúde dos serviços e Diagnóstico |
| `analista.joyce` | Analista de Redes (`analista_redes`) | + Incidentes e Aprovações |
| `gestor.joyce` | Gestor de TI (`gestor_ti`) | + Auditoria (todas as áreas) |

Qualquer outro nome mostra o erro de credenciais inválidas, o que também serve para testar a tela de erro.

## Cenários para testar estados visuais

Acrescente `?cenario=` ao endereço e recarregue:

| Endereço | Mostra |
|---|---|
| `http://localhost:5173/` | Dados normais: serviços disponíveis, fora do ar, sem dados e desativados |
| `/?cenario=vazio` | Listas vazias ("Nenhum serviço cadastrado", "Nenhum incidente registrado") |
| `/?cenario=erro` | API fora do ar: mensagens de erro e botão "Tentar novamente" |
| `/?cenario=lento` | Respostas de 2,5 s, para ver "Carregando dados…" |
| `/?cenario=falha-trilha` | Auditoria com falha de integridade (alerta vermelho) |

As ações funcionam: reconhecer e resolver incidente, criar e decidir aprovação e pedir diagnóstico.
As alterações ficam só na memória do navegador; recarregar a página volta aos dados iniciais.
Para testar a regra de "quatro olhos", crie uma solicitação como `analista.a`, saia e decida como `gestor.b`.

## Comandos do dia a dia

| Comando | Para quê |
|---|---|
| `npm run dev:mock` | Painel com API simulada (uso principal) |
| `npm run dev` | Painel apontando para a API real em `http://localhost:8000` (precisa do backend) |
| `npm run lint` | Verifica o código; precisa passar antes do PR |
| `npm test` | Testes de componentes (Vitest); precisa passar antes do PR |
| `npm run build` | Gera a versão de produção; o modo mock não entra nela |

## Problemas comuns

- **`npm ci` falha com versão do Node:** confira com `node --version`; instale a versão 24 LTS.
- **Porta 5173 ocupada:** o Vite escolhe outra porta e mostra o endereço no terminal.
- **Tela "A API está indisponível":** você usou `npm run dev` sem o backend. Use `npm run dev:mock`.
- **Mudou o CSS e nada aconteceu:** o Vite recarrega sozinho; se não recarregar, use Ctrl+F5.

## Ver com a API real (opcional)

Quando quiser conferir uma alteração com o backend de verdade, peça ao Vinny ou ao Iohan, ou siga o
[roteiro completo](../doc/instalacao-desenvolvimento.md). Ele exige Python, PostgreSQL e variáveis de ambiente.
