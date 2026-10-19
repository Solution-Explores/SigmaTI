# Relatório de Evidências: Autenticação e Perfis (RF07) #6

**Data de Execução**: 2026-10-18  
**Ambiente**: Python 3.14.6 / Windows 11 / FastAPI 0.142.2 / pytest 9.1.1  
**Status**: Todas as suítes aprovadas com 100% de sucesso (Zero regressões)

---

## 1. Execução dos Testes de Sessão, JWT e Matriz RBAC

Comando executado:
```powershell
& .venv\Scripts\python.exe -m pytest tests/test_session_auth.py -v
```

Resultado da execução:
```text
============================= test session starts ==============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.7.0 -- D:\iohan\Faculdade\TCC\SigmaTi\SigmaTI\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\iohan\Faculdade\TCC\SigmaTi\SigmaTI
plugins: anyio-4.15.1
collected 67 items

tests/test_session_auth.py::TestHashingESenhas::test_hash_gera_salts_unicos PASSED [  1%]
tests/test_session_auth.py::TestHashingESenhas::test_verificar_senha_formato_invalido PASSED [  2%]
tests/test_session_auth.py::TestFluxoLoginESessaoJWT::test_login_sucesso_retorna_jwt_e_nao_expoe_chave_permanente PASSED [  4%]
tests/test_session_auth.py::TestFluxoLoginESessaoJWT::test_rota_me_e_logout PASSED [  5%]
tests/test_session_auth.py::TestFluxoLoginESessaoJWT::test_token_expirado_rejeitado_com_401 PASSED [  7%]
tests/test_session_auth.py::TestFluxoLoginESessaoJWT::test_token_assinatura_invalida_rejeitado_com_401 PASSED [  8%]
tests/test_session_auth.py::TestRateLimitingEAuditoria::test_bloqueio_apos_5_tentativas_e_registro_na_auditchain PASSED [ 10%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[GET-/api/status-None-suporte_n1] PASSED [ 11%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[GET-/api/alertas-None-suporte_n1] PASSED [ 13%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[POST-/api/alertas-payload2-suporte_n1] PASSED [ 14%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[GET-/api/pacotes-None-analista_redes] PASSED [ 16%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[GET-/api/incidentes-None-analista_redes] PASSED [ 17%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[GET-/api/relatorios-None-gestor_ti] PASSED [ 19%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[GET-/api/usuarios-None-gestor_ti] PASSED [ 20%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[POST-/api/usuarios-payload7-gestor_ti] PASSED [ 22%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[POST-/api/chaves/rotacao-None-gestor_ti] PASSED [ 23%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[GET-/api/n8n/acesso-None-gestor_ti] PASSED [ 25%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[POST-/api/eng/probe-payload10-analista_redes] PASSED [ 26%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[POST-/api/eng/slo/avaliar-payload11-analista_redes] PASSED [ 28%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[POST-/api/eng/incidentes/metricas-payload12-analista_redes] PASSED [ 29%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[POST-/api/eng/anomalias-payload13-analista_redes] PASSED [ 31%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_requisicao_sem_token_retorna_401[GET-/api/eng/auditoria/verificar-None-gestor_ti] PASSED [ 32%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[GET-/api/status-None-suporte_n1] PASSED [ 34%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[GET-/api/alertas-None-suporte_n1] PASSED [ 35%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[POST-/api/alertas-payload2-suporte_n1] PASSED [ 37%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[GET-/api/pacotes-None-analista_redes] PASSED [ 38%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[GET-/api/incidentes-None-analista_redes] PASSED [ 40%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[GET-/api/relatorios-None-gestor_ti] PASSED [ 41%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[GET-/api/usuarios-None-gestor_ti] PASSED [ 43%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[POST-/api/usuarios-payload7-gestor_ti] PASSED [ 44%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[POST-/api/chaves/rotacao-None-gestor_ti] PASSED [ 46%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[GET-/api/n8n/acesso-None-gestor_ti] PASSED [ 47%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[POST-/api/eng/probe-payload10-analista_redes] PASSED [ 49%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[POST-/api/eng/slo/avaliar-payload11-analista_redes] PASSED [ 50%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[POST-/api/eng/incidentes/metricas-payload12-analista_redes] PASSED [ 52%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[POST-/api/eng/anomalias-payload13-analista_redes] PASSED [ 53%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_suporte_n1[GET-/api/eng/auditoria/verificar-None-gestor_ti] PASSED [ 55%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[GET-/api/status-None-suporte_n1] PASSED [ 56%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[GET-/api/alertas-None-suporte_n1] PASSED [ 58%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[POST-/api/alertas-payload2-suporte_n1] PASSED [ 59%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[GET-/api/pacotes-None-analista_redes] PASSED [ 61%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[GET-/api/incidentes-None-analista_redes] PASSED [ 62%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[GET-/api/relatorios-None-gestor_ti] PASSED [ 64%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[GET-/api/usuarios-None-gestor_ti] PASSED [ 65%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[POST-/api/usuarios-payload7-gestor_ti] PASSED [ 67%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[POST-/api/chaves/rotacao-None-gestor_ti] PASSED [ 68%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[GET-/api/n8n/acesso-None-gestor_ti] PASSED [ 70%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[POST-/api/eng/probe-payload10-analista_redes] PASSED [ 71%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[POST-/api/eng/slo/avaliar-payload11-analista_redes] PASSED [ 73%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[POST-/api/eng/incidentes/metricas-payload12-analista_redes] PASSED [ 74%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[POST-/api/eng/anomalias-payload13-analista_redes] PASSED [ 76%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_analista_redes[GET-/api/eng/auditoria/verificar-None-gestor_ti] PASSED [ 77%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[GET-/api/status-None-suporte_n1] PASSED [ 79%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[GET-/api/alertas-None-suporte_n1] PASSED [ 80%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[POST-/api/alertas-payload2-suporte_n1] PASSED [ 82%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[GET-/api/pacotes-None-analista_redes] PASSED [ 83%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[GET-/api/incidentes-None-analista_redes] PASSED [ 85%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[GET-/api/relatorios-None-gestor_ti] PASSED [ 86%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[GET-/api/usuarios-None-gestor_ti] PASSED [ 88%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[POST-/api/usuarios-payload7-gestor_ti] PASSED [ 89%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[POST-/api/chaves/rotacao-None-gestor_ti] PASSED [ 91%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[GET-/api/n8n/acesso-None-gestor_ti] PASSED [ 92%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[POST-/api/eng/probe-payload10-analista_redes] PASSED [ 94%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[POST-/api/eng/slo/avaliar-payload11-analista_redes] PASSED [ 95%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[POST-/api/eng/incidentes/metricas-payload12-analista_redes] PASSED [ 97%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[POST-/api/eng/anomalias-payload13-analista_redes] PASSED [ 98%]
tests/test_session_auth.py::TestMatrizPermissoesRBAC::test_matriz_perfil_gestor_ti[GET-/api/eng/auditoria/verificar-None-gestor_ti] PASSED [100%]

============================= 67 passed in 7.12s ==============================
```

---

## 2. Bateria Geral de Regressão da Aplicação

Comando executado:
```powershell
$env:PYTHONPATH=".;engenharia"; & .venv\Scripts\python.exe -m pytest tests -q
```

Resultado da execução:
```text
280 passed in 30.06s
```

Comando executado no núcleo de engenharia:
```powershell
$env:PYTHONPATH=".;engenharia"; & .venv\Scripts\python.exe -m pytest engenharia/tests -q
```

Resultado da execução:
```text
54 passed, 1 skipped in 2.06s
```

---

## 3. Sumário Consolidado

- **Total de Testes Automatizados Executados**: 334 testes
- **Taxa de Sucesso**: 100.0%
- **Regressões Detectadas**: Nenhuma
- **Status do Bloqueador B9**: Mitigado e homologado
- **Status da Issue #6**: Pronta para encerramento
