"""Tests de AN-15 — Moran's I global/local con pesos de contigüidad.

Rejilla 3×3 hecha a mano (rook): valores en gradiente → I>0 con p pequeña;
tablero de ajedrez → I<0; aleatorio → p grande. Contigüidad desde polígonos
sintéticos con shapely para la parte geométrica.
"""
import numpy as np
import pandas as pd
import pytest

import spatial_autocorrelation as sa


def _grid_w(side: int = 3) -> pd.DataFrame:
    """Matriz binaria de vecindad rook para una rejilla side×side."""
    n = side * side
    W = np.zeros((n, n))
    for r in range(side):
        for c in range(side):
            i = r * side + c
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < side and 0 <= cc < side:
                    W[i, rr * side + cc] = 1.0
    ids = [f"c{i}" for i in range(n)]
    return pd.DataFrame(W, index=ids, columns=ids)


def test_morans_i_positive_for_gradient():
    W = _grid_w()
    vals = pd.Series([0, 0, 0, 5, 5, 5, 10, 10, 10], index=W.index, dtype=float)
    i, p = sa.morans_i(vals, W, n_perm=999, seed=42)
    assert i > 0.3
    assert p < 0.05


def test_morans_i_negative_for_checkerboard():
    W = _grid_w()
    vals = pd.Series([1, 0, 1, 0, 1, 0, 1, 0, 1], index=W.index, dtype=float)
    i, _p = sa.morans_i(vals, W, n_perm=99, seed=42)
    assert i < -0.5


def test_morans_i_random_not_significant():
    W = _grid_w(4)
    rng = np.random.default_rng(7)
    vals = pd.Series(rng.normal(size=16), index=W.index)
    _i, p = sa.morans_i(vals, W, n_perm=999, seed=42)
    assert p > 0.1


def test_morans_i_handles_nan_by_dropping():
    W = _grid_w()
    vals = pd.Series([0, 0, 0, 5, 5, 5, 10, 10, np.nan], index=W.index)
    i, p = sa.morans_i(vals, W, n_perm=99, seed=1)
    assert np.isfinite(i)


def test_local_moran_flags_gradient_extremes():
    W = _grid_w()
    vals = pd.Series([0, 0, 0, 5, 5, 5, 10, 10, 10], index=W.index, dtype=float)
    loc = sa.local_moran(vals, W)
    # extremos rodeados de similares → I_i positivo en las esquinas del gradiente
    assert loc.loc["c0", "I_local"] > 0
    assert loc.loc["c8", "I_local"] > 0


def test_neighbours_from_synthetic_polygons():
    """Dos cuadrados que comparten borde son vecinos; uno lejano, no."""
    features = [
        {"properties": {"barrio_id": "a"},
         "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}},
        {"properties": {"barrio_id": "b"},
         "geometry": {"type": "Polygon", "coordinates": [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]]}},
        {"properties": {"barrio_id": "c"},
         "geometry": {"type": "Polygon", "coordinates": [[[5, 5], [6, 5], [6, 6], [5, 6], [5, 5]]]}},
    ]
    W = sa.contiguity_from_features(features)
    assert W.loc["a", "b"] == 1.0
    assert W.loc["a", "c"] == 0.0
    assert (np.diag(W) == 0).all()


def test_real_geojson_contiguity():
    W = sa.load_weights()
    assert W.shape == (19, 19)
    assert (W.values == W.values.T).all()
    # Los únicos sin vecino son los exclaves reales del municipio.
    isolated = set(W.index[W.sum(axis=1) == 0])
    assert isolated == {"landerbaso", "oarain", "zubieta"}
    # El núcleo urbano está bien conectado.
    assert W.loc["erdialdea"].sum() >= 3
