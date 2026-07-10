"""Labor/study mobility + localized employment — city indicators (REC-17).

REC-17 asked for Eustat origin-destination commuting matrices. Those don't
exist in the PxWeb bank at municipio×municipio grain (checked jul-2026: the
old census OD matrices are not published there); what exists is:

- **EMPA** table ``PX_050407_cempa_empa_mt02`` — employed residents by
  categorical *lugar de trabajo* (own municipality / other municipality of the
  territorio / other territorio / outside CAE), 2021–.
- **EME** table ``PX_040606_ceme_me02`` — students 16+ by *lugar de estudios*
  (same categories), 2021–.
- **DIRAE** table ``PX_200163_cdirae_est07`` — persons employed in
  establishments *located* in the municipality, 1995–.

Together they close H4's missing half ("sin dejar de concentrar actividad"):
``jobs_located`` (jobs in the city) over EMPA's employed residents gives the
job-concentration ratio (>1 = the city imports workers), and the categorical
shares say how much resident life happens inside the municipality. See
``build.ensure_eustat_movilidad`` / ``ensure_eustat_dirae_empleo`` for the
fetches. Only city granularity, like every Eustat source in this project.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..model import Indicator

RAW_EMPA = "eustat_empa_movilidad.json"
RAW_EME = "eustat_eme_movilidad.json"
RAW_DIRAE = "eustat_dirae_empleo.json"

SOURCE_EMPA = (
    "Eustat — Población ocupada por ámbitos territoriales y lugar de trabajo "
    "(EMPA, tabla PX_050407_cempa_empa_mt02), Donostia / San Sebastián"
)
SOURCE_EME = (
    "Eustat — Población estudiante de 16 y más años por ámbitos territoriales "
    "y lugar de estudio (EME, tabla PX_040606_ceme_me02), Donostia / San Sebastián"
)
SOURCE_DIRAE = (
    "Eustat — Personas empleadas en establecimientos por ámbitos territoriales "
    "(DIRAE, tabla PX_200163_cdirae_est07), Donostia / San Sebastián"
)
SOURCE_RATIO = (
    "Eustat — empleo localizado (DIRAE est07) / ocupados residentes (EMPA mt02), "
    "Donostia / San Sebastián; >1 = la ciudad importa trabajadores"
)

_TOTAL = "_T"
_IN_OWN_MUNICIPALITY = "10"


def _year_values(payload: dict, lugar: str | None) -> dict[str, float]:
    """periodo -> value; ``lugar`` filters the mobility key, None = 2-dim table."""
    out: dict[str, float] = {}
    for row in payload.get("data", []):
        key = row["key"]
        if lugar is not None and key[1] != lugar:
            continue
        try:
            value = float(row["values"][0])
        except (TypeError, ValueError):
            continue  # PxWeb's ":" (not available) or other marker
        out[key[-1]] = value
    return out


def _pct_in_own(payload: dict) -> dict[str, float]:
    total = _year_values(payload, _TOTAL)
    own = _year_values(payload, _IN_OWN_MUNICIPALITY)
    return {year: own[year] / total[year] * 100.0
            for year in own if total.get(year)}


def indicators_from_pxweb(empa: dict | None, eme: dict | None,
                          dirae: dict | None) -> list[Indicator]:
    """Pure transform: up to three PxWeb responses -> city indicators (unit-tested).

    Indicators whose inputs are absent are dropped, never emitted empty.
    """
    jobs = _year_values(dirae, None) if dirae else {}
    residents = _year_values(empa, _TOTAL) if empa else {}
    specs = [
        ("jobs_located", "Empleos localizados en la ciudad (Eustat DIRAE)",
         "personas", SOURCE_DIRAE,
         jobs),
        ("residents_work_in_city_pct",
         "Ocupados residentes que trabajan en su propio municipio", "%", SOURCE_EMPA,
         _pct_in_own(empa) if empa else {}),
        ("residents_study_in_city_pct",
         "Estudiantes residentes que estudian en su propio municipio", "%", SOURCE_EME,
         _pct_in_own(eme) if eme else {}),
        ("job_concentration_ratio",
         "Ratio empleos localizados / ocupados residentes", "ratio", SOURCE_RATIO,
         {year: jobs[year] / residents[year]
          for year in jobs if residents.get(year)}),
    ]
    indicators = []
    for ind_id, label, unit, source, by_year in specs:
        if not by_year:
            continue
        ind = Indicator(id=ind_id, label=label, unit=unit, theme="economy", source=source)
        ind.values = {year: {"value": value, "source": source}
                      for year, value in by_year.items()}
        indicators.append(ind)
    return indicators


def _load(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def build_indicators(raw_dir: Path) -> list[Indicator]:
    return indicators_from_pxweb(
        empa=_load(raw_dir / RAW_EMPA),
        eme=_load(raw_dir / RAW_EME),
        dirae=_load(raw_dir / RAW_DIRAE),
    )
