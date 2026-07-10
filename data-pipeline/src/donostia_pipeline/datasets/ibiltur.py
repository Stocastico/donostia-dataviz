"""IBILTUR Ocio — curated annual leisure-tourism indicators (REC-10).

There is no structured open dataset at Donostia grain: Basquetour (the Basque
tourism agency) publishes one destination-level PDF "ficha" per edition of its
IBILTUR survey. This reads a **hand-curated, source-cited** CSV
(``ibiltur_donostia.csv``), same approach as ``mice.py``.

Only **IBILTUR Ocio** (overnight leisure tourists) is covered here — the
excursionist and MICE-business segments the brief also asks about have no
Donostia-specific published figure yet (only Euskadi-wide ones), so they are
not represented rather than guessed.

Caveat that keeps this to a single 2023 point for now: Basquetour's editions
aren't all annual/comparable — e.g. the 2022 destination PDF is "IBILTUR
Verano" (summer-only), not "Ocio" (full year), so mixing it with 2023 would
manufacture a misleading trend. Extend by adding rows once another *Ocio*
(full-year) edition for Donostia is published.
"""

from __future__ import annotations

import csv

from .. import config
from ..model import Indicator

CURATED_FILE = "ibiltur_donostia.csv"

# id -> (label, unit, theme).
META: dict[str, tuple[str, str, str]] = {
    "ibiltur_ocio_spend_per_person": (
        "Gasto turístico de ocio por persona (IBILTUR Ocio)", "€", "tourism"),
    "ibiltur_ocio_spend_per_person_day": (
        "Gasto turístico de ocio por persona y día (IBILTUR Ocio)", "€/día", "tourism"),
    "ibiltur_ocio_economic_impact": (
        "Impacto económico del turismo de ocio (IBILTUR Ocio)", "M€", "tourism"),
}
SOURCE = "Basquetour — IBILTUR Ocio, ficha de destino Donostia/San Sebastián (ver columna source)"


def indicators_from_rows(rows) -> list[Indicator]:
    """Group curated rows into Indicator objects (pure; unit-tested)."""
    indicators: dict[str, Indicator] = {}
    for row in rows:
        ind_id = row["indicator_id"].strip()
        meta = META.get(ind_id)
        if not meta:
            continue  # unknown id → skip rather than guess
        label, unit, theme = meta
        ind = indicators.get(ind_id)
        if ind is None:
            ind = Indicator(id=ind_id, label=label, unit=unit, theme=theme, source=SOURCE)
            indicators[ind_id] = ind
        try:
            value = float(row["value"])
        except (TypeError, ValueError):
            continue
        ind.values[row["year"].strip()] = {"value": value, "source": row["source"].strip()}
    return list(indicators.values())


def build_indicators() -> list[Indicator]:
    path = config.CURATED_DIR / CURATED_FILE
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return indicators_from_rows(list(csv.DictReader(fh)))
