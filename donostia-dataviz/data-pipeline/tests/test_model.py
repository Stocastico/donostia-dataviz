"""Unit tests for the Metric contract validator."""

import pytest

from donostia_pipeline.model import Metric, validate

IDS = {"gros", "egia"}


def _metric(**kw) -> Metric:
    base = dict(
        id="m",
        label="M",
        unit="x",
        kind="sequential",
        theme="t",
        source="s",
        geo_grain="barrio",
        time_grain="year",
        periods=["2000", "2001"],
        values={"gros": {"2000": 1.0, "2001": 2.0}},
    )
    base.update(kw)
    return Metric(**base)


def test_valid_metric_passes():
    validate(_metric(), IDS)


def test_unknown_barrio_rejected():
    with pytest.raises(ValueError, match="not in reference geometry"):
        validate(_metric(values={"nowhere": {"2000": 1.0}}), IDS)


def test_unknown_period_rejected():
    with pytest.raises(ValueError, match="not in periods"):
        validate(_metric(values={"gros": {"1999": 1.0}}), IDS)


def test_unsorted_periods_rejected():
    with pytest.raises(ValueError, match="sorted and unique"):
        validate(_metric(periods=["2001", "2000"]), IDS)


def test_negative_sequential_rejected():
    with pytest.raises(ValueError, match="negative"):
        validate(_metric(values={"gros": {"2000": -1.0}}), IDS)


def test_diverging_allows_negative():
    validate(_metric(kind="diverging", values={"gros": {"2000": -1.0}}), IDS)
