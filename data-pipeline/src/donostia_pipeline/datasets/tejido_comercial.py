"""Commercial fabric: retail vs. hospitality establishment share (REC-7).

There is no open dataset of commercial licenses by category and barrio (the
brief's original ask), so this uses a **city-grain proxy**: Eustat's business
directory (CDIRAE), table ``PX_200163_cdirae_est04b`` — establishment counts
by municipio and full CNAE-2009 activity code — filtered server-side to
Donostia (municipio ``20069``), all codes, all years (see
``build.ensure_eustat_comercio``).

Two CNAE-2009 divisions are summed client-side (the source has no
section/division-level rows, only ~630 individual 4-digit activities):

* **47xx** — "Comercio al por menor" (retail trade): resident-facing shops.
* **55xx/56xx** — accommodation + food and beverage service (hospitality):
  the closest available proxy for tourist-facing establishments.

This is a **proxy for a compositional shift**, not a causal claim: rising
hospitality / falling retail share is consistent with (but doesn't prove)
"sustitución residente→turista" — other explanations (e.g. e-commerce
eroding retail generally) aren't ruled out. Eustat's ``"-"`` marker means
zero (not missing/confidential) in this table, unlike ``":"``.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from ..model import Indicator

RAW_FILE = "eustat_comercio_donostia.json"
SOURCE = (
    "Eustat — Directorio de Actividades Económicas (CDIRAE), establecimientos "
    "por municipio y CNAE-2009 (tabla PX_200163_cdirae_est04b), Donostia-San Sebastián"
)

_TOTAL_CODE = "0"
_RETAIL_PREFIX = "47"
_HOSPITALITY_PREFIXES = ("55", "56")

# key = [municipio, CNAE-2009, periodo]
_CNAE_IDX = 1
_PERIOD_IDX = 2


def establishments_from_pxweb(payload: dict) -> list[Indicator]:
    """Pure transform: a PxWeb query response -> 3 Indicators (unit-tested)."""
    by_period: dict[str, dict[str, float]] = defaultdict(
        lambda: {"total": None, "retail": 0.0, "hospitality": 0.0}
    )
    for row in payload.get("data", []):
        key = row["key"]
        cnae = key[_CNAE_IDX]
        try:
            value = float(row["values"][0])
        except (TypeError, ValueError):
            continue  # "-" (zero) or ":" (confidential) — either way, add nothing
        bucket = by_period[key[_PERIOD_IDX]]
        if cnae == _TOTAL_CODE:
            bucket["total"] = value
        elif cnae.startswith(_RETAIL_PREFIX):
            bucket["retail"] += value
        elif cnae.startswith(_HOSPITALITY_PREFIXES):
            bucket["hospitality"] += value

    total_ind = Indicator(id="total_establishments", label="Esercizi totali (Donostia)",
                           unit="locali", theme="economy", source=SOURCE)
    retail_ind = Indicator(id="retail_establishments_share",
                            label="Quota commercio al dettaglio (% esercizi)",
                            unit="%", theme="economy", source=SOURCE)
    hospitality_ind = Indicator(id="hospitality_establishments_share",
                                 label="Quota alloggio/ristorazione (% esercizi)",
                                 unit="%", theme="economy", source=SOURCE)

    for period, counts in by_period.items():
        total = counts["total"]
        if not total:
            continue
        total_ind.values[period] = {"value": total, "source": SOURCE}
        retail_ind.values[period] = {
            "value": round(counts["retail"] / total * 100, 2), "source": SOURCE,
        }
        hospitality_ind.values[period] = {
            "value": round(counts["hospitality"] / total * 100, 2), "source": SOURCE,
        }
    return [total_ind, retail_ind, hospitality_ind]


def build_indicators(raw_dir: Path) -> list[Indicator]:
    path = raw_dir / RAW_FILE
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return establishments_from_pxweb(payload)
