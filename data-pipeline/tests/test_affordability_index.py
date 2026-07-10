"""TDD: HU-7 affordability index (venta/alquiler/salario/IPC, city, 2016=100)."""

from donostia_pipeline.datasets import affordability_index as ai
from donostia_pipeline.model import Metric


def _metric(mid: str, values: dict) -> Metric:
    return Metric(id=mid, label=mid, unit="", kind="sequential", theme="housing",
                  source="", geo_grain="barrio", time_grain="year", values=values)


POP = {"a": {2016: 100, 2017: 100}, "b": {2016: 300, 2017: 300}}


def test_weighted_city_is_population_weighted():
    vals = {"a": {2016: 10.0}, "b": {2016: 20.0}}
    city = ai.weighted_city(vals, POP)
    # (10*100 + 20*300) / 400 = 17.5
    assert city[2016] == 17.5


def test_weighted_city_carries_forward_missing_population_year():
    # 2018 has no padrón → uses each barrio's latest (2017) weights, so the year
    # is not dropped (this is what lets the sale series reach 2026).
    vals = {"a": {2018: 10.0}, "b": {2018: 20.0}}
    city = ai.weighted_city(vals, POP)
    assert city[2018] == 17.5


def test_rebase_sets_base_year_to_100():
    idx = ai.rebase({2016: 200.0, 2020: 260.0}, 2016)
    assert idx[2016] == 100.0
    assert idx[2020] == 130.0


def test_rebase_empty_without_base_year():
    assert ai.rebase({2020: 260.0}, 2016) == {}


def test_build_payload_shape_and_growth():
    metrics = {
        "population": _metric("population", POP),
        "sale_price_eur_m2": _metric("sale_price_eur_m2",
                                     {"a": {"2016": 100.0, "2023": 130.0, "2026": 160.0},
                                      "b": {"2016": 100.0, "2023": 130.0, "2026": 160.0}}),
        "rent_eur_m2": _metric("rent_eur_m2",
                               {"a": {"2016": 10.0, "2023": 12.0}, "b": {"2016": 10.0, "2023": 12.0}}),
        "income_labor": _metric("income_labor",
                                {"a": {"2016": 100.0, "2023": 120.0}, "b": {"2016": 100.0, "2023": 120.0}}),
    }
    ipc = {2016: 100.0, 2023: 120.0, 2025: 127.0}
    payload = ai.build_payload(metrics, ipc, base_year=2016)

    ids = [s["id"] for s in payload["series"]]
    assert ids == ["sale", "rent", "salary", "ipc"]  # IPC last (reference)
    assert payload["baseYear"] == 2016 and payload["commonEnd"] == 2023
    sale = next(s for s in payload["series"] if s["id"] == "sale")
    assert sale["data"]["2016"] == 100.0 and sale["confidence"] == "proxy"
    assert sale["growth"] == {"common": 30.0, "full": 60.0}
    assert sale["lastYear"] == 2026
    ipc_s = next(s for s in payload["series"] if s["id"] == "ipc")
    assert ipc_s["dash"] is True
    assert ipc_s["growth"]["common"] == 20.0


def test_missing_metric_is_skipped():
    payload = ai.build_payload({"population": _metric("population", POP)}, {2016: 100.0})
    # only IPC survives (no barrio metrics present)
    assert [s["id"] for s in payload["series"]] == ["ipc"]
