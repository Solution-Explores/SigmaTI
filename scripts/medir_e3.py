"""E3: burn rate com queda prolongada e com corte curto.

Critério da #11: alvo caído por 10 min deve chegar a `page`; corte de 10 s não
deve paginar.

Duas condições, no sistema real (PostgreSQL isolado, API real, SSE real, alvo TCP
em loopback):

  A. queda de 10 min. Mede em que segundo a regra de `page` dispara, amostrando
     o burn rate a cada 2 s sobre o intervalo de indisponibilidade que o sistema
     registra (da detecção até agora, ainda aberto).

  B. corte de 10 s, com o serviço restabelecido na MESMA porta. Observa o que o
     sistema faz com o incidente depois da recuperação, e amostra o burn rate
     por 5 min.

Para a condição B o cálculo é feito duas vezes, de propósito:
  * `pelo_sistema`: usa o intervalo como o sistema o registra;
  * `limitado_em_10s`: usa o intervalo recortado nos 10 s reais de queda.
A diferença entre os dois é o resultado do experimento.
"""
import argparse
import datetime as dt
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
import uuid
from datetime import timedelta, timezone
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

import validate_collection as vc
from persistence.database import open_database
from persistence.identity import PostgresIdentityStore
from persistence.operational import PostgresOperationalStore
from auth import password_hasher
from sigma_eng import slo as slo_mod

OBJETIVO = slo_mod.SLO("disponibilidade dos alvos", alvo_pct=99.9, janela_dias=30)


class ServicoFixo:
    """Como o TCPService do ensaio, mas em porta escolhida, para poder voltar."""

    def __init__(self, porta=0):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("127.0.0.1", porta))
        self.port = self.socket.getsockname()[1]
        self.socket.listen(512)
        self.socket.settimeout(0.05)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        while not self.stop_event.is_set():
            try:
                conexao, _ = self.socket.accept()
                conexao.close()
            except socket.timeout:
                continue
            except OSError:
                return

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=1)
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.socket.close()


def primeira_pagina(intervalos, agora):
    """Regras disparadas agora, e se alguma delas é `page`."""
    disparos = slo_mod.burn_alerts(OBJETIVO, intervalos, agora)
    return disparos, any(d["acao"] == "page" for d in disparos)


def amostrar(inicio_indisponibilidade, duracao_s, passo_s, fim_indisponibilidade=None):
    """Amostra o burn rate ao longo do tempo. Devolve as amostras e o 1o `page`.

    Se fim_indisponibilidade for None, a queda esta em curso e o intervalo vai
    crescendo ate agora. Se for dado, o intervalo fica fixo nele.
    """
    amostras, page_em = [], None
    t_inicio = time.monotonic()
    while True:
        decorrido = time.monotonic() - t_inicio
        agora = dt.datetime.now(timezone.utc)
        fim = fim_indisponibilidade or agora
        intervalos = [(inicio_indisponibilidade, fim)] if fim > inicio_indisponibilidade else []
        disparos, paginou = (primeira_pagina(intervalos, agora) if intervalos else ([], False))
        amostras.append({
            "segundos_desde_a_queda": round(decorrido, 1),
            "burn_1h": round(slo_mod.burn_rate(OBJETIVO, intervalos, agora, timedelta(hours=1)), 3) if intervalos else 0.0,
            "burn_5min": round(slo_mod.burn_rate(OBJETIVO, intervalos, agora, timedelta(minutes=5)), 3) if intervalos else 0.0,
            "regras": [d["acao"] + "@" + str(d["limiar"]) for d in disparos]})
        if paginou and page_em is None:
            page_em = round(decorrido, 1)
        if decorrido >= duracao_s:
            return amostras, page_em
        time.sleep(passo_s)


