"""Normalize the barrios geometry into the single reference GeoJSON.

Reads the raw Donostia ``auzoak.json`` (already EPSG:4326), dissolves multipart
barrios (the same ``KodAuzo`` appearing as several polygons) into one feature,
assigns the stable ``barrio_id`` slug + clean ``name``, and simplifies the
geometry so it is light enough to ship to the browser.
"""

from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

from . import config

# Raw council names are SCREAMING CAPS; map to nicely-cased display names.
DISPLAY_NAME_OVERRIDES: dict[str, str] = {
    "amaraberri": "Amara Berri",
    "miramon-zorroaga": "Miramón-Zorroaga",
    "mirakruz-bidebieta": "Mirakruz-Bidebieta",
    "ategorrieta-ulia": "Ategorrieta-Ulia",
    "erdialdea": "Erdialdea (Centro)",
}

# Douglas–Peucker tolerance in degrees (~0.00012° ≈ 13 m at this latitude):
# enough detail for a city choropleth, ~10x smaller files.
SIMPLIFY_TOLERANCE = 0.00012


def _display_name(barrio_id: str, raw_name: str) -> str:
    if barrio_id in DISPLAY_NAME_OVERRIDES:
        return DISPLAY_NAME_OVERRIDES[barrio_id]
    return raw_name.title()


def normalize_barrios(raw_path: Path) -> dict:
    """Build the reference ``barrios.geojson`` dict from the raw council file.

    Dissolves by ``KodAuzo`` so each barrio is exactly one feature keyed by a
    stable ``barrio_id``; simplifies geometry for the web.
    """
    # The council file is UTF-8 with a BOM.
    raw = json.loads(raw_path.read_text(encoding="utf-8-sig"))

    # Group polygons by barrio code, remembering the first raw name seen.
    geoms_by_code: dict[str, list] = {}
    name_by_code: dict[str, str] = {}
    for feature in raw["features"]:
        props = feature["properties"]
        code = str(props["KodAuzo"])
        name_by_code.setdefault(code, props.get("name") or props.get("IzenAuzo"))
        geoms_by_code.setdefault(code, []).append(shape(feature["geometry"]))

    features = []
    for code, geoms in geoms_by_code.items():
        merged = unary_union(geoms)
        merged = merged.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
        raw_name = name_by_code[code]
        barrio_id = config.slugify_barrio(raw_name)
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "barrio_id": barrio_id,
                    "name": _display_name(barrio_id, raw_name),
                    "kod_auzo": code,
                },
                "geometry": mapping(merged),
            }
        )

    features.sort(key=lambda f: f["properties"]["name"])
    return {"type": "FeatureCollection", "name": "Donostia barrios", "features": features}


def barrio_ids(geojson: dict) -> set[str]:
    """The set of valid ``barrio_id``s — used by dataset modules and tests."""
    return {f["properties"]["barrio_id"] for f in geojson["features"]}
