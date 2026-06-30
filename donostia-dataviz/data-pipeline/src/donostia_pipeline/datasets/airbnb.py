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
SNAPSHOT = "2025-09"  # Inside Airbnb Euskadi snapshot 2025-09-29
SOURCE = (
    "Inside Airbnb — Euskadi (snapshot 2025-09-29); join spaziale punto→barrio"
)
SOURCE_REVIEWS = (
    "Inside Airbnb — recensioni per mese (proxy di presenza turistica, "
    "«modello San Francisco»: una recensione ≈ un soggiorno recensito); snapshot 2025-09-29"
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

    counts: dict[str, int] = defaultdict(int)
    for barrio_id in _listing_barrio(ctx, index).values():
        counts[barrio_id] += 1
    # Every barrio present (0 if no listing), then normalized per capita.
    full = {bid: counts.get(bid, 0) for bid in index.barrio_ids}
    rates = rate_per_1000(full, ctx.population_latest or {})

    return [
        Metric(
            id="airbnb_density",
            label="Densità Airbnb (annunci per 1000 ab.)",
            unit="per 1000 ab.",
            kind="sequential",
            theme="tourism",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[SNAPSHOT],
            values={bid: {SNAPSHOT: rate} for bid, rate in rates.items()},
        )
    ]


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
            label="Recensioni Airbnb / mese (proxy di presenza turistica)",
            unit="recensioni",
            theme="tourism",
            source=SOURCE_REVIEWS,
            kind="month-year",
            years=years,
            values=values,
        )
    ]
