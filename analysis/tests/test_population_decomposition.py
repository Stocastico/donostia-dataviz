"""Tests de AN-12 — descomposición de la pérdida de población por cohortes.

La pieza central es la identidad contable exacta del residuo por cohortes:

    ΔP = nacimientos_proxy − defunciones_esperadas + migración_neta

construida por diseño: los grupos quinquenales de la pirámide envejecen un
grupo por ventana de 5 años, la mortalidad esperada sale de las ₅qx de
Gipuzkoa (INE) y el residuo es la estimación de migración neta.
"""
import json

import numpy as np
import pandas as pd
import pytest

import population_decomposition as pdec


# ------------------------------------------------------------------ slug ----
def test_slug_normaliza_nombres_del_padron():
    assert pdec.slug("ERDIALDEA") == "erdialdea"
    assert pdec.slug("AÑORGA") == "anorga"
    assert pdec.slug("ATEGORRIETA - ULIA") == "ategorrieta-ulia"
    assert pdec.slug("MIRAMON - ZORROAGA") == "miramon-zorroaga"
    assert pdec.slug("AMARABERRI") == "amaraberri"


# ------------------------------------------------------------- parse qx ----
def _ine_series(nombre: str, valores: dict[int, float]) -> dict:
    return {"Nombre": nombre,
            "Data": [{"Anyo": a, "Valor": v} for a, v in valores.items()]}


def test_parse_qx_convierte_por_mil_y_edades():
    payload = [
        _ine_series("Gipuzkoa. Total. 0 años. Riesgo de muerte. Dato base. ",
                    {2000: 3.4}),
        _ine_series("Gipuzkoa. Total. De 1 a 4 años. Riesgo de muerte. Dato base. ",
                    {2000: 0.3}),
        _ine_series("Gipuzkoa. Total. De 25 a 29 años. Riesgo de muerte. Dato base. ",
                    {2000: 3.0}),
        _ine_series("Gipuzkoa. Total. 95 y más años. Riesgo de muerte. Dato base. ",
                    {2000: 1000.0}),
        _ine_series("Gipuzkoa. Hombres. 0 años. Riesgo de muerte. Dato base. ",
                    {2000: 4.0}),
    ]
    qx = pdec.parse_qx(payload)
    total = qx[(qx.sexo == "Total") & (qx.year == 2000)].set_index("age_lo").qx
    assert total.loc[0] == pytest.approx(0.0034)
    assert total.loc[1] == pytest.approx(0.0003)
    assert total.loc[25] == pytest.approx(0.0030)
    assert total.loc[95] == pytest.approx(1.0)
    assert set(qx.sexo) == {"Total", "Hombres"}


def test_parse_qx_ignora_grupo_90_y_mas_solapado():
    payload = [
        _ine_series("Gipuzkoa. Total. De 90 a 94 años. Riesgo de muerte. Dato base. ",
                    {2000: 690.0}),
        _ine_series("Gipuzkoa. Total. 90 y más años. Riesgo de muerte. Dato base. ",
                    {1985: 800.0}),
        _ine_series("Gipuzkoa. Total. 95 y más años. Riesgo de muerte. Dato base. ",
                    {2000: 1000.0}),
    ]
    qx = pdec.parse_qx(payload)
    assert set(qx.age_lo) == {90, 95}


# ------------------------------------------------------------ window q5 ----
def _qx_constante(q: float) -> pd.DataFrame:
    """₅qx constante en todas las edades INE (0, 1, 5, 10, …, 95) y años."""
    rows = []
    for year in range(2000, 2005):
        for age in [0, 1] + list(range(5, 96, 5)):
            rows.append({"sexo": "Total", "year": year, "age_lo": age,
                         "qx": 1.0 if age == 95 else q})
    return pd.DataFrame(rows)


def test_window_q5_combina_0_y_1a4_y_cierra_95():
    q5 = pdec.window_q5(_qx_constante(0.01), 2000, 2005)
    assert len(q5) == pdec.N_GROUPS
    # grupo 00-04 = 1 − (1−q0)(1−q1_4)
    assert q5[0] == pytest.approx(1 - 0.99 * 0.99)
    assert q5[1] == pytest.approx(0.01)   # 05-09
    assert q5[-1] == pytest.approx(1.0)   # 95+ (intervalo abierto)


def test_window_q5_promedia_los_anios_de_la_ventana():
    qx = _qx_constante(0.01)
    qx.loc[(qx.year == 2004) & (qx.age_lo == 25), "qx"] = 0.03
    q5 = pdec.window_q5(qx, 2000, 2005)
    i25 = pdec.AGE_LOS_PYR.index(25)
    assert q5[i25] == pytest.approx((0.01 * 4 + 0.03) / 5)


# ----------------------------------------------------------- decompose ----
def _pyramid(rows: list[tuple[str, int, int, float]]) -> pd.DataFrame:
    """(barrio, year, age_idx, pop) → formato interno largo."""
    return pd.DataFrame(rows, columns=["barrio", "year", "age_idx", "pop"])


