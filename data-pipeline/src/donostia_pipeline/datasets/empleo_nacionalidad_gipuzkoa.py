"""Employment stability by nationality, and R&D-personnel intensity (REC-21).

Two annual **city-context** indicators (no barrio grain exists for either —
Eustat does not publish the Basque Labour Force Survey, nor R&D-personnel
statistics, below territorio histórico; see
``docs/intermedia/ANALISIS-EXTRANJEROS-EMPLEO.md``). Grain is **Gipuzkoa**,
not Donostia — the closest available context, since the capital concentrates
roughly a third of the territory's population and most of its research
centres.

- ``unemployment_rate_spanish_gipuzkoa`` / ``unemployment_rate_foreign_gipuzkoa``
  — Eustat PRA ``PX_050403_cpra_tab17`` ("Tasas de actividad, ocupación y
  paro... por nacionalidad"), tasa "Tasa de paro", promedio anual. Tests the
  "sin trabajo estable" half of the migration-profile question: foreign
  unemployment roughly doubles Spanish unemployment in Gipuzkoa.
- ``randd_personnel_per_1000_employed_gipuzkoa`` — Eustat R&D-personnel
  survey ``PX_043201_cid_res08c`` (personal EDP, sector "Total", ocupación
  "Total") divided by total employed population from PRA ``cpra_tab04``
  (territorio histórico Gipuzkoa, promedio anual) × 1000. Tests "mucha más
  investigación que la media española" — INE reports 13.6‰ for Spain (2024,
  press release, cited as a fixed comparison point since INE does not
  publish this ratio through an open API table).
"""

from __future__ import annotations

import json
from pathlib import Path

from ..model import Indicator

RAW_TASAS = "eustat_tasas_nacionalidad_gipuzkoa.json"
RAW_ID_PERSONAL = "eustat_id_personal_gipuzkoa.json"
RAW_OCUPADOS = "eustat_poblacion_ocupada_total.json"

SOURCE_TASAS = (
    "Eustat — Tasas de actividad, ocupación y paro por nacionalidad y "
    "trimestre (tabla PX_050403_cpra_tab17), Gipuzkoa, promedio anual"
)
SOURCE_ID = (
    "Eustat — Personal EDP dedicado a I+D por sector de ejecución y "
    "territorio histórico (tabla PX_043201_cid_res08c), Gipuzkoa, sobre "
    "población ocupada de Eustat PRA (tabla PX_050403_cpra_tab04); "
    "referencia España 2024: 13,6‰ (INE, nota de prensa)"
)

# tasas: key = [tasa (%), territorio histórico, nacionalidad, trimestre, periodo]
_TASA_PARO = "30"
_NAC_ESPANOLA = "20"
_NAC_EXTRANJERA = "30"


def _paro_por_nacionalidad(payload: dict) -> list[Indicator]:
    indicators = {
        "unemployment_rate_spanish_gipuzkoa": Indicator(
            id="unemployment_rate_spanish_gipuzkoa",
            label="Tasso di disoccupazione — nazionalità spagnola (Gipuzkoa)",
            unit="%", theme="economy", source=SOURCE_TASAS),
        "unemployment_rate_foreign_gipuzkoa": Indicator(
            id="unemployment_rate_foreign_gipuzkoa",
            label="Tasso di disoccupazione — nazionalità straniera (Gipuzkoa)",
            unit="%", theme="economy", source=SOURCE_TASAS),
    }
    nac_to_id = {
        _NAC_ESPANOLA: "unemployment_rate_spanish_gipuzkoa",
        _NAC_EXTRANJERA: "unemployment_rate_foreign_gipuzkoa",
    }
    for row in payload.get("data", []):
        key = row["key"]
        if key[0] != _TASA_PARO:
            continue
        ind_id = nac_to_id.get(key[2])
        if ind_id is None:
            continue
        try:
            value = float(row["values"][0])
        except (TypeError, ValueError):
            continue  # PxWeb's ":" — dato no disponible (año en curso)
        indicators[ind_id].values[key[4]] = {"value": value, "source": SOURCE_TASAS}
    return list(indicators.values())


# id_personal: key = [territorio histórico, sector de ejecución, ocupación, sexo, periodo]
# ocupados: key = [relación con la actividad, territorio histórico, sexo, trimestre, periodo]
_SECTOR_TOTAL = "00"
_OCUPACION_TOTAL = "100"
_TERRITORIO_GIPUZKOA_ID = "20"


def _randd_ratio(id_payload: dict, ocupados_payload: dict) -> list[Indicator]:
    personal: dict[str, float] = {}
    for row in id_payload.get("data", []):
        key = row["key"]
        if key[1] != _SECTOR_TOTAL or key[2] != _OCUPACION_TOTAL:
            continue
        try:
            personal[key[4]] = float(row["values"][0])
        except (TypeError, ValueError):
            continue

    ocupados: dict[str, float] = {}
    for row in ocupados_payload.get("data", []):
        key = row["key"]
        if key[1] != _TERRITORIO_GIPUZKOA_ID:
            continue
        try:
            ocupados[key[4]] = float(row["values"][0]) * 1000  # tab04 viene en miles
        except (TypeError, ValueError):
            continue

    indicator = Indicator(
        id="randd_personnel_per_1000_employed_gipuzkoa",
        label="Personale I+D per 1000 occupati (Gipuzkoa)",
        unit="‰", theme="economy", source=SOURCE_ID,
    )
    for year, count in personal.items():
        denom = ocupados.get(year)
        if denom:
            indicator.values[year] = {
                "value": round(count / denom * 1000, 2), "source": SOURCE_ID,
            }
    return [indicator] if indicator.values else []


def _load(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def build_indicators(raw_dir: Path) -> list[Indicator]:
    indicators: list[Indicator] = []
    tasas = _load(raw_dir / RAW_TASAS)
    if tasas:
        indicators.extend(_paro_por_nacionalidad(tasas))
    id_personal = _load(raw_dir / RAW_ID_PERSONAL)
    ocupados = _load(raw_dir / RAW_OCUPADOS)
    if id_personal and ocupados:
        indicators.extend(_randd_ratio(id_personal, ocupados))
    return indicators
