"""TDD: unemployment rate, annual city indicator (REC-5).

Source shape: a Eustat PxWeb query response (table PX_050403_cpra_tab19,
capital=Donostia/San Sebastián, tasa=paro, trimestre=promedio anual) — one
row per (tasa, capital, sexo, trimestre, periodo) key.
"""

import json
from pathlib import Path

from donostia_pipeline.datasets import paro


def _row(sexo: str, periodo: str, value: str) -> dict:
    return {"key": ["30", "30", sexo, "10", periodo], "values": [value]}


def test_rate_by_sex_from_pxweb():
    payload = {"data": [
        _row("10", "2015", "12.0"),
        _row("20", "2015", "10.5"),
        _row("30", "2015", "13.4"),
    ]}
    by_id = {i.id: i for i in paro.unemployment_rate_from_pxweb(payload)}
    assert by_id["unemployment_rate"].values["2015"]["value"] == 12.0
    assert by_id["unemployment_rate_men"].values["2015"]["value"] == 10.5
    assert by_id["unemployment_rate_women"].values["2015"]["value"] == 13.4


def test_suppressed_marker_is_skipped_not_zero():
    payload = {"data": [
        _row("10", "2026", ":"),  # PxWeb confidentiality/not-yet-available marker
        _row("10", "2025", "5.0"),
    ]}
    (ind,) = [i for i in paro.unemployment_rate_from_pxweb(payload) if i.id == "unemployment_rate"]
    assert "2026" not in ind.values
    assert ind.values["2025"]["value"] == 5.0


def test_indicators_have_expected_metadata():
    payload = {"data": [_row("10", "2015", "12.0")]}
    (ind,) = [i for i in paro.unemployment_rate_from_pxweb(payload) if i.id == "unemployment_rate"]
    assert ind.unit == "%"
    assert ind.theme == "economy"
    assert "Eustat" in ind.source


def test_build_indicators_reads_cached_json(tmp_path: Path):
    payload = {"data": [_row("10", "2025", "5.0"), _row("20", "2025", "4.2")]}
    (tmp_path / paro.RAW_FILE).write_text(json.dumps(payload), encoding="utf-8")
    by_id = {i.id: i for i in paro.build_indicators(tmp_path)}
    assert by_id["unemployment_rate"].values["2025"]["value"] == 5.0
    assert by_id["unemployment_rate_men"].values["2025"]["value"] == 4.2


def test_build_indicators_missing_file_returns_empty(tmp_path: Path):
    assert paro.build_indicators(tmp_path) == []
