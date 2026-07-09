"""Tests de HU-5/HU-6 — desestacionalización del turismo (pernoctaciones INE).

Funciones puras con fixtures + integración contra la serie mensual real
(`series_long.csv`, overnight_stays 2005–2026). Hallazgo esperado: la
estacionalidad cae (la temporada baja crece más rápido que agosto); el cruce
directo con MICE no es posible (MICE solo anual) → limitación declarada.
"""
import numpy as np
import pandas as pd
import pytest

import tourism_deseasonalization as td


# --------------------------------------------------------- funciones puras ----
def test_seasonality_metrics_flat_year():
    flat = {m: 100.0 for m in range(1, 13)}
    s = td.seasonality_metrics(flat)
    assert s["cv"] == pytest.approx(0.0)
    assert s["peak_trough"] == pytest.approx(1.0)
    assert s["summer_share"] == pytest.approx(3 / 12 * 100)   # JAS = 3 de 12


def test_seasonality_metrics_peaky_year():
    peaky = {m: 10.0 for m in range(1, 13)}
    peaky[8] = 120.0                       # agosto disparado
    s = td.seasonality_metrics(peaky)
    assert s["peak_trough"] == pytest.approx(12.0)
    assert s["summer_share"] > 50          # JAS domina


def test_complete_years_filters_incomplete():
    df = pd.DataFrame({
        "year": [2019] * 12 + [2020] * 10,
        "month": list(range(1, 13)) + list(range(1, 11)),
        "value": [1.0] * 22,
    })
    assert td.complete_years(df) == [2019]     # 2020 solo tiene 10 meses


def test_month_growth_ratio():
    df = pd.DataFrame({
        "year": [2005] * 3 + [2025] * 3,
        "month": [1, 2, 8, 1, 2, 8],
        "value": [100.0, 100.0, 100.0, 300.0, 200.0, 150.0],
    })
    g = td.month_growth(df, 2005, 2025)
    assert g[1] == pytest.approx(3.0)      # enero ×3
    assert g[8] == pytest.approx(1.5)      # agosto ×1.5


# ------------------------------------------------------- integración real ----
def test_real_summer_share_falls():
    ym = td.year_metrics(td.read_overnight())
    assert ym.loc[2005, "summer_share"] == pytest.approx(37.2, abs=0.5)
    assert ym.loc[2025, "summer_share"] == pytest.approx(31.9, abs=0.5)
    assert ym.loc[2025, "summer_share"] < ym.loc[2005, "summer_share"]


def test_real_seasonality_lower_recent_than_early():
    ym = td.year_metrics(td.read_overnight())
    # media 2023–2025 menos estacional (CV) que 2005–2007
    early = ym.loc[[2005, 2006, 2007], "cv"].mean()
    late = ym.loc[[2023, 2024, 2025], "cv"].mean()
    assert late < early


def test_real_low_season_grows_faster_than_peak():
    """El mecanismo: valle (Ene/Feb/Nov/Dic) crece más que el pico (Ago)."""
    g = td.month_growth(td.read_overnight(), 2005, 2025)
    valley = np.mean([g[1], g[2], g[11], g[12]])
    peak = g[8]
    assert valley > peak


def test_2020_and_2026_excluded_as_incomplete():
    years = td.complete_years(td.read_overnight())
    assert 2020 not in years        # COVID: faltan meses
    assert 2026 not in years        # año en curso
    assert 2019 in years and 2025 in years
