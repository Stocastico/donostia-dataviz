"""TDD: retail/hospitality establishment share, annual city indicator (REC-7).

Source shape: a Eustat PxWeb query response (table PX_200163_cdirae_est04b,
municipio=20069 Donostia/San Sebastián, all CNAE-2009 codes, all years) —
one row per (municipio, CNAE-2009, periodo) key. CNAE 47xx = retail trade
("comercio al por menor"); 55xx/56xx = hospitality (accommodation + food and
beverage service) — the proxy for tourist-facing establishments.
"""

import json
from pathlib import Path

from donostia_pipeline.datasets import tejido_comercial as tc


def _row(cnae: str, periodo: str, value: str) -> dict:
    return {"key": ["20069", cnae, periodo], "values": [value]}


def test_shares_from_total_and_cnae_prefixes():
    payload = {"data": [
        _row("0", "2020", "1000"),   # total
        _row("4711", "2020", "80"),  # retail (47xx)
        _row("4720", "2020", "40"),  # retail (47xx)
        _row("5610", "2020", "60"),  # hospitality (56xx)
        _row("5510", "2020", "20"),  # hospitality (55xx)
        _row("6201", "2020", "10"),  # neither bucket — ignored
    ]}
    by_id = {i.id: i for i in tc.establishments_from_pxweb(payload)}
    assert by_id["total_establishments"].values["2020"]["value"] == 1000.0
    assert by_id["retail_establishments_share"].values["2020"]["value"] == 12.0  # 120/1000
    assert by_id["hospitality_establishments_share"].values["2020"]["value"] == 8.0  # 80/1000


def test_dash_marker_counts_as_zero_not_missing():
    payload = {"data": [
        _row("0", "2020", "1000"),
        _row("4711", "2020", "-"),  # Eustat's "-" == zero, not confidential
    ]}
    by_id = {i.id: i for i in tc.establishments_from_pxweb(payload)}
    assert by_id["retail_establishments_share"].values["2020"]["value"] == 0.0


def test_year_without_total_is_dropped():
    payload = {"data": [_row("4711", "2020", "80")]}  # no total row for this year
    by_id = {i.id: i for i in tc.establishments_from_pxweb(payload)}
    assert by_id["retail_establishments_share"].values == {}


def test_indicators_have_expected_metadata():
    payload = {"data": [_row("0", "2020", "1000")]}
    (ind,) = [i for i in tc.establishments_from_pxweb(payload) if i.id == "total_establishments"]
    assert ind.unit == "locali"
    assert ind.theme == "economy"
    assert "Eustat" in ind.source


def test_build_indicators_reads_cached_json(tmp_path: Path):
    payload = {"data": [
        _row("0", "2025", "18037"),
        _row("4711", "2025", "2277"),
    ]}
    (tmp_path / tc.RAW_FILE).write_text(json.dumps(payload), encoding="utf-8")
    by_id = {i.id: i for i in tc.build_indicators(tmp_path)}
    assert by_id["total_establishments"].values["2025"]["value"] == 18037.0


def test_build_indicators_missing_file_returns_empty(tmp_path: Path):
    assert tc.build_indicators(tmp_path) == []
