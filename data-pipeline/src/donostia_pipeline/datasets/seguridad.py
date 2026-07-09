"""Security: perceived (in)security and real crime — city indicators (HU-1).

Two curated, source-cited inputs in ``datos/input/`` (like MICE): they answer
the user's HU-1 ("perceived security has fallen a lot — but that isn't true").

* **Perception** — ``percepcion_seguridad_eustat.csv`` (Eustat ECV, families by
  perceived security grade and zone, 1989–2024). We emit the **share of
  families reporting any security problem** = (Total − "Ningún problema") /
  Total × 100, for the Donostia zone and for the C.A. de Euskadi:
  ``perception_insecurity_donostia`` / ``perception_insecurity_euskadi``.

* **Crime** — ``criminalidad_donostia.csv`` (partial press/official series):
  ``crime_rate_1000`` (rate per 1,000) and ``crime_infractions`` (known
  penal infractions). Partial by design — the full official annual series
  (Portal Estadístico de Criminalidad) is a declared gap (see FUENTES.md).

All city-grain, theme ``security``. Pure transforms are unit-tested.
"""

from __future__ import annotations

import csv
from collections import defaultdict

from .. import config
from ..model import Indicator

PERCEPTION_FILE = "percepcion_seguridad_eustat.csv"
CRIME_FILE = "criminalidad_donostia.csv"

PERCEPTION_SOURCE = (
    "Eustat — Encuesta de Condiciones de Vida, familias por grado de seguridad "
    "ciudadana y zona (tabla PX_010901_cecv_ma04_3); % con algún problema"
)
_ZONA_INDICATOR = {
    "70": ("perception_insecurity_donostia",
           "Famiglie con problemi di sicurezza — Donostia (%)"),
    "00": ("perception_insecurity_euskadi",
           "Famiglie con problemi di sicurezza — Euskadi (%)"),
}

# Crime indicator_id → (label, unit). Level series only (rates/counts); the
# year-on-year % row is skipped (not a level).
_CRIME_META = {
    "tasa_criminalidad_1000": ("crime_rate_1000",
                               "Tasso di criminalità (per 1000 ab.)", "per 1000 ab."),
    "infracciones_penales": ("crime_infractions",
                             "Infrazioni penali conosciute (Donostia)", "infrazioni"),
}


def perception_indicators_from_rows(rows) -> list[Indicator]:
    """Curated perception rows → one insecurity-share Indicator per zone."""
    # totals[zona][year][grado] = familias_miles
    by: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict))
    for row in rows:
        zona = str(row["zona_id"]).zfill(2)
        if zona not in _ZONA_INDICATOR:
            continue
        val = row.get("familias_miles", "")
        if val in ("", None):
            continue
        try:
            by[zona][str(row["year"]).strip()][row["grado"].strip()] = float(val)
        except (TypeError, ValueError):
            continue

    out = []
    for zona, (ind_id, label) in _ZONA_INDICATOR.items():
        ind = Indicator(id=ind_id, label=label, unit="%", theme="security",
                        source=PERCEPTION_SOURCE)
        for year, grades in by.get(zona, {}).items():
            total = grades.get("Total")
            ningun = grades.get("Ningun_problema")
            if not total or ningun is None:
                continue
            share = round((total - ningun) / total * 100.0, 1)
            ind.values[year] = {"value": share, "source": PERCEPTION_SOURCE}
        if ind.values:
            out.append(ind)
    return out


def crime_indicators_from_rows(rows) -> list[Indicator]:
    """Curated crime rows → level Indicators (rate, counts); per-row source."""
    indicators: dict[str, Indicator] = {}
    for row in rows:
        meta = _CRIME_META.get(row["indicator_id"].strip())
        if not meta:
            continue  # e.g. var_interanual_pct → skip (not a level)
        ind_id, label, unit = meta
        ind = indicators.get(ind_id)
        if ind is None:
            ind = Indicator(id=ind_id, label=label, unit=unit, theme="security",
                            source="Ministerio del Interior / Ertzaintza (parcial)")
            indicators[ind_id] = ind
        try:
            value = float(row["value"])
        except (TypeError, ValueError):
            continue
        ind.values[row["year"].strip()] = {"value": value,
                                            "source": row["source"].strip()}
    return list(indicators.values())


def build_indicators() -> list[Indicator]:
    out: list[Indicator] = []
    ppath = config.CURATED_DIR / PERCEPTION_FILE
    if ppath.exists():
        with ppath.open(encoding="utf-8", newline="") as fh:
            out += perception_indicators_from_rows(list(csv.DictReader(fh)))
    cpath = config.CURATED_DIR / CRIME_FILE
    if cpath.exists():
        with cpath.open(encoding="utf-8", newline="") as fh:
            out += crime_indicators_from_rows(list(csv.DictReader(fh)))
    return out
