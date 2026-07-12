"""Inside Airbnb — short-let density per barrio + monthly activity proxy (REC-4).

Source: Inside Airbnb, Euskadi region snapshot (``listings.csv.gz`` +
``reviews.csv.gz``). The region file covers the whole Basque Country, so we never
hard-filter by the source's ``neighbourhood`` field; instead each listing's
``(longitude, latitude)`` is assigned to a barrio by point-in-polygon against the
reference geometry (``ctx.barrio_index``). Listings outside Donostia fall outside
every barrio and are dropped — the same "join once, at ingestion" principle used
for the other GIS sources.

Two outputs, matching ``docs/PLAN-RECOLECCION.md`` §REC-4:

1. **Density** (``build`` → ``airbnb_density``): listings per 1000 inhabitants per
   barrio (snapshot). Comparable with ``vut_density`` — but Inside Airbnb counts
   *all* active listings (incl. unregistered), a wider universe than the legal VUT
   census, so the two are read together, not as the same thing.
2. **Activity series** (``build_series`` → ``airbnb_reviews``): reviews per month
   for the city's listings — the standard "San Francisco model" proxy for guest
   stays over time (a review ≈ a completed, reviewed booking). This is the
   temporal pressure series the snapshot VUT census cannot give. **Proxy**: it
   undercounts real stays (not every guest reviews) and is shaped by the platform's
   growth — read as a trajectory, not an occupancy count.
"""

from __future__ import annotations

import csv
import gzip
from collections import defaultdict
from pathlib import Path

from ..model import BuildContext, Metric, Series
from ..spatial import BarrioIndex, rate_per_1000

LISTINGS_GZ = "airbnb_listings.csv.gz"
REVIEWS_GZ = "airbnb_reviews.csv.gz"
SNAPSHOT = "2026-06"  # Inside Airbnb Euskadi snapshot 2026-06-30
SOURCE = (
    "Inside Airbnb — Euskadi (snapshot 2026-06-30); join espacial punto→barrio"
)
SOURCE_REVIEWS = (
    "Inside Airbnb — reseñas por mes (proxy de presencia turística, "
    "«modelo San Francisco»: una reseña ≈ una estancia reseñada); snapshot 2026-06-30"
)


def _open_gz(path: Path):
    """Open a gzipped CSV as a text stream (utf-8); lat/lon/id/date are ASCII."""
    return gzip.open(path, "rt", encoding="utf-8", newline="")


def _listing_barrio(ctx: BuildContext, index: BarrioIndex) -> dict[str, str]:
    """Map each listing id → barrio_id by point-in-polygon; drop those outside."""
    out: dict[str, str] = {}
    with _open_gz(ctx.raw_dir / LISTINGS_GZ) as fh:
        for row in csv.DictReader(fh):
            lon, lat = row.get("longitude"), row.get("latitude")
            if not lon or not lat:
                continue
            try:
                barrio_id = index.assign_point(float(lon), float(lat))
            except ValueError:
                continue
            if barrio_id is not None:
                out[row["id"]] = barrio_id
    return out


def build(ctx: BuildContext) -> list[Metric]:
    index = ctx.barrio_index
    if not isinstance(index, BarrioIndex):
        return []
    listings_path = ctx.raw_dir / LISTINGS_GZ
    if not listings_path.exists():
        return []

    listing_barrio = _listing_barrio(ctx, index)
    counts: dict[str, int] = defaultdict(int)
    for barrio_id in listing_barrio.values():
        counts[barrio_id] += 1
    # Every barrio present (0 if no listing), then normalized per capita.
    full = {bid: counts.get(bid, 0) for bid in index.barrio_ids}
    rates = rate_per_1000(full, ctx.population_latest or {})

    metrics = [
        Metric(
            id="airbnb_density",
            label="Densidad Airbnb (anuncios por 1000 hab.)",
            unit="por 1000 hab.",
            kind="sequential",
            theme="tourism",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[SNAPSHOT],
            values={bid: {SNAPSHOT: rate} for bid, rate in rates.items()},
        )
    ]

    # Barrio×year activity panel (for AN-6 lead/lag): reviews per barrio per year,
    # per capita. Reviews are the standard occupancy proxy; the per-year panel is
    # what the snapshot density can't give.
    activity = _activity_metric(ctx, index, listing_barrio)
    if activity is not None:
        metrics.append(activity)
    return metrics


def _reviews_by_barrio_year(ctx: BuildContext, listing_barrio: dict[str, str]) -> dict[str, dict[str, int]]:
    """barrio_id → {year → review count}, for listings inside the city."""
    acc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    with _open_gz(ctx.raw_dir / REVIEWS_GZ) as fh:
        for row in csv.DictReader(fh):
            barrio_id = listing_barrio.get(row.get("listing_id", ""))
            if barrio_id is None:
                continue
            year = (row.get("date") or "")[:4]
            if year.isdigit():
                acc[barrio_id][year] += 1
    return acc


def _activity_metric(
    ctx: BuildContext, index: BarrioIndex, listing_barrio: dict[str, str]
) -> Metric | None:
    """Reviews-per-1000-ab. per barrio per year (None if reviews not present)."""
    if not (ctx.raw_dir / REVIEWS_GZ).exists():
        return None
    population = ctx.population_latest or {}
    by_year = _reviews_by_barrio_year(ctx, listing_barrio)
    periods = sorted({y for years in by_year.values() for y in years})
    if not periods:
        return None

    # A barrio with no reviews in a year had ~zero activity (0.0, not n/d); only
    # barrios with unknown population are left null. The denominator is the latest
    # population (a fixed-denominator simplification, flagged in provenance).
    values: dict[str, dict[str, float | None]] = {}
    for bid in index.barrio_ids:
        pop = population.get(bid)
        if not pop:
            continue
        years = by_year.get(bid, {})
        values[bid] = {p: round(years.get(p, 0) / pop * 1000.0, 1) for p in periods}

    return Metric(
        id="airbnb_activity",
        label="Actividad Airbnb (reseñas/año por 1000 hab.)",
        unit="por 1000 hab./año",
        kind="sequential",
        theme="tourism",
        source=SOURCE_REVIEWS,
        geo_grain="barrio",
        time_grain="year",
        periods=periods,
        values=values,
    )


def build_series(ctx: BuildContext) -> list[Series]:
    index = ctx.barrio_index
    if not isinstance(index, BarrioIndex):
        return []
    reviews_path = ctx.raw_dir / REVIEWS_GZ
    listings_path = ctx.raw_dir / LISTINGS_GZ
    if not reviews_path.exists() or not listings_path.exists():
        return []

    city_listings = set(_listing_barrio(ctx, index))  # ids inside any barrio
    acc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    with _open_gz(reviews_path) as fh:
        for row in csv.DictReader(fh):
            if row.get("listing_id") not in city_listings:
                continue
            date = row.get("date") or ""
            parts = date.split("-")
            if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
                continue
            year, month = parts[0], str(int(parts[1]))  # strip leading zero
            acc[year][month] += 1

    years = sorted(acc)
    values: dict[str, dict[str, float | None]] = {
        year: {m: float(acc[year][m]) for m in sorted(acc[year], key=int)}
        for year in years
    }

    return [
        Series(
            id="airbnb_reviews",
            label="Reseñas Airbnb / mes (proxy de presencia turística)",
            unit="reseñas",
            theme="tourism",
            source=SOURCE_REVIEWS,
            kind="month-year",
            years=years,
            values=values,
        )
    ]
