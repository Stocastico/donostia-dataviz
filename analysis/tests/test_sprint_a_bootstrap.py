"""Tests de AN-10 — bootstrap IC95% para las correlaciones publicadas (sprint_a).

Unitarios con datos sintéticos + una verificación de integración sobre el
metrics_long.csv versionado (las filas de robustez llevan el intervalo).
"""
import numpy as np
import pandas as pd
import pytest

import sprint_a


def test_perfect_correlation_gives_tight_ci_at_one():
    x = pd.Series(np.arange(12.0))
    y = 2.0 * x + 1.0
    lo, hi = sprint_a.bootstrap_ci_pearson(x, y, n_boot=200, seed=1)
    assert lo == pytest.approx(1.0)
    assert hi == pytest.approx(1.0)


def test_ci_is_reproducible_with_seed():
    rng = np.random.default_rng(0)
    x = pd.Series(rng.normal(size=15))
    y = pd.Series(rng.normal(size=15))
    a = sprint_a.bootstrap_ci_pearson(x, y, n_boot=500, seed=42)
    b = sprint_a.bootstrap_ci_pearson(x, y, n_boot=500, seed=42)
    assert a == b


def test_ci_bounds_bracket_point_estimate_and_stay_in_range():
    rng = np.random.default_rng(3)
    x = pd.Series(rng.normal(size=20))
    y = pd.Series(x + rng.normal(scale=0.8, size=20))
    lo, hi = sprint_a.bootstrap_ci_pearson(x, y, n_boot=1000, seed=42)
    r = x.corr(y)
    assert -1.0 <= lo < r < hi <= 1.0


def test_independent_data_ci_contains_zero():
    rng = np.random.default_rng(7)
    x = pd.Series(rng.normal(size=200))
    y = pd.Series(rng.normal(size=200))
    lo, hi = sprint_a.bootstrap_ci_pearson(x, y, n_boot=1000, seed=42)
    assert lo < 0.0 < hi


def test_too_few_points_returns_nan():
    x = pd.Series([1.0, 2.0])
    y = pd.Series([2.0, 1.0])
    lo, hi = sprint_a.bootstrap_ci_pearson(x, y, n_boot=100, seed=1)
    assert np.isnan(lo) and np.isnan(hi)


def test_correlations_robustness_rows_carry_ci(tmp_path):
    """Integración: cada par clave publicado lleva IC95% coherente con su r."""
    df = sprint_a.load()
    _, _, robust = sprint_a.correlations(df)
    for row in robust:
        assert "pearson_ci95_lo" in row and "pearson_ci95_hi" in row
        assert row["pearson_ci95_lo"] <= row["pearson"] <= row["pearson_ci95_hi"]
        assert -1.0 <= row["pearson_ci95_lo"] <= row["pearson_ci95_hi"] <= 1.0
