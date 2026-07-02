"""Night-noise exposure per barrio — GIS areal metric (REC-2).

Source: Donostia Open Data ``ruido-noche`` — the strategic night-noise map
(Lnight), shipped as a zipped shapefile in EPSG:25830. The map is a set of
**nested iso-contours** (one polygon per threshold: Lnight ≥ 50/55/60/65/70 dB),
not a partition, so each polygon is the whole area at or above that level.

We surface the **share of each barrio's area exposed to ≥ 55 dB at night** — the
EU Environmental Noise Directive / WHO night-noise threshold above which sleep
disturbance is documented. Computed by areal overlap against the reference
geometry (``ctx.barrio_index``); the GIS module (P0.2) reprojects the SHP.

Choices and caveats (documented, not hidden):
* **Night** (Lnight, not day) noise: the health-relevant band.
* This is a **general night-noise exposure** metric. Strategic noise maps are
  dominated by **transport** (road/rail) noise, so the ranking reflects traffic
  arteries and the rail corridor (Amara, Intxaurrondo, Martutene) far more than
  leisure/tourism noise — it does **not** isolate nightlife. Read it as a
  quality-of-life / environmental-pressure layer, not as a tourism proxy.
* **% of area**, not population-weighted: we have no intra-barrio population
  surface, so this is area exposure, a defensible proxy — read as such.
* 2022 snapshot (latest of the 2008/2017/2022 biennial maps).
"""

from __future__ import annotations

from ..gis_io import load_shapefile_zip
from ..model import BuildContext, Metric
from ..spatial import BarrioIndex

ZIP_NAME = "ruido_noche_2022.zip"
PERIOD = "2022"
THRESHOLD_DB = 55
SOURCE = "Donostia Open Data — mapa estratégico de ruido nocturno (Lnight) 2022 (areal join)"


def _exposed_geoms(feature_collection: dict, threshold: int) -> list[dict]:
    """Geometries of contours at or above ``threshold`` dB (nested → outermost
    such contour already covers the louder ones)."""
    geoms = []
    for feat in feature_collection.get("features", []):
        iso = feat.get("properties", {}).get("Isovalue")
        if iso is not None and iso >= threshold and feat.get("geometry"):
            geoms.append(feat["geometry"])
    return geoms


def build(ctx: BuildContext) -> list[Metric]:
    index = ctx.barrio_index
    if not isinstance(index, BarrioIndex):
        return []
    zip_path = ctx.raw_dir / ZIP_NAME
    if not zip_path.exists():
        return []

    fc = load_shapefile_zip(zip_path)
    fractions = index.coverage_fraction(_exposed_geoms(fc, THRESHOLD_DB))
    values = {bid: {PERIOD: round(frac * 100, 1)} for bid, frac in fractions.items()}

    return [
        Metric(
            id="noise_night_pct55",
            label="Area esposta a rumore notturno ≥55 dB",
            unit="%",
            kind="sequential",
            theme="environment",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="year",
            periods=[PERIOD],
            values=values,
        )
    ]
