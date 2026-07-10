"""Security: perceived (in)security and real crime — city indicators (HU-1).

Two curated, source-cited inputs in ``datos/input/`` (like MICE): they answer
the user's HU-1 ("perceived security has fallen a lot — but that isn't true").

* **Perception** — ``percepcion_seguridad_eustat.csv`` (Eustat ECV, families by
  perceived security grade and zone, 1989–2024). We emit the **share of
  families reporting any security problem** = (Total − "Ningún problema") /
  Total × 100, for the Donostia zone and for the C.A. de Euskadi:
  ``perception_insecurity_donostia`` / ``perception_insecurity_euskadi``.

* **Crime — city** — ``criminalidad_donostia.csv`` (partial press/official
  series): ``crime_rate_1000`` (rate per 1,000) and ``crime_infractions``
  (known penal infractions of **Donostia**). Partial by design (press points).

* **Crime — province** — ``criminalidad_gipuzkoa_mir.csv`` (full official
  annual series, Portal Estadístico de Criminalidad / Min. Interior):
  ``crime_infractions_gipuzkoa`` from the ``TOTAL INFRACCIONES PENALES`` row,
  Gipuzkoa 2010–2024. ⚠️ **Province, not the city** — Donostia ≈ ⅓ of
  Gipuzkoa; the label says so and any narrative must too. It is the complete
  real backdrop the Donostia series lacks (regional trend, not exact city).

All city/province-grain, theme ``security``. Pure transforms are unit-tested.
"""

from __future__ import annotations

import csv
from collections import defaultdict

from .. import config
from ..model import Indicator

PERCEPTION_FILE = "percepcion_seguridad_eustat.csv"
CRIME_FILE = "criminalidad_donostia.csv"
CRIME_GIPUZKOA_FILE = "criminalidad_gipuzkoa_mir.csv"
CRIME_GIPUZKOA_TOTAL = "TOTAL INFRACCIONES PENALES"

PERCEPTION_SOURCE = (
    "Eustat — Encuesta de Condiciones de Vida, familias por grado de seguridad "
    "ciudadana y zona (tabla PX_010901_cecv_ma04_3); % con algún problema"
)
_ZONA_INDICATOR = {
    "70": ("perception_insecurity_donostia",
           "Familias con problemas de seguridad — Donostia (%)"),
    "00": ("perception_insecurity_euskadi",
           "Familias con problemas de seguridad — Euskadi (%)"),
}

# Crime indicator_id → (label, unit). Level series only (rates/counts); the
# year-on-year % row is skipped (not a level).
_CRIME_META = {
    "tasa_criminalidad_1000": ("crime_rate_1000",
                               "Tasa de criminalidad (por 1000 hab.)", "por 1000 hab."),
    "infracciones_penales": ("crime_infractions",
                             "Infracciones penales conocidas (Donostia)", "infracciones"),
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


def crime_gipuzkoa_indicators_from_rows(rows) -> list[Indicator]:
    """Curated province rows → the total-infractions Indicator (Gipuzkoa).

    Only the ``TOTAL INFRACCIONES PENALES`` typology becomes an indicator; the
    per-typology breakdown stays in the CSV for the analysis layer.
    """
    ind = Indicator(
        id="crime_infractions_gipuzkoa",
        label="Infracciones penales conocidas — Gipuzkoa (provincia)",
        unit="infracciones", theme="security",
        source="Portal Estadístico de Criminalidad (Min. Interior) — Gipuzkoa")
    for row in rows:
        if row.get("tipologia", "").strip() != CRIME_GIPUZKOA_TOTAL:
            continue
        try:
            value = float(str(row["infracciones"]).strip())
        except (TypeError, ValueError, KeyError):
            continue
        ind.values[str(row["year"]).strip()] = {
            "value": value, "source": row.get("source", "").strip()}
    return [ind] if ind.values else []


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
    gpath = config.CURATED_DIR / CRIME_GIPUZKOA_FILE
    if gpath.exists():
        with gpath.open(encoding="utf-8", newline="") as fh:
            out += crime_gipuzkoa_indicators_from_rows(list(csv.DictReader(fh)))
    return out
