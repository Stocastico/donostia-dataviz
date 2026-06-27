"""Education level per barrio — share with university studies.

Source: Donostia Open Data ``demografia-nivelestudios`` →
``demografianivelestudiosbarrio.csv``. One row per (year, barrio, study level)
where ``Ehuneko_Totala`` is that level's share of the barrio population as a
proportion (0–1). We pick the ``UNIVERSITARIOS`` level and emit it as a
percentage. Annual series 2000–2025, joined by ``AuzoKodea``.
"""

from __future__ import annotations

import csv

from ..model import BuildContext, Metric

CSV_NAME = "estudios_barrio.csv"
UNIVERSITY_LEVEL = "UNIVERSITARIOS"
SOURCE = "Donostia Open Data — nivel de estudios por barrio"


def build(ctx: BuildContext) -> list[Metric]:
    values: dict[str, dict[str, float | None]] = {}
    years: set[str] = set()

    with (ctx.raw_dir / CSV_NAME).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["Ikasketak_es"].strip().upper() != UNIVERSITY_LEVEL:
                continue
            barrio_id = ctx.code_to_id.get(row["AuzoKodea"].strip())
            if not barrio_id:
                continue
            try:
                pct = float(row["Ehuneko_Totala"]) * 100.0
            except (TypeError, ValueError):
                continue
            year = row["Urtea"].strip()
            years.add(year)
            values.setdefault(barrio_id, {})[year] = round(pct, 2)

    return [
        Metric(
            id="pct_university",
            label="Popolazione con studi universitari",
            unit="%",
            kind="sequential",
            theme="education",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="year",
            periods=sorted(years),
            values=values,
        )
    ]
