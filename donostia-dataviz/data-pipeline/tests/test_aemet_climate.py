"""TDD: monthly temperature + precipitation series, AEMET Igeldo (1024E)."""

import json

from conftest import write_csv

from donostia_pipeline.datasets import aemet_climate

# Raw shape = list of AEMET monthly records. fecha "YYYY-M", M=13 is the annual
# summary (must be excluded); values are strings, sometimes comma-decimal/empty.
RAW = json.dumps(
    [
        {"fecha": "2019-1", "tm_mes": "9.4", "p_mes": "100.0", "ta_max": "15.0", "nt_30": "0"},
        {"fecha": "2019-7", "tm_mes": "20,5", "p_mes": "30.0", "ta_max": "38.3(18)", "nt_30": "3"},
        {"fecha": "2019-13", "tm_mes": "14.0", "p_mes": "1200.0"},  # annual → drop
        {"fecha": "2020-1", "tm_mes": "", "p_mes": "80.0", "ta_max": "", "nt_30": ""},
    ]
)


def _build(make_ctx):
    ctx = make_ctx({})
    write_csv(ctx.raw_dir, "aemet_igeldo.json", RAW)
    return {s.id: s for s in aemet_climate.build_series(ctx)}


def test_temperature_series_parses_dot_and_comma(make_ctx):
    t = _build(make_ctx)["temp_avg"]
    assert t.unit == "°C"
    assert t.theme == "climate"
    assert t.values["2019"]["1"] == 9.4
    assert t.values["2019"]["7"] == 20.5  # "20,5" parsed


def test_annual_row_excluded(make_ctx):
    t = _build(make_ctx)["temp_avg"]
    assert "13" not in t.values["2019"]


def test_missing_value_is_omitted(make_ctx):
    s = _build(make_ctx)
    # 2020 January temp is empty → absent; but precip present → 2020 in precip.
    assert "1" not in s["temp_avg"].values.get("2020", {})
    assert s["precip"].values["2020"]["1"] == 80.0


def test_both_series_share_year_axis(make_ctx):
    s = _build(make_ctx)
    assert s["temp_avg"].years == ["2019", "2020"]
    assert s["precip"].unit == "mm"


def test_temp_max_strips_the_day_in_parentheses(make_ctx):
    tmax = _build(make_ctx)["temp_max"]
    assert tmax.unit == "°C"
    assert tmax.theme == "climate"
    assert tmax.values["2019"]["1"] == 15.0
    assert tmax.values["2019"]["7"] == 38.3  # "38.3(18)" → 38.3


def test_hot_days_counts_days_over_30(make_ctx):
    hot = _build(make_ctx)["hot_days_30"]
    assert hot.unit == "giorni"
    assert hot.values["2019"]["1"] == 0.0
    assert hot.values["2019"]["7"] == 3.0
