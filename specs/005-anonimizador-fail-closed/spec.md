# Feature Specification: Anonimização LGPD Robusta e Fail-Closed (RF05) #5

**Feature Branch**: `005-anonimizador-fail-closed`  
**Created**: 2026-10-18  
**Status**: Concluído / Pronto para Revisão  
**Input**: Issue #5 — Correção de vulnerabilidade e conformidade LGPD (Bloqueadores B6 e B7 de `engenharia/docs/05-seguranca-e-pendencias.md`, requisitos RF05 e RNF08).

---

## Contexto e Motivação

A função legada `anonimizar_dados` em `main.py` cobria apenas IPv4 por expressão regular simples e o literal `"dr.joao"`. Além disso, o campo `alerta.equipamento` era enviado cru diretamente no prompt da IA, expondo a topologia física da instituição hospitalar.

Esse comportamento contradizia o **Requisito RF05** e as promessas da documentação do projeto:
1. **RF05 (Privacidade e LGPD)**: IPs viram sub-redes, equipamentos viram categorias funcionais genéricas, nomes próprios e identificadores médicos são removidos antes de qualquer transmissão à nuvem.
2. **Sem Tabela de/para (Zero-Pseudonimização)**: em estrita conformidade com o Art. 12 da LGPD, o sistema não retém mapeamentos de correspondência reversível.
3. **Falha Segura (*Fail-Closed*)**: o README e o estudo de caso prometem: *"se o filtro falhar, nada é enviado"*. Qualquer exceção ou detecção de resíduo deve cancelar a transmissão externa à IA e registrar auditoria.
4. **Validação Científica para o TCC (RNF08 / Experimento E6)**: necessidade de comprovação empírica de eficácia (Recall de PII $\ge 99\%$) com relatório formal em `resultados/`.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Sanitização Abrangente de Identificadores (Priority: P1) 🎯 MVP

Como analista do sistema de monitoramento hospitalar,  
Quero que alertas com logs contendo endereços de rede, nomes de máquinas e dados pessoais/clínicos sejam sistematicamente generalizados e sanitizados por regras testáveis,  
Para que nenhum dado pessoal identificado ou identificável seja transmitido ao provedor externo de LLM, cumprindo a LGPD sem tabelas reversíveis de/para.

**Why this priority**: É o núcleo do requisito funcional RF05 e elimina o bloqueador B6.

**Independent Test**: Testado unitariamente fornecendo textos com cada classe de identificador em `tests/test_sanitizer.py` sem dependência de banco ou provedor de IA.

**Acceptance Scenarios**:
1. **Given** um alerta contendo IPv4 (`192.168.1.55`), **When** processado, **Then** é generalizado para sub-rede `/24` (`192.168.1.0/24`).
2. **Given** um alerta contendo IPv6 (`2001:db8:85a3::8a2e:370:7334`), **When** processado, **Then** é generalizado para prefixo `/64` (`2001:db8:85a3::/64`).
3. **Given** um endereço MAC (`00:1B:44:11:3A:B7`), **When** processado, **Then** é substituído por `[MAC_MASCARADO]`.
4. **Given** um hostname de equipamento (`sw-core-01`, `tomografo-ge-01`), **When** processado no erro ou no campo `equipamento`, **Then** é categorizado funcionalmente (`[SWITCH_REDE]`, `[EQUIPAMENTO_IMAGEM]`).
5. **Given** dados pessoais ou médicos (e-mails, CPFs, CNS, prontuários, nomes próprios clínicos), **When** processados, **Then** são substituídos por seus marcadores padronizados (`[EMAIL_REMOVIDO]`, `[CPF_REMOVIDO]`, `[CNS_REMOVIDO]`, `[PRONTUARIO_REMOVIDO]`, `[NOME_REMOVIDO]`, `[USUARIO_MEDICO]`).
6. **Given** a execução da sanitização, **When** concluída, **Then** nenhuma tabela de/para reversível é mantida em memória ou persistência.

---

### User Story 2 — Falha Segura (*Fail-Closed*) com Validação Residual e Auditoria (Priority: P1)

Como encarregado de segurança da infraestrutura hospitalar,  
Quero que qualquer falha, erro interno ou resíduo de dado sensível detectado após a sanitização bloqueie imediatamente a chamada à IA e registre trilha de auditoria,  
Para garantir que falhas no algoritmo nunca resultem em vazamento de dados para terceiros.

