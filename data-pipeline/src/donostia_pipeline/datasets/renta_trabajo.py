"""Labor income (wages) per barrio — the *salary* proxy for HU-7.

Source: Eustat PxWeb table ``PX_173402_crpf_rpf_rp22_2p`` ("Renta personal
media de la C.A. de Euskadi por barrio de residencia de las capitales, según
tipo de renta"), filtered server-side to Donostia's barrios and **tipo de renta
110 = renta del trabajo** — see ``build.ensure_eustat_renta_trabajo`` for the
fetch.

Why a separate metric from ``income_total``: the disposable/total income that
``renta.py`` already emits includes pensions, capital and transfers, and in
2016–2023 grew faster than rent. **Labor income (wages)** — what a working
person actually earns — grew *slower* than rent in the same window, which is the
measure HU-7 ("imposible vivir solo con un sueldo") really needs. Keeping both
lets the story show that the answer depends on which income you look at.

Annual series 2016–2023 (the ``crpf`` panel), one value per barrio per year.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from ..model import BuildContext, Metric

RAW_FILE = "eustat_renta_trabajo.json"
SOURCE = (
    "Eustat — Renta personal media por barrio de residencia de las capitales, "
    "según tipo de renta (tabla PX_173402_crpf_rpf_rp22_2p), Donostia, "
    "renta del trabajo (tipo 110)"
)
LABOR_INCOME_CODE = "110"  # tipo de renta: renta del trabajo

# Eustat 8-digit barrio code → project barrio_id. Municipio 20069 (city total)
# is intentionally absent so it is skipped (metrics are per-barrio).
EUSTAT_BARRIO_TO_ID = {
    "20069001": "aiete",
    "20069002": "altza",
    "20069003": "amaraberri",
    "20069004": "antigua",
    "20069005": "anorga",
    "20069006": "ategorrieta-ulia",
    "20069007": "erdialdea",       # "Centro"
    "20069008": "egia",
    "20069009": "gros",
    "20069010": "ibaeta",
    "20069011": "igeldo",
    "20069020": "intxaurrondo",
    "20069018": "landerbaso",      # "Landarbaso"
    "20069013": "loiola",
    "20069014": "martutene",
    "20069015": "mirakruz-bidebieta",  # "Miracruz-Bidebieta"
    "20069016": "miramon-zorroaga",
    "20069017": "zubieta",
}


def income_labor_from_pxweb(payload: dict) -> list[Metric]:
    """Pure transform: PxWeb query response → the ``income_labor`` Metric.

    PxWeb ``json`` format: ``data`` is a list of ``{"key": [...], "values": [...]}``
    with ``key = [barrios, tipo de renta, periodo]``.
    """
    values: dict[str, dict[str, float | None]] = defaultdict(dict)
    periods: set[str] = set()
    for row in payload.get("data", []):
        key = row["key"]
        bcode, tipo, period = key[0], key[1], key[2]
        if tipo != LABOR_INCOME_CODE:
            continue
        barrio_id = EUSTAT_BARRIO_TO_ID.get(bcode)
        if not barrio_id:
            continue  # municipio total or a non-Donostia barrio
        try:
            value = float(row["values"][0])
        except (TypeError, ValueError, IndexError):
            continue  # PxWeb ":" (confidential) or missing
        values[barrio_id][period] = value
        periods.add(period)

    if not values:
        return []
    return [
        Metric(
            id="income_labor",
            label="Renta del trabajo per cápita",
            unit="€",
            kind="sequential",
            theme="economy",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="year",
            periods=sorted(periods),
            values=dict(values),
        )
    ]


def build(ctx: BuildContext) -> list[Metric]:
    path = ctx.raw_dir / RAW_FILE
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return income_labor_from_pxweb(payload)
