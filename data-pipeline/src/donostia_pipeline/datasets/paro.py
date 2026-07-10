"""Unemployment rate — annual city indicator (REC-5).

Source: Eustat PxWeb table ``PX_050403_cpra_tab19`` ("Tasas de actividad,
ocupación y paro... por capitales, sexo y trimestre"), filtered server-side
to capital Donostia/San Sebastián (``30``), tasa "Tasa de paro" (``30``) and
trimestre "Promedio anual" (``10``) — see ``build.ensure_eustat_paro`` for
the fetch.

Only city (capital) granularity — **no per-barrio figure exists** for this
dataset (REC-5's caveat in BACKLOG.md); the "ventana barrio 2016-19" the
archived plan flagged as unverified was not found in Eustat's PxWeb bank.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..model import Indicator

RAW_FILE = "eustat_paro_donostia.json"
SOURCE = (
    "Eustat — Tasas de actividad, ocupación y paro por capitales, sexo y "
    "trimestre (tabla PX_050403_cpra_tab19), Donostia-San Sebastián, promedio anual"
)

# key = [tasa (%), capital, sexo, trimestre, periodo]
_SEXO_IDX = 2
_PERIOD_IDX = 4
_SEXO_CODES = {"10": "unemployment_rate", "20": "unemployment_rate_men", "30": "unemployment_rate_women"}
_LABELS = {
    "unemployment_rate": "Tasa de paro (Donostia)",
    "unemployment_rate_men": "Tasa de paro — hombres",
    "unemployment_rate_women": "Tasa de paro — mujeres",
}


def unemployment_rate_from_pxweb(payload: dict) -> list[Indicator]:
    """Pure transform: a PxWeb query response -> one Indicator per sex (unit-tested)."""
    indicators = {
        ind_id: Indicator(id=ind_id, label=label, unit="%", theme="economy", source=SOURCE)
        for ind_id, label in _LABELS.items()
    }
    for row in payload.get("data", []):
        key = row["key"]
        ind_id = _SEXO_CODES.get(key[_SEXO_IDX])
        if ind_id is None:
            continue
        try:
            value = float(row["values"][0])
        except (TypeError, ValueError):
            continue  # PxWeb's ":" (confidential/not-yet-available) or other marker
        indicators[ind_id].values[key[_PERIOD_IDX]] = {"value": value, "source": SOURCE}
    return list(indicators.values())


def build_indicators(raw_dir: Path) -> list[Indicator]:
    path = raw_dir / RAW_FILE
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return unemployment_rate_from_pxweb(payload)
