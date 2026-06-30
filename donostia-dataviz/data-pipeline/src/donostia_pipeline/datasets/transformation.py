"""Derived metrics: Urban Transformation Index (AN-8) — for the VIZ-6 dashboard.

Surfaces ``analysis/transformation_index.py`` / ``docs/INDICE-TRANSFORMACION.md``
as choropleth metrics so the frontend can render the documented index as a
side-by-side dashboard. Reads only metrics already in the store (income, rent,
% university, VUT density) — same pattern as ``barrio_profiles`` /
``change_velocity`` — and re-implements the **exact** documented computation, so
the maps mirror the reviewed analysis (``tests/test_transformation.py`` locks the
numbers against the committed data).

**This is NOT a gentrification index** (project decision): with the available
data we cannot demonstrate displacement/turnover of residents. It measures
*observable transformation*, with two transparent modes and components in plain
sight:

* **Socioeconomic mode** (Freeman 2005, adapted): a barrio is *susceptible* if its
  base-year (2016) income is below the city median, and shows transformation if
  university-share growth and rent growth exceed the city median. → a categorical
  class + a continuous score (mean of the two local-excess z-scores).
* **Tourism-pressure mode** (provisional): mean z-score of VUT density and rent
  *level* (the "touristic-expensive city") — levels, not growth, so it doesn't
  penalize centres already expensive in the base year.

The two component maps (``univ_excess`` / ``rent_excess``) expose the local
excess-over-median that drives the socioeconomic score (shift-share idea: nets out
the macro/inflation component common to the whole city).
"""

from __future__ import annotations

import numpy as np

from ..model import Metric

BASE_YEAR = 2016
MIN_POINTS = 3  # need ≥3 years to fit a defensible annual rate
PERIOD = "indice"  # single snapshot period

INCOME = "income_total"
RENT = "rent_eur_m2"
UNIV = "pct_university"
VUT = "vut_density"

# Socioeconomic classes, fixed order → the categorical index a barrio gets is its
# position here. Internal Spanish keys (from the analysis) map to these UI labels.
CLASS_LABELS = [
    "In trasformazione",
    "Trasformazione incipiente",
    "Stabile / senza trasformazione",
    "Consolidato / non suscettibile",
]
_CLASS_INDEX = {
    "en transformación": 0,
    "transformación incipiente": 1,
    "estable": 2,
    "consolidado / no susceptible": 3,
}

SOURCE = (
    "Derivata — Indice di Trasformazione Urbana (AN-8; cfr. INDICE-TRANSFORMACION.md)"
)


def _year_series(metric: Metric) -> dict[str, dict[int, float]]:
    """barrio_id → {year:int → value}, digit years ≥ BASE_YEAR, non-null only."""
    out: dict[str, dict[int, float]] = {}
    for bid, by_period in metric.values.items():
        pts = {
            int(p): float(v)
            for p, v in by_period.items()
            if v is not None and p.isdigit() and int(p) >= BASE_YEAR
        }
        if pts:
            out[bid] = pts
    return out


def _latest(metric: Metric, bid: str) -> float:
    for period in sorted(metric.values.get(bid, {}), reverse=True):
        v = metric.values[bid][period]
        if v is not None:
            return float(v)
    return np.nan


def _annual_rate(points: dict[int, float], kind: str) -> float:
    """Annualized rate: percentage points/year ("pp") or %/year ("level")."""
    if len(points) < MIN_POINTS:
        return np.nan
    years = sorted(points)
    xs = np.array(years, dtype=float)
    ys = np.array([points[y] for y in years], dtype=float)
    slope = np.polyfit(xs, ys, 1)[0]
    if kind == "pp":
        return float(slope)
    mean = ys.mean()
    return float(100.0 * slope / mean) if mean else np.nan


def _z(values: np.ndarray) -> np.ndarray:
    """Z-score over the non-NaN entries (sample std, ddof=1; matches pandas)."""
    mask = ~np.isnan(values)
    if mask.sum() < 2:
        return np.full_like(values, np.nan)
    mean = values[mask].mean()
    std = values[mask].std(ddof=1)
    if std == 0:
        return np.full_like(values, np.nan)
    return (values - mean) / std


