"""Protected-housing (Etxebide) footprint per barrio (REC-15).

Source: Open Data Euskadi — *Promociones de Etxebide para compra y alquiler de
vivienda protegida* (one row per promotion, whole Basque Country). Each row
carries UTM (EPSG:25830) coordinates and the number of dwellings, so promotions
are assigned to a barrio by point-in-polygon (``ctx.barrio_index``) and the
dwellings summed, then normalized per 1000 inhabitants — never a raw count.

This answers the "tensión residencial" gap the project's spine had: MET-1 maps
where renting is hardest; this maps where the public/protected stock actually
landed. A barrio heavy on pressure and light on protected housing is the story.

⚠️ Caveats (documented as MET-4 assumptions in ``provenance.py``):
  * **Etxebide-managed promotions only** (VISESA / Alokabide / Gobierno Vasco),
    not the municipal patronato nor every VPO ever built → a *floor* of the
    protected footprint, a proxy for public-housing supply, not a census.
  * **Cumulative snapshot**, not a time series (mostly "Terminada" + a few "En
    Curso"); ``period = "actual"``.
  * The published CSV has a **shifted header**: the dwelling count sits in the
    column labelled ``Tipologia`` (``NumViviendas`` is empty in every row);
    ``Reg Acceso`` holds the tenure. Parsed by that reality, not the labels.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ..gis_io import reproject_point
from ..model import BuildContext, Metric
from ..spatial import BarrioIndex, rate_per_1000

CSV_NAME = "promociones_etxebide.csv"
PERIOD = "actual"
SOURCE = "Open Data Euskadi — Promociones de Etxebide (join spaziale punto→barrio)"

# Header labels are unreliable (see module docstring): read by position.
_COL_DWELLINGS = 8  # labelled "Tipologia", actually the dwelling count
_COL_UTMX = 10
_COL_UTMY = 11


@dataclass(frozen=True)
class Promo:
    utmx: float
    utmy: float
    dwellings: int


def _num(s: str) -> float:
    return float(s.strip().replace(",", "."))


def parse_rows(csv_path: Path) -> list[Promo]:
    """Read the Etxebide promotions CSV (``;`` sep, latin-1) → list of Promo.

    Rows without a usable dwelling count or coordinates are skipped; no
    municipality filter (the barrio geometry drops anything outside the city).
    """
    out: list[Promo] = []
    with csv_path.open(encoding="latin-1", newline="") as fh:
        reader = csv.reader(fh, delimiter=";")
        next(reader, None)  # header
        for row in reader:
            if len(row) <= _COL_UTMY:
                continue
            try:
                dwellings = int(row[_COL_DWELLINGS].strip())
                utmx = _num(row[_COL_UTMX])
                utmy = _num(row[_COL_UTMY])
            except (ValueError, IndexError):
                continue
            out.append(Promo(utmx=utmx, utmy=utmy, dwellings=dwellings))
    return out


def aggregate(
    index: BarrioIndex, located: Iterable[tuple[float, float, int]]
) -> dict[str, int]:
    """Sum dwelling weights per barrio for ``(lon, lat, dwellings)`` points.

    Every barrio is present (0 if none); points outside the city are dropped.
    """
    totals = {bid: 0 for bid in index.barrio_ids}
    for lon, lat, dwellings in located:
        bid = index.assign_point(lon, lat)
        if bid is not None:
            totals[bid] += dwellings
    return totals


def build(ctx: BuildContext) -> list[Metric]:
    index = ctx.barrio_index
    if not isinstance(index, BarrioIndex):
        return []

    rows = parse_rows(ctx.raw_dir / CSV_NAME)
    located = ((*reproject_point(r.utmx, r.utmy), r.dwellings) for r in rows)
    totals = aggregate(index, located)
    rates = rate_per_1000(totals, ctx.population_latest or {})

    return [
        Metric(
            id="vpo_dwellings_per_1000",
            label="Viviendas protegidas Etxebide (por 1000 hab.)",
            unit="por 1000 hab.",
            kind="sequential",
            theme="housing",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[PERIOD],
            values={bid: {PERIOD: rate} for bid, rate in rates.items()},
        )
    ]
