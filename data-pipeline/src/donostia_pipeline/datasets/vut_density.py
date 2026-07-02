"""Derived metric: touristic-housing density per 1000 inhabitants.

Combines two raw sources already used elsewhere:
* the VUT census (``vtur_censo.csv``) — units per barrio (by name), and
* demographics (``demo_barrio.csv``) — population per barrio (by code), of which
  we take the latest available year.

density(barrio) = VUT units / population(latest year) * 1000

This is the brief's "tasso di touristificazione" proxy expressed per capita. A
single snapshot period, since the VUT census has no time dimension. Populated
barrios with no VUT are 0; barrios with no/zero population are left null.
"""

from __future__ import annotations

import csv
from collections import defaultdict

from ..config import canonical_barrio_id
from ..model import BuildContext, Metric
from . import demografia

VUT_CSV = "vtur_censo.csv"
PERIOD = "actual"
SOURCE = "Derivata — censo VUT / popolazione (Donostia Open Data)"


def _vut_units_by_barrio(ctx: BuildContext) -> dict[str, int]:
    units: dict[str, int] = defaultdict(int)
    with (ctx.raw_dir / VUT_CSV).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            barrio_id = canonical_barrio_id(row["Auzoa"])
            if barrio_id in ctx.barrio_ids:
                units[barrio_id] += 1
    return units


def build(ctx: BuildContext) -> list[Metric]:
    units = _vut_units_by_barrio(ctx)
    population = demografia.population_latest_by_barrio(ctx.raw_dir, ctx.code_to_id)

    values: dict[str, dict[str, float | None]] = {}
    for barrio_id, pop in population.items():
        density = round(units.get(barrio_id, 0) / pop * 1000.0, 2) if pop else None
        values[barrio_id] = {PERIOD: density}

    return [
        Metric(
            id="vut_density",
            label="Densità VUT (per 1000 abitanti)",
            unit="per 1000 ab.",
            kind="sequential",
            theme="tourism",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[PERIOD],
            values=values,
        )
    ]
