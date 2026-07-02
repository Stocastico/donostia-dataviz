"""Tests de AN-9 — sensibilidad de pesos del Índice de Transformación (AN-8).

Datos sintéticos, sin tocar metrics_long.csv: cada test construye un DataFrame
de componentes (barrio × componente) con estructura conocida y verifica que la
maquinaria de permutación de pesos / variantes fijas / PCA se comporta como
debe. La ejecución sobre datos reales es el CLI (python analysis/index_sensitivity.py).
"""
import numpy as np
import pandas as pd
import pytest

import index_sensitivity as ixs


@pytest.fixture
def dominante() -> pd.DataFrame:
    """'top' domina ambos componentes → debe ser rank 1 con cualquier peso."""
    return pd.DataFrame(
        {"c1": [10.0, 5.0, 1.0, 0.0], "c2": [8.0, 4.0, 2.0, 1.0]},
        index=["top", "mid", "low", "min"],
    )


@pytest.fixture
def cruzado() -> pd.DataFrame:
    """'a' gana en c1, 'b' gana en c2 → el ranking depende del peso."""
    return pd.DataFrame(
        {"c1": [10.0, 0.0, 5.0], "c2": [0.0, 10.0, 5.0]},
        index=["a", "b", "c"],
    )


# ---------------------------------------------------------------- pesos ----
def test_random_weights_simplex():
    w = ixs.random_weights(n=200, k=3, seed=42)
    assert w.shape == (200, 3)
    assert (w >= 0).all()
    np.testing.assert_allclose(w.sum(axis=1), 1.0)


def test_random_weights_reproducible():
    a = ixs.random_weights(n=10, k=2, seed=7)
    b = ixs.random_weights(n=10, k=2, seed=7)
    np.testing.assert_array_equal(a, b)


# --------------------------------------------------------------- scores ----
def test_score_equal_weights_matches_mean_of_z(dominante):
    """Con pesos iguales el score reproduce el índice AN-8 (media de z-scores)."""
    got = ixs.score(dominante, np.array([0.5, 0.5]))
    z = (dominante - dominante.mean()) / dominante.std()
    expected = z.mean(axis=1)
    pd.testing.assert_series_equal(got, expected, check_names=False)


def test_score_single_component_orders_by_that_component(cruzado):
    got = ixs.score(cruzado, np.array([1.0, 0.0]))
    assert got.idxmax() == "a"
    got = ixs.score(cruzado, np.array([0.0, 1.0]))
    assert got.idxmax() == "b"


def test_ranks_rank1_is_best(dominante):
    r = ixs.ranks(dominante, np.array([0.5, 0.5]))
    assert r["top"] == 1
    assert r["min"] == len(dominante)


def test_rows_with_nan_are_excluded(dominante):
    df = dominante.copy()
    df.loc["top", "c1"] = np.nan
    r = ixs.ranks(df, np.array([0.5, 0.5]))
    assert "top" not in r.index
    assert len(r) == 3


# ----------------------------------------------------------- estabilidad ----
def test_rank_stability_dominant_always_first(dominante):
    tab = ixs.rank_stability(dominante, n=500, seed=42)
    assert tab.loc["top", "rank_min"] == 1
    assert tab.loc["top", "rank_max"] == 1
    assert tab.loc["top", "pct_top1"] == 1.0
    # el último en todo tampoco puede salir de la última posición
    assert tab.loc["min", "rank_min"] == len(dominante)


def test_rank_stability_contested_varies(cruzado):
    tab = ixs.rank_stability(cruzado, n=500, seed=42)
    # 'a' y 'b' oscilan entre el 1º y el último puesto según el peso
    assert tab.loc["a", "rank_min"] == 1
    assert tab.loc["a", "rank_max"] == 3
    assert 0.0 < tab.loc["a", "pct_top1"] < 1.0


def test_rank_stability_has_equal_weight_baseline(dominante):
    tab = ixs.rank_stability(dominante, n=50, seed=1)
    r_igual = ixs.ranks(dominante, np.array([0.5, 0.5]))
    pd.testing.assert_series_equal(
        tab["rank_igual"].astype(int), r_igual.loc[tab.index].astype(int),
        check_names=False,
    )


# -------------------------------------------------------- variantes fijas ----
def test_fixed_variants_columns_and_extremes(cruzado):
    tab = ixs.fixed_variants(
        cruzado, {"60/40": (0.6, 0.4), "40/60": (0.4, 0.6)}
    )
    assert list(tab.columns) == ["60/40", "40/60"]
    assert tab.loc["a", "60/40"] == 1  # más peso a c1 → gana quien domina c1
    assert tab.loc["b", "40/60"] == 1


# ------------------------------------------------------------------ PCA ----
def test_pca_perfectly_correlated_components():
    """Componentes idénticos → PC1 explica ~100% y ordena como el factor común."""
    base = pd.Series([3.0, 1.0, 2.0, 0.0], index=list("abcd"))
    df = pd.DataFrame({"c1": base, "c2": base * 2.0})
    scores, loadings, evr = ixs.pca_contrast(df)
    assert evr == pytest.approx(1.0)
    assert scores.idxmax() == "a"
    assert scores.idxmin() == "d"
    # convención de signo: cargas positivas (más componente = más transformación)
    assert (loadings > 0).all()


def test_pca_scores_align_with_equal_weight_score(dominante):
    scores, _, _ = ixs.pca_contrast(dominante)
    equal = ixs.score(dominante, np.array([0.5, 0.5]))
    assert scores.corr(equal) > 0.99


# ------------------------------------------------- datos reales (committed) ----
def test_componentes_reales_reproducen_ranking_publicado():
    """Con pesos iguales se reproduce el ranking publicado (INDICE-TRANSFORMACION.md):
    Modo A: Loiola 1º, Egia 2º (N=13) · Modo B: Erdialdea 1º, Gros 2º."""
    comps = ixs.load_components()
    a = comps["socioeconomico"]
    assert len(a) == 13
    ra = ixs.ranks(a, np.array([0.5, 0.5]))
    assert ra["loiola"] == 1
    assert ra["egia"] == 2

    b = comps["presion_turistica"]
    assert list(b.columns) == ["vut_density", "airbnb_density", "alquiler_nivel"]
    rb = ixs.ranks(b, np.full(3, 1 / 3))
    assert rb["erdialdea"] == 1
    assert rb["gros"] == 2
