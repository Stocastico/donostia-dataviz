"""The ``Metric`` value object — the pipeline's half of the data contract.

A dataset module builds ``Metric`` objects; ``build.py`` serializes them to
``metric_<id>.json`` and a combined ``metrics.json`` registry exactly as
``docs/DATA-CONTRACT.md`` specifies. ``validate`` enforces the contract
invariants so a malformed dataset fails the pipeline rather than the browser.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BuildContext:
    """What every dataset module needs to do its join + lookups."""

    raw_dir: Path
    barrio_ids: set[str]
    # KodAuzo code -> barrio_id, for datasets that carry the barrio code
    code_to_id: dict[str, str]


@dataclass
class Metric:
    """One choropleth metric over barrios and periods."""

    id: str
    label: str
    unit: str
    kind: str  # "sequential" | "diverging"
    theme: str
    source: str
    geo_grain: str  # "barrio"
    time_grain: str  # "year" | "month" | "snapshot"
    status: str = "live"  # "live" | "partial" | "planned"
    periods: list[str] = field(default_factory=list)
    # values[barrio_id][period] -> number | None
    values: dict[str, dict[str, float | None]] = field(default_factory=dict)

    def to_metric_file(self) -> dict:
        """The ``metric_<id>.json`` payload."""
        return {
            "id": self.id,
            "label": self.label,
            "unit": self.unit,
            "kind": self.kind,
            "theme": self.theme,
            "source": self.source,
            "periods": self.periods,
            "values": self.values,
        }

    def to_registry_entry(self) -> dict:
        """The lightweight descriptor for ``metrics.json``."""
        return {
            "id": self.id,
            "label": self.label,
            "unit": self.unit,
            "theme": self.theme,
            "kind": self.kind,
            "geoGrain": self.geo_grain,
            "timeGrain": self.time_grain,
            "source": self.source,
            "status": self.status,
            "periods": self.periods,
        }


def validate(metric: Metric, valid_barrio_ids: set[str]) -> None:
    """Raise ``ValueError`` if ``metric`` breaks a data-contract invariant."""
    if metric.kind not in ("sequential", "diverging"):
        raise ValueError(f"{metric.id}: bad kind {metric.kind!r}")
    if metric.status not in ("live", "partial", "planned"):
        raise ValueError(f"{metric.id}: bad status {metric.status!r}")

    # periods sorted ascending and unique
    if list(metric.periods) != sorted(set(metric.periods)):
        raise ValueError(f"{metric.id}: periods must be sorted and unique")
    period_set = set(metric.periods)

    for barrio_id, by_period in metric.values.items():
        if barrio_id not in valid_barrio_ids:
            raise ValueError(
                f"{metric.id}: barrio_id {barrio_id!r} not in reference geometry"
            )
        for period, value in by_period.items():
            if period not in period_set:
                raise ValueError(
                    f"{metric.id}: period {period!r} for {barrio_id!r} not in periods"
                )
            if value is None:
                continue
            # sequential metrics are counts/densities → never negative
            if metric.kind == "sequential" and value < 0:
                raise ValueError(
                    f"{metric.id}: negative value {value} for {barrio_id}/{period}"
                )
