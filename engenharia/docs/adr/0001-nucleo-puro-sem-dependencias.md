# ADR 0001 · Núcleo em Python puro, sem banco nem framework

- **Status:** aceito
- **Contexto:** quando a regra de negócio fica acoplada a ORM, WebSocket e LLM, é difícil testar e medir isoladamente (o cálculo de SLO, por exemplo, só rodaria com banco).
- **Decisão:** `sigma_eng` recebe dados (intervalos, séries, eventos) e devolve resultados. Relógio, conector de rede e executor de comandos são injetáveis. Só `api.py` depende de FastAPI.
- **Consequências:** (+) 58 testes rápidos e determinísticos, sem infraestrutura; (+) os experimentos reutilizam o mesmo código de produção; (−) a persistência fica para uma camada adaptadora (ver issues).