def _classify(susceptible: bool, up_univ: bool, up_rent: bool) -> str:
    if not susceptible:
        return "consolidado / no susceptible"
    n = int(up_univ) + int(up_rent)
    return {2: "en transformación", 1: "transformación incipiente", 0: "estable"}[n]


def _diverging(metric_id: str, label: str, unit: str, by_barrio: dict[str, float]) -> Metric:
    values = {
        bid: {PERIOD: round(float(v), 2)}
        for bid, v in by_barrio.items()
        if v is not None and not np.isnan(v)
    }
    return Metric(
        id=metric_id,
        label=label,
        unit=unit,
        kind="diverging",
        theme="transformation",
        source=SOURCE,
        geo_grain="barrio",
        time_grain="snapshot",
        periods=[PERIOD],
        values=values,
    )


def build_from_metrics(metrics: dict[str, Metric]) -> list[Metric]:
    income, rent, univ = metrics.get(INCOME), metrics.get(RENT), metrics.get(UNIV)
    vut = metrics.get(VUT)
    if income is None or rent is None or univ is None:
        return []

    inc_y = _year_series(income)
    rent_y = _year_series(rent)
    univ_y = _year_series(univ)

    ids = sorted(set(inc_y) | set(rent_y))
    if not ids:
        return []

    renta_base = np.array([inc_y.get(b, {}).get(BASE_YEAR, np.nan) for b in ids])
    alquiler_nivel = np.array([_latest(rent, b) for b in ids])
    vut_density = np.array([_latest(vut, b) if vut else np.nan for b in ids])
    univ_rate = np.array([_annual_rate(univ_y.get(b, {}), "pp") for b in ids])
    rent_rate = np.array([_annual_rate(rent_y.get(b, {}), "level") for b in ids])

    # Local excess over the city median (shift-share: nets out the common macro term).
    univ_excess = univ_rate - np.nanmedian(univ_rate)
    rent_excess = rent_rate - np.nanmedian(rent_rate)

    # --- A) Socioeconomic mode (Freeman) ---
    median_income = np.nanmedian(renta_base)
    median_univ = np.nanmedian(univ_rate)
    median_rent = np.nanmedian(rent_rate)
    score_socio = np.nanmean(np.vstack([_z(univ_excess), _z(rent_excess)]), axis=0)

    class_values: dict[str, dict[str, float | None]] = {}
    for i, bid in enumerate(ids):
        if np.isnan(renta_base[i]) or np.isnan(univ_rate[i]) or np.isnan(rent_rate[i]):
            continue  # "datos insuficientes" → no value (renders as n/d)
        klass = _classify(
            renta_base[i] < median_income,
            univ_rate[i] > median_univ,
            rent_rate[i] > median_rent,
        )
        class_values[bid] = {PERIOD: float(_CLASS_INDEX[klass])}

    # --- B) Tourism-pressure mode (levels; provisional) ---
    score_tourism = np.nanmean(np.vstack([_z(vut_density), _z(alquiler_nivel)]), axis=0)

    by = lambda arr: {bid: arr[i] for i, bid in enumerate(ids)}  # noqa: E731

    out: list[Metric] = [
        Metric(
            id="transform_class",
            label="Trasformazione socioeconomica (classe)",
            unit="",
            kind="categorical",
            theme="transformation",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[PERIOD],
            values=class_values,
            categories=list(CLASS_LABELS),
        ),
        _diverging("transform_socio_score", "Score di trasformazione socioeconomica", "z", by(score_socio)),
        _diverging("transform_tourism_score", "Score di pressione turistica", "z", by(score_tourism)),
        _diverging("transform_univ_excess", "Eccesso crescita laureati (vs mediana)", "p.p./anno", by(univ_excess)),
        _diverging("transform_rent_excess", "Eccesso crescita affitto (vs mediana)", "%/anno", by(rent_excess)),
    ]
    return out
