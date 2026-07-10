"""HU-3 — Barrio-level commercial typology from OpenStreetMap (choropleth).

The HU-3 analysis (`analysis/commercial_typology.py`) classifies OSM commerce
and hospitality per barrio. This module lifts its headline barrio metric —
``hosteleria_share`` (hospitality as a share of all street-level premises) — to
the pipeline, so the app can map "which barrios are almost monofunctional
hospitality" (the Parte Vieja / centre) vs. everyday-shop barrios.

Data is a **curated snapshot** (`datos/input/tipologia_comercial_osm.csv`,
generated from Overpass) — not a live fetch — so the build stays reproducible
offline, like MICE/Ibiltur. ⚠️ OSM is a snapshot (foto actual, no evolución) and
its completeness varies by barrio; the metric is a **proportion, not a count**,
and barrios with too few mapped premises (< ``MIN_LOCALES``) are left null
(their share is an artefact, e.g. Miramón 5 locales → 100 %). The temporal proof
("shops close, bars open") is the city CNAE series (REC-7), triangulated in the
analysis — not this snapshot.

Stored as a percentage (0–100), theme ``tourism``, single snapshot period.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .. import config
from ..model import BuildContext, Metric

CSV = "tipologia_comercial_osm.csv"
PERIOD = "actual"
MIN_LOCALES = 15  # por debajo, la cuota es ruido de tejido fino → sin dato
SOURCE = (
    "OpenStreetMap (Overpass, shop=* + hostelería amenity=*), snapshot jul-2026; "
    "análisis HU-3 (analysis/commercial_typology.py)"
)


def build_from_csv(path: Path, barrio_ids: set[str]) -> list[Metric]:
    values: dict[str, dict[str, float | None]] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            bid = row["barrio_id"].strip()
            if bid not in barrio_ids:
                continue
            try:
                total = int(row["n_locales_total"])
                share = float(row["hosteleria_share"])
            except (TypeError, ValueError):
                continue
            values[bid] = {
                PERIOD: round(share * 100.0, 1) if total >= MIN_LOCALES else None
            }
    return [
        Metric(
            id="hosteleria_share",
            label="Cuota de restauración entre los locales (OSM)",
            unit="%",
            kind="sequential",
            theme="tourism",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[PERIOD],
            values=values,
        )
    ]


def build(ctx: BuildContext) -> list[Metric]:
    return build_from_csv(config.CURATED_DIR / CSV, ctx.barrio_ids)
