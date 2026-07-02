"""Tests de REC-14 — isla de calor superficial por barrio (Landsat C2 L2).

Piezas puras (sin red ni rasterio): conversión DN→°C, máscara de nubes del
qa_pixel, media zonal por polígono sobre una rejilla y la combinación de
escenas en anomalías respecto a la media de ciudad.
"""
import numpy as np
import pandas as pd

import heat_island as hi


def test_dn_to_celsius_scales_and_masks_nodata():
    dn = np.array([[0, 44000], [46926, 0]], dtype=np.uint16)
    c = hi.dn_to_celsius(dn)
    assert np.isnan(c[0, 0]) and np.isnan(c[1, 1])          # nodata = 0
    assert round(float(c[0, 1]), 1) == 26.2                  # 44000 DN
    assert round(float(c[1, 0]), 1) == 36.2                  # 46926 DN


def test_clear_mask_rejects_cloud_shadow_and_cirrus():
    clear = np.uint16(0b0000000000000000)
    cloud = np.uint16(1 << 3)
    shadow = np.uint16(1 << 4)
    dilated = np.uint16(1 << 1)
    cirrus = np.uint16(1 << 2)
    qa = np.array([[clear, cloud], [shadow, dilated], [cirrus, clear]])
    mask = hi.clear_mask(qa)
    assert mask.tolist() == [[True, False], [False, False], [False, True]]


def _grid():
    """Rejilla 2×2 de paso 1 con origen (0,2): centros en (0.5,1.5)…(1.5,0.5)."""
    return (0.0, 1.0, 2.0, -1.0)  # x0, dx, y0, dy (affine sin rotación)


def _square(barrio_id, x0, y0, lado=1.0):
    return {
        "properties": {"barrio_id": barrio_id},
        "geometry": {"type": "Polygon", "coordinates": [[
            [x0, y0], [x0 + lado, y0], [x0 + lado, y0 + lado],
            [x0, y0 + lado], [x0, y0]]]},
    }


def test_zonal_means_per_polygon():
    lst = np.array([[10.0, 20.0], [30.0, np.nan]])
    # barrio "a" = columna izquierda (2 px), "b" = celda superior derecha
    features = [_square("a", 0, 0, 1), _square("b", 1, 1, 1)]
    features[0]["geometry"]["coordinates"] = [[[0, 0], [1, 0], [1, 2], [0, 2], [0, 0]]]
    out = hi.zonal_means(lst, _grid(), features)
    assert out["a"] == (20.0, 2)   # (10+30)/2
    assert out["b"] == (20.0, 1)
    # el px NaN (abajo-derecha) no cuenta para nadie


def test_anomaly_table_averages_scene_anomalies():
    per_scene = [
        {"a": (20.0, 50), "b": (24.0, 50)},   # media ciudad 22 → a −2, b +2
        {"a": (10.0, 50), "b": (16.0, 50)},   # media ciudad 13 → a −3, b +3
    ]
    table = hi.anomaly_table(per_scene)
    assert isinstance(table, pd.DataFrame)
    assert round(table.loc["a", "lst_anomaly"], 2) == -2.5
    assert round(table.loc["b", "lst_anomaly"], 2) == 2.5
    assert table.loc["a", "n_scenes"] == 2


def test_anomaly_table_skips_barrios_with_few_pixels():
    per_scene = [{"a": (20.0, 5), "tiny": (99.0, 1)}]
    table = hi.anomaly_table(per_scene, min_pixels=3)
    assert "tiny" not in table.index
