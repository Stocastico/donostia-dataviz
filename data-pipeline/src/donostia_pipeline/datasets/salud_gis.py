"""Health facilities per 1000 inhabitants (REC-18) — GIS spatial-join metric.

Source: Donostia Open Data ``servicios-salud`` GeoJSON (point per facility —
hospitals, ambulatorios, health centres — served in WGS84). Same pattern as
``educacion_gis``: assign each point to a barrio by point-in-polygon
(``ctx.barrio_index``) and normalize the count by latest-year population
(``ctx.population_latest``); never a raw count on the map. Snapshot metric.

Together with ``schools_per_1000`` this is the "ciudad vivida" / accessibility
side of the two-cities story (H4): where the everyday services actually sit,
next to where the pressure is. If the GeoJSON isn't present, yields nothing so
the pipeline still runs.
"""

from __future__ import annotations

from ..gis_io import load_geojson, point_coords
from ..model import BuildContext, Metric
from ..spatial import BarrioIndex, rate_per_1000

GEOJSON_NAME = "salud.json"
PERIOD = "actual"
SOURCE = "Donostia Open Data — equipamientos de salud (join spaziale punto→barrio)"


def build(ctx: BuildContext) -> list[Metric]:
    index = ctx.barrio_index
    if not isinstance(index, BarrioIndex):
        return []

    geojson = load_geojson(ctx.raw_dir / GEOJSON_NAME)
    counts = index.count_points(point_coords(geojson["features"]))
    rates = rate_per_1000(counts, ctx.population_latest or {})

    return [
        Metric(
            id="health_per_1000",
            label="Servizi sanitari (per 1000 ab.)",
            unit="per 1000 ab.",
            kind="sequential",
            theme="health",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[PERIOD],
            values={bid: {PERIOD: rate} for bid, rate in rates.items()},
        )
    ]
