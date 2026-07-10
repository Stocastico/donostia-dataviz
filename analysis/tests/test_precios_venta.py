"""Tests de REC-25 — cifras del precio de venta €/m² (analysis/precios_venta.py)."""

import pandas as pd
import pytest

import precios_venta as pv


def _df(*triples):
    return pd.DataFrame(triples, columns=["zona_idealista", "mes", "precio_eur_m2"])


def test_annual_mean_needs_min_months():
    df = _df(
        ("A", "2011-01", 100), ("A", "2011-02", 200),  # 2 meses → se cae
        ("A", "2012-01", 100), ("A", "2012-02", 200), ("A", "2012-03", 300),  # 3 → 200
    )
    annual = pv.annual_means(df)
    assert 2011 not in annual.columns or pd.isna(annual.loc["A", 2011])
    assert annual.loc["A", 2012] == 200


def test_years_before_first_year_excluded():
    df = _df(*[("A", f"2010-0{m}", 100) for m in range(1, 4)],
             *[("A", f"2011-0{m}", 200) for m in range(1, 4)])
    annual = pv.annual_means(df)
    assert list(annual.columns) == [2011]


def test_surge_from_trough():
    annual = pd.DataFrame({2013: [4000], 2014: [3000], 2026: [6000]}, index=["A"])
    surge = pv.surge_from_trough(annual)
    r = surge.iloc[0]
    assert r["min_year"] == 2014 and r["min"] == 3000
    assert r["last_year"] == 2026 and r["last"] == 6000
    assert r["surge_pct"] == pytest.approx(100.0)  # 3000 → 6000


def test_window_growth_only_zones_with_both_years():
    annual = pd.DataFrame({2016: [100, 200], 2026: [160, None]}, index=["A", "B"])
    w = pv.window_growth(annual, 2016, 2026)
    assert w.to_dict() == {"A": 60.0}  # B sin 2026 → fuera


def test_real_snapshot_shapes_and_story():
    df = pd.read_csv(pv.CSV)
    annual = pv.annual_means(df)
    # zonas rotas excluidas ya en el CSV curado
    assert "Miramon-Zorroaga" not in annual.index
    assert "Loiola-Martutene" not in annual.index
    # el techo (centro) por encima del suelo (este) en el último año
    last = int(annual.columns.max())
    assert annual.loc[pv.CEIL, last] > annual.loc[pv.FLOOR, last]
    # subida de ciudad 2016→2023 en el entorno del +29 % que cita el relato
    w = pv.window_growth(annual, 2016, 2023)
    assert 20 <= w.mean() <= 40
