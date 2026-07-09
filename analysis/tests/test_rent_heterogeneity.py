"""Tests de H7 — ¿la presión del alquiler es uniforme por barrio? ¿y Zubieta?

El usuario propone que barrios pequeños/periféricos (p. ej. Zubieta) tendrían
dinámicas de precio propias. Doble hallazgo: (1) esos barrios **no tienen dato**
EMA (mercado fino) → no verificable; (2) entre los que sí, el este barato subió
más (convergencia en %). Funciones puras + integración con `rent_eur_m2` real.
"""
import numpy as np
import pandas as pd
import pytest

import rent_heterogeneity as rh


# --------------------------------------------------------- funciones puras ----
def test_classify_coverage():
    assert rh.classify_coverage(9, 9) == "completa"
    assert rh.classify_coverage(4, 9) == "parcial"
    assert rh.classify_coverage(0, 9) == "sin dato"


def test_coverage_counts_periods_and_marks_absent_as_sin_dato():
    df = pd.DataFrame({
        "barrio_id": ["gros", "gros"],
        "barrio_name": ["Gros", "Gros"],
        "period": [2016, 2024],
        "value": [12.2, 15.9],
    })
    universe = {"gros": "Gros", "zubieta": "Zubieta"}   # zubieta ausente en df
    cov = rh.coverage(df, universe)
    assert cov.loc["gros", "n_periods"] == 2
    assert cov.loc["zubieta", "n_periods"] == 0
    assert cov.loc["zubieta", "status"] == "sin dato"


def test_rent_growth_only_when_both_endpoints():
    df = pd.DataFrame({
        "barrio_id": ["loiola", "loiola", "martutene"],
        "barrio_name": ["Loiola", "Loiola", "Martutene"],
        "period": [2016, 2024, 2016],       # martutene sin 2024
        "value": [9.2, 13.6, 8.9],
    })
    g = rh.rent_growth(df, 2016, 2024)
    assert "loiola" in g.index and "martutene" not in g.index
    assert g.loc["loiola", "growth_pct"] == pytest.approx((13.6 / 9.2 - 1) * 100)


# ------------------------------------------------------- integración real ----
def test_real_zubieta_and_peripherals_have_no_rent_data():
    cov = rh.coverage(rh.read_rent(), rh.barrio_universe())
    sin = set(cov[cov["status"] == "sin dato"].index)
    assert {"zubieta", "igeldo", "anorga", "miramon-zorroaga"} <= sin
    assert len(sin) == 6            # 6 de 19 barrios sin dato EMA


def test_real_full_coverage_count():
    cov = rh.coverage(rh.read_rent(), rh.barrio_universe())
    full = cov[cov["status"] == "completa"]
    assert len(full) == 11          # 11 barrios con los 9 periodos


def test_real_cheap_east_grew_fastest():
    g = rh.rent_growth(rh.read_rent(), 2016, 2024)
    top = g["growth_pct"].idxmax()
    assert top == "loiola"                       # el este obrero encabeza
    assert g.loc["loiola", "growth_pct"] > g.loc["erdialdea", "growth_pct"]


def test_real_convergence_sign_cheaper_grew_more():
    """corr(nivel inicial, crecimiento) < 0: los baratos suben más (% convergencia)."""
    corr = rh.level_growth_corr(rh.read_rent(), 2016, 2024)
    assert corr < 0
