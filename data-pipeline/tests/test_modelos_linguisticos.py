"""TDD: language-model schooling share, annual city indicator (REC-9).

Source shape: a Eustat PxWeb query response (table PX_040601_ceens_mun01,
municipio=20069 Donostia/San Sebastián) — one row per
(municipio, titularidad, nivel, modelo, características, periodo) key.
"""

import json
from pathlib import Path

from donostia_pipeline.datasets import modelos_linguisticos as ml


def _row(modelo: str, periodo: str, value: str) -> dict:
    return {"key": ["20069", "10", "100", modelo, "10", periodo], "values": [value]}


def test_pct_by_model_from_total_and_component():
    payload = {"data": [
        _row("10", "19831984", "1000"),  # total
        _row("20", "19831984", "700"),  # model A
        _row("30", "19831984", "200"),  # model B
        _row("40", "19831984", "100"),  # model D
    ]}
    by_id = {i.id: i for i in ml.pct_by_model_from_pxweb(payload)}
    assert by_id["pct_language_model_a"].values["1983/1984"]["value"] == 70.0
    assert by_id["pct_language_model_b"].values["1983/1984"]["value"] == 20.0
    assert by_id["pct_language_model_d"].values["1983/1984"]["value"] == 10.0


def test_suppressed_marker_is_skipped_not_zero():
    payload = {"data": [
        _row("10", "20122013", "1000"),
        _row("20", "20122013", "800"),
        _row("30", "20122013", "200"),
        _row("40", "20122013", ":"),  # PxWeb confidentiality marker
    ]}
    by_id = {i.id: i for i in ml.pct_by_model_from_pxweb(payload)}
    assert "2012/2013" not in by_id["pct_language_model_d"].values
    assert by_id["pct_language_model_a"].values["2012/2013"]["value"] == 80.0


def test_year_without_total_is_dropped():
    payload = {"data": [
        _row("20", "19901991", "500"),  # no total row for this period
    ]}
    by_id = {i.id: i for i in ml.pct_by_model_from_pxweb(payload)}
    assert by_id["pct_language_model_a"].values == {}


def test_indicators_have_expected_metadata():
    payload = {"data": [_row("10", "19831984", "1000"), _row("20", "19831984", "700")]}
    (ind,) = [i for i in ml.pct_by_model_from_pxweb(payload) if i.id == "pct_language_model_a"]
    assert ind.unit == "%"
    assert ind.theme == "demography"
    assert "Eustat" in ind.source


def test_build_indicators_reads_cached_json(tmp_path: Path):
    payload = {"data": [
        _row("10", "20202021", "1000"),
        _row("20", "20202021", "300"),
        _row("30", "20202021", "200"),
        _row("40", "20202021", "500"),
    ]}
    (tmp_path / ml.RAW_FILE).write_text(json.dumps(payload), encoding="utf-8")
    by_id = {i.id: i for i in ml.build_indicators(tmp_path)}
    assert by_id["pct_language_model_d"].values["2020/2021"]["value"] == 50.0
