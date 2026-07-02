"""Derived metrics: per-barrio *velocity of change* (annualized rates).

Surfaces the Sprint A "velocità di cambiamento" analysis (AN-2,
``docs/ANALISIS-SPRINT-A.md`` §2) as choropleth metrics: instead of a barrio's
*level* on a metric, its *annualized rate of change* over the recent comparable
window (``WINDOW_START``→latest). Reads only metrics already in the store, so it
touches no raw files — same pattern as ``housing_tension``.

Two flavours, matching the analysis:

* **level** metrics (income, rent, population) → **%/year**, the regression
  slope as a share of the window mean (a +3 means "grew ~3% per year").
* **pp** metrics (% university, % foreign) → **percentage points/year**, the raw
  slope (these are already percentages, so a relative % would double-count).

Each output is a *diverging snapshot* metric (one value per barrio, centred at
zero → blue = declining, red = growing), so it plugs straight into the existing
choropleth/legend without a new view.

Caveat (documented, not hidden): the rate is a simple least-squares slope over
the window; with few points and non-homogeneous end years between metrics it is a
*descriptive* trajectory, not a forecast. Peripheral barrios with sparse series
(e.g. new residential growth) can show large population rates — read alongside
the analysis note.
"""

from __future__ import annotations

from ..model import Metric

WINDOW_START = 2016  # recent window comparable across metrics (see AN-2)

# base metric id -> (kind, label, unit). "level" → %/year; "pp" → points/year.
TREND_SPECS: dict[str, tuple[str, str, str]] = {
    "income_total": ("level", "Velocità reddito", "%/anno"),
    "rent_eur_m2": ("level", "Velocità affitto", "%/anno"),
    "population": ("level", "Velocità popolazione", "%/anno"),
    "pct_university": ("pp", "Velocità laureati", "p.p./anno"),
    "pct_foreign": ("pp", "Velocità stranieri", "p.p./anno"),
}
MIN_POINTS = 3  # need at least 3 years to fit a defensible slope


def _slope(xs: list[float], ys: list[float]) -> float:
    """Ordinary-least-squares slope of ``ys`` on ``xs`` (pure Python)."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


def _annualized_rate(years: list[int], vals: list[float], kind: str) -> float | None:
    """Annualized rate over the window: %/year (level) or points/year (pp)."""
    if len(years) < MIN_POINTS:
        return None
    xs = [float(y) for y in years]
    slope = _slope(xs, vals)
    if kind == "pp":
        return round(slope, 3)
    mean = sum(vals) / len(vals)
    if mean == 0:
        return None
    return round(100.0 * slope / mean, 3)


def _velocity_for(base: Metric, kind: str, label: str, unit: str) -> Metric | None:
    """Build one velocity metric from a base metric, or None if no barrio qualifies."""
    values: dict[str, dict[str, float | None]] = {}
    end_year = WINDOW_START
    for barrio_id, by_period in base.values.items():
        points = sorted(
            (int(p), v)
            for p, v in by_period.items()
            if v is not None and p.isdigit() and int(p) >= WINDOW_START
        )
        if len(points) < MIN_POINTS:
            continue
        years = [y for y, _ in points]
        rate = _annualized_rate(years, [v for _, v in points], kind)
        if rate is None:
            continue
        end_year = max(end_year, years[-1])
        # period stamped after we know the window's end; filled in below
        values[barrio_id] = {"_rate": rate}

    if not values:
        return None

    period = f"{WINDOW_START}–{end_year}"  # e.g. "2016–2024"
    values = {bid: {period: v["_rate"]} for bid, v in values.items()}

    return Metric(
        id=f"velocity_{base.id}",
        label=label,
        unit=unit,
        kind="diverging",
        theme="change",
        source=f"Derivata — tasso annualizzato {period} di «{base.label}» (regressione OLS)",
        geo_grain="barrio",
        time_grain="snapshot",
        periods=[period],
        values=values,
    )


def build_from_metrics(metrics: dict[str, Metric]) -> list[Metric]:
    out: list[Metric] = []
    for base_id, (kind, label, unit) in TREND_SPECS.items():
        base = metrics.get(base_id)
        if base is None:
            continue
        m = _velocity_for(base, kind, label, unit)
        if m is not None:
            out.append(m)
    return out