def run(database_url, output, minutos_a, segundos_b, minutos_observacao_b):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    schema = "sigma_e3_" + uuid.uuid4().hex
    root_engine = create_engine(database_url, hide_parameters=True)
    engine = None
    servicos = []
    with root_engine.begin() as c:
        c.execute(text(f"CREATE SCHEMA {schema}"))
    try:
        isolated = make_url(database_url).update_query_dict(
            {"options": "-csearch_path=" + schema}).render_as_string(hide_password=False)
        env = dict(os.environ, SIGMA_DATABASE_URL=isolated,
                   SIGMA_COLLECTION_ENABLED="1", SIGMA_COLLECTION_CONCURRENCY="32",
                   SIGMA_COLLECTION_SEED="0", OPENROUTER_API_KEY="fake-only",
                   SIGMA_LLM_MODEL="test/model", SIGMA_JWT_SECRET=secrets.token_hex(32),
                   SIGMA_CORS_ORIGINS="http://localhost:5173", PYTHON_DOTENV_DISABLED="1",
                   SIGMA_PROBE_NETS="127.0.0.0/8",
                   SIGMA_AUDIT_PATH=str(output.parent / schema / "audit.jsonl"))
        mig = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                             cwd=ROOT, env=env, text=True, capture_output=True)
        if mig.returncode:
            raise RuntimeError("Migracao falhou: " + mig.stderr[-800:])
        engine = open_database(isolated)
        store = PostgresOperationalStore(engine)
        user, pw = "e3-burn", secrets.token_urlsafe(24)
        PostgresIdentityStore(engine).save_user(user, password_hasher.hash(pw), "gestor_ti")

        def derrubar(base, token, client, porta=0):
            """Cria alvo, espera medicao boa, derruba e espera a deteccao."""
            servico = ServicoFixo(porta)
            servicos.append(servico)
            status, alvo = vc.request(base, "POST", "/api/eng/alvos", {
                "nome": "e3-burn", "host": "127.0.0.1", "porta": servico.port,
                "intervalo_s": 0.5, "timeout_s": 0.5}, token)
            assert status == 200, status
            ident = alvo["id"]
            vc.wait_until(lambda: any(r["sucesso"] for r in store.measurements(ident)))
            porta_usada = servico.port
            servico.stop()
            _, _, payload = client.wait(lambda f, d: d.get("acao") == "incident.created"
                                        and d.get("alvo_id") == ident, timeout=20)
            incidente = payload["incidente_id"]
            linha = [r for r in store.incidents(limit=500) if r["id"] == incidente][0]
            return ident, incidente, linha["detectado_em"], porta_usada

        with vc.api_server(env, output.with_suffix(".log")) as base:
            status, login = vc.request(base, "POST", "/api/auth/login",
                                       {"username": user, "password": pw})
            assert status == 200, status
            token = login["access_token"]
            client = vc.SSEClient(base, token)
            try:
                # ---- Condicao A: queda prolongada -------------------------
                print("A: queda de", minutos_a, "min", flush=True)
                ident_a, inc_a, det_a, _ = derrubar(base, token, client)
                amostras_a, page_a = amostrar(det_a, minutos_a * 60, 2.0)
                aberto_a = [r for r in store.incidents(limit=500) if r["id"] == inc_a][0]
                vc.request(base, "PATCH", "/api/eng/alvos/" + ident_a, {"ativo": False}, token)

                # ---- Condicao B: corte curto, com retorno do servico ------
                print("B: corte de", segundos_b, "s", flush=True)
                ident_b, inc_b, det_b, porta_b = derrubar(base, token, client)
                time.sleep(segundos_b)
                retorno = ServicoFixo(porta_b)
                servicos.append(retorno)
                fim_real_b = dt.datetime.now(timezone.utc)
                # O alvo responde de novo: confirma pela propria coleta.
                vc.wait_until(lambda: any(
                    r["sucesso"] for r in store.measurements(ident_b)
                    if r["ts"] > fim_real_b - timedelta(seconds=1)), timeout=30)
                recuperado_em = dt.datetime.now(timezone.utc)
                # O sistema fecha o incidente sozinho quando a sonda volta (#71)?
                # Se fechar, o intervalo que ele registra termina ali, e e esse
                # intervalo que o burn rate tem de usar. Se nao fechar, a queda
                # segue "em curso" e o intervalo cresce ate agora.
                def fechado():
                    linha = [r for r in store.incidents(limit=500) if r["id"] == inc_b][0]
                    return linha["resolvido_em"]
                try:
                    vc.wait_until(lambda: fechado() is not None, timeout=20)
                except Exception:
                    pass
                fim_registrado = fechado()
                amostras_b, page_b = amostrar(det_b, minutos_observacao_b * 60, 5.0, fim_registrado)
                linha_b = [r for r in store.incidents(limit=500) if r["id"] == inc_b][0]
                # O mesmo calculo, com o intervalo recortado na queda real.
                agora_b = dt.datetime.now(timezone.utc)
                limitado = [(det_b, recuperado_em)]
                disparos_lim, page_lim = primeira_pagina(limitado, agora_b)
                burn_lim = {f"{j}": round(slo_mod.burn_rate(OBJETIVO, limitado, agora_b, d), 3)
                            for j, d in (("5min", timedelta(minutes=5)),
                                         ("1h", timedelta(hours=1)),
                                         ("6h", timedelta(hours=6)))}
                vc.request(base, "PATCH", "/api/eng/alvos/" + ident_b, {"ativo": False}, token)
            finally:
                client.close()

        relatorio = {
            "sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                                  capture_output=True).stdout.strip(),
            "slo": {"alvo_pct": OBJETIVO.alvo_pct, "janela_dias": OBJETIVO.janela_dias},
            "regras": [{"longa": str(l), "curta": str(c), "limiar": t, "acao": a}
                       for l, c, t, a in slo_mod.BURN_RULES],
            "A_queda_prolongada": {
                "duracao_min": minutos_a,
                "page_em_segundos": page_a,
                "incidente_resolvido_pelo_sistema": aberto_a["resolvido_em"] is not None,
                "burn_final": amostras_a[-1],
                "amostras": amostras_a},
            "B_corte_curto": {
                "duracao_real_s": segundos_b,
                "observacao_min": minutos_observacao_b,
                "alvo_voltou_a_responder": True,
                "incidente_resolvido_pelo_sistema": linha_b["resolvido_em"] is not None,
                "fim_registrado_pelo_sistema": (linha_b["resolvido_em"].isoformat()
                                                if linha_b["resolvido_em"] else None),
                "duracao_registrada_s": (round((linha_b["resolvido_em"] - det_b).total_seconds(), 3)
                                         if linha_b["resolvido_em"] else None),
                "pelo_sistema": {"page_em_segundos": page_b, "burn_final": amostras_b[-1]},
                "limitado_em_10s": {"paginou": page_lim, "regras": disparos_lim,
                                    "burn_por_janela": burn_lim},
                "amostras": amostras_b},
        }
        output.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
        resumo = {k: v for k, v in relatorio.items()}
        resumo["A_queda_prolongada"] = {k: v for k, v in relatorio["A_queda_prolongada"].items()
                                        if k != "amostras"}
        resumo["B_corte_curto"] = {k: v for k, v in relatorio["B_corte_curto"].items()
                                   if k != "amostras"}
        print(json.dumps(resumo, indent=2, ensure_ascii=False))
        return relatorio
    finally:
        for s in servicos:
            try:
                s.stop()
            except Exception:
                pass
        if engine is not None:
            engine.dispose()
        with root_engine.begin() as c:
            c.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        root_engine.dispose()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    p.add_argument("--minutos-a", type=int, default=10)
    p.add_argument("--segundos-b", type=int, default=10)
    p.add_argument("--observacao-b", type=int, default=5)
    a = p.parse_args()
    run(os.environ["SIGMA_TEST_DATABASE_URL"], a.output, a.minutos_a, a.segundos_b, a.observacao_b)
