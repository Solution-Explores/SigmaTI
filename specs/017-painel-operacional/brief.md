# #15 — Painel operacional

## Direção
Extensão do painel SIGMA existente, sem troca de identidade: azul sobre fundo escuro, fonte de sistema, painéis planos com borda e raio de 12px. Tema claro requerido pela issue. Quatro áreas operacionais e diagnóstico anterior preservado. Código é a referência visual; não há comp aprovado.

## Contrato
Saúde: estados, orçamento e projeção apenas quando sustentados pelas medições. Incidentes: média, mediana e p95, com ausência de amostra explícita. Aprovações: justificativa, papéis e quatro olhos. Auditoria: integridade da trilha de sondas e eventos operacionais separados. SSE autenticado com cursor e reconexão; fallback de atualização a cada 15s. Sessão apenas em memória.

## Evidência local — 20/10/2026 UTC−4
- 16 testes de componentes/parser/ciclo de sessão aprovados.
- 3 testes PostgreSQL da API e 1 orquestrador com 4 histórias reais de navegador aprovados (28,47s). Após a revisão do limite de orçamento, 4 testes da API aprovados em 6,07s, incluindo orçamento exatamente esgotado.
- 3 testes de regressão do diagnóstico aprovados; build e lint aprovados.
- Axe: nenhuma violação nas regras WCAG 2 A/AA e 2.1 AA nas capturas testadas. Não equivale a certificação completa.
- Chrome instalado e PostgreSQL 17 descartável locais. CI usa Chromium e PostgreSQL 15.
- Capturas verificadas em `.impeccable/review/panel-*.png` (ignoradas pelo Git); CI publica capturas como artifacts.
- Contexto e detector Impeccable indisponíveis: motor 0.1.15 ausente e cache protegido. Fallback: leitura direta do projeto, craft-floor, capturas e revisão técnica.

## Limites
MTTD não é inventado: não existe início real da falha persistido. Janelas parciais mostram limite máximo do orçamento, sem projeção finita. Ausência de medição recente é desconhecida. A verificação JSONL não atesta os eventos PostgreSQL. Dados e alvos de teste são sintéticos; não atestam uma rede hospitalar real.

## Revisão técnica
Impeccable finish reviewer, contexto novo e seis capturas: sem defeito visual material identificado na extensão. Disposição inicial `fix` pela ausência de PRODUCT.md. Documenter extraiu PRODUCT.md, DESIGN.md e `.impeccable/design.json` do código existente; verdict pass: achado documental `resolved`, disposição `ship` no escopo dessa correção. Não é revisão humana independente nem certificação integral. Nenhuma alteração de interface ocorreu após as capturas revisadas.

## Correção após CI
O primeiro CI da #15 aprovou pacote e configuração/API, mas o job PostgreSQL terminou com 458 aprovados e 1 falha: axe encontrou contraste 2,1:1 no botão Atualizar saúde durante a transição de cores ao mudar de tema (run 39425590466). Removida a transição; a troca é imediata, sem relaxar o teste. Build/lint aprovados. Regressão local completa: 459 aprovados em 417,89s (Chrome/PG17). O ensaio focado após a correção aprovou as 4 histórias do navegador (orquestrador 1 aprovado em 29,59s), regenerando as seis capturas.
