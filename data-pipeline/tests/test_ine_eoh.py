"""TDD: monthly overnight-stays series for San Sebastián (datasets.ine_eoh).

The pipeline fetches two INE wstempus series — pernoctaciones of residents in
Spain (EOT2721) and abroad (EOT2722) — and sums them per (year, month) into a
single total series for the seasonality heatmap.
"""

import json

from conftest import write_csv

from donostia_pipeline.datasets import ine_eoh

# Minimal INE DATOS_SERIE shape: Data is a list of {Anyo, FK_Periodo, Valor}.
ESP = json.dumps(
    {
        "COD": "EOT2721",
        "Data": [
            {"Anyo": 2020, "FK_Periodo": 1, "Valor": 100.0},
            {"Anyo": 2020, "FK_Periodo": 2, "Valor": 200.0},
            {"Anyo": 2021, "FK_Periodo": 1, "Valor": 150.0},
            {"Anyo": 2021, "FK_Periodo": 2, "Valor": 300.0},
        ],
    }
)
EXT = json.dumps(
    {
        "COD": "EOT2722",
        "Data": [
            {"Anyo": 2020, "FK_Periodo": 1, "Valor": 50.0},
            {"Anyo": 2020, "FK_Periodo": 2, "Valor": 60.0},
            {"Anyo": 2021, "FK_Periodo": 1, "Valor": 25.0},
            # 2021 month 2 only present in ESP
        ],
    }
)


def _build(make_ctx):
    ctx = make_ctx({})
    write_csv(ctx.raw_dir, "ine_pernoct_esp.json", ESP)
    write_csv(ctx.raw_dir, "ine_pernoct_ext.json", EXT)
    return {s.id: s for s in ine_eoh.build_series(ctx)}


def test_total_overnight_stays_sums_both_residences(make_ctx):
    s = _build(make_ctx)["overnight_stays"]
    assert s.years == ["2020", "2021"]
    assert s.values["2020"]["1"] == 150.0  # 100 + 50
    assert s.values["2020"]["2"] == 260.0  # 200 + 60
    assert s.values["2021"]["1"] == 175.0  # 150 + 25


def test_month_present_in_one_source_only_still_counts(make_ctx):
    s = _build(make_ctx)["overnight_stays"]
    assert s.values["2021"]["2"] == 300.0  # ESP only


def test_metadata(make_ctx):
    s = _build(make_ctx)["overnight_stays"]
    assert s.unit == "pernottamenti"
    assert s.kind == "month-year"
    assert s.theme == "tourism"
