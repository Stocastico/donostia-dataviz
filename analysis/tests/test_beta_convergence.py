"""Tests de AN-13 — beta-convergencia: Δindicador ~ α + β·nivel_inicial.

β<0 (IC excluye 0) → convergencia (los que partían bajos suben más);
β>0 → divergencia; IC conteniendo 0 → compatible con brecha estable.
"""
import numpy as np
import pandas as pd
import pytest

import beta_convergence as bc


# ------------------------------------------------------------------ OLS ----
def test_ols_exact_line():
    x = pd.Series([1.0, 2.0, 3.0, 4.0], index=list("abcd"))
    y = 2.0 * x + 1.0
    fit = bc.ols(x, y)
    assert fit["beta"] == pytest.approx(2.0)
    assert fit["alpha"] == pytest.approx(1.0)
    assert fit["r2"] == pytest.approx(1.0)
    assert fit["n"] == 4


def test_ols_drops_nan_pairs():
    x = pd.Series([1.0, 2.0, np.nan, 4.0], index=list("abcd"))
    y = pd.Series([1.0, np.nan, 3.0, 4.0], index=list("abcd"))
    fit = bc.ols(x, y)
    assert fit["n"] == 2


def test_ols_too_few_points_returns_nan():
    x = pd.Series([1.0, 2.0])
    fit = bc.ols(x, 2 * x)
    assert np.isnan(fit["beta"])


# ------------------------------------------------------------ bootstrap ----
def test_convergence_detected_ci_below_zero():
    rng = np.random.default_rng(42)
    level0 = pd.Series(rng.uniform(10, 30, size=15))
    rate = -0.5 * level0 + rng.normal(scale=0.5, size=15)
    lo, hi = bc.bootstrap_beta_ci(level0, rate, n_boot=500, seed=1)
    assert hi < 0  # IC95 entero por debajo de cero → convergencia


def test_stable_gap_ci_contains_zero():
    rng = np.random.default_rng(7)
    level0 = pd.Series(rng.uniform(10, 30, size=15))
    rate = pd.Series(rng.normal(scale=1.0, size=15))  # independiente del nivel
    lo, hi = bc.bootstrap_beta_ci(level0, rate, n_boot=500, seed=1)
    assert lo < 0 < hi


def test_bootstrap_reproducible():
    rng = np.random.default_rng(3)
    x = pd.Series(rng.uniform(0, 1, 12))
    y = pd.Series(rng.normal(size=12))
    assert (bc.bootstrap_beta_ci(x, y, n_boot=200, seed=5)
            == bc.bootstrap_beta_ci(x, y, n_boot=200, seed=5))


# ------------------------------------------------------- datos reales ----
def test_convergence_table_real_data_structure():
    tab = bc.convergence_table(bc.load())
    assert set(tab.index) == {"income_total", "rent_eur_m2", "pct_university"}
    for _, row in tab.iterrows():
        assert row["n"] >= 10  # los 13 clasificables, o más
        assert row["ci95_lo"] <= row["beta"] <= row["ci95_hi"]
        assert row["lectura"] in {"convergencia", "divergencia",
                                  "compatible con brecha estable"}
