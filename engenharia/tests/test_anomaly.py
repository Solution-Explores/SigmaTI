import random

import pytest

from sigma_eng.anomaly import EwmaDetector, MadDetector, avaliar


def _serie(seed=1, n=400, base=20.0, ruido=1.0):
    rng = random.Random(seed)
    return [base + rng.gauss(0, ruido) for _ in range(n)]


def test_sem_falsos_alarmes_em_serie_estavel():
    for det in (EwmaDetector(), MadDetector()):
        alarmes = sum(det.update(x) for x in _serie())
        assert alarmes <= 2  # k alto: praticamente nenhum


@pytest.mark.parametrize("fabrica", [EwmaDetector, MadDetector])
def test_detecta_degrau_com_pouco_atraso(fabrica):
    serie = _serie()
    rot = [False] * len(serie)
    for i in range(200, 240):
        serie[i] += 40
        rot[i] = True
    r = avaliar(fabrica(), serie, rot)
    assert r.eventos == 1 and r.eventos_detectados == 1
    assert r.atraso_medio <= 1
    assert r.revocacao > 0.9


def test_congelar_evita_virar_novo_normal():
    serie = _serie(n=300)
    for i in range(100, 300):
        serie[i] += 50
    com = EwmaDetector(congelar_em_anomalia=True)
    sem = EwmaDetector(congelar_em_anomalia=False)
    a_com = sum(com.update(x) for x in serie)
    a_sem = sum(sem.update(x) for x in serie)
    assert a_com > a_sem  # sem congelar, o modelo "aprende" a falha e silencia


def test_validacao():
    with pytest.raises(ValueError):
        EwmaDetector(alpha=0)
    with pytest.raises(ValueError):
        MadDetector(janela=3)
    with pytest.raises(ValueError):
        avaliar(EwmaDetector(), [1, 2], [True])


def test_serie_constante_nao_quebra():
    det = EwmaDetector()
    assert not any(det.update(5.0) for _ in range(100))
    assert det.update(5.5)  # qualquer desvio é anômalo quando a variância é zero


def test_reaprende_apos_mudanca_permanente_de_patamar():
    serie = _serie(n=500)
    for i in range(100, 500):
        serie[i] += 50  # novo patamar definitivo
    det = EwmaDetector(reaprender_apos=30)
    alarmes = [det.update(x) for x in serie]
    assert any(alarmes[100:130])       # alerta no início
    assert not any(alarmes[300:])      # e silencia depois de aceitar o novo normal
