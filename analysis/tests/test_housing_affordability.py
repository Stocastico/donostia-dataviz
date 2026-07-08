"""Tests de HU-7 — asequibilidad: alquiler vs. renta vs. IPC.

Funciones puras probadas con datos sintéticos; dos comprobaciones de
integración contra los CSV reales del repo (anclas conocidas: IPC nacional
2016→2024 ≈ +23,7 %; alquiler Erdialdea 2016→2024 ≈ +29,2 %, citado en TESIS).
"""
import numpy as np
import pandas as pd
import pytest

import housing_affordability as ha


# --------------------------------------------------------------- rebase ----
def test_rebase_sets_base_year_to_100():
    s = pd.Series({2016: 10.0, 2020: 12.0, 2024: 15.0})
    r = ha.rebase(s, 2016)
    assert r[2016] == pytest.approx(100.0)
    assert r[2020] == pytest.approx(120.0)
    assert r[2024] == pytest.approx(150.0)


def test_rebase_missing_base_year_raises():
    s = pd.Series({2017: 10.0})
    with pytest.raises(KeyError):
        ha.rebase(s, 2016)


# ------------------------------------------------------ crecimiento/CAGR ----
def test_cumulative_growth_pct():
    s = pd.Series({2016: 100.0, 2024: 129.2})
    assert ha.cumulative_growth_pct(s, 2016, 2024) == pytest.approx(29.2, abs=1e-6)


def test_cagr_pct_matches_compound_definition():
    # +21 % en 2 años → CAGR = sqrt(1.21)-1 = 10 %
    s = pd.Series({2020: 100.0, 2022: 121.0})
    assert ha.cagr_pct(s, 2020, 2022) == pytest.approx(10.0, abs=1e-9)


# ---------------------------------------------------------------- deflate ---
def test_deflate_real_index_removes_inflation():
    # nominal +10 %, IPC +5 % ⇒ real ≈ +4,76 %
    nominal = pd.Series({2016: 100.0, 2024: 110.0})
    ipc = pd.Series({2016: 100.0, 2024: 105.0})
    real = ha.deflate_to_index(nominal, ipc, 2016)
    assert real[2016] == pytest.approx(100.0)
    assert real[2024] == pytest.approx(110.0 / 105.0 * 100, abs=1e-9)
    assert ha.cumulative_growth_pct(real, 2016, 2024) == pytest.approx(
        (1.10 / 1.05 - 1) * 100, abs=1e-9)


# --------------------------------------------------- media ponderada ciudad -
def test_population_weighted_city():
    value = pd.DataFrame({
        "barrio_id": ["a", "b", "a", "b"],
        "year": [2016, 2016, 2020, 2020],
        "value": [10.0, 20.0, 12.0, 22.0],
    })
    pop = pd.DataFrame({
        "barrio_id": ["a", "b", "a", "b"],
        "year": [2016, 2016, 2020, 2020],
        "value": [100.0, 300.0, 100.0, 300.0],
    })
    city = ha.population_weighted_city(value, pop)
    # 2016: (10*100 + 20*300)/400 = 17.5
    assert city[2016] == pytest.approx(17.5)
    assert city[2020] == pytest.approx((12 * 100 + 22 * 300) / 400)


def test_population_weighted_city_skips_barrio_without_population():
    value = pd.DataFrame({"barrio_id": ["a", "z"], "year": [2016, 2016],
                          "value": [10.0, 99.0]})
    pop = pd.DataFrame({"barrio_id": ["a"], "year": [2016], "value": [50.0]})
    city = ha.population_weighted_city(value, pop)
    assert city[2016] == pytest.approx(10.0)  # 'z' sin población se ignora


# ---------------------------------------------- esfuerzo (fórmula proyecto) -
def test_effort_ratio_matches_housing_tension_formula():
    rent = pd.Series({2016: 12.0})
    income = pd.Series({2016: 20000.0})
    eff = ha.effort_ratio(rent, income, m2=30)
    # 12 * 12 * 30 / 20000 * 100 = 21.6
    assert eff[2016] == pytest.approx(21.6)


def test_effort_ratio_aligns_common_years_only():
    rent = pd.Series({2016: 12.0, 2024: 16.0})
    income = pd.Series({2016: 20000.0})  # sin 2024
    eff = ha.effort_ratio(rent, income)
    assert list(eff.index) == [2016]


# --------------------------------------------------------- integración -----
def test_read_ipc_real_file_and_anchor():
    ipc = ha.read_ipc()
    assert ipc[2021] == pytest.approx(100.0, abs=0.01)  # base 2021
    # IPC nacional 2016→2024 ≈ +23,7 %
    assert ha.cumulative_growth_pct(ipc, 2016, 2024) == pytest.approx(23.7, abs=0.3)


def test_read_metric_rent_erdialdea_anchor():
    rent = ha.read_metric("rent_eur_m2")
    s = ha.series_by_year(rent, "erdialdea")
    assert s[2016] == pytest.approx(12.8419, abs=1e-3)
    assert s[2024] == pytest.approx(16.5889, abs=1e-3)
    # +29,2 % citado en TESIS-CIUDAD
    assert ha.cumulative_growth_pct(s, 2016, 2024) == pytest.approx(29.2, abs=0.3)


def test_rent_beats_inflation_citywide_2016_2024():
    """El núcleo de HU-7: el alquiler de ciudad crece más que el IPC."""
    rent = ha.read_metric("rent_eur_m2")
    pop = ha.read_metric("population")
    ipc = ha.read_ipc()
    city_rent = ha.population_weighted_city(rent, pop)
    rent_g = ha.cumulative_growth_pct(city_rent, 2016, 2024)
    ipc_g = ha.cumulative_growth_pct(ipc, 2016, 2024)
    assert rent_g > ipc_g  # alquiler por encima de la inflación
