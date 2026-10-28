> Atualização 19/10/2026: entrega parcial em correção/revisão. As afirmações de conclusão abaixo são históricas e não equivalem ao aceite integral. Consulte [a revisão da sprint](../011-recuperacao-sprint/evidencias.md).

# Registro da Entrega — Issue #5

**Título do PR / Issue**: `feat(seguranca): modulo anonimizador com fail-closed e experimento E6 (RF05 #5)`  
**Issue Relacionada**: [#5](https://github.com/Solution-Explores/SigmaTI/issues/5)  
**Bloqueadores Mitigados**: B6 e B7 de `engenharia/docs/05-seguranca-e-pendencias.md`  
**Requisitos Atendidos**: RF05 (Privacidade, generalização e fail-closed) e RNF08 (Testes empíricos de vazamento e degradação)  
**Especificação Spec-Kit**: [spec.md](spec.md) | [plan.md](plan.md) | [tasks.md](tasks.md) | [evidencias.md](evidencias.md)

---

## 1. Problema Abordado

A função de anonimização original tratava exclusivamente endereços IPv4 simples e a string literal `"dr.joao"`. Adicionalmente:
- O campo `alerta.equipamento` era enviado em texto claro, expondo a topologia física da infraestrutura hospitalar;
- Faltavam regras para IPv6, MACs, hostnames de equipamentos, documentos pessoais (CPF, CNS), prontuários médicos e nomes de profissionais;
- Inexistia mecanismo de *Fail-Closed*: exceções ou escapes de detecção não impediam o fluxo em direção à nuvem;
- Faltava comprovação quantitativa dos números de privacidade para a monografia do TCC.

---

## 2. Implementação Realizada

1. **Módulo `sanitizer.py`**:
   - Generalização de IPv4 para sub-redes `/24` e IPv6 para prefixos `/64` utilizando `ipaddress`.
   - Mascaramento de endereços MAC (`[MAC_MASCARADO]`).
   - Mapeamento determinístico de hostnames e equipamentos para categorias funcionais genéricas (`[SWITCH_REDE]`, `[ROTEADOR_REDE]`, `[SERVIDOR_HOSPITALAR]`, `[EQUIPAMENTO_IMAGEM]`, `[DISPOSITIVO_BIOMEDICO]`, etc.).
   - Remoção de CPFs (com validação de dígitos), Cartão SUS (CNS), prontuários médicos e e-mails.
   - Remoção de nomes próprios clínicos por heurística de cargos e lista configurada.
   - Conformidade estrita com o RF05: nenhuma tabela de correspondência reversível de/para (zero-pseudonimização).
2. **Garantia Fail-Closed e Auditoria**:
   - Inspeção em segunda passada (*two-pass detection*): reexecução dos detectores sobre o texto de saída.
   - Bloqueio imediato da chamada ao provedor de IA (`consultar_ia`) na presença de qualquer exceção ou resíduo de PII.
   - Registro de auditoria seguro (`AUDIT_PRIVACY`) com informações do evento e sem vazamento de dados brutos.
3. **Experimento E6 e Validação Empírica para o TCC**:
   - Corpus sintético anotado com 50 casos balanceados em `tests/data/corpus_sintetico_pii.json`.
   - Script de benchmark `scripts/executar_experimento_e6.py`.
   - Relatório científico oficial gerado em `engenharia/resultados/experimento-e6-anonimizacao.md`:
     - **Recall de PII: 100.00%** (Meta: $\ge 99\%$)
     - **Precisão: 100.00%**
     - **Falsos Positivos: 0.00%**
     - **Falsos Negativos (Vazamentos): 0**

---

## 3. Critérios de Aceite Verificados

- [x] Testes cobrem cada tipo de identificador (`tests/test_sanitizer.py`).
- [x] Falha injetada no anonimizador comprova zero chamadas externas (`tests/test_fail_closed.py`).
- [x] Relatório de recall/precisão versionado em `engenharia/resultados/experimento-e6-anonimizacao.md`.
- [x] Suíte de testes passando com 127 testes aprovados.
