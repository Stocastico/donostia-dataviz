"""Tests de HU-1 — percepción de (in)seguridad vs. criminalidad real ('tijera').

Funciones puras con fixtures; integración contra los CSV curados reales
(percepción Eustat zona Donostia 1989–2024; criminalidad parcial).
"""
import pandas as pd
import pytest

import perception_vs_crime as pc


# ------------------------------------------------ % de familias con problema -
def test_insecurity_share_from_grades():
    df = pd.DataFrame({
        "zona_id": ["70"] * 5,
        "year": [2024] * 5,
        "grado": ["Total", "Ningun_problema", "Algun_problema",
                  "Varios_problemas", "Muchos_problemas"],
        "familias_miles": [100.0, 78.5, 15.0, 6.0, 0.5],
    })
    s = pc.insecurity_share(df, "70")
    # con algún problema = (15 + 6 + 0.5)/100 = 21.5 %
    assert s[2024] == pytest.approx(21.5, abs=1e-6)


def test_insecurity_share_uses_total_as_denominator_not_sum():
    # el 'Total' es el denominador oficial (redondeos hacen que no cuadre la suma)
    df = pd.DataFrame({
        "zona_id": ["70", "70", "70"],
        "year": [2019, 2019, 2019],
        "grado": ["Total", "Ningun_problema", "Algun_problema"],
        "familias_miles": [167.6, 143.1, 19.6],
    })
    s = pc.insecurity_share(df, "70")
    assert s[2019] == pytest.approx((167.6 - 143.1) / 167.6 * 100, abs=1e-6)


# --------------------------------------------------------- dirección/tendencia
def test_trend_direction_labels():
    up = pd.Series({2019: 14.6, 2024: 21.5})
    down = pd.Series({2019: 21.5, 2024: 14.6})
    flat = pd.Series({2019: 20.0, 2024: 20.2})
    assert pc.trend_direction(up, 2019, 2024) == "sube"
    assert pc.trend_direction(down, 2019, 2024) == "baja"
    assert pc.trend_direction(flat, 2019, 2024, threshold=1.0) == "estable"


# ---------------------------------------------------------------- la tijera --
def test_scissors_diverge_when_perception_up_crime_down():
    perc = pd.Series({2019: 14.6, 2024: 21.5})   # percepción de problema sube
    crime = pd.Series({2019: 64.0, 2024: 55.0})  # criminalidad baja
    r = pc.scissors(perc, crime, 2019, 2024)
    assert r["perception"] == "sube"
    assert r["crime"] == "baja"
    assert r["veredicto"] == "divergen"           # la 'tijera' de HU-1


def test_scissors_coincide_when_both_rise():
    perc = pd.Series({2019: 14.6, 2024: 21.5})
    crime = pd.Series({2019: 64.0, 2024: 72.0})
    r = pc.scissors(perc, crime, 2019, 2024)
    assert r["veredicto"] == "coinciden"


# --------------------------------------------------------- integración real --
def test_read_perception_real_donostia_anchors():
    df = pc.read_perception()
    s = pc.insecurity_share(df, "70")
    assert s[1989] == pytest.approx(35.4, abs=0.2)   # máximo histórico
    assert s[2019] == pytest.approx(14.6, abs=0.2)   # mínimo reciente
    assert s[2024] == pytest.approx(21.5, abs=0.2)   # repunte 2024


def test_long_run_perception_better_than_1989():
    """El núcleo honesto de HU-1: 2024 percibe MENOS problemas que 1989."""
    df = pc.read_perception()
    s = pc.insecurity_share(df, "70")
    assert s[2024] < s[1989]            # 'ha bajado mucho' es falso a largo plazo
    assert s[2024] > s[2019]            # pero sí hay repunte reciente 2019→2024


def test_read_crime_real_partial_series():
    df = pc.read_crime()
    counts = pc.crime_series(df, "infracciones_penales")
    assert counts[2021] == pytest.approx(12705)
    assert counts[2020] < counts[2019]  # caída COVID 2020


# ------------------------------------ serie oficial Gipuzkoa (Min. Interior) --
def test_gipuzkoa_series_total_from_rows():
    df = pd.DataFrame({
        "provincia": ["Gipuzkoa"] * 4,
        "tipologia": ["TOTAL INFRACCIONES PENALES", "TOTAL INFRACCIONES PENALES",
                      "5.1.-Hurtos", "5.1.-Hurtos"],
        "year": [2019, 2024, 2019, 2024],
        "infracciones": [25016, 33425, 6094, 8023],
    })
    total = pc.gipuzkoa_series(df)                       # default = TOTAL
    assert total[2019] == pytest.approx(25016)
    assert total[2024] == pytest.approx(33425)
    hurtos = pc.gipuzkoa_series(df, "5.1.-Hurtos")
    assert hurtos[2024] == pytest.approx(8023)


def test_read_crime_gipuzkoa_real_anchors():
    df = pc.read_crime_gipuzkoa()
    total = pc.gipuzkoa_series(df)
    # serie completa y oficial 2010–2024 (provincia, no municipio)
    assert total.index.min() == 2010 and total.index.max() == 2024
    assert total[2010] == pytest.approx(24260)
    assert total[2024] == pytest.approx(33425)
    # plana en la década de 2010, salto reciente
    assert abs(total[2019] - total[2010]) / total[2010] < 0.10   # ~plana
    assert (total[2024] - total[2019]) / total[2019] > 0.25       # +34% real


def test_scissors_real_2019_2024_coincide():
    """Con la serie oficial: percepción↑ y criminalidad real↑ → COINCIDEN."""
    df = pc.read_perception()
    perc = pc.insecurity_share(df, "70")
    crime = pc.read_crime_gipuzkoa()
    total = pc.gipuzkoa_series(crime)
    r = pc.scissors(perc, total, 2019, 2024, threshold=1.0)
    assert r["perception"] == "sube"
    assert r["crime"] == "sube"
    assert r["veredicto"] == "coinciden"          # la 'tijera' NO se sostiene
