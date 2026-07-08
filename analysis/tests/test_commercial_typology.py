"""Tests de HU-3 — tipología comercial (OSM) por barrio.

La clasificación (juicio curado, editable) y la agregación se prueban con
fixtures; la carga vía Overpass es de red y no se testea (patrón heat_island).
"""
import pandas as pd
import pytest

import commercial_typology as ct


# ----------------------------------------------------------- clasificación --
@pytest.mark.parametrize("shop,expected", [
    ("gift", "turistico"),
    ("souvenir", "turistico"),
    ("confectionery", "turistico"),
    ("chocolate", "turistico"),
    ("art", "turistico"),
    ("bakery", "cotidiano"),
    ("greengrocer", "cotidiano"),
    ("butcher", "cotidiano"),
    ("hardware", "cotidiano"),      # ferretería, el ejemplo del usuario
    ("doityourself", "cotidiano"),
    ("supermarket", "cotidiano"),
    ("pharmacy", "cotidiano"),
    ("hairdresser", "cotidiano"),
    ("clothes", "otro"),            # retail general, no sesga a ningún lado
    ("jewelry", "otro"),
    ("books", "otro"),
])
def test_classify_shop_buckets(shop, expected):
    assert ct.classify({"shop": shop}) == expected


def test_classify_vacant():
    assert ct.classify({"shop": "vacant"}) == "vacant"
    assert ct.classify({"disused:shop": "yes"}) == "vacant"


def test_classify_hospitality_from_amenity():
    assert ct.classify({"amenity": "bar"}) == "hosteleria"
    assert ct.classify({"amenity": "restaurant"}) == "hosteleria"
    assert ct.classify({"amenity": "cafe"}) == "hosteleria"


def test_classify_amenity_takes_precedence_over_shop():
    # un local con amenity de hostelería cuenta como hostelería
    assert ct.classify({"amenity": "bar", "shop": "convenience"}) == "hosteleria"


def test_classify_unknown_and_empty():
    assert ct.classify({"shop": "spaceship"}) == "otro"   # shop desconocido → otro
    assert ct.classify({"amenity": "bench"}) is None      # ni comercio ni hostelería
    assert ct.classify({}) is None


# ------------------------------------------------------------ parseo OSM ----
def test_parse_overpass_node_and_way_center():
    elements = [
        {"type": "node", "id": 1, "lon": -1.98, "lat": 43.32,
         "tags": {"shop": "gift"}},
        {"type": "way", "id": 2, "center": {"lon": -1.99, "lat": 43.31},
         "tags": {"amenity": "bar"}},
        {"type": "node", "id": 3, "lon": -1.98, "lat": 43.32,
         "tags": {"amenity": "bench"}},   # se descarta (category None)
    ]
    df = ct.parse_overpass(elements)
    assert len(df) == 2
    assert set(df["category"]) == {"turistico", "hosteleria"}
    assert df.iloc[1]["lon"] == pytest.approx(-1.99)


# -------------------------------------------------- asignación a barrio ----
def _square(barrio_id, x0, y0, x1, y1):
    return {"type": "Feature", "properties": {"barrio_id": barrio_id},
            "geometry": {"type": "Polygon", "coordinates": [[
                [x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]}}


def test_assign_barrio_point_in_polygon():
    features = [_square("uno", -2.0, 43.30, -1.99, 43.31),
                _square("dos", -1.99, 43.30, -1.98, 43.31)]
    df = pd.DataFrame({"lon": [-1.995, -1.985, -1.90],
                       "lat": [43.305, 43.305, 43.40],
                       "category": ["gift", "bakery", "gift"]})
    out = ct.assign_barrio(df, features)
    assert list(out["barrio_id"]) == ["uno", "dos"]  # el 3º cae fuera → dropna


# ----------------------------------------------------- mezcla por barrio ----
def test_mix_by_barrio_counts_and_ratios():
    df = pd.DataFrame({
        "barrio_id": ["c"] * 6,
        "category": ["hosteleria", "hosteleria", "hosteleria",
                     "turistico", "cotidiano", "vacant"],
    })
    mix = ct.mix_by_barrio(df).set_index("barrio_id")
    row = mix.loc["c"]
    assert row["hosteleria"] == 3
    assert row["turistico"] == 1
    assert row["cotidiano"] == 1
    assert row["vacant"] == 1
    # n_comercios = comercios activos (turistico+cotidiano+otro), sin vacíos
    assert row["n_comercios"] == 2
    # hosteleria_share = 3 / (3 hosteleria + 2 comercios activos) = 0.6
    assert row["hosteleria_share"] == pytest.approx(3 / 5)
    # turistico_share_shops = turistico/(turistico+cotidiano) = 1/2
    assert row["turistico_share_shops"] == pytest.approx(0.5)
    assert row["vacancy_rate"] == pytest.approx(1 / 3)  # 1 vacant / 3 (2 activos+1)


# ------------------------------------------ triangulación temporal CNAE ----
def test_cnae_trend_real_endpoints():
    """El eje TEMPORAL de HU-3 (REC-7): retail baja, hostelería sube."""
    trend = ct.read_cnae_trend()
    retail = trend["retail_establishments_share"]
    hosp = trend["hospitality_establishments_share"]
    assert retail[2008] == pytest.approx(14.89, abs=0.01)
    assert retail[retail.index.max()] < retail[2008]   # comercio ↓
    assert hosp[hosp.index.max()] > hosp[2008]          # hostelería ↑
