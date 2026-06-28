"""MICE (congresses & meetings) — curated annual indicators.

There is no structured open dataset for Donostia's MICE figures: they live in
annual PDF memorias, press releases and ICCA reports. So this dataset reads a
**hand-curated, source-cited** CSV (``curated/mice_donostia.csv``) rather than
fetching anything. Each row is one (indicator, year) observation with its own
citation; extending the series = adding rows.

Indicators:
* ``mice_icca_congresses`` — international association congresses counted by ICCA
  (strict criteria), the comparable world-ranking metric.
* ``mice_events_total`` — total professional events (Convention Bureau).
* ``mice_attendees`` — total attendees (Convention Bureau).
"""

from __future__ import annotations

import csv

from .. import config
from ..model import Indicator

CURATED_FILE = "mice_donostia.csv"

# id -> (label, unit, theme). Defines which indicator ids are recognised.
META: dict[str, tuple[str, str, str]] = {
    "mice_icca_congresses": ("Congressi internazionali (ICCA)", "congressi", "tourism"),
    "mice_events_total": ("Eventi professionali (totale)", "eventi", "tourism"),
    "mice_attendees": ("Partecipanti a congressi", "persone", "tourism"),
}
SOURCE = "Curato da memorias DSS Turismoa, Convention Bureau e ICCA (vedi colonna source)"


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
    with path.open(encoding="utf-8", newline="") as fh:
        return indicators_from_rows(list(csv.DictReader(fh)))
