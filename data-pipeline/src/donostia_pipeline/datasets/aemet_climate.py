"""AEMET climate — monthly temperature and precipitation, Igeldo station.

Source: AEMET OpenData, monthly climatological values for the
Donostia/San Sebastián — Igeldo station (index ``1024E``). Each raw record has
``fecha`` ``"YYYY-M"`` (where ``M`` 1–12 is a month and ``13`` is the annual
summary, which we drop) plus string values ``tm_mes`` (mean temperature, °C) and
``p_mes`` (total precipitation, mm). We emit two city-grain monthly series for
the seasonality view.

The raw file is fetched by ``build.ensure_aemet`` (2-step AEMET API, needs a
free ``AEMET_API_KEY``); if it is absent this module yields nothing, so the
pipeline still runs without a key.
"""

from __future__ import annotations

import json
from collections import defaultdict

from ..model import BuildContext, Series

RAW_FILE = "aemet_igeldo.json"
SOURCE = "AEMET OpenData — valores climatológicos mensuales, estación Igeldo (1024E)"


def _parse(value: object) -> float | None:
    """Parse an AEMET numeric string (dot or comma decimal); None if absent."""
    if value is None:
        return None
    text = str(value).strip().replace(",", ".")
    if not text or text in {"-", "Ip"}:  # Ip = precipitación inapreciable
        return None
    try:
        return float(text)
    except ValueError:
        return None


def build_series(ctx: BuildContext) -> list[Series]:
    path = ctx.raw_dir / RAW_FILE
    if not path.exists():
        return []  # no API key / not fetched → skip gracefully

    records = json.loads(path.read_text(encoding="utf-8"))
    temp: dict[str, dict[str, float | None]] = defaultdict(dict)
    precip: dict[str, dict[str, float | None]] = defaultdict(dict)
    temp_max: dict[str, dict[str, float | None]] = defaultdict(dict)
    hot_days: dict[str, dict[str, float | None]] = defaultdict(dict)
    years: set[str] = set()

    for rec in records:
        year, _, month = str(rec.get("fecha", "")).partition("-")
        if not month or not month.isdigit() or int(month) > 12:
            continue  # skip the annual (mes=13) summary rows
        month = str(int(month))
        years.add(year)
        tm = _parse(rec.get("tm_mes"))
        pm = _parse(rec.get("p_mes"))
        # ta_max is the month's absolute peak, formatted "38.3(18)" (day in
        # parentheses) → keep the part before "(". nt_30 = days with tmax ≥ 30°C.
        tx = _parse(str(rec.get("ta_max", "")).split("(")[0])
        nh = _parse(rec.get("nt_30"))
        if tm is not None:
            temp[year][month] = tm
        if pm is not None:
            precip[year][month] = pm
        if tx is not None:
            temp_max[year][month] = tx
        if nh is not None:
            hot_days[year][month] = nh

    sorted_years = sorted(years)

    def _series(id_: str, label: str, unit: str, values: dict) -> Series:
        return Series(
            id=id_,
            label=label,
            unit=unit,
            theme="climate",
            source=SOURCE,
            kind="month-year",
            years=sorted_years,
            values={y: dict(sorted(values[y].items(), key=lambda kv: int(kv[0])))
                    for y in sorted_years if y in values},
        )

    return [
        _series("temp_avg", "Temperatura media mensual", "°C", temp),
        _series("temp_max", "Temperatura máxima absoluta", "°C", temp_max),
        _series("precip", "Precipitaciones mensuales", "mm", precip),
        _series("hot_days_30", "Días de calor (máx ≥ 30°C)", "días", hot_days),
    ]
