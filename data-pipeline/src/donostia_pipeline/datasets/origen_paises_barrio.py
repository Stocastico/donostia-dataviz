"""Per-barrio top-N countries of origin, with a decade of evolution (REC-21-web).

Companion to ``demografia_origen_region`` (the regional choropleth metrics):
that module answers "how much of each barrio is of region X"; this one keeps the
individual countries so the app can show a "chi vive nel barrio · origini" card
— the top foreign nationalities in each barrio and how each has moved over the
last ten years.

Not a ``Metric`` (a per-barrio list of country records doesn't fit the single
scalar-per-cell model), so it exports its own ``origen_paises_barrio.json`` into
``web/src/data/`` from the same ``demo_barrio.csv`` used everywhere else.

⚠️ MET-5 applies in full: country of origin is **not** a proxy for anything
(income, tourism, transformation). The card is descriptive; the app copy says so.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from .demografia_origen_region import COUNTRY_TO_REGION

CSV_NAME = "demo_barrio.csv"
SPAIN = "ESPAÑA"
SOURCE = "Donostia Open Data — demografía por nacionalidad y barrio (demografianacionalidadbarrio.csv)"

# Connectors kept lowercase when title-casing the source's uppercase names
# ("ESTADOS UNIDOS DE AMERICA" -> "Estados Unidos de America").
_CONNECTORS = {"de", "del", "la", "las", "los", "y", "e"}


def _display(country: str) -> str:
    """Title-case a source country name, keeping Spanish connectors lowercase."""
    words = country.strip().lower().split()
    return " ".join(
        w if w in _CONNECTORS and i > 0 else w.capitalize()
        for i, w in enumerate(words)
    )


def build_payload(
    csv_path: Path,
    code_to_id: dict[str, str],
    barrio_names: dict[str, str],
    top_n: int = 5,
    span: int = 10,
) -> dict:
    """Read ``demo_barrio.csv`` → per-barrio top-N foreign countries payload.

    ``span`` is the look-back in years for the evolution column; if the
    latest-minus-span year is missing, falls back to the earliest year present
    (same rule as ``perfil_extranjeros_empleo.top_countries``).
    """
    # (barrio_id, year, country) -> people, plus total pop per (barrio, year).
    people: dict[tuple[str, str, str], int] = defaultdict(int)
    total: dict[tuple[str, str], int] = defaultdict(int)
    years: set[str] = set()

    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            barrio_id = code_to_id.get(row["AuzoKodea"].strip())
            if not barrio_id:
                continue  # "Ezezaguna" (unassigned) → skip
            year = row["Urtea"].strip()
            try:
                n = int(row["PertsonenKop"])
            except (TypeError, ValueError):
                continue
            years.add(year)
            total[(barrio_id, year)] += n
            country = row["Jatorria"].strip().upper()
            if country != SPAIN:
                people[(barrio_id, year, country)] += n

    if not years:
        return {"latestYear": None, "pastYear": None, "source": SOURCE, "barrios": {}}

    latest = max(years)
    target = str(int(latest) - span)
    past = target if target in years else min(years)

    barrios: dict[str, dict] = {}
    for barrio_id in sorted(code_to_id.values()):
        pop = total.get((barrio_id, latest), 0)
        foreign = [
            (country, n)
            for (b, y, country), n in people.items()
            if b == barrio_id and y == latest
        ]
        foreign.sort(key=lambda x: (-x[1], x[0]))
        top = []
        for country, n in foreign[:top_n]:
            top.append({
                "country": _display(country),
                "region": COUNTRY_TO_REGION.get(country, "otros"),
                "peopleLatest": n,
                "peoplePast": people.get((barrio_id, past, country), 0),
                "pctOfBarrio": round(n / pop * 100, 2) if pop else 0.0,
            })
        barrios[barrio_id] = {
            "name": barrio_names.get(barrio_id, barrio_id),
            "foreignLatest": sum(n for _, n in foreign),
            "top": top,
        }

    return {"latestYear": latest, "pastYear": past, "source": SOURCE, "barrios": barrios}


def write_json(
    csv_path: Path,
    dest: Path,
    code_to_id: dict[str, str],
    barrio_names: dict[str, str],
) -> dict:
    """Build the payload and write it to ``dest`` (compact JSON). Returns it."""
    payload = build_payload(csv_path, code_to_id, barrio_names)
    dest.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return payload
