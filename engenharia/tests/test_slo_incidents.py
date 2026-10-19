from datetime import datetime, timedelta, timezone

import pytest

from sigma_eng import incidents, slo

T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
H = timedelta(hours=1)


def test_uniao_nao_dupla_contagem():
    # Dois incidentes sobrepostos (30 min + 30 min com 15 min em comum) = 45 min, não 60.
    ivs = [(T0, T0 + timedelta(minutes=30)), (T0 + timedelta(minutes=15), T0 + timedelta(minutes=45))]
    assert slo.downtime_minutes(ivs, T0 - H, T0 + H) == 45


def test_incidente_cruzando_borda_e_recortado():
    inicio = T0
    ivs = [(T0 - timedelta(minutes=30), T0 + timedelta(minutes=30))]
    assert slo.downtime_minutes(ivs, inicio, T0 + H) == 30


def test_orcamento_99_9_em_30_dias():
    objetivo = slo.SLO("x", 99.9, 30)
    agora = T0 + timedelta(days=30)
    r = slo.error_budget(objetivo, [], agora)
    assert r.orcamento_total_min == pytest.approx(43.2)
    assert r.status == "healthy" and r.restante_pct == 100 and r.esgota_em is None


def test_status_at_risk_e_breaching():
    objetivo = slo.SLO("x", 99.9, 30)
    agora = T0 + timedelta(days=30)
    # 35 min de 43,2 → restam 19% → at_risk
    r = slo.error_budget(objetivo, [(agora - timedelta(days=2), agora - timedelta(days=2) + timedelta(minutes=35))], agora)
    assert r.status == "at_risk"
    # 60 min → estourou
    r = slo.error_budget(objetivo, [(agora - timedelta(days=2), agora - timedelta(days=2) + timedelta(minutes=60))], agora)
    assert r.status == "breaching" and r.restante_min == 0


def test_burn_rate_definicao_sre():
    objetivo = slo.SLO("x", 99.9, 30)
    agora = T0 + timedelta(days=30)
    # Fora do ar durante toda a última hora: erro observado 100% / permitido 0,1% = 1000
    assert slo.burn_rate(objetivo, [(agora - H, agora)], agora, H) == pytest.approx(1000)
    assert slo.burn_rate(objetivo, [], agora, H) == 0


def test_alerta_page_em_queda_total_e_silencio_apos_recuperacao():
    objetivo = slo.SLO("x", 99.9, 30)
    agora = T0 + timedelta(days=30)
    queda = [(agora - timedelta(minutes=10), agora)]
    assert any(a["acao"] == "page" for a in slo.burn_alerts(objetivo, queda, agora))
    # 20 min após a recuperação a janela curta (5 min) zera → regra de 1h não dispara
    depois = agora + timedelta(minutes=20)
    assert not any(a["limiar"] == 14.4 for a in slo.burn_alerts(objetivo, queda, depois))


def test_pico_curto_nao_pagina():
    objetivo = slo.SLO("x", 99.9, 30)
    agora = T0 + timedelta(days=30)
    # 10 s de queda: janela longa não passa de 14,4
    assert slo.burn_alerts(objetivo, [(agora - timedelta(seconds=10), agora)], agora) == []


def test_slo_invalido():
    with pytest.raises(ValueError):
        slo.SLO("x", 100)
    with pytest.raises(ValueError):
        slo.downtime_minutes([], T0, T0)


def test_metricas_incidentes():
    i1 = incidents.Incidente("a", inicio_real=T0, detectado_em=T0 + timedelta(seconds=30),
                             reconhecido_em=T0 + timedelta(seconds=90), resolvido_em=T0 + timedelta(minutes=10, seconds=30))
    i2 = incidents.Incidente("b", inicio_real=T0, detectado_em=T0 + timedelta(seconds=10))
    i3 = incidents.Incidente("c", detectado_em=T0, resolvido_em=T0 - H)  # relógio fora de ordem
    m = incidents.metricas([i1, i2, i3])
    assert m["total"] == 3
    assert m["MTTD"]["n"] == 2 and m["MTTD"]["media_s"] == 20
    assert m["MTTA"]["n"] == 1 and m["MTTA"]["media_s"] == 60
    assert m["MTTR"]["n"] == 1 and m["MTTR"]["media_s"] == 600


def test_intervalo_indisponivel():
    i = incidents.Incidente("a", detectado_em=T0, resolvido_em=T0 + H)
    assert i.intervalo_indisponivel() == (T0, T0 + H)
    assert incidents.Incidente("b", detectado_em=T0).intervalo_indisponivel() is None
