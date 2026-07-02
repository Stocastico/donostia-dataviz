"""TDD: confidence provenance stamping (provenance) + committed coverage."""

import json
from pathlib import Path

from donostia_pipeline import provenance
from donostia_pipeline.model import Metric

DATA_DIR = Path(__file__).resolve().parents[2] / "web" / "src" / "data"


def _metric(mid):
    return Metric(id=mid, label=mid, unit="x", kind="sequential", theme="t", source="s",
                  geo_grain="barrio", time_grain="year", periods=["2020"], values={})


def test_apply_sets_known_tiers():
    ms = [_metric("rent_eur_m2"), _metric("housing_tension"), _metric("noise_night_pct55")]
    provenance.apply(ms)
    tiers = {m.id: m.confidence for m in ms}
    assert tiers == {
        "rent_eur_m2": "observed",
        "housing_tension": "derived",
        "noise_night_pct55": "proxy",
    }
    # housing_tension carries its m² assumption
    ht = next(m for m in ms if m.id == "housing_tension")
    assert any("30 m²" in a for a in ht.assumptions)


def test_velocity_metrics_are_derived():
    m = _metric("velocity_rent_eur_m2")
    provenance.apply([m])
    assert m.confidence == "derived"
    assert m.assumptions  # has the OLS note


def test_unknown_metric_defaults_to_observed_no_assumptions():
    m = _metric("brand_new_metric")
    provenance.apply([m])
    assert m.confidence == "observed"
    assert m.assumptions == []


def test_every_classified_id_is_a_valid_tier():
    for mid, (tier, assumptions) in provenance.CONFIDENCE.items():
        assert tier in ("observed", "derived", "proxy"), mid
        assert isinstance(assumptions, list)


def test_committed_metrics_all_carry_confidence():
    """Every live metric file should have a valid confidence tier (regenerated)."""
    for path in DATA_DIR.glob("metric_*.json"):
        d = json.loads(path.read_text(encoding="utf-8"))
        assert d.get("confidence") in ("observed", "derived", "proxy"), path.name
