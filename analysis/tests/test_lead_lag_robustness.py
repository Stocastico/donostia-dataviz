"""Tests de AN-16 — blindaje del lead/lag AN-6.

Sintéticos con semilla fija: series largas donde ADF/KPSS tienen respuesta
conocida, y paneles construidos con estructura conocida (shock común de año,
señal desfasada) para el control por efectos fijos de año y el test de
permutación.
"""
import numpy as np
import pandas as pd
import pytest

import lead_lag_robustness as llr


# ------------------------------------------------------------- ADF / KPSS ----
def test_df_tstat_rejects_for_white_noise():
    rng = np.random.default_rng(42)
    y = rng.normal(size=200)
    t = llr.df_tstat(y)
    assert t < llr.DF_CRIT["5%"]  # ruido blanco: claramente estacionario


def test_df_tstat_does_not_reject_for_random_walk():
    rng = np.random.default_rng(42)
    y = np.cumsum(rng.normal(size=200))
    t = llr.df_tstat(y)
    assert t > llr.DF_CRIT["5%"]  # paseo aleatorio: no se rechaza raíz unitaria


def test_df_tstat_short_series_returns_nan():
    assert np.isnan(llr.df_tstat(np.array([1.0, 2.0, 3.0])))


def test_df_tstat_constant_series_returns_nan():
    """Serie constante (ocurre en el panel real): X'X singular → NaN, no crash."""
    assert np.isnan(llr.df_tstat(np.zeros(10)))


def test_kpss_stat_constant_series_returns_nan():
    assert np.isnan(llr.kpss_stat(np.ones(10)))


def test_kpss_stat_small_for_stationary_noise():
    rng = np.random.default_rng(7)
    y = rng.normal(size=200)
    assert llr.kpss_stat(y) < llr.KPSS_CRIT["5%"]


def test_kpss_stat_large_for_random_walk():
    rng = np.random.default_rng(7)
    y = np.cumsum(rng.normal(size=200))
    assert llr.kpss_stat(y) > llr.KPSS_CRIT["1%"]


# ------------------------------------------------- efectos fijos de año ----
def _panel(values: dict[str, dict[int, float]]) -> pd.DataFrame:
    return pd.DataFrame(values).T


def test_demean_by_year_zeroes_column_means_and_keeps_nan():
    p = _panel({
        "a": {2020: 1.0, 2021: 4.0},
        "b": {2020: 3.0, 2021: np.nan},
    })
    d = llr.demean_by_year(p)
    assert d.loc["a", 2020] == pytest.approx(-1.0)
    assert d.loc["b", 2020] == pytest.approx(1.0)
    assert d.loc["a", 2021] == pytest.approx(0.0)  # único valor del año
    assert np.isnan(d.loc["b", 2021])


def test_year_fe_kills_common_shock_correlation():
    """Un shock común de año (macro) infla r contemporáneo; el FE de año lo quita."""
    rng = np.random.default_rng(42)
    years = list(range(2010, 2025))
    barrios = [f"b{i}" for i in range(12)]
    shock = rng.normal(scale=3.0, size=len(years))  # macro común
    act = _panel({b: {y: shock[j] + rng.normal(scale=0.5)
                      for j, y in enumerate(years)} for b in barrios})
    rent = _panel({b: {y: shock[j] + rng.normal(scale=0.5)
                       for j, y in enumerate(years)} for b in barrios})

    naive = llr.panel_corr_at_lag(act, rent, lag=0)
    fe = llr.panel_corr_at_lag(llr.demean_by_year(act), llr.demean_by_year(rent), lag=0)
    assert naive > 0.8          # el shock común domina
    assert abs(fe) < 0.3        # sin el componente común, casi nada


def test_panel_corr_recovers_lagged_signal():
    """Señal desfasada 1 año sin shock común → r(lag=1) alto, r(lag=0) bajo."""
    rng = np.random.default_rng(3)
    years = list(range(2010, 2026))
    barrios = [f"b{i}" for i in range(10)]
    act = {b: {y: rng.normal() for y in years} for b in barrios}
    rent = {b: {y: act[b][y - 1] + rng.normal(scale=0.3) for y in years[1:]}
            for b in barrios}
    r1 = llr.panel_corr_at_lag(_panel(act), _panel(rent), lag=1)
    r0 = llr.panel_corr_at_lag(_panel(act), _panel(rent), lag=0)
    assert r1 > 0.8
    assert abs(r0) < 0.3


# ------------------------------------------------------- permutaciones ----
def test_permutation_pvalue_small_for_real_lagged_signal():
    rng = np.random.default_rng(3)
    years = list(range(2010, 2026))
    barrios = [f"b{i}" for i in range(10)]
    act = {b: {y: rng.normal() for y in years} for b in barrios}
    rent = {b: {y: act[b][y - 1] + rng.normal(scale=0.3) for y in years[1:]}
            for b in barrios}
    p = llr.permutation_pvalue(_panel(act), _panel(rent), lag=1,
                               n_perm=500, seed=42)
    assert p < 0.05


def test_permutation_pvalue_large_for_noise():
    rng = np.random.default_rng(11)
    years = list(range(2010, 2026))
    barrios = [f"b{i}" for i in range(10)]
    act = _panel({b: {y: rng.normal() for y in years} for b in barrios})
    rent = _panel({b: {y: rng.normal() for y in years} for b in barrios})
    p = llr.permutation_pvalue(act, rent, lag=1, n_perm=500, seed=42)
    assert p > 0.1


def test_permutation_pvalue_reproducible():
    rng = np.random.default_rng(5)
    years = list(range(2012, 2025))
    act = _panel({f"b{i}": {y: rng.normal() for y in years} for i in range(6)})
    rent = _panel({f"b{i}": {y: rng.normal() for y in years} for i in range(6)})
    a = llr.permutation_pvalue(act, rent, lag=1, n_perm=200, seed=9)
    b = llr.permutation_pvalue(act, rent, lag=1, n_perm=200, seed=9)
    assert a == b
