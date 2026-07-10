"""TDD: Urban Transformation Index derived metrics (datasets.transformation).

Beyond the helper unit tests, we lock the *documented* results
(INDICE-TRANSFORMACION.md) against the committed base metrics — if a data update
shifts a barrio's class or score, this test flags it.
"""

import json
import math
from pathlib import Path

import numpy as np

from donostia_pipeline.datasets import transformation as tr
from donostia_pipeline.model import Metric, validate

DATA_DIR = Path(__file__).resolve().parents[2] / "web" / "src" / "data"


def test_annual_rate_pp_and_level():
    pts = {2016: 10.0, 2017: 11.0, 2018: 12.0, 2019: 13.0}  # +1/yr, mean 11.5
    assert math.isclose(tr._annual_rate(pts, "pp"), 1.0)
    assert math.isclose(tr._annual_rate(pts, "level"), 100.0 * 1.0 / 11.5)
    assert math.isnan(tr._annual_rate({2016: 1.0, 2017: 2.0}, "pp"))  # <3 points


def test_z_uses_sample_std_and_ignores_nan():
    z = tr._z(np.array([1.0, 2.0, 3.0, np.nan]))
    # sample std (ddof=1) of [1,2,3] is 1.0, mean 2.0 → centred z
    assert math.isclose(z[0], -1.0) and math.isclose(z[2], 1.0)
    assert math.isnan(z[3])


def test_classify_rules():
    assert tr._classify(False, True, True) == "consolidado / no susceptible"
    assert tr._classify(True, True, True) == "en transformación"
    assert tr._classify(True, True, False) == "transformación incipiente"
    assert tr._classify(True, False, False) == "estable"


def test_missing_base_metrics_yield_nothing():
    assert tr.build_from_metrics({}) == []


def _load(metric_id):
    d = json.loads((DATA_DIR / f"metric_{metric_id}.json").read_text(encoding="utf-8"))
    return Metric(id=d["id"], label=d["label"], unit=d["unit"], kind=d["kind"],
                  theme=d["theme"], source=d["source"], geo_grain="barrio",
                  time_grain="year", periods=d["periods"], values=d["values"])


def _build_real():
    metrics = {v: _load(v) for v in (tr.INCOME, tr.RENT, tr.UNIV, tr.VUT, tr.AIRBNB)}
    return {m.id: m for m in tr.build_from_metrics(metrics)}


def test_documented_classes_and_scores():
    out = _build_real()
    valid_ids = {f["properties"]["barrio_id"]
                 for f in json.loads((DATA_DIR / "barrios.geojson").read_text("utf-8"))["features"]}

    cls = out["transform_class"]
    validate(cls, valid_ids)
    assert cls.kind == "categorical"
    assert cls.categories == tr.CLASS_LABELS

    def klass(bid):
        return cls.categories[int(cls.values[bid][tr.PERIOD])]

    assert klass("loiola") == "En transformación"
    assert klass("egia") == "Transformación incipiente"
    assert klass("erdialdea") == "Consolidado / no susceptible"
    assert klass("martutene") == "Estable / sin transformación"

    socio = out["transform_socio_score"]
    validate(socio, valid_ids)
    assert socio.kind == "diverging"
    assert socio.values["loiola"][tr.PERIOD] == 1.02
    assert socio.values["egia"][tr.PERIOD] == 0.23

    tour = out["transform_tourism_score"]
    # Consolidated with Airbnb density (REC-4): the two touristic centres lead.
    assert tour.values["erdialdea"][tr.PERIOD] == 2.40
    assert tour.values["gros"][tr.PERIOD] == 1.37
    # diverging scores carry negatives (e.g. Martutene)
    assert tour.values["martutene"][tr.PERIOD] < 0
    # "expensive but not touristic": Aiete (high rent, low Airbnb) now scores near
    # zero, no longer a false positive of the rent-only signal.
    assert tour.values["aiete"][tr.PERIOD] < 0.2
    # all transform metrics share the same classifiable set (the documented N=13)
    assert len(tour.values) == 13 == len(out["transform_socio_score"].values) == len(cls.values)


def test_components_are_diverging_and_centered():
    out = _build_real()
    for mid in ("transform_univ_excess", "transform_rent_excess"):
        m = out[mid]
        assert m.kind == "diverging"
        vals = [v[tr.PERIOD] for v in m.values.values()]
        assert min(vals) < 0 < max(vals)  # excess over median straddles zero
