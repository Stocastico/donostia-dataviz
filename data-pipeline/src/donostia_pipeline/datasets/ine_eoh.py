"""INE Hotel Occupancy Survey (EOH) — monthly overnight stays, San Sebastián.

Source: INE wstempus API, table 2078 "Viajeros y pernoctaciones por puntos
turísticos". For Donostia-San Sebastián the relevant series are
``EOT2721`` (pernoctaciones, residentes en España) and ``EOT2722`` (residentes
en el extranjero). We sum them per (year, month) into one total overnight-stays
series — a city-grain monthly time series for the seasonality heatmap.

Each raw file is one INE ``DATOS_SERIE`` response: ``{"Data": [{"Anyo",
"FK_Periodo" (1-12 = month), "Valor"}, ...]}``.
"""

from __future__ import annotations

import json
from collections import defaultdict

from ..model import BuildContext, Series

ESP_FILE = "ine_pernoct_esp.json"  # EOT2721
EXT_FILE = "ine_pernoct_ext.json"  # EOT2722
SOURCE = "INE — Encuesta de Ocupación Hotelera, tabla 2078 (puntos turísticos)"


def _add_series_file(ctx: BuildContext, name: str, acc: dict[str, dict[str, float]]) -> None:
    """Add one INE series file's monthly values into ``acc[year][month]``."""
    raw = json.loads((ctx.raw_dir / name).read_text(encoding="utf-8"))
    for point in raw.get("Data", []):
        value = point.get("Valor")
        if value is None:
            continue
        year = str(point["Anyo"])
        month = str(point["FK_Periodo"])
        acc[year][month] = acc[year].get(month, 0.0) + float(value)


def build_series(ctx: BuildContext) -> list[Series]:
    acc: dict[str, dict[str, float]] = defaultdict(dict)
    _add_series_file(ctx, ESP_FILE, acc)
    _add_series_file(ctx, EXT_FILE, acc)

    years = sorted(acc)
    values: dict[str, dict[str, float | None]] = {
        year: dict(sorted(acc[year].items(), key=lambda kv: int(kv[0])))
        for year in years
    }

    return [
        Series(
            id="overnight_stays",
            label="Pernoctaciones totales (hotel)",
            unit="pernoctaciones",
            theme="tourism",
            source=SOURCE,
            kind="month-year",
            years=years,
            values=values,
        )
    ]