def _stationary(barrio="egia", pop=100.0):
    """Pirámide plana: misma población en cada grupo, dos cortes."""
    rows = []
    for year in (2000, 2005):
        for i in range(pdec.N_GROUPS):
            rows.append((barrio, year, i, pop))
    return _pyramid(rows)


def test_decompose_identidad_contable_exacta():
    rng = np.random.default_rng(42)
    rows = []
    for year in (2000, 2005):
        for i in range(pdec.N_GROUPS):
            rows.append(("egia", year, i, float(rng.integers(50, 500))))
    pyr = _pyramid(rows)
    q5 = np.full(pdec.N_GROUPS, 0.05)
    q5[-1] = 1.0
    out = pdec.decompose(pyr, q5, 2000, 2005).loc["egia"]
    assert out["delta"] == pytest.approx(
        out["nacimientos_proxy"] - out["defunciones_esperadas"]
        + out["migracion_neta"])


def test_decompose_sin_mortalidad_ni_migracion():
    """Pirámide plana sin muertes: cada cohorte reemplaza a la anterior;
    el 95+ recibe 90-94 + 95+ (200) pero mantiene 100 → −100 de migración
    en ese grupo, compensada por el proxy de nacimientos (+100). Neto: Δ=0."""
    pyr = _stationary()
    q5 = np.zeros(pdec.N_GROUPS)
    out = pdec.decompose(pyr, q5, 2000, 2005).loc["egia"]
    assert out["delta"] == pytest.approx(0.0)
    assert out["defunciones_esperadas"] == pytest.approx(0.0)
    assert out["nacimientos_proxy"] == pytest.approx(100.0)
    assert out["migracion_neta"] == pytest.approx(-100.0)


def test_decompose_detecta_migracion_inyectada():
    """+80 personas extra en 30-34 en t1 sobre los supervivientes exactos."""
    q = 0.02
    rows = []
    for i in range(pdec.N_GROUPS):
        rows.append(("gros", 2000, i, 100.0))
    for i in range(pdec.N_GROUPS):
        if i == 0:
            pop = 90.0                      # nacidos en la ventana
        elif i == pdec.N_GROUPS - 1:
            pop = 100.0 * (1 - q) + 0.0     # recibe 90-94; 95+ no sobrevive
        else:
            pop = 100.0 * (1 - q)
        i30 = pdec.AGE_LOS_PYR.index(30)
        if i == i30:
            pop += 80.0
        rows.append(("gros", 2005, i, pop))
    pyr = _pyramid(rows)
    q5 = np.full(pdec.N_GROUPS, q)
    q5[-1] = 1.0
    out = pdec.decompose(pyr, q5, 2000, 2005).loc["gros"]
    assert out["migracion_neta"] == pytest.approx(80.0)
    assert out["nacimientos_proxy"] == pytest.approx(90.0)
    assert out["defunciones_esperadas"] == pytest.approx(19 * 100 * q + 100)


def test_decompose_migracion_por_edad():
    q = 0.0
    rows = []
    for i in range(pdec.N_GROUPS):
        rows.append(("egia", 2000, i, 100.0))
    for i in range(pdec.N_GROUPS):
        pop = 100.0 if 0 < i < pdec.N_GROUPS - 1 else 0.0
        i25, i30 = pdec.AGE_LOS_PYR.index(25), pdec.AGE_LOS_PYR.index(30)
        if i == i25:
            pop -= 30.0   # se van veinteañeros (cohorte 20-24 → 25-29)
        if i == i30:
            pop += 10.0
        rows.append(("egia", 2005, i, pop))
    pyr = _pyramid(rows)
    m = pdec.migration_by_age(pyr, np.zeros(pdec.N_GROUPS), 2000, 2005)
    i25, i30 = pdec.AGE_LOS_PYR.index(25), pdec.AGE_LOS_PYR.index(30)
    assert m.loc["egia", i25] == pytest.approx(-30.0)
    assert m.loc["egia", i30] == pytest.approx(10.0)


def test_youth_exodus_tasa_de_cohorte():
    """Cohortes 25-39 en t0 (llegan a 30-44 en t1): tasa neta conjunta."""
    rows = []
    for i in range(pdec.N_GROUPS):
        rows.append(("erdialdea", 2000, i, 200.0))
        # sin mortalidad, cohortes estacionarias salvo fuga del 25-39
        pop = 200.0 if 0 < i < pdec.N_GROUPS - 1 else 0.0
        for lo in (30, 35, 40):           # destinos de 25-29, 30-34, 35-39
            if i == pdec.AGE_LOS_PYR.index(lo):
                pop -= 20.0
        rows.append(("erdialdea", 2005, i, pop))
    pyr = _pyramid(rows)
    tasa = pdec.youth_net_rate(pyr, np.zeros(pdec.N_GROUPS), 2000, 2005)
    assert tasa.loc["erdialdea"] == pytest.approx(-60.0 / 600.0)
