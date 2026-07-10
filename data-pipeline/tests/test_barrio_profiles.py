"""TDD: derived barrio-typology categorical metric (datasets.barrio_profiles).

The clustering is deterministic, so beyond the helper unit tests we lock the
*documented* assignment (ANALISIS-SPRINT-A.md §3) against the committed base
metrics — if a data update shifts a barrio's profile, this test flags it.
"""

import json
from pathlib import Path

from donostia_pipeline.datasets import barrio_profiles as bp
from donostia_pipeline.model import Metric, validate

DATA_DIR = Path(__file__).resolve().parents[2] / "web" / "src" / "data"


def _name(income, university, vut, rent):
    return bp._name({
        "income_total": income, "pct_university": university,
        "vut_density": vut, "rent_eur_m2": rent,
    })


def test_centroid_naming_rules():
    assert _name(1.0, 1.0, 1.0, 1.0) == "Central turístico, renta alta"
    assert _name(1.0, 1.0, 0.0, -1.0) == "Residencial acomodado"
    assert _name(-1.0, -1.0, -0.5, -0.5) == "Popular / en tensión"
    assert _name(0.0, 0.0, 0.0, 0.0) == "Transicional / mixto"


def test_latest_picks_max_period_skipping_nulls():
    m = Metric(id="x", label="x", unit="x", kind="sequential", theme="t", source="s",
               geo_grain="barrio", time_grain="year", periods=["2020", "2021", "2022"],
               values={"gros": {"2020": 1.0, "2021": 2.0, "2022": None}})
    assert bp._latest(m, "gros") == 2.0      # 2022 is null → falls back to 2021
    assert bp._latest(m, "absent") is None


def test_missing_base_metrics_yield_nothing():
    assert bp.build_from_metrics({}) == []


def _load(metric_id):
    d = json.loads((DATA_DIR / f"metric_{metric_id}.json").read_text(encoding="utf-8"))
    return Metric(id=d["id"], label=d["label"], unit=d["unit"], kind=d["kind"],
                  theme=d["theme"], source=d["source"], geo_grain="barrio",
                  time_grain="year", periods=d["periods"], values=d["values"])


def test_documented_assignment_is_reproduced():
    metrics = {v: _load(v) for v in bp.CLUSTER_VARS}
    (m,) = bp.build_from_metrics(metrics)

    # categorical metric, valid against the contract
    valid_ids = {f["properties"]["barrio_id"]
                 for f in json.loads((DATA_DIR / "barrios.geojson").read_text("utf-8"))["features"]}
    validate(m, valid_ids)
    assert m.kind == "categorical"
    assert m.categories == bp.PROFILES

    groups: dict[str, list[str]] = {c: [] for c in m.categories}
    for bid, by_period in m.values.items():
        groups[m.categories[int(by_period["perfil"])]].append(bid)

    assert sorted(groups["Central turístico, renta alta"]) == ["erdialdea", "gros"]
    assert sorted(groups["Residencial acomodado"]) == ["aiete", "antigua", "ibaeta"]
    assert sorted(groups["Transicional / mixto"]) == ["amaraberri", "ategorrieta-ulia", "egia"]
    assert sorted(groups["Popular / en tensión"]) == [
        "altza", "intxaurrondo", "loiola", "martutene", "mirakruz-bidebieta",
    ]
    assert len(m.values) == 13  # the barrios carrying all four variables


def test_clustering_is_deterministic():
    metrics = {v: _load(v) for v in bp.CLUSTER_VARS}
    (a,) = bp.build_from_metrics(metrics)
    (b,) = bp.build_from_metrics(metrics)
    assert a.values == b.values
