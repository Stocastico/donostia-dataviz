"""Tests de REC-13 — serie de snapshots de anuncios activos Inside Airbnb.

Piezas: resumen por snapshot (activos, % entire home, % con licencia),
reseñas en los 12 meses previos a cada fecha de snapshot (proxy de actividad,
mismo universo de listings) y la comparación de crecimientos que cuantifica
el sesgo de adopción (MET-7).
"""
import pandas as pd

import airbnb_snapshots as snaps


def _snapshot(ids, room_types=None, licenses=None) -> pd.DataFrame:
    n = len(ids)
    return pd.DataFrame({
        "id": ids,
        "room_type": room_types or ["Entire home/apt"] * n,
        "license": licenses if licenses is not None else [""] * n,
        "longitude": [0.5] * n,
        "latitude": [0.5] * n,
    })


# ------------------------------------------------- resumen por snapshot ----
def test_snapshot_summary_counts_and_shares():
    df = _snapshot(
        [1, 2, 3, 4],
        room_types=["Entire home/apt", "Entire home/apt", "Private room", "Hotel room"],
        licenses=["ESS00009", "", None, "Exempt"],
    )
    s = snaps.snapshot_summary(df)
    assert s["n_active"] == 4
    assert s["pct_entire_home"] == 50.0
    assert s["pct_licensed"] == 50.0  # "" y None no cuentan como licencia


# ------------------------------------------- reseñas por ventana de 12m ----
def test_reviews_ltm_counts_only_window_and_universe():
    reviews = pd.DataFrame({
        "listing_id": [1, 1, 2, 9],
        "date": ["2025-01-15", "2023-01-15", "2024-10-01", "2025-01-15"],
    })
    # el listing 9 no pertenece al universo Donostia → fuera
    out = snaps.reviews_ltm(reviews, universe={1, 2}, snapshot_dates=["2025-03-27"])
    assert out == {"2025-03-27": 2}  # 2025-01-15 (id 1) y 2024-10-01 (id 2)


# ------------------------------------------------- comparación MET-7 ----
def test_growth_comparison_quantifies_adoption_bias():
    active = {"2023-12-29": 100, "2025-09-29": 110}
    ltm = {"2023-12-29": 1000, "2025-09-29": 1500}
    g = snaps.growth_comparison(active, ltm)
    assert round(g["active_growth_pct"], 1) == 10.0
    assert round(g["reviews_growth_pct"], 1) == 50.0
    # las reseñas crecen 4.5× más que la oferta activa → el proxy exagera
    assert round(g["bias_ratio"], 2) == round(1.5 / 1.1, 2)


def test_barrio_counts_per_snapshot_uses_point_in_polygon():
    features = [{
        "properties": {"barrio_id": "egia"},
        "geometry": {"type": "Polygon", "coordinates": [[
            [0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
    }]
    df = _snapshot([1, 2, 3])
    df.loc[2, ["longitude", "latitude"]] = [99.0, 99.0]  # fuera de Donostia
    counts = snaps.barrio_counts(df, features)
    assert counts.to_dict() == {"egia": 2}
