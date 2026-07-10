"""Tests de AN-6 (refinamiento) — lead/lag con la 2ª señal REATE, grano ciudad.

Dos frentes:
  * las **cargas** de datos (`city_rent_growth`, `licenses_flow`) sobre CSV mínimos
    sintéticos → forma y valores conocidos (diferencias, índice de año int);
  * la **mecánica** del lead/lag (emparejado por desfase, detrend, permutación)
    sobre series construidas con estructura conocida y semilla fija.
"""
import numpy as np
import pandas as pd
import pytest

import lead_lag_reate as llr


# --------------------------------------------------------------- cargas ----
def test_city_rent_growth_is_first_difference_of_yearly_mean():
    m = pd.DataFrame({
        "metric_id": ["rent_eur_m2"] * 6,
        "period": ["2016", "2016", "2017", "2017", "2018", "2018"],
        "value": [10.0, 12.0, 12.0, 14.0, 13.0, 15.0],  # medias 11, 13, 14
    })
    g = llr.city_rent_growth(m)
    assert list(g.index) == [2017, 2018]           # se pierde el primer año
    assert g.loc[2017] == pytest.approx(2.0)       # 13 − 11
    assert g.loc[2018] == pytest.approx(1.0)       # 14 − 13


def test_city_rent_growth_ignores_other_metrics_and_nonyear_periods():
    m = pd.DataFrame({
        "metric_id": ["rent_eur_m2", "rent_eur_m2", "otra", "rent_eur_m2"],
        "period": ["2016", "2017", "2016", "media_movil"],
        "value": [10.0, 11.0, 999.0, 500.0],
    })
    g = llr.city_rent_growth(m)
    assert list(g.index) == [2017]
    assert g.loc[2017] == pytest.approx(1.0)


def test_licenses_flow_indexed_by_int_year_sorted():
    ind = pd.DataFrame({
        "id": ["vut_licenses_new", "vut_licenses_new", "otro"],
        "year": [2018, 2016, 2016],
        "value": [189.0, 175.0, 42.0],
    })
    s = llr.licenses_flow(ind)
    assert list(s.index) == [2016, 2018]           # ordenado, solo la señal
    assert s.index.dtype.kind == "i"
    assert s.loc[2016] == 175.0


# --------------------------------------------------- lead/lag mecánica ----
def test_corr_at_lag_aligns_signal_lag_positive_precedes():
    # target[t] = signal[t-1] exactamente → r(+1) perfecto, n = puntos solapados
    signal = pd.Series({2015: 1.0, 2016: 2.0, 2017: 5.0, 2018: 9.0})
    target = pd.Series({2016: 1.0, 2017: 2.0, 2018: 5.0})
    r, n = llr._corr_at_lag(signal, target, lag=1)
    assert r == pytest.approx(1.0)
    assert n == 3


def test_corr_at_lag_drops_years_without_source():
    signal = pd.Series({2017: 3.0, 2018: 4.0})
    target = pd.Series({2016: 1.0, 2017: 2.0, 2018: 3.0})
    # lag=0: solo 2017 y 2018 tienen señal → n=2 → _pearson exige ≥3 → NaN
    r, n = llr._corr_at_lag(signal, target, lag=0)
    assert n == 2
    assert np.isnan(r)


def test_lead_lag_series_columns_and_reading():
    signal = pd.Series({y: float(y) for y in range(2014, 2022)})
    target = pd.Series({y: float(y) for y in range(2016, 2022)})
    tab = llr.lead_lag_series(signal, target)
    assert list(tab.columns) == ["lag_anni", "r", "n", "lectura"]
    assert set(tab.lag_anni) == set(llr.LAGS)
    pos = tab[tab.lag_anni == 1].iloc[0]
    assert "turismo precede" in pos.lectura
    assert tab[tab.lag_anni == 0].iloc[0].lectura.startswith("mismo año")


