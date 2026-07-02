"""Recycling rate — annual city indicator from the waste-collection dataset.

Source: Donostia Open Data ``residuos`` → ``datos-residuos.csv`` (annual,
city-level). Rows are kg by ``Año`` × ``Tipo de recogida`` × classification ×
``Ambito``. The recycling rate is the share of urban waste collected separately:

    recycling_rate(%) = (Recogida selectiva + Autocompostaje) / total × 100

over the URBANO ambit (industrial waste excluded). Annual 2010–2024 — a
sustainability trend (≈29 % in 2010 → ≈41 % in 2023).
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from ..model import Indicator

CSV_NAME = "residuos.csv"
RECYCLED_TYPES = {"Recogida selectiva", "Autocompostaje"}
REST_TYPE = "Rechazo"
SOURCE = "Donostia Open Data — recogida de residuos (ámbito urbano)"


def recycling_rate_from_rows(rows) -> list[Indicator]:
    """Pure transform: kg rows → a recycling-rate Indicator (unit-tested)."""
    recycled: dict[str, int] = defaultdict(int)
    rest: dict[str, int] = defaultdict(int)
    for row in rows:
        if row.get("Ambito") == "INDUSTRIAL":  # urban (+ blank) only
            continue
        try:
            kg = int(row["Total (kg)"])
        except (TypeError, ValueError):
            continue
        tipo = row["Tipo de recogida"]
        year = row["Año"].strip()
        if tipo in RECYCLED_TYPES:
            recycled[year] += kg
        elif tipo == REST_TYPE:
            rest[year] += kg

    values = {}
    for year in sorted(set(recycled) | set(rest)):
        total = recycled[year] + rest[year]
        # Require both fractions present: a year with no Rechazo is incomplete
        # (would be a bogus 100 %), so skip it.
        if total > 0 and rest[year] > 0:
            values[year] = {
                "value": round(recycled[year] / total * 100, 2),
                "source": SOURCE,
            }

    return [
        Indicator(
            id="recycling_rate",
            label="Tasso di raccolta differenziata",
            unit="%",
            theme="environment",
            source=SOURCE,
            values=values,
        )
    ]


def build_indicators(raw_dir: Path) -> list[Indicator]:
    with (raw_dir / CSV_NAME).open(encoding="utf-8-sig", newline="") as fh:
        return recycling_rate_from_rows(list(csv.DictReader(fh, delimiter=";")))
