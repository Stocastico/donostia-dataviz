"""Spatial join of GIS datasets onto the reference barrios.

This is the bridge that lets GIS sources (points like schools/health centres,
grids like noise maps, polygons like green areas) be aggregated to ``barrio_id``
against the single reference geometry — the same "join once, at ingestion"
principle used for attribute datasets, extended to geometry.

Inputs are expected in EPSG:4326 (lon/lat); convert/​reproject SHP at load time
(``ogr2ogr``/``mapshaper`` or :mod:`pyproj`) before handing geometries here.

Only :mod:`shapely` is used (no geopandas/GDAL). An ``STRtree`` keeps point and
grid joins fast even for thousands of features.
"""

from __future__ import annotations

from typing import Iterable

from shapely.geometry import Point, shape
from shapely.strtree import STRtree


class BarrioIndex:
    """A spatial index over the reference barrios for point/areal joins."""

    def __init__(self, barrios_geojson: dict):
        feats = barrios_geojson["features"]
        self.barrio_ids: list[str] = [f["properties"]["barrio_id"] for f in feats]
        self._geoms = [shape(f["geometry"]) for f in feats]
        self._tree = STRtree(self._geoms)

    def assign_point(self, lon: float, lat: float) -> str | None:
        """Return the ``barrio_id`` containing ``(lon, lat)``, or None if outside.

        Uses the index to shortlist candidates, then prefers a true ``contains``;
        a point exactly on a shared edge falls back to the first barrio (in
        feature order) that touches it, for determinism.
        """
        point = Point(lon, lat)
        candidates = [int(i) for i in self._tree.query(point)]
        if not candidates:
            return None
        candidates.sort()  # feature order → deterministic boundary handling
        for i in candidates:
            if self._geoms[i].contains(point):
                return self.barrio_ids[i]
        for i in candidates:
            if self._geoms[i].intersects(point):  # on a boundary
                return self.barrio_ids[i]
        return None

    def count_points(self, points: Iterable[tuple[float, float]]) -> dict[str, int]:
        """Count points per barrio. Every barrio is present (0 if none); points
        outside the city are dropped."""
        counts = {bid: 0 for bid in self.barrio_ids}
        for lon, lat in points:
            bid = self.assign_point(lon, lat)
            if bid is not None:
                counts[bid] += 1
        return counts

    def areal_interpolate(
        self,
        features: Iterable[tuple[dict, float | None]],
        mode: str = "mean",
    ) -> dict[str, float | None]:
        """Aggregate valued source geometries to barrios, weighted by overlap area.

        ``features`` is an iterable of ``(geojson_geometry, value)``.

        * ``mode="mean"`` — area-weighted mean for *intensive* variables (e.g.
          noise dB): ``Σ(area∩ · v) / Σ(area∩)``. Barrios with no overlap → None.
        * ``mode="sum"`` — *extensive* variables split by overlap fraction of each
          source: ``Σ(v · area∩ / area_source)``. Barrios with no overlap → 0.
        """
        if mode not in ("mean", "sum"):
            raise ValueError(f"bad mode {mode!r}")
        num = {bid: 0.0 for bid in self.barrio_ids}
        weight = {bid: 0.0 for bid in self.barrio_ids}

        for geom_dict, value in features:
            if value is None:
                continue
            src = shape(geom_dict)
            src_area = src.area
            for i in (int(j) for j in self._tree.query(src)):
                inter_area = self._geoms[i].intersection(src).area
                if inter_area <= 0:
                    continue
                bid = self.barrio_ids[i]
                if mode == "mean":
                    num[bid] += inter_area * value
                    weight[bid] += inter_area
                elif src_area > 0:  # sum
                    num[bid] += value * (inter_area / src_area)

        if mode == "mean":
            return {bid: (num[bid] / weight[bid] if weight[bid] > 0 else None)
                    for bid in self.barrio_ids}
        return {bid: num[bid] for bid in self.barrio_ids}


def rate_per_1000(
    counts: dict[str, float],
    population: dict[str, float],
) -> dict[str, float | None]:
    """Normalize per-barrio counts to a rate per 1000 inhabitants.

    None when population is zero/unknown (rate undefined) — never map raw counts.
    """
    out: dict[str, float | None] = {}
    for bid, n in counts.items():
        pop = population.get(bid)
        out[bid] = round(n / pop * 1000.0, 2) if pop else None
    return out
