"""REATE tourist-license history — annual city indicators (REC-12).

Source: Open Data Euskadi, dataset "Viviendas y habitaciones de vivienda
particular para uso turístico en Euskadi" (registro REATE del Gobierno Vasco,
Ley 13/2016 de Turismo): ``viviendas.json`` (VUT) + ``habitaciones.json``
(HUT), one record per registered unit with the registration date in
``FechainscripcionREATE`` (dd/mm/yyyy) — see ``build.ensure_reate`` for the
fetch. This is the second tourist-supply signal, independent of Airbnb's
adoption bias (MET-7), that AN-16/REC-12 called for.

**Survivorship caveat**: the files are a *living registry snapshot* — units
that deregistered (bajas) are simply gone, and no baja dates are published.
Every curve here is therefore of *surviving* licenses: early years
underestimate the true flow of altas, and the cumulative series is a floor of
the legal supply that existed at each date. The caveat travels in ``SOURCE``
so every rendered point carries it.

Only city granularity: records have street addresses and postal codes but no
barrio and no coordinates (same callejero limitation as REC-8).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..model import Indicator

RAW_VIVIENDAS = "reate_viviendas.json"
RAW_HABITACIONES = "reate_habitaciones.json"
SOURCE = (
    "Gobierno Vasco / Open Data Euskadi — registro REATE de viviendas y "
    "habitaciones de uso turístico (snapshot vivo: solo altas supervivientes, "
    "las bajas no se publican)"
)

_FECHA_RE = re.compile(r"\d{2}/\d{2}/(\d{4})$")
_LABELS = {
    "vut_licenses_new": ("Nuevas licencias turísticas VUT/HUT (REATE)", "licencias"),
    "vut_licenses_cumulative": ("Licencias turísticas VUT/HUT acumuladas (REATE)", "licencias"),
    "vut_plazas_cumulative": ("Plazas turísticas legales acumuladas (REATE)", "plazas"),
}


def licenses_from_reate(viviendas: list[dict], habitaciones: list[dict]) -> list[Indicator]:
    """Pure transform: REATE records -> three annual indicators (unit-tested)."""
    new_by_year: dict[int, float] = {}
    plazas_by_year: dict[int, float] = {}
    for record in list(viviendas) + list(habitaciones):
        if "Donostia" not in (record.get("Municipio") or ""):
            continue
        match = _FECHA_RE.fullmatch(record.get("FechainscripcionREATE") or "")
        if match is None:
            continue
        year = int(match.group(1))
        new_by_year[year] = new_by_year.get(year, 0.0) + 1.0
        try:
            plazas = float(record.get("Capacidad"))
        except (TypeError, ValueError):
            plazas = 0.0
        plazas_by_year[year] = plazas_by_year.get(year, 0.0) + plazas

    indicators = {
        ind_id: Indicator(id=ind_id, label=label, unit=unit, theme="tourism", source=SOURCE)
        for ind_id, (label, unit) in _LABELS.items()
    }
    if new_by_year:
        cum_units = cum_plazas = 0.0
        for year in range(min(new_by_year), max(new_by_year) + 1):
            cum_units += new_by_year.get(year, 0.0)
            cum_plazas += plazas_by_year.get(year, 0.0)
            point = str(year)
            indicators["vut_licenses_new"].values[point] = {
                "value": new_by_year.get(year, 0.0), "source": SOURCE}
            indicators["vut_licenses_cumulative"].values[point] = {
                "value": cum_units, "source": SOURCE}
            indicators["vut_plazas_cumulative"].values[point] = {
                "value": cum_plazas, "source": SOURCE}
    return list(indicators.values())


def build_indicators(raw_dir: Path) -> list[Indicator]:
    paths = (raw_dir / RAW_VIVIENDAS, raw_dir / RAW_HABITACIONES)
    if not all(p.exists() for p in paths):
        return []  # never build half a curve from one of the two files
    viviendas, habitaciones = (json.loads(p.read_text(encoding="utf-8")) for p in paths)
    return licenses_from_reate(viviendas, habitaciones)
