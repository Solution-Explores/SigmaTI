# Issue #9 — pacote instalável do núcleo de engenharia

Base: `dev@086129c9b8dd119d72877f493e1828ef2a46c949` (PR #32 integrado).
Branch: `feat/9-pacote-sigma-eng`.

- [x] `engenharia/pyproject.toml` com metadados e extras `api`/`dev`.
- [x] Núcleo sem dependências externas; Python 3.12+.
- [x] Instalações editável e wheel importam `sigma_eng` fora do checkout.
- [x] Aplicação e auditoria usam apenas o import `sigma_eng`.
- [x] Remover alteração de `sys.path` do main e caminho `engenharia` do pytest.
- [x] API do pacote recebe a política de autorização explicitamente.
- [x] Preservar a localização da trilha de engenharia na aplicação hospedeira.
- [x] Testar 401/403 em todas as rotas de engenharia após a mudança.
- [x] CI instala `pip install -e .[dev]` em `engenharia/` e valida wheel/editável isoladamente.
- [x] Atualizar instruções de instalação e registrar evidências.
- [ ] Revisar e integrar esta entrega na dev; fechar #9 somente após entrega aprovada.

Não implementar PostgreSQL/sessões, scheduler ou as demais issues nesta alteração.
A autorização de dispensa da revisão de outro integrante foi específica do PR #32.
