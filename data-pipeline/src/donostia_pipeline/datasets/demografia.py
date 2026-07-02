"""Demographics by barrio — population and share of foreign residents.

Source: Donostia Open Data ``demografia-origen`` →
``demografianacionalidadbarrio.csv``. One row per (year, barrio, nationality,
gender split) with columns ``Urtea`` (year), ``AuzoKodea`` (barrio code),
``Auzoa`` (barrio name), ``Jatorria`` (nationality/origin), ``PertsonenKop``
(total persons). We aggregate per barrio per year into total population and the
percentage of residents whose origin is not Spain. Annual series 2000–2025 —
this is the metric that exercises the time slider.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from ..model import BuildContext, Metric

CSV_NAME = "demo_barrio.csv"
SPAIN = "ESPAÑA"
SOURCE = "Donostia Open Data — demografía por nacionalidad y barrio"


def population_latest_by_barrio(raw_dir: Path, code_to_id: dict[str, str]) -> dict[str, int]:
    """Total population per barrio for the latest year in the demographics file.

    Shared by metrics that normalize counts per capita (VUT density, GIS service
    rates). Sums ``PertsonenKop`` across nationalities for the most recent year.
    """
    rows: list[tuple[str, str, int]] = []  # (year, barrio_id, people)
    with (raw_dir / CSV_NAME).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            barrio_id = code_to_id.get(row["AuzoKodea"].strip())
            if not barrio_id:
                continue
            try:
                people = int(row["PertsonenKop"])
            except (TypeError, ValueError):
                continue
            rows.append((row["Urtea"].strip(), barrio_id, people))
    if not rows:
        return {}
    latest = max(year for year, _, _ in rows)
    population: dict[str, int] = defaultdict(int)
    for year, barrio_id, people in rows:
        if year == latest:
            population[barrio_id] += people
    return dict(population)


def build(ctx: BuildContext) -> list[Metric]:
    # (barrio_id, year) -> [total, foreign]
    total: dict[tuple[str, str], int] = defaultdict(int)
    foreign: dict[tuple[str, str], int] = defaultdict(int)
    years: set[str] = set()

    with (ctx.raw_dir / CSV_NAME).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            code = row["AuzoKodea"].strip()
            barrio_id = ctx.code_to_id.get(code)
            if not barrio_id:
                # Blank code = "Ezezaguna" (unassigned) → skip.
                continue
            year = row["Urtea"].strip()
            try:
                people = int(row["PertsonenKop"])
            except (TypeError, ValueError):
                continue
            years.add(year)
            total[(barrio_id, year)] += people
            if row["Jatorria"].strip().upper() != SPAIN:
                foreign[(barrio_id, year)] += people

    periods = sorted(years)

    pop_values: dict[str, dict[str, float | None]] = defaultdict(dict)
    pct_values: dict[str, dict[str, float | None]] = defaultdict(dict)
    for (barrio_id, year), pop in total.items():
        pop_values[barrio_id][year] = float(pop)
        share = (foreign[(barrio_id, year)] / pop * 100.0) if pop else None
        pct_values[barrio_id][year] = round(share, 2) if share is not None else None

    population = Metric(
        id="population",
        label="Popolazione residente",
        unit="abitanti",
        kind="sequential",
        theme="demography",
        source=SOURCE,
        geo_grain="barrio",
        time_grain="year",
        periods=periods,
        values=dict(pop_values),
    )
    pct_foreign = Metric(
        id="pct_foreign",
        label="Popolazione straniera",
        unit="%",
        kind="sequential",
        theme="demography",
        source=SOURCE,
        geo_grain="barrio",
        time_grain="year",
        periods=periods,
        values=dict(pct_values),
    )
    return [population, pct_foreign]
