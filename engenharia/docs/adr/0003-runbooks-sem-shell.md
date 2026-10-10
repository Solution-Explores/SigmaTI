# ADR 0003 · Runbooks sem shell, com allowlist e dry-run padrão

- **Status:** aceito
- **Contexto:** executar passos por um shell, substituindo variáveis por texto, permite injeção de comando: um valor como `10.0.0.1; rm -rf /` vira execução arbitrária. Em rede hospitalar o impacto é inaceitável.
- **Decisão:** `shlex.split` + `shell=False`; executável deve estar na allowlist; valores de variáveis seguem `^[A-Za-z0-9_.:/@=-]{1,128}$` e não podem começar com `-`; todos os passos são validados antes de o primeiro executar; `dry_run=True` é o padrão; passos com `requires_approval` exigem uma aprovação do mesmo `execução:passo`, de uso único.
- **Consequências:** (+) a classe de injeção por variável deixa de existir; (−) runbooks com pipes/redirecionamentos não funcionam e devem virar passos separados ou scripts revisados e allowlistados.