**Why this priority**: Resolve o bloqueador B7. Garante que o sistema nunca falhe de forma permissiva (*fail-open*).

**Independent Test**: Injeção de falha simulada (`Mock(side_effect=RuntimeError)`) e detecção residual forçada comprovando `provider_handler.assert_not_called()`.

**Acceptance Scenarios**:
1. **Given** que a função de anonimização lance exceção durante o processamento, **When** a rota `/api/alertas` interceptar o erro, **Then** nenhuma chamada externa é disparada para a IA (`assert_not_called`).
2. **Given** que a detecção residual (segunda passada) encontre PII não neutralizada na saída, **When** for identificada, **Then** dispara `SanitizationResidualError`, bloqueia o envio externo e registra na trilha de auditoria (`AUDIT_PRIVACY`).
3. **Given** a ocorrência de bloqueio fail-closed, **When** o log for emitido, **Then** nenhum dado bruto sensível da requisição é exposto nos logs.

---

### User Story 3 — Validação Empírica via Corpus Sintético e Experimento E6 (Priority: P2)

Como pesquisador do TCC,  
Quero um corpus de teste sintético balanceado e um script de avaliação automática,  
Para calcular Recall de PII (meta $\ge 99\%$) e falsos positivos, gerando relatório do Experimento E6 em `resultados/` para compor a monografia.

**Why this priority**: Fornece comprovação científica quantitativa exigida pelo RNF08 para o TCC.

**Independent Test**: Execução de `scripts/executar_experimento_e6.py` consumindo `tests/data/corpus_sintetico_pii.json` e gerando `resultados/experimento-e6-anonimizacao.md`.

**Acceptance Scenarios**:
1. **Given** o corpus sintético anotado com 50 casos (positivos e negativos), **When** avaliado pelo script, **Then** o Recall atinge $\ge 99.0\%$ com zero vazamentos.
2. **Given** a finalização da avaliação, **When** concluída, **Then** o relatório em Markdown com matriz de confusão e métricas é gerado em `resultados/experimento-e6-anonimizacao.md`.

---

## Edge Cases

- **Números de versão vs IPv4**: Sequências como `6.4.21` e `1.80.0` não são confundidas nem mascaradas como sub-redes IP.
- **Identificadores colados a pontuações**: Expressões como `prontuário #987654` e `IP 192.168.1.55:` são identificadas sem corromper pontuações adjacentes.
- **Palavras técnicas reservadas**: Termos como "terminal", "switch", "servidor" em frases técnicas não são confundidos com nomes de pessoas.
- **CPFs reais vs fictícios**: Suporte a CPFs formatados e contextuais com validação de dígitos verificadores para evitar falsos positivos.

---

## Requirements *(mandatory)*

- **FR-001**: O sistema DEVE fornecer o módulo `sanitizer.py` com regras determinísticas para IPv4 (/24), IPv6 (/64), MAC, hostnames/equipamentos, e-mails, CPFs, CNS, prontuários e nomes.
- **FR-002**: O sistema DEVE categorizar o campo `alerta.equipamento` antes da montagem do prompt.
- **FR-003**: O sistema NÃO DEVE persistir tabelas de correspondência de/para reversíveis (RF05).
- **FR-004**: O sistema DEVE executar validação residual em segunda passada (*two-pass detection*).
- **FR-005**: O sistema DEVE adotar comportamento estritamente **Fail-Closed**: na presença de exceção ou resíduo, nenhuma chamada externa é disparada.
- **FR-006**: O sistema DEVE registrar tentativas de envio bloqueadas na trilha de auditoria sem vazar dados brutos.
- **FR-007**: O sistema DEVE manter corpus de teste sintético em `tests/data/corpus_sintetico_pii.json` e script de avaliação em `scripts/executar_experimento_e6.py`.

---

## Success Criteria *(mandatory)*

- **SC-001**: 100% dos tipos de identificadores previstos cobertos por testes automatizados (`tests/test_sanitizer.py`).
- **SC-002**: 0 chamadas externas realizadas ao provedor de IA em falhas injetadas comprovado em `tests/test_fail_closed.py`.
- **SC-003**: Recall de PII de 100.00% obtido no Experimento E6 (superando a meta de $\ge 99\%$).
- **SC-004**: Relatório oficial do Experimento E6 gerado e versionado em `resultados/experimento-e6-anonimizacao.md`.
