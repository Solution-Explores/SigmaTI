# Relatório do Experimento E6: Avaliação Empírica do Módulo de Anonimização LGPD (RF05)

**Data de Execução**: 18/10/2026 02:59:46  
**Projeto**: SIGMA — Sistema Integrado de Gestão e Monitoramento de Alertas  
**Objetivo do Experimento**: Avaliar a eficácia da generalização e remoção de dados pessoais identificáveis (PII) e de infraestrutura hospitalar com base nos requisitos **RF05** e **RNF08** para o Trabalho de Conclusão de Curso (TCC).

---

## 1. Resumo Executivo e Métricas Principais

| Métrica | Meta Estipulada | Valor Obtido no Experimento E6 | Status |
|---|---|---|---|
| **Recall de PII** | >= 99.0% | **100.00%** | APROVADO |
| **Precisão** | Alta | **100.00%** | APROVADO |
| **Taxa de Falsos Positivos** | <= 5.0% | **0.00%** | APROVADO |
| **Acurácia Global** | >= 95.0% | **100.00%** | APROVADO |

---

## 2. Matriz de Confusão

O corpus sintético contém **50 amostras**, balanceadas entre logs contendo PII/dados hospitalares (25 casos) e logs puramente técnicos (25 casos):

| | Classificado como Sensível (Sanitizado) | Classificado como Não Sensível | Total Real |
|---|---|---|---|
| **Casos Reais com PII (Positivos)** | **25** (Verdadeiros Positivos) | **0** (Falsos Negativos / Vazamento) | **25** |
| **Casos Reais Técnicos (Negativos)** | **0** (Falsos Positivos) | **25** (Verdadeiros Negativos) | **25** |

> **Nota sobre Vazamento (Falsos Negativos):** O valor de FN foi **0**, comprovando que nenhum identificador do corpus escapou do pipeline de sanitização.

---

## 3. Classes de Identificadores Testados

As seguintes classes foram submetidas ao teste no corpus com 100% de cobertura individual:

1. **Endereçamento de Rede**:
   - IPv4 generalizado para sub-redes `/24` (ex: `192.168.1.0/24`).
   - IPv6 generalizado para prefixo `/64` (ex: `2001:db8:85a3::/64`).
   - Endereços MAC substituídos por `[MAC_MASCARADO]`.
2. **Equipamentos e Topologia**:
   - Hostnames e switches clínicos convertidos em categorias funcionais (`[SWITCH_REDE]`, `[ROTEADOR_REDE]`, `[SERVIDOR_HOSPITALAR]`, `[EQUIPAMENTO_IMAGEM]`, `[DISPOSITIVO_BIOMEDICO]`).
3. **Dados Civis e Clínicos (LGPD)**:
   - CPFs substituídos por `[CPF_REMOVIDO]`.
   - Cartões Nacionais de Saúde (CNS / SUS) substituídos por `[CNS_REMOVIDO]`.
   - Números de Prontuário médico substituídos por `[PRONTUARIO_REMOVIDO]`.
   - Contatos eletrônicos substituídos por `[EMAIL_REMOVIDO]`.
4. **Nomes Próprios**:
   - Nomes precedidos por pronomes de tratamento/papéis clínicos (Dr., Dra., Enf., Paciente) substituídos por `[NOME_REMOVIDO]`.
   - Nomes configurados legados (como `dr.joao`) substituídos por `[USUARIO_MEDICO]`.

---

## 4. Garantia de Falha Segura (*Fail-Closed*)

Além da transformação determinística, o módulo foi auditado sob:
- **Detecção Residual (Two-Pass Verification)**: Reexecução estrita dos detectores sobre o texto de saída. Qualquer resquício aborta imediatamente o envio externo.
- **Injeção de Falhas**: Simulação de exceções durante o processamento comprovou que a chamada externa para a nuvem é cancelada (`mock_client.post.assert_not_called()`).
- **Conformidade com o Art. 12 da LGPD**: Ausência total de tabelas de correspondência reversíveis (zero-pseudonimização).

---

## 5. Conclusão para o TCC

O Experimento E6 confirma empiricamente que o módulo de anonimização do SIGMA atinge **100.00% de Recall de PII**, atendendo à meta de >= 99% estipulada no planejamento do TCC, com **0 vazamentos de dados pessoais** e taxa controlada de falsos positivos (0.00%), preservando a clareza técnica dos logs para diagnóstico pela IA.
