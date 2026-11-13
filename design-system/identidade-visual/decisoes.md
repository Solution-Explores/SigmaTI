# DS-03 · Decisões de marca e paleta

**Situação: ADOTADA, opção 1 (identidade v4), em 04/11/2026.** A Joyce informou que o Vinícius aprovou a proposta (a aprovação não está registrada por escrito neste repositório). Nada aqui foi aplicado ao painel ainda: a aplicação é das tarefas DS-06 e DS-08.
O restante do documento mantém a comparação das três opções que existia antes da decisão.

- **Responsável pelo registro:** Joyce Yasmin. **Revisor visual:** Vinny. **Referência:** issue #31, tarefa DS-03 do plano `design-system/tarefas-joyce.md`.
- **Prancha da proposta principal:** [`prancha-identidade-v4.html`](prancha-identidade-v4.html) (abre direto no navegador, claro e escuro, sem script e sem pedido a sites externos).
- Dados, nomes e valores da prancha são fictícios.

## 1. Decisão necessária

Hoje existem três conjuntos de cores diferentes (ver [README](README.md)). A equipe precisa escolher **um** e a identidade que vai com ele.

| Opção | O que é | A favor (verificado) | Contra (verificado) |
|---|---|---|---|
| **1 · Identidade v4 (proposta principal)** | Símbolo novo (cruz de nós de rede com batimento), Índigo Sigma, Petróleo Sinal e Azul Profundo, com Atkinson Hyperlegible e IBM Plex Mono sugeridas para a DS-05 | Todos os pares de texto com 4,94:1 ou mais nos dois temas (seção 3); verde fica só no estado "Disponível"; "Desconhecido" é neutro e tracejado; o nome "TI" tem contraste forte | **Substitui o logotipo enviado pelo Vinny** (Σ com pulso, azul ou verde) e muda as cores do painel; exige confirmar com o hospital se há regra de sinalização para o símbolo em cruz |
| **2 · Azul do logotipo enviado** | Σ com pulso em `#1AB2FF`, fundo `#2E3133` (Adobe Color) | Mantém o logotipo que o Vinny enviou; menor mudança no painel | "TI" do logo com 1.87:1 sobre o fundo; `#1AB2FF` sobre branco dá só 2.37:1, então o tema claro precisa de azul mais escuro (o painel já usa `#12568E`, 7.64:1) |
| **3 · Verde do logotipo enviado** | Σ com pulso em `#41BA50`, fundo `#213323` | Mantém o logotipo que o Vinny enviou | O verde **já é a cor do estado "Disponível"** e se confundiria com a marca; `#41BA50` sobre branco dá 2.51:1; "TI" do logo com 1.64:1 |

O protótipo do Vinny usa um terceiro azul (`#1D4ED8` no claro e `#60A5FA` no escuro). Ele não é uma opção separada aqui, só uma referência.

### Registro da decisão (preencher na reunião)

- Opção escolhida: [x] 1 · v4  [ ] 2 · azul do logotipo  [ ] 3 · verde do logotipo  [ ] outra
- Data da decisão: 04/11/2026
- Quem decidiu: Vinícius Lima (aprovação informada pela Joyce Yasmin)
- Observações e ajustes pedidos: nenhum informado. Seguem abertos: validação da borda de campo (`#4F6577` claro e `#4F7C9E` escuro), fonte (DS-05) e os metadados C2PA dos SVGs.

## 2. Opção 1 · Identidade v4 (proposta principal)

**Conceito:** "A rede do hospital, sempre com pulso". O símbolo junta uma cruz de saúde, a topologia de rede (um nó central e quatro nós) e um batimento no braço esquerdo. Evita a cruz vermelha, cujo emblema tem uso restrito.

### Papéis de cor

| Papel | Tema claro | Tema escuro | Observação |
|---|---|---|---|
| Marca | Índigo Sigma `#3730A3` | Índigo claro `#A5B4FC` | Só marca e ação, nunca estado |
| Pulso e destaque | Petróleo Sinal `#0E7490` | Ciano claro `#22D3EE` | Gráficos de pulso e destaques |
| Fundo | Névoa `#F3F6F8` | Azul Profundo `#0A1E30` | |
| Superfície (cartão) | Branco `#FFFFFF` | `#11293D` | |
| Texto | Azul Profundo `#0A1E30` | Giz `#E3EEF6` | |
| Texto secundário | Aço `#4F6577` | Aço claro `#9FB3C4` | |
| Disponível | `#15563C` | `#ABEBCF` | Igual ao verde que o painel já usa |
| Atenção | `#7A4A00` | `#FFD479` | Difere do painel atual (DS-08) |
| Erro | `#A82A20` | `#FF9E94` | Difere do painel atual (DS-08) |
| Desconhecido (neutro) | Aço `#4F6577` | Aço claro `#9FB3C4` | Borda tracejada, nunca verde |

**Marca distinta do estado "Disponível":** a marca é índigo e petróleo, e o verde fica só no estado. Matiz aproximado: `#3730A3` ≈ 244°, `#0E7490` ≈ 193°, `#15563C` ≈ 156°, `#ABEBCF` ≈ 154°. Além da cor, todo estado tem ícone e texto.

### Estados (regras mantidas)

Nenhum estado depende só da cor: Disponível, Atenção e Erro têm ícone e texto, e Desconhecido usa borda tracejada. Frases como "Sem dados recentes", "Até X min" e "Sem início real de falha registrado" continuam como estão.

