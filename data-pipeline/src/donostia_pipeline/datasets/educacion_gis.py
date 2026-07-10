"""Educational facilities per 1000 inhabitants — first GIS spatial-join metric.

Source: Donostia Open Data ``servicios-educativos`` GeoJSON (point per facility,
WGS84). The points carry no barrio field, so we assign each to a barrio by
point-in-polygon against the reference geometry (``ctx.barrio_index``), then
normalize the per-barrio count by the latest-year population
(``ctx.population_latest``) — never a raw count on the map. Snapshot metric.

If no spatial index is available (e.g. the GeoJSON wasn't fetched), yields
nothing so the pipeline still runs.
"""

from __future__ import annotations

from ..gis_io import load_geojson, point_coords
from ..model import BuildContext, Metric
from ..spatial import BarrioIndex, rate_per_1000

GEOJSON_NAME = "educativos.json"
PERIOD = "actual"
SOURCE = "Donostia Open Data — equipamientos educativos (join espacial punto→barrio)"


def build(ctx: BuildContext) -> list[Metric]:
    index = ctx.barrio_index
    if not isinstance(index, BarrioIndex):
        return []

    geojson = load_geojson(ctx.raw_dir / GEOJSON_NAME)
    counts = index.count_points(point_coords(geojson["features"]))
    rates = rate_per_1000(counts, ctx.population_latest or {})

    return [
        Metric(
            id="schools_per_1000",
            label="Centros educativos (por 1000 hab.)",
            unit="por 1000 hab.",
            kind="sequential",
            theme="education",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[PERIOD],
            values={bid: {PERIOD: rate} for bid, rate in rates.items()},
        )
    ]
