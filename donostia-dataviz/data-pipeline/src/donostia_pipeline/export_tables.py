"""Tidy CSV export of every processed dataset.

Writes language-agnostic "long" tables so the data can be reused outside this
project (pandas, R, JS, …) without parsing the app-specific JSON. One row per
observation:

* ``metrics_long.csv`` — metric_id, label, theme, unit, barrio_id, barrio_name,
  period, value
* ``series_long.csv``  — series_id, label, theme, unit, year, month, value
* ``indicators_long.csv`` — id, label, theme, unit, year, value, source (annual
  city indicators, e.g. MICE)
* ``barrios.csv`` — barrio_id, name, kod_auzo

The functions returning rows are pure (easy to test); ``write_csv`` serializes
deterministically.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .model import Indicator, Metric, Series

METRIC_FIELDS = [
    "metric_id", "label", "theme", "unit",
    "barrio_id", "barrio_name", "period", "value",
]
SERIES_FIELDS = ["series_id", "label", "theme", "unit", "year", "month", "value"]
INDICATOR_FIELDS = ["id", "label", "theme", "unit", "year", "value", "source"]
BARRIO_FIELDS = ["barrio_id", "name", "kod_auzo"]


def metric_long_rows(metrics: Iterable[Metric], barrio_names: dict[str, str]) -> list[dict]:
    rows = []
    for metric in metrics:
        for barrio_id, by_period in metric.values.items():
            for period, value in by_period.items():
                rows.append({
                    "metric_id": metric.id,
                    "label": metric.label,
                    "theme": metric.theme,
                    "unit": metric.unit,
                    "barrio_id": barrio_id,
                    "barrio_name": barrio_names.get(barrio_id, ""),
                    "period": period,
                    "value": value,
                })
    rows.sort(key=lambda r: (r["metric_id"], r["barrio_id"], r["period"]))
    return rows


def series_long_rows(series_list: Iterable[Series]) -> list[dict]:
    rows = []
    for series in series_list:
        for year, by_month in series.values.items():
            for month, value in by_month.items():
                rows.append({
                    "series_id": series.id,
                    "label": series.label,
                    "theme": series.theme,
                    "unit": series.unit,
                    "year": year,
                    "month": month,
                    "value": value,
                })
    rows.sort(key=lambda r: (r["series_id"], r["year"], int(r["month"])))
    return rows


def indicator_long_rows(indicators: Iterable[Indicator]) -> list[dict]:
    rows = []
    for ind in indicators:
        for year, point in ind.values.items():
            rows.append({
                "id": ind.id,
                "label": ind.label,
                "theme": ind.theme,
                "unit": ind.unit,
                "year": year,
                "value": point["value"],
                "source": point.get("source", ind.source),
            })
    rows.sort(key=lambda r: (r["id"], r["year"]))
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
