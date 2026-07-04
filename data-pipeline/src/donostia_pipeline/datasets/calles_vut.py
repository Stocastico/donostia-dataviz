"""Touristic housing (VUT/HUT) per **street** — street-granularity export.

Every other tourism metric in this project is aggregated to the 19 official
barrios. This one deliberately stops one level lower: the VUT census
(``vtur_censo.csv``) carries a full street address in ``helbidea`` (e.g.
``"ABUZTUAREN 31 KALEA 12; 01-DR"``), and the Donostia callejero
(*Nombres de calle*, zipped SHP) provides a **stable street code**
(``KodKalea``), ES/EU names and a **representative label point** per street.

Matching address → street lets us count touristic units per street and place a
point on the map, revealing which concrete streets are saturated — the Parte
Vieja axes, the beach-front paseos — that a barrio average washes out. It also
retires the long-standing "street addresses only, no callejero in the project"
limitation the backlog flags for both VUT (REC-12) and the catastro (REC-8).

Not a :class:`~donostia_pipeline.model.Metric`: the value lives on street
geometry, not on ``barrio_id``, so — like ``origen_paises_barrio`` — it exports
its own ``street_vut.json`` into ``web/src/data/``.

Method and honest caveats:
* **Match** is a longest-prefix lookup of the normalised address against every
  callejero name variant (EU/ES, long/short). Longest-prefix (not "cut at the
  first digit") is what keeps streets whose *name* contains a number, such as
  ``31 de Agosto`` / ``Abuztuaren 31 Kalea``. On the current census this
  matches 100 % of rows; ``matchRate`` in the payload keeps the pipeline honest
  if a future census introduces unmatched addresses.
* **Point, not line.** The callejero SHP ships label points, so each street is
  a single representative point (the centroid of its label points), not its
  axis. Read the map as "touristic units at this street", located at the
  street's label anchor — a point density, not a linear extent.
* **Snapshot.** The VUT census has no time dimension (same as ``vut``); this is
  a current-state map, not a trend.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from ..gis_io import load_shapefile_zip

RAW_ZIP = "callejero.zip"
CSV_NAME = "vtur_censo.csv"
SOURCE = (
    "Donostia Open Data — censo viviendas turísticas (helbidea) × "
    "callejero municipal (Nombres de calle, KodKalea)"
)

# Callejero name fields tried when indexing a street, richest/most-canonical
# first. Every non-empty variant is indexed so the address matcher can hit any
# of the forms the census uses (it mixes EU and ES spellings).
_NAME_FIELDS = ("IzenKalea", "IzenKaleaL", "NomCalleLa", "NomCalleCo", "IzenKaleaM")


def normalize(text: str) -> str:
    """Uppercase, strip accents, drop punctuation, collapse whitespace."""
    stripped = "".join(
        c for c in unicodedata.normalize("NFD", (text or "").upper())
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", stripped)).strip()


def build_index(callejero_fc: dict) -> dict:
    """Index the callejero: normalised name → code, plus per-code display info.

    ``by_name`` maps every normalised name variant to a street code (first
    writer wins, so the canonical EU name registered first is preferred).
    ``by_code`` carries display names and the representative point (centroid of
    the street's label points).
    """
    by_name: dict[str, str] = {}
    names: dict[str, dict] = {}
    pts: dict[str, list[tuple[float, float]]] = defaultdict(list)

    for feat in callejero_fc.get("features", []):
        props = feat.get("properties", {})
        code = str(props.get("KodKalea", "")).strip()
        if not code:
            continue
        for field in _NAME_FIELDS:
            key = normalize(props.get(field, ""))
            if key:
                by_name.setdefault(key, code)
        # Keep the first non-empty display names seen for the code.
        if code not in names:
            names[code] = {
                "nameEu": (props.get("IzenKaleaL") or props.get("IzenKalea") or "").strip(),
                "nameEs": (props.get("NomCalleLa") or props.get("NomCalleCo") or "").strip(),
            }
        geom = feat.get("geometry") or {}
        if geom.get("type") == "Point":
            lon, lat = geom["coordinates"][0], geom["coordinates"][1]
            pts[code].append((lon, lat))

    by_code: dict[str, dict] = {}
    for code, info in names.items():
        coords = pts.get(code, [])
        if not coords:
            continue  # a named row with no point can't be placed on the map
        lon = round(sum(c[0] for c in coords) / len(coords), 6)
        lat = round(sum(c[1] for c in coords) / len(coords), 6)
        by_code[code] = {**info, "lon": lon, "lat": lat}

    return {"by_name": by_name, "by_code": by_code}


def match_code(helbidea: str, index: dict) -> str | None:
    """Return the street code for an address, or ``None`` if unmatched.

    Longest-prefix match: try the whole normalised address, then drop trailing
    tokens (portal number, floor/door) one at a time until a callejero name
    matches. Longest-first is what protects street names that *contain* a
    number (e.g. ``Abuztuaren 31 Kalea``) from being truncated at that number.
    """
    tokens = normalize(helbidea).split()
    by_name = index["by_name"]
    for j in range(len(tokens), 0, -1):
        candidate = " ".join(tokens[:j])
        if candidate in by_name:
            return by_name[candidate]
    return None


def build_payload(callejero_fc: dict, vut_rows: list[dict]) -> dict:
    """Aggregate the VUT census to streets. Returns the ``street_vut.json`` payload."""
    index = build_index(callejero_fc)
    by_code = index["by_code"]

    units: dict[str, int] = defaultdict(int)
    vut: dict[str, int] = defaultdict(int)
    hut: dict[str, int] = defaultdict(int)
    beds: dict[str, int] = defaultdict(int)
    matched = 0

    for row in vut_rows:
        code = match_code(row.get("helbidea", ""), index)
        if code is None or code not in by_code:
            continue
        matched += 1
        units[code] += 1
        if str(row.get("Mota", "")).strip().upper() == "HUT":
            hut[code] += 1
        else:
            vut[code] += 1
        try:
            beds[code] += int(row.get("plazak"))
        except (TypeError, ValueError):
            pass

    streets = []
    for code in sorted(units, key=lambda c: (-units[c], c)):
        info = by_code[code]
        streets.append({
            "code": code,
            "nameEu": info["nameEu"],
            "nameEs": info["nameEs"],
            "lon": info["lon"],
            "lat": info["lat"],
            "units": units[code],
            "vut": vut[code],
            "hut": hut[code],
            "beds": beds[code],
        })

    total = len(vut_rows)
    return {
        "source": SOURCE,
        "totalRows": total,
        "matchedRows": matched,
        "matchRate": round(matched / total * 100, 1) if total else 0.0,
        "streetCount": len(streets),
        "streets": streets,
    }


def write_json(zip_path: Path, csv_path: Path, dest: Path) -> dict:
    """Read the callejero SHP + VUT census and write ``street_vut.json``. Returns it."""
    callejero_fc = load_shapefile_zip(zip_path)
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        vut_rows = list(csv.DictReader(fh))
    payload = build_payload(callejero_fc, vut_rows)
    dest.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
