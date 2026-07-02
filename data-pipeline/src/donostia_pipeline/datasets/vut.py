"""Viviendas de Uso Turístico (VUT/HUT) — touristic-housing census.

Source: Donostia Open Data ``censo-viviendas-turisticas`` — a *current snapshot*
(no time dimension), one row per authorized unit with columns
``Auzoa`` (barrio), ``helbidea`` (address), ``Mota`` (VUT/HUT), ``plazak``
(licensed beds). We aggregate per barrio into two snapshot metrics: number of
units and total licensed beds. (Per-capita density is a derived metric added
once demographics population is available.)
"""

from __future__ import annotations

import csv

from ..config import canonical_barrio_id
from ..model import BuildContext, Metric

CSV_NAME = "vtur_censo.csv"
# Single snapshot period — the census has no historical series.
PERIOD = "actual"
SOURCE = "Donostia Open Data — censo viviendas turísticas (snapshot)"


def build(ctx: BuildContext) -> list[Metric]:
    units: dict[str, int] = {}
    plazas: dict[str, int] = {}

    with (ctx.raw_dir / CSV_NAME).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            barrio_id = canonical_barrio_id(row["Auzoa"])
            if barrio_id not in ctx.barrio_ids:
                # "Ezezaguna" (unknown) and any unmatched bucket are dropped.
                continue
            units[barrio_id] = units.get(barrio_id, 0) + 1
            try:
                beds = int(row["plazak"])
            except (TypeError, ValueError):
                beds = 0
            plazas[barrio_id] = plazas.get(barrio_id, 0) + beds

    count_metric = Metric(
        id="vut_count",
        label="Viviendas turísticas (VUT/HUT)",
        unit="unità",
        kind="sequential",
        theme="tourism",
        source=SOURCE,
        geo_grain="barrio",
        time_grain="snapshot",
        periods=[PERIOD],
        values={bid: {PERIOD: float(n)} for bid, n in units.items()},
    )
    plazas_metric = Metric(
        id="vut_plazas",
        label="Posti letto turistici (plazas VUT/HUT)",
        unit="posti letto",
        kind="sequential",
        theme="tourism",
        source=SOURCE,
        geo_grain="barrio",
        time_grain="snapshot",
        periods=[PERIOD],
        values={bid: {PERIOD: float(n)} for bid, n in plazas.items()},
    )
    return [count_metric, plazas_metric]
