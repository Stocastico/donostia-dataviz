"""Tests de AN-11 — tipologías de barrio (clustering jerárquico, numpy puro).

Sintéticos: dos/tres nubes bien separadas cuya estructura el clustering debe
recuperar, silhouette con respuesta conocida y vecino más parecido en una
configuración trivial.
"""
import numpy as np
import pandas as pd
import pytest

import barrio_typology as bt


@pytest.fixture
def dos_nubes() -> pd.DataFrame:
    """8 puntos: 4 alrededor de (0,0), 4 alrededor de (10,10)."""
    rng = np.random.default_rng(42)
    a = rng.normal(loc=0.0, scale=0.3, size=(4, 2))
    b = rng.normal(loc=10.0, scale=0.3, size=(4, 2))
    X = np.vstack([a, b])
    return pd.DataFrame(X, index=[f"p{i}" for i in range(8)], columns=["x", "y"])


def test_linkage_has_n_minus_1_merges(dos_nubes):
    merges = bt.linkage_average(dos_nubes.to_numpy(float))
    assert len(merges) == len(dos_nubes) - 1
    # las alturas de fusión no decrecen (average linkage sobre euclídea)
    heights = [m[2] for m in merges]
    assert all(h2 >= h1 - 1e-9 for h1, h2 in zip(heights, heights[1:]))


def test_cut_k2_recovers_the_two_clouds(dos_nubes):
    labels = bt.cut_labels(bt.linkage_average(dos_nubes.to_numpy(float)),
                           n=len(dos_nubes), k=2)
    assert len(set(labels[:4])) == 1
    assert len(set(labels[4:])) == 1
    assert labels[0] != labels[7]


def test_silhouette_high_for_true_clusters_low_for_random(dos_nubes):
    X = dos_nubes.to_numpy(float)
    good = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    bad = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    assert bt.silhouette_mean(X, good) > 0.8
    assert bt.silhouette_mean(X, bad) < 0.2
    assert bt.silhouette_mean(X, good) > bt.silhouette_mean(X, bad)


def test_silhouette_singleton_cluster_counts_as_zero():
    X = np.array([[0.0], [0.1], [5.0]])
    labels = np.array([0, 0, 1])  # el tercero es singleton
    s = bt.silhouette_mean(X, labels)
    assert np.isfinite(s)


def test_nearest_neighbour_trivial():
    df = pd.DataFrame({"v": [0.0, 1.0, 10.0]}, index=["a", "b", "c"])
    nn = bt.nearest_neighbour(df)
    assert nn.loc["a", "vecino"] == "b"
    assert nn.loc["b", "vecino"] == "a"
    assert nn.loc["c", "vecino"] == "b"


def test_silhouette_by_k_real_data_shape():
    """Integración: la tabla k→silhouette existe para k=2..6 sobre los datos reales."""
    X = bt.load_typology_vars()
    tab = bt.silhouette_by_k(X, ks=range(2, 7))
    assert list(tab.index) == [2, 3, 4, 5, 6]
    assert tab["silhouette"].between(-1, 1).all()
    assert len(X) >= 13
