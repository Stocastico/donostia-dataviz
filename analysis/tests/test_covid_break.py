"""Tests de AN-20 — ruptura COVID: pendientes pre (≤2019) vs post (≥2021)."""
import numpy as np
import pandas as pd
import pytest

import covid_break as cb


def _series(d: dict[int, float]) -> pd.Series:
    return pd.Series(d, dtype=float)


def test_segmented_slopes_recovers_known_slopes():
    """Pre: +2/año (2012–2019); post: +6/año (2021–2024); 2020 es un cráter."""
    pre = {y: 2.0 * (y - 2012) for y in range(2012, 2020)}
    post = {y: 20.0 + 6.0 * (y - 2021) for y in range(2021, 2025)}
    s = _series({**pre, 2020: 1.0, **post})
    seg = cb.segmented_slopes(s)
    assert seg["slope_pre"] == pytest.approx(2.0)
    assert seg["slope_post"] == pytest.approx(6.0)
    assert seg["n_pre"] == 8
    assert seg["n_post"] == 4
    assert seg["aceleracion"] == pytest.approx(3.0)  # post/pre


def test_segmented_slopes_excludes_2020():
    """El cráter de 2020 no debe contaminar ninguna de las dos pendientes."""
    flat = {y: 10.0 for y in range(2015, 2025)}
    flat[2020] = 0.0
    seg = cb.segmented_slopes(_series(flat))
    assert seg["slope_pre"] == pytest.approx(0.0, abs=1e-9)
    assert seg["slope_post"] == pytest.approx(0.0, abs=1e-9)


def test_segmented_slopes_short_segment_is_nan():
    s = _series({2018: 1.0, 2019: 2.0, 2021: 3.0, 2022: 4.0})
    seg = cb.segmented_slopes(s)  # 2 puntos por tramo: insuficiente (<3)
    assert np.isnan(seg["slope_pre"])
    assert np.isnan(seg["slope_post"])


def test_recovery_year_first_year_at_or_above_2019():
    s = _series({2019: 100.0, 2020: 30.0, 2021: 80.0, 2022: 105.0, 2023: 120.0})
    assert cb.recovery_year(s) == 2022


def test_recovery_year_none_if_never_recovers():
    s = _series({2019: 100.0, 2020: 30.0, 2021: 50.0})
    assert cb.recovery_year(s) is None


def test_real_data_tables_structure():
    city, barrios = cb.build_tables()
    assert "airbnb_activity_city" in city.index
    assert {"slope_pre", "slope_post", "aceleracion", "recuperacion"} <= set(city.columns)
    # tabla por barrio: pendientes airbnb pre/post para los barrios con datos
    assert len(barrios) >= 10
    assert {"slope_pre", "slope_post"} <= set(barrios.columns)
