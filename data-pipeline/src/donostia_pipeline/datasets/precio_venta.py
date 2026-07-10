"""REC-25 — Precio de venta €/m² por barrio (idealista, choropleth).

idealista publishes monthly asking-price (€/m²) series per neighbourhood of
Donostia in its press room ("sala de prensa"). The site blocks automated clients
(403, anti-bot), so the history is a **curated snapshot** contributed by the user
(`datos/input/precios_venta_idealista.csv`, monthly long form) — not a live
fetch — like MICE/Ibiltur/OSM. This closes the 🔴 sale-price gap of HU-7 (rent vs
salary vs IPC) and gives the "city that gets more expensive" story its missing
temporal, buy-side dimension.

Two things it is **not**:

* **Not transaction prices.** These are **asking prices** of listed dwellings
  (oferta), an upper-bound proxy for what changes hands → ``proxy`` confidence.
* **Not the official 19-barrio geometry.** idealista uses its own ~12 zones. We
  map them to ``barrio_id`` with a documented crosswalk (``CROSSWALK``):
  - 1:1 for Amara/Gros/Antiguo/Egia/Intxaurrondo/Ategorrieta,
  - 1:many where an idealista zone spans several official barrios
    (Aiete-Añorga-Ibaeta → 3; Altza-Bidebieta → 2) — every contained barrio gets
    the **same** zone value (declared: no sub-zone detail),
  - ``erdialdea`` takes **Centro-Miraconcha** (its residential core; the
    ~20 %-cheaper *Parte Vieja* zone lives inside erdialdea too but is kept out
    of the map to avoid diluting it — it is shown separately in the narrative).
  Two idealista zones (Miramón-Zorroaga, Loiola-Martutene) are **excluded at
  source**: byte-identical duplicated series that both stop in 2019 — a source
  artefact, already dropped from the curated CSV.

Monthly detail is aggregated to a **calendar-year mean** (≥ ``MIN_MONTHS`` months
present) so the choropleth carries annual periods, comparable with ``rent_eur_m2``
(the ~186-month grain would swamp the TimeSlider / small multiples). The finer
monthly series feeds the narrative chart in ``output/historias.html``.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from .. import config
from ..model import BuildContext, Metric

CSV_NAME = "precios_venta_idealista.csv"
MIN_MONTHS = 3  # months needed in a calendar year for a defensible annual mean
FIRST_YEAR = 2011  # 2010 is only a partial tail for a few zones → drop it

# idealista zone -> official barrio_id(s). erdialdea = Centro-Miraconcha
# (user decision jul-2026); Parte Vieja intentionally absent (narrative only);
# Miramón-Zorroaga / Loiola-Martutene absent (excluded at source, see docstring).
CROSSWALK: dict[str, list[str]] = {
    "Amara": ["amaraberri"],
    "Gros": ["gros"],
    "Antiguo": ["antigua"],
    "Egia": ["egia"],
    "Intxaurrondo": ["intxaurrondo"],
    "Ategorrieta": ["ategorrieta-ulia"],
    "Aiete-Anorga-Ibaeta": ["aiete", "anorga", "ibaeta"],
    "Altza-Bidebieta": ["altza", "mirakruz-bidebieta"],
    "Centro-Miraconcha": ["erdialdea"],
}

SOURCE = (
    "idealista, sala de prensa (informes de precio de vivienda en venta por "
    "barrio, €/m² de oferta); serie mensual curada 2010–2026, media anual "
    "(REC-25, aportada por el usuario)"
)
# Confidence tier + assumptions live centrally in provenance.py (MET-4).


def _annual_means(rows) -> dict[str, dict[int, float]]:
    """zona -> {year -> mean €/m²} over months present (≥ MIN_MONTHS, ≥ FIRST_YEAR)."""
    buckets: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        zona = row["zona_idealista"].strip()
        year = int(row["mes"][:4])
        if year < FIRST_YEAR:
            continue
        try:
            buckets[zona][year].append(float(row["precio_eur_m2"]))
        except (TypeError, ValueError):
            continue
    return {
        zona: {y: round(sum(v) / len(v)) for y, v in years.items() if len(v) >= MIN_MONTHS}
        for zona, years in buckets.items()
    }


def build_from_rows(rows, barrio_ids: set[str]) -> list[Metric]:
    by_zona = _annual_means(rows)

    values: dict[str, dict[str, float | None]] = {}
    year_set: set[int] = set()
    for zona, targets in CROSSWALK.items():
        annual = by_zona.get(zona)
        if not annual:
            continue
        year_set.update(annual)
        for bid in targets:
            if bid not in barrio_ids:
                continue
            values[bid] = {str(y): v for y, v in sorted(annual.items())}

    periods = [str(y) for y in sorted(year_set)]
    return [
        Metric(
            id="sale_price_eur_m2",
            label="Precio de venta (€/m²)",
            unit="€/m²",
            kind="sequential",
            theme="housing",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="year",
            status="live",
            periods=periods,
            values=values,
        )
    ]


def build(ctx: BuildContext) -> list[Metric]:
    path = config.CURATED_DIR / CSV_NAME
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return build_from_rows(rows, ctx.barrio_ids)
