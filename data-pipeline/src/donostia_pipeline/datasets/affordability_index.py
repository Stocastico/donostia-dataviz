"""HU-7 — Índice de asequibilidad: venta vs. alquiler vs. salario vs. IPC (app).

Exporta un JSON a medida (``web/src/data/affordability_index.json``, como
``origen_paises_barrio.json``) con cuatro series de **ciudad** indexadas a
**2016 = 100**, para que el dashboard cuente en una sola vista lo que el análisis
``analysis/housing_affordability.py`` y la Historia 1 ya narran: **comprar y
alquilar se han encarecido más deprisa que el sueldo y que la inflación**.

Las cuatro series (media **ponderada por población** de los barrios que reportan,
método idéntico al del análisis; para años sin padrón se arrastra el último año
disponible, de modo que la venta llega a 2026):

* **venta** — ``sale_price_eur_m2`` (idealista, oferta; *proxy*),
* **alquiler** — ``rent_eur_m2`` (EMA),
* **salario** — ``income_labor`` (renta del trabajo, Eustat),
* **IPC** — índice general nacional (``datos/input/ipc_espana.csv``), línea de
  referencia (la inflación a batir).

Cada serie corre sobre su propio rango disponible; el ``growth`` reportado
distingue la **ventana común 2016–2023** (comparación limpia a cuatro bandas) y
el **acumulado hasta el último año** de cada serie. Descriptivo, no causal.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from ..model import Metric

BASE_YEAR = 2016
COMMON_END = 2023  # alquiler ∩ salario ∩ IPC ∩ venta → comparación a 4 bandas

# id → (metric_id | None para IPC, label italiano, color, dashed, confidence).
# Colores validados (dataviz): venta ámbar, alquiler azul, salario verde; IPC gris
# discontinuo = línea de referencia (identidad por trazo + etiqueta, no solo color).
SERIES_SPEC = [
    ("sale", "sale_price_eur_m2", "Prezzo di vendita", "#b5730f", False, "proxy"),
    ("rent", "rent_eur_m2", "Affitto", "#2166ac", False, "observed"),
    ("salary", "income_labor", "Salario (reddito da lavoro)", "#2a9d6f", False, "observed"),
    ("ipc", None, "IPC (inflazione)", "#8a94a6", True, "observed"),
]

SOURCE = (
    "Elaborazione: media ponderata per popolazione, base 2016=100. Prezzo di "
    "vendita idealista (offerta, REC-25) · affitto EMA · salario Eustat (reddito "
    "da lavoro) · IPC nazionale INE."
)
NOTE = (
    "Serie di città (media dei barrios pesata per popolazione), ognuna sul proprio "
    "intervallo disponibile. Il prezzo di vendita è di **offerta** (proxy). "
    "Descrittivo, non causale."
)


def _int_year_values(metric: Metric) -> dict[str, dict[int, float]]:
    """Metric.values (años string) → {barrio_id: {año int: valor}} sin nulos."""
    out: dict[str, dict[int, float]] = {}
    for bid, by_period in metric.values.items():
        ys = {int(p): v for p, v in by_period.items()
              if v is not None and str(p).isdigit()}
        if ys:
            out[bid] = ys
    return out


def weighted_city(values: dict[str, dict[int, float]],
                  pop: dict[str, dict[int, float]]) -> dict[int, float]:
    """Media ponderada por población, año a año.

    Para un año sin padrón en un barrio se usa su **último** año disponible
    (arrastre) — así las series (p.ej. venta 2026) no se cortan donde acaba el
    padrón, sin que la composición cambie de forma brusca.
    """
    def weight(bid: str, year: int) -> float | None:
        ys = pop.get(bid)
        if not ys:
            return None
        return ys.get(year, ys[max(ys)])

    years = sorted({y for ys in values.values() for y in ys})
    out: dict[int, float] = {}
    for year in years:
        num = den = 0.0
        for bid, ys in values.items():
            if year in ys:
                w = weight(bid, year)
                if w:
                    num += ys[year] * w
                    den += w
        if den:
            out[year] = num / den
    return out


def rebase(series: dict[int, float], base_year: int) -> dict[int, float]:
    """Reescala a base_year = 100 (vacío si falta el año base)."""
    if base_year not in series:
        return {}
    base = series[base_year]
    return {y: v / base * 100.0 for y, v in series.items()}


def _growth(series: dict[int, float], y0: int, y1: int) -> float | None:
    if y0 in series and y1 in series and series[y0]:
        return round((series[y1] / series[y0] - 1.0) * 100.0, 1)
    return None


def read_ipc(path: Path) -> dict[int, float]:
    with path.open(encoding="utf-8", newline="") as fh:
        return {int(r["year"]): float(r["value"]) for r in csv.DictReader(fh)}


def build_payload(metrics_by_id: dict[str, Metric], ipc_by_year: dict[int, float],
                  base_year: int = BASE_YEAR) -> dict:
    pop_metric = metrics_by_id.get("population")
    pop = _int_year_values(pop_metric) if pop_metric else {}

    series_out = []
    for sid, metric_id, label, color, dashed, confidence in SERIES_SPEC:
        if metric_id is None:  # IPC — city series already
            city = {y: v for y, v in ipc_by_year.items()}
        else:
            m = metrics_by_id.get(metric_id)
            if m is None:
                continue
            city = weighted_city(_int_year_values(m), pop)
        indexed = rebase(city, base_year)
        if not indexed:
            continue
        last = max(indexed)
        entry = {
            "id": sid,
            "label": label,
            "color": color,
            "confidence": confidence,
            "data": {str(y): round(v, 1) for y, v in sorted(indexed.items())},
            "lastYear": last,
            "growth": {
                "common": _growth(indexed, base_year, COMMON_END),
                "full": _growth(indexed, base_year, last),
            },
        }
        if dashed:
            entry["dash"] = True
        series_out.append(entry)

    return {
        "baseYear": base_year,
        "commonEnd": COMMON_END,
        "unit": "indice (2016 = 100)",
        "series": series_out,
        "source": SOURCE,
        "note": NOTE,
    }


def write_json(path: Path, metrics_by_id: dict[str, Metric], ipc_path: Path,
               base_year: int = BASE_YEAR) -> dict:
    payload = build_payload(metrics_by_id, read_ipc(ipc_path), base_year)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
