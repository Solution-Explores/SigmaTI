# Evidências de Testes e Validação — Issue #5

**Data**: 2026-10-18  
**Ambiente**: Python 3.14 / pytest 9.1.1  
**Escopo**: Sanitizer, Fail-Closed, Auditoria, Integração com Provedor e Experimento E6

---

## 1. Execução dos Testes Unitários e de Integração

### Comando:
```bash
pytest tests/test_sanitizer.py tests/test_fail_closed.py tests/test_provider.py tests/test_public_errors.py -v
```

### Resultado:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\iohan\Faculdade\TCC\SigmaTi\SigmaTI
plugins: anyio-4.15.1
collected 127 items

tests/test_sanitizer.py::TestIdentificadoresRede::test_ipv4_generalizacao_para_subrede_24 PASSED [  0%]
tests/test_sanitizer.py::TestIdentificadoresRede::test_ipv4_preserva_numeros_de_versao PASSED [  1%]
tests/test_sanitizer.py::TestIdentificadoresRede::test_ipv6_generalizacao_para_prefixo_64 PASSED [  2%]
tests/test_sanitizer.py::TestIdentificadoresRede::test_mac_address_mascarado PASSED [  3%]
tests/test_sanitizer.py::TestIdentificadoresEquipamentos::test_categorizacao_equipamentos[sw-core-01-[SWITCH_REDE]] PASSED [  3%]
...
tests/test_sanitizer.py::TestZeroPseudonimizacao::test_sem_tabela_reversivel_em_memoria PASSED [ 23%]
tests/test_fail_closed.py::TestFailClosedSanitizacao::test_falha_injetada_no_anonimizador_impede_chamada_externa PASSED [ 24%]
tests/test_fail_closed.py::TestFailClosedSanitizacao::test_deteccao_residual_aciona_fail_closed_e_auditoria PASSED [ 25%]
tests/test_fail_closed.py::TestFailClosedSanitizacao::test_fluxo_completo_com_dados_sensiveis_sanitiza_e_chama_ia PASSED [ 25%]
tests/test_provider.py::test_success_payload_and_shared_client_lifecycle PASSED [ 26%]
...
tests/test_public_errors.py::test_error_boundary_never_starts_second_response PASSED [100%]

============================= 127 passed in 16.21s =============================
```

---

## 2. Execução do Experimento E6

### Comando:
```bash
python scripts/executar_experimento_e6.py
```

### Saída:
```text
Carregando corpus de tests/data/corpus_sintetico_pii.json...
Executando Experimento E6 em 50 amostras...

Resultados do Experimento E6:
- Amostras analisadas: 50
- Recall de PII: 100.00% (Meta: >= 99%)
- Precisão: 100.00%
- Falsos Positivos: 0 (0.00%)
- Falsos Negativos (Vazamentos): 0
- Acurácia Geral: 100.00%

Relatório gerado com sucesso em: resultados/experimento-e6-anonimizacao.md
```

---

## 3. Verificação dos Critérios de Aceite

| Critério de Aceite | Evidência de Cumprimento |
|---|---|
| **1. Testes cobrem cada tipo de identificador** | 30 casos de teste em `tests/test_sanitizer.py` cobrindo IPv4, IPv6, MAC, hostnames/equipamentos, e-mails, CPFs, CNS, prontuários e nomes clínicos. |
| **2. Falha injetada no anonimizador $\Rightarrow$ nenhuma chamada externa** | Teste `test_falha_injetada_no_anonimizador_impede_chamada_externa` e `test_deteccao_residual_aciona_fail_closed_e_auditoria` em `tests/test_fail_closed.py` comprovando `provider_handler.assert_not_called()`. |
| **3. Relatório de recall/precisão em `resultados/`** | Relatório oficial gerado e consolidado em `resultados/experimento-e6-anonimizacao.md` com matriz de confusão e 100% de Recall. |
