"""Disposable income per barrio, and the gender income gap.

Source: Donostia Open Data ``eustat_renta`` → ``eustatrentabarrio.csv``. One row
per (year, barrio) with disposable income per capita columns: ``RentaPer_Total``
plus ``RentaPer_Hombres`` / ``RentaPer_Mujeres`` (by gender). We emit:

* ``income_total`` — disposable income per capita (€), per barrio per year.
* ``income_gender_gap`` — ``(male − female) / male × 100`` (%), the share by
  which men's per-capita income exceeds women's (the brief's gender-gap proxy).

Annual series 2016–2023, joined to the geometry by ``CodBarrio``.
"""

from __future__ import annotations

import csv
from collections import defaultdict

from ..model import BuildContext, Metric

CSV_NAME = "renta_barrio.csv"
SOURCE = "Donostia Open Data — renta disponible por barrio (Eustat)"


def _to_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build(ctx: BuildContext) -> list[Metric]:
    income: dict[str, dict[str, float | None]] = defaultdict(dict)
    gap: dict[str, dict[str, float | None]] = defaultdict(dict)
    years: set[str] = set()

    with (ctx.raw_dir / CSV_NAME).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            barrio_id = ctx.code_to_id.get(row["CodBarrio"].strip())
            if not barrio_id:
                continue
            year = row["Anyo"].strip()
            total = _to_int(row["RentaPer_Total"])
            if total is None:
                continue
            years.add(year)
            income[barrio_id][year] = float(total)

            male = _to_int(row.get("RentaPer_Hombres", ""))
            female = _to_int(row.get("RentaPer_Mujeres", ""))
            if male and female is not None:
                gap[barrio_id][year] = round((male - female) / male * 100.0, 2)

    periods = sorted(years)
    return [
        Metric(
            id="income_total",
            label="Renta disponibile pro capite",
            unit="€",
            kind="sequential",
            theme="economy",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="year",
            periods=periods,
            values=dict(income),
        ),
        Metric(
            id="income_gender_gap",
            label="Divario di reddito di genere",
            unit="%",
            kind="sequential",
            theme="economy",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="year",
            periods=periods,
            values=dict(gap),
        ),
    ]
