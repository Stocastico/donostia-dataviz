"""Age structure by barrio — ageing index and young-adult share (REC-1).

Source: Donostia Open Data ``demografia-piramideedad`` →
``demografiapiramideedadbarrio.csv``. One row per (year, barrio, 5-year age
band, gender split) with ``Urtea`` (year), ``AuzoKodea`` (barrio code),
``Auzoa`` (name), ``AdinTartea`` (age band, e.g. ``"00 - 04"`` … ``"95 - >="``)
and ``PertsonenKop`` (total persons). Same ``AuzoKodea`` join as
``demografia.py`` — no spatial join needed.

Two derived metrics (annual series 2000–2025), answering "who lives in
Donostia" (`GAP-ANALYSIS.md` output #3):

* ``ageing_index`` — population ≥65 ÷ population <15 × 100 (índice de
  envejecimiento). 100 means as many elders as children; higher = older barrio.
* ``pct_youth_adults`` — share aged 25–39, the family-forming / working cohort
  whose presence (or absence) signals residential renewal vs. ageing.

Caveat (documented, not hidden): bands are 5-year, so "25–39" is exactly the
25-29/30-34/35-39 bands; we do not interpolate a median age from banded data.
"""

from __future__ import annotations

import csv
from collections import defaultdict

from ..model import BuildContext, Metric

CSV_NAME = "edad_barrio.csv"
SOURCE = "Donostia Open Data — población por edad y género por barrio (Padrón)"

# Young-adult cohort: bands whose lower bound is 25, 30 or 35 (ages 25–39).
YOUTH_ADULT_LOW = {25, 30, 35}


def _band_low(band: str) -> int | None:
    """Lower bound of an age band like ``"00 - 04"`` or ``"95 - >="``."""
    try:
        return int(band.split("-")[0].strip())
    except (ValueError, IndexError):
        return None


def build(ctx: BuildContext) -> list[Metric]:
    # (barrio_id, year) -> counts
    under15: dict[tuple[str, str], int] = defaultdict(int)
    over64: dict[tuple[str, str], int] = defaultdict(int)
    youth_adults: dict[tuple[str, str], int] = defaultdict(int)
    total: dict[tuple[str, str], int] = defaultdict(int)
    years: set[str] = set()

    with (ctx.raw_dir / CSV_NAME).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            barrio_id = ctx.code_to_id.get(row["AuzoKodea"].strip())
            if not barrio_id:
                # Blank code = "Ezezaguna" (unassigned) → skip.
                continue
            low = _band_low(row["AdinTartea"].strip())
            if low is None:
                continue
            try:
                people = int(row["PertsonenKop"])
            except (TypeError, ValueError):
                continue
            year = row["Urtea"].strip()
            years.add(year)
            key = (barrio_id, year)
            total[key] += people
            if low < 15:
                under15[key] += people
            elif low >= 65:
                over64[key] += people
            if low in YOUTH_ADULT_LOW:
                youth_adults[key] += people

    periods = sorted(years)
    ageing: dict[str, dict[str, float | None]] = defaultdict(dict)
    youth: dict[str, dict[str, float | None]] = defaultdict(dict)
    for key, tot in total.items():
        barrio_id, year = key
        kids = under15[key]
        ageing[barrio_id][year] = round(over64[key] / kids * 100.0, 1) if kids else None
        youth[barrio_id][year] = round(youth_adults[key] / tot * 100.0, 2) if tot else None

    ageing_index = Metric(
        id="ageing_index",
        label="Indice di vecchiaia (≥65 / <15)",
        unit="",
        kind="sequential",
        theme="demography",
        source=SOURCE,
        geo_grain="barrio",
        time_grain="year",
        periods=periods,
        values=dict(ageing),
    )
    pct_youth_adults = Metric(
        id="pct_youth_adults",
        label="Popolazione 25–39 anni",
        unit="%",
        kind="sequential",
        theme="demography",
        source=SOURCE,
        geo_grain="barrio",
        time_grain="year",
        periods=periods,
        values=dict(youth),
    )
    return [ageing_index, pct_youth_adults]
