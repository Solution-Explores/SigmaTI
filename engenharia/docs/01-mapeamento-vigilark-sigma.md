# 01 · Mapeamento Sentinel Vigilark → SIGMA

O Sentinel Vigilark é uma plataforma de monitoramento e segurança para nuvem, do mesmo autor. O SIGMA monitora uma rede hospitalar on-premise. Foram levadas ao SIGMA apenas as **ideias de funcionalidade** que fazem sentido no segundo contexto, **adaptadas e reescritas em Python puro** (sem ORM, SDK de nuvem ou LLM no núcleo) para serem testáveis e mensuráveis. O Vigilark é de mesma autoria; o código e a documentação do SIGMA não expõem o código-fonte dele.

## Funcionalidades levadas ao SIGMA

| Funcionalidade de referência | SIGMA (`sigma_eng/`) | Adaptação para o contexto hospitalar |
|---|---|---|
| Vigilância de serviços (disponibilidade e TLS) | `probe.py` | + repetição com perda, jitter e percentis; + allowlist de redes (anti-SSRF); inspeção de certificado opcional; relógio e conector injetáveis |
| SLO e orçamento de erros | `slo.py` | Funções puras; indisponibilidade como união de intervalos; recorte na janela; burn rate pela definição do SRE Workbook; alertas em múltiplas janelas |
| Gestão de incidentes | `incidents.py` | Só as métricas: MTTD/MTTA/MTTR com definições fixas, sem acoplamento a banco ou WebSocket |
| Trilha de auditoria | `audit_chain.py` | Cadeia de hash (opcionalmente HMAC), JSONL com `fsync`, verificação |
| Aprovações humanas | `approvals.py` | Máquina de estados; quatro olhos; papéis do SIGMA; expiração checada na decisão |
| Runbooks | `runbooks.py` | Execução sem shell; allowlist; validação de variáveis; dry-run por padrão; validação prévia de todos os passos |

## Novo (sem equivalente no Vigilark)

| Módulo | Motivo |
|---|---|
| `anomaly.py` | O SIGMA precisa **detectar** (RF01) e provar a qualidade da detecção, em vez de depender de alertas externos |
| `stats.py` | Percentis e resumos sem dependências |
| `experimentos/` | Reprodutibilidade para o TCC |

## Fora de escopo

| Área | Decisão |
|---|---|
| Módulos específicos de nuvem AWS (segurança, custos, IAM) | SIGMA é on-premise |
| Módulos de segurança ofensiva | Inadequados em rede hospitalar sem janela e autorização formais |
| Licenciamento comercial | O SIGMA é acadêmico |
| Assistente LLM no núcleo | O SIGMA já tem pipeline próprio de IA com anonimização (RF05) |

Itens com potencial futuro (postmortem estruturado, PRR, vigilância de mudanças, cofre de credenciais) estão nas issues do repositório.

## Propriedades garantidas (com teste)

Decisões de projeto que o núcleo do SIGMA assume e verifica automaticamente.

| # | Propriedade | Por que importa | Teste |
|---|---|---|---|
| 1 | Indisponibilidade é a **união** dos intervalos, sem dupla contagem | Incidentes sobrepostos não podem inflar o downtime nem "estourar" o SLO sem motivo | `test_uniao_nao_dupla_contagem` |
| 2 | Incidentes que cruzam a borda da janela são **recortados** | Um incidente que começou antes da janela e segue ativo precisa contar a parte que cai dentro dela | `test_incidente_cruzando_borda_e_recortado` |
| 3 | Runbooks **não usam shell**; só executam binários da allowlist, com variáveis validadas | Elimina a classe de injeção de comando por variável | `test_injecao_em_variavel_bloqueada`, `test_executor_real_sem_shell` |
| 4 | Aprovação vencida **não pode ser concedida**, mesmo sem varredura de expiração | Evita aprovar uma ação cujo contexto já mudou | `test_aprovacao_vencida_nao_pode_ser_aprovada` |

Nota de definição: o *burn rate* aqui é a razão entre o erro observado e o erro permitido pelo SLO (SRE Workbook), a mesma unidade usada nos limiares de alerta (14,4; 6; 3; 1).
