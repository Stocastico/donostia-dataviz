"""Tests de AN-19 — regresión múltiple exploratoria del alquiler.

Sintéticos con estructura conocida (coeficientes recuperables, predictor
irrelevante) + estructura sobre los datos reales versionados.
"""
import numpy as np
import pandas as pd
import pytest

import rent_drivers as rd


@pytest.fixture
def datos_conocidos():
    """y = 2·a + 0·b + ruido pequeño; N=40 para que el OLS sea nítido."""
    rng = np.random.default_rng(42)
    X = pd.DataFrame({"a": rng.normal(size=40), "b": rng.normal(size=40)})
    y = 2.0 * X["a"] + rng.normal(scale=0.1, size=40)
    return X, y


def test_ols_multi_recovers_coefficients(datos_conocidos):
    X, y = datos_conocidos
    fit = rd.ols_multi(X, y)
    assert fit["coef"]["a"] == pytest.approx(2.0, abs=0.1)
    assert fit["coef"]["b"] == pytest.approx(0.0, abs=0.1)
    assert fit["r2"] > 0.95
    assert fit["n"] == 40


def test_ols_multi_drops_incomplete_rows(datos_conocidos):
    X, y = datos_conocidos
    X = X.copy()
    X.loc[0, "a"] = np.nan
    fit = rd.ols_multi(X, y)
    assert fit["n"] == 39


def test_ols_multi_too_few_rows_returns_nan():
    X = pd.DataFrame({"a": [1.0, 2.0], "b": [0.0, 1.0]})
    fit = rd.ols_multi(X, pd.Series([1.0, 2.0]))
    assert np.isnan(fit["r2"])


def test_bootstrap_ci_excludes_zero_for_real_effect(datos_conocidos):
    X, y = datos_conocidos
    ci = rd.bootstrap_coef_ci(X, y, n_boot=300, seed=1)
    assert ci["a"][0] > 0          # efecto real: IC enteramente positivo
    assert ci["b"][0] < 0 < ci["b"][1]  # irrelevante: IC cruza el 0


def test_delta_r2_positive_only_for_informative_predictor(datos_conocidos):
    X, y = datos_conocidos
    # añadir 'a' a un modelo solo-b debe subir mucho el R²; añadir 'b' a solo-a, casi nada
    gain_a = rd.delta_r2(X, y, add="a")
    gain_b = rd.delta_r2(X, y, add="b")
    assert gain_a > 0.5
    assert gain_b < 0.05


def test_real_data_report_structure():
    rep = rd.build_report()
    assert rep["n"] >= 12
    coefs = rep["modelo_completo"]["coef"]
    assert set(coefs) == {"income_total", "pct_university", "airbnb_density"}
    assert 0.0 <= rep["modelo_completo"]["r2"] <= 1.0
    assert "delta_r2_airbnb" in rep