# ------------------------------------------------------------- detrend ----
def test_detrend_removes_linear_trend():
    s = pd.Series({y: 2.0 * y + 3.0 for y in range(2010, 2020)})  # recta pura
    d = llr.detrend(s)
    assert np.allclose(d.values, 0.0, atol=1e-6)                  # residuo nulo


def test_detrend_keeps_curvature():
    s = pd.Series({y: float((y - 2015) ** 2) for y in range(2010, 2021)})
    d = llr.detrend(s)
    # una parábola no es lineal → quedan residuos no triviales
    assert np.nanstd(d.values) > 1.0


def test_detrend_short_series_centers_on_mean():
    s = pd.Series({2016: 1.0, 2017: 5.0})
    d = llr.detrend(s)
    assert d.loc[2016] == pytest.approx(-2.0)
    assert d.loc[2017] == pytest.approx(2.0)


# -------------------------------------------------------- permutación ----
def test_permutation_pvalue_small_for_perfect_lagged_signal():
    signal = pd.Series({y: float(v) for y, v in
                        zip(range(2010, 2022), [3, 1, 4, 1, 5, 9, 2, 6, 8, 7, 0, 5])})
    target = pd.Series({y: signal.loc[y - 1] for y in range(2011, 2022)})
    p = llr.permutation_pvalue(signal, target, lag=1, n_perm=2000, seed=1)
    assert p < 0.05


def test_permutation_pvalue_reproducible():
    signal = pd.Series({y: float(y % 5) for y in range(2010, 2022)})
    target = pd.Series({y: float((y * 7) % 3) for y in range(2012, 2022)})
    a = llr.permutation_pvalue(signal, target, lag=1, n_perm=300, seed=9)
    b = llr.permutation_pvalue(signal, target, lag=1, n_perm=300, seed=9)
    assert a == b


def test_permutation_pvalue_nan_when_corr_undefined():
    # solapamiento < 3 → r NaN → p NaN (no crash)
    signal = pd.Series({2017: 1.0, 2018: 2.0})
    target = pd.Series({2018: 1.0, 2019: 2.0})
    assert np.isnan(llr.permutation_pvalue(signal, target, lag=0, n_perm=50, seed=1))


# ------------------------------------------------------- robustez tabla ----
def test_robustness_table_shape_and_columns():
    signal = pd.Series({y: float((y * 3) % 7) for y in range(2014, 2024)})
    target = pd.Series({y: float((y * 5) % 4) for y in range(2016, 2024)})
    rob = llr.robustness_table(signal, target, n_perm=200, seed=3)
    assert list(rob.columns) == ["lag_anni", "n", "r_crudo", "r_detrended", "p_perm"]
    assert len(rob) == len(list(llr.LAGS))


def test_detrend_shrinks_trend_crossing_correlation():
    """Tendencias opuestas + ruido independiente → r crudo fuerte y espurio que
    se desploma al quitar las tendencias.

    Reproduce el artefacto real: licencias que bajan vs. alquiler que sube dan un
    r crudo cercano a −1 que es puro cruce de tendencias; el ruido subyacente no
    está correlacionado, así que detrended cae hacia 0.
    """
    rng = np.random.default_rng(0)
    years = list(range(2008, 2024))
    n_signal = rng.normal(scale=1.0, size=len(years))
    n_target = rng.normal(scale=1.0, size=len(years))
    signal = pd.Series({y: -3.0 * y + n_signal[i] for i, y in enumerate(years)})
    target = pd.Series({y: 3.0 * y + n_target[i] for i, y in enumerate(years)})
    r_raw, _ = llr._corr_at_lag(signal, target, lag=0)
    r_det, _ = llr._corr_at_lag(llr.detrend(signal), llr.detrend(target), lag=0)
    assert r_raw < -0.99                       # la tendencia domina el crudo
    assert abs(r_det) < abs(r_raw)             # el detrend lo encoge…
    assert abs(r_det) < 0.6                    # …hasta ruido sin señal clara
