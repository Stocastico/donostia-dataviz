"""TDD: labor income (wages) per barrio — the salary proxy for HU-7.

Source shape: Eustat PxWeb table PX_173402_crpf_rpf_rp22_2p, key =
[barrios, tipo de renta, periodo]. Only tipo 110 (renta del trabajo) is kept.
"""

import json
from pathlib import Path

from donostia_pipeline.datasets import renta_trabajo


def _row(bcode: str, tipo: str, periodo: str, value: str) -> dict:
    return {"key": [bcode, tipo, periodo], "values": [value]}


def test_income_labor_maps_eustat_codes_to_barrio_ids():
    payload = {"data": [
        _row("20069007", "110", "2016", "12672"),   # Centro → erdialdea
        _row("20069009", "110", "2016", "12317"),   # Gros
    ]}
    (m,) = renta_trabajo.income_labor_from_pxweb(payload)
    assert m.id == "income_labor"
    assert m.values["erdialdea"]["2016"] == 12672.0
    assert m.values["gros"]["2016"] == 12317.0


def test_income_labor_skips_municipio_total_and_other_tipos():
    payload = {"data": [
        _row("20069", "110", "2016", "13447"),      # municipio total → fuera
        _row("20069009", "100", "2016", "24000"),   # renta total → fuera
        _row("20069009", "110", "2016", "12317"),   # trabajo → dentro
    ]}
    (m,) = renta_trabajo.income_labor_from_pxweb(payload)
    assert list(m.values.keys()) == ["gros"]
    assert "2016" in m.values["gros"]


def test_income_labor_skips_suppressed_marker():
    payload = {"data": [
        _row("20069009", "110", "2016", ":"),       # confidencial
        _row("20069009", "110", "2017", "12800"),
    ]}
    (m,) = renta_trabajo.income_labor_from_pxweb(payload)
    assert "2016" not in m.values["gros"]
    assert m.values["gros"]["2017"] == 12800.0


def test_income_labor_periods_sorted_and_metadata():
    payload = {"data": [
        _row("20069009", "110", "2018", "13000"),
        _row("20069009", "110", "2016", "12317"),
    ]}
    (m,) = renta_trabajo.income_labor_from_pxweb(payload)
    assert m.periods == ["2016", "2018"]   # ordenado
    assert m.unit == "€"
    assert m.theme == "economy"
    assert m.geo_grain == "barrio"
    assert "renta del trabajo" in m.source.lower()


def test_empty_payload_returns_no_metric():
    assert renta_trabajo.income_labor_from_pxweb({"data": []}) == []


def test_build_reads_cached_json(tmp_path: Path):
    payload = {"data": [_row("20069009", "110", "2016", "12317")]}
    (tmp_path / renta_trabajo.RAW_FILE).write_text(json.dumps(payload),
                                                   encoding="utf-8")

    class _Ctx:
        raw_dir = tmp_path
    (m,) = renta_trabajo.build(_Ctx())
    assert m.values["gros"]["2016"] == 12317.0


def test_build_missing_file_returns_empty(tmp_path: Path):
    class _Ctx:
        raw_dir = tmp_path
    assert renta_trabajo.build(_Ctx()) == []