## 3. Contraste medido

Calculado por script com a fórmula WCAG 2.1. Mínimo de 4,5:1 para texto e de 3:1 para bordas de campo e ícones.

### Tema claro

| Par | Cor | Sobre branco | Sobre Névoa | Passa |
|---|---|---|---|---|
| Texto principal (Azul Profundo) | `#0A1E30` | 16.92:1 | 15.59:1 | sim |
| Texto secundário (Aço) | `#4F6577` | 6.07:1 | 5.59:1 | sim |
| Marca em texto, link e ícone (Índigo Sigma) | `#3730A3` | 9.93:1 | 9.15:1 | sim |
| Pulso e destaque (Petróleo Sinal) | `#0E7490` | 5.36:1 | 4.94:1 | sim |
| Texto do botão (branco sobre Índigo) | `#FFFFFF` | 9.93:1 | 9.93:1 | sim |
| Estado Disponível | `#15563C` | 8.65:1 | 7.97:1 | sim |
| Estado Atenção | `#7A4A00` | 7.48:1 | 6.89:1 | sim |
| Estado Erro | `#A82A20` | 6.96:1 | 6.41:1 | sim |
| Estado Desconhecido (Aço) | `#4F6577` | 6.07:1 | 5.59:1 | sim |
| Borda de campo (proposta, mínimo 3:1) | `#4F6577` | 6.07:1 | 5.59:1 | sim |

### Tema escuro

| Par | Cor | Sobre `#0A1E30` | Sobre `#11293D` | Passa |
|---|---|---|---|---|
| Texto principal (Giz) | `#E3EEF6` | 14.36:1 | 12.66:1 | sim |
| Texto secundário (Aço claro) | `#9FB3C4` | 7.83:1 | 6.90:1 | sim |
| Marca em texto, link e ícone (Índigo claro) | `#A5B4FC` | 8.49:1 | 7.48:1 | sim |
| Pulso e destaque (Ciano claro) | `#22D3EE` | 9.36:1 | 8.25:1 | sim |
| Texto do botão (Azul Profundo sobre Índigo claro) | `#0A1E30` | 8.49:1 | 8.49:1 | sim |
| Estado Disponível | `#ABEBCF` | 12.50:1 | 11.02:1 | sim |
| Estado Atenção | `#FFD479` | 12.04:1 | 10.61:1 | sim |
| Estado Erro | `#FF9E94` | 8.52:1 | 7.51:1 | sim |
| Estado Desconhecido (Aço claro) | `#9FB3C4` | 7.83:1 | 6.90:1 | sim |
| Borda de campo (proposta, mínimo 3:1) | `#4F7C9E` | 3.79:1 | 3.34:1 | sim |

Observações:
- Nas linhas de **botão**, o contraste é do texto sobre a cor do botão, por isso as duas colunas repetem o mesmo valor.
- A **borda de campo não está definida na prancha**. As bordas dos cartões dela (`#C5CED3` no claro, 1.60:1, e `#2C4A63` no escuro, 1.61:1) servem de decoração, mas **não servem para campos de formulário**. Por isso a tabela traz uma proposta de borda de campo, a validar.
- O foco de teclado do painel atual é amarelo (`#F5D773` no escuro e `#7B3E00` no claro) e continua previsto. A cor de "Atenção" também é amarela, então o foco precisa de um contorno visível e espesso, e todo estado já tem texto.
- Contraste medido sobre os fundos indicados, e não sobre o painel renderizado. Hover, desabilitado e foco renderizados ficam para a DS-08.

## 4. Como foi verificado

- Todos os contrastes foram recalculados por script em 30/10/2026 e batem com os da prancha.
- A prancha abre sem rolagem lateral em 390 px e em 1440 px, não tem script e não faz pedidos a sites externos.
- Não foi aplicada ao painel; a comparação com o painel atual é só de referência.

## 5. O que este documento NÃO decide

- **Fonte (DS-05):** Substituída pela DS-05. A prancha mostra Atkinson Hyperlegible e IBM Plex Mono, mas a decisão da DS-05 (`tipografia.md`, em revisão no PR #86) é a pilha "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif, sem arquivo de fonte no repositório. Onde houver diferença, vale o `tipografia.md` depois de aprovado; a tipografia da prancha é a sugestão anterior.
- **Logotipos vetoriais (DS-04):** os 9 arquivos SVG estão nesta pasta. Falta testar a área de proteção e o tamanho mínimo em tamanho real.
- **Aplicação ao painel (DS-06 e DS-08):** tokens, temas e comparação com as cores atuais do painel.
- **Símbolo em cruz no hospital:** Resolvido em 04/11/2026: símbolo em cruz permitido; logotipo do hospital proibido.
- **Fotografias:** nenhuma foi produzida; precisam de autorização do hospital.

## 6. Próximos passos

- **Opção 1 adotada:** DS-04 (SVGs, entregues), DS-05 (fonte), DS-06 em diante.
- **Se a opção 2 ou 3 for escolhida:** DS-04 redesenha o logotipo escolhido em vetor, reforçando o "TI", e a paleta correspondente entra na DS-06.
- **Em qualquer caso:** registrar a decisão na seção 1 e avisar Vinny e Iohan antes de qualquer mudança de cor no painel.

Refs #31
