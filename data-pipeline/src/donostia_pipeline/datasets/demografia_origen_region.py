"""Demographics by barrio — population share by broad region of origin (REC-21).

Same source and CSV as ``demografia.py`` (``demografia-origen`` →
``demografianacionalidadbarrio.csv``, one row per year/barrio/nationality),
but instead of collapsing every non-Spanish origin into a single
``pct_foreign``, this groups the 57 country values into broader regions of
origin. The aggregate hides two populations that move in opposite directions
with barrio income (see ``docs/NOTA-METODOLOGICA.md`` MET-5 and
``docs/intermedia/ANALISIS-EXTRANJEROS-EMPLEO.md``): this module makes that
visible as a per-region choropleth instead of one blended number.

The country→region grouping follows known Spanish migration patterns (recent
economic migration vs. high-income/free-movement Europe), not destination
occupation — that cross does not exist in any public dataset at this grain
(see the analysis doc's data-gap section). Annual series 2000–2025, same as
``pct_foreign``.
"""

from __future__ import annotations

import csv
from collections import defaultdict

from ..model import BuildContext, Metric

CSV_NAME = "demo_barrio.csv"
SPAIN = "ESPAÑA"
SOURCE = "Donostia Open Data — demografía por nacionalidad y barrio (agrupación por región)"

# País -> región. Deliberadamente más fino que "extranjero sí/no": separa
# patrones de origen migratorio conocidos (económico reciente vs.
# cualificado/rentista) en vez de destino laboral, que no está en los datos.
COUNTRY_TO_REGION: dict[str, str] = {
    "ARGENTINA": "latam", "BOLIVIA": "latam", "BRASIL": "latam", "CHILE": "latam",
    "COLOMBIA": "latam", "COSTA RICA": "latam", "CUBA": "latam", "ECUADOR": "latam",
    "EL SALVADOR": "latam", "GUATEMALA": "latam", "HONDURAS": "latam",
    "MEXICO": "latam", "NICARAGUA": "latam", "PARAGUAY": "latam", "PERU": "latam",
    "REPUBLICA DOMINICANA": "latam", "URUGUAY": "latam", "VENEZUELA": "latam",
    "MARRUECOS": "norte_africa", "ARGELIA": "norte_africa",
    "SENEGAL": "africa_subsahariana", "MALI": "africa_subsahariana",
    "CAMERUN": "africa_subsahariana", "GHANA": "africa_subsahariana",
    "GUINEA ECUATORIAL": "africa_subsahariana", "NIGERIA": "africa_subsahariana",
    "MAURITANIA": "africa_subsahariana",
    "ALEMANIA": "europa_occidental", "FRANCIA": "europa_occidental",
    "ITALIA": "europa_occidental", "PAISES BAJOS": "europa_occidental",
    "REINO UNIDO": "europa_occidental", "IRLANDA": "europa_occidental",
    "SUECIA": "europa_occidental", "GRECIA": "europa_occidental",
    "PORTUGAL": "europa_occidental",
    "RUMANIA": "europa_este", "BULGARIA": "europa_este", "POLONIA": "europa_este",
    "MOLDAVIA": "europa_este", "UCRANIA": "europa_este", "RUSIA": "europa_este",
    "GEORGIA": "europa_este", "ARMENIA": "europa_este",
    "IRAN": "oriente_medio", "SIRIA": "oriente_medio",
    "CHINA": "asia", "FILIPINAS": "asia", "INDIA": "asia", "JAPON": "asia",
    "COREA": "asia", "VIETNAM": "asia", "NEPAL": "asia", "PAKISTAN": "asia",
    "MONGOLIA": "asia",
    "ESTADOS UNIDOS DE AMERICA": "norteamerica_oceania", "AUSTRALIA": "norteamerica_oceania",
}

REGIONS: dict[str, str] = {
    "latam": "Población de origen latinoamericano",
    "norte_africa": "Población de origen norteafricano",
    "africa_subsahariana": "Población de origen subsahariano",
    "europa_occidental": "Población de origen europeo occidental",
    "europa_este": "Población de origen de Europa del Este",
    "oriente_medio": "Población de origen de Oriente Medio",
    "asia": "Población de origen asiático (oriental/meridional)",
    "norteamerica_oceania": "Población de origen norteamericano/oceánico",
}


def build(ctx: BuildContext) -> list[Metric]:
    # (barrio_id, year) -> total population, and -> {region: count}
    total: dict[tuple[str, str], int] = defaultdict(int)
    by_region: dict[str, dict[tuple[str, str], int]] = {
        region: defaultdict(int) for region in REGIONS
    }
    years: set[str] = set()

    with (ctx.raw_dir / CSV_NAME).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            code = row["AuzoKodea"].strip()
            barrio_id = ctx.code_to_id.get(code)
            if not barrio_id:
                continue  # "Ezezaguna" (unassigned) → skip, same as demografia.py
            year = row["Urtea"].strip()
            try:
                people = int(row["PertsonenKop"])
            except (TypeError, ValueError):
                continue
            years.add(year)
            total[(barrio_id, year)] += people

            country = row["Jatorria"].strip().upper()
            if country == SPAIN:
                continue
            region = COUNTRY_TO_REGION.get(country)
            if region:
                by_region[region][(barrio_id, year)] += people

    periods = sorted(years)
    metrics = []
    for region, label in REGIONS.items():
        values: dict[str, dict[str, float | None]] = defaultdict(dict)
        for (barrio_id, year), pop in total.items():
            count = by_region[region].get((barrio_id, year), 0)
            share = (count / pop * 100.0) if pop else None
            values[barrio_id][year] = round(share, 3) if share is not None else None
        metrics.append(Metric(
            id=f"pct_origin_{region}",
            label=label,
            unit="%",
            kind="sequential",
            theme="demography",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="year",
            periods=periods,
            values=dict(values),
        ))
    return metrics
