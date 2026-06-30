"""Municipal fiscality — annual city indicators (REC-3).

Sources: Donostia Open Data ``impuestos_tipo`` → ``pfi_impuestos_tipo_ciudad_ckan.csv``
and ``tasas_tipo`` → ``pfi_tasas_tipo_ciudad_ckan.csv``. Each row is an amount
``Kopurua`` (€) for a year ``Urtea`` and a tax/fee type. We sum to the yearly
city total and report it in **millions of euros**, as two line indicators
rendered by the generic ``IndicatorsSection``.

Caveat (documented, not hidden): these are amounts **emitted/billed**
(*igorritako*), not necessarily collected, and are nominal € (not inflation- or
population-adjusted) — read as a coarse municipal-finance trend, city context.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from ..model import Indicator

IMPUESTOS_CSV = "impuestos_ciudad.csv"
TASAS_CSV = "tasas_ciudad.csv"
IMP_SOURCE = "Donostia Open Data — impuestos emitidos (ciudad, importe nominal)"
TASAS_SOURCE = "Donostia Open Data — tasas emitidas (ciudad, importe nominal)"


def _yearly_total_millions(rows, source: str) -> dict[str, dict]:
    """Pure transform: rows with ``Urtea``/``Kopurua`` → {year: {value M€, source}}."""
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        try:
            amount = float(row["Kopurua"])  # parse before touching totals
            year = row["Urtea"].strip()
        except (TypeError, ValueError, KeyError):
            continue
        totals[year] += amount
    return {
        year: {"value": round(total / 1e6, 1), "source": source}
        for year, total in sorted(totals.items())
    }


def _read(raw_dir: Path, name: str):
    with (raw_dir / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def build_indicators(raw_dir: Path) -> list[Indicator]:
    out: list[Indicator] = []
    imp = raw_dir / IMPUESTOS_CSV
    if imp.exists():
        out.append(Indicator(
            id="tax_revenue",
            label="Imposte comunali emesse (M€)",
            unit="M€",
            theme="economy",
            source=IMP_SOURCE,
            values=_yearly_total_millions(_read(raw_dir, IMPUESTOS_CSV), IMP_SOURCE),
        ))
    tasas = raw_dir / TASAS_CSV
    if tasas.exists():
        out.append(Indicator(
            id="fee_revenue",
            label="Tasse comunali emesse (M€)",
            unit="M€",
            theme="economy",
            source=TASAS_SOURCE,
            values=_yearly_total_millions(_read(raw_dir, TASAS_CSV), TASAS_SOURCE),
        ))
    return out
