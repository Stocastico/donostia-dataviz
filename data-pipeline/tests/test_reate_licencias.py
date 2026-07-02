"""TDD: REC-12 — REATE tourist-license history, annual city indicators.

Source shape: the Open Data Euskadi REATE snapshots (``viviendas.json`` +
``habitaciones.json``) — one record per *currently registered* unit, with the
original registration date in ``FechainscripcionREATE`` (dd/mm/yyyy). The file
is a living registry: deregistered units (bajas) disappear, so every curve we
derive is of *surviving* licenses (see module docstring).
"""

import json
from pathlib import Path

from donostia_pipeline.datasets import reate_licencias


def _unit(fecha: str, municipio: str = "Donostia / San Sebastián",
          capacidad: str = "4") -> dict:
    return {
        "Municipio": municipio,
        "FechainscripcionREATE": fecha,
        "Capacidad": capacidad,
    }


def test_new_licenses_per_year_counts_vut_and_hut_together():
    viviendas = [_unit("05/09/2016"), _unit("01/01/2017"), _unit("31/12/2017")]
    habitaciones = [_unit("15/06/2017")]
    by_id = {i.id: i for i in reate_licencias.licenses_from_reate(viviendas, habitaciones)}
    new = by_id["vut_licenses_new"].values
    assert new["2016"]["value"] == 1.0
    assert new["2017"]["value"] == 3.0


def test_gap_years_are_zero_new_and_carry_forward_cumulative():
    viviendas = [_unit("01/01/2016"), _unit("01/01/2019"), _unit("02/02/2019")]
    by_id = {i.id: i for i in reate_licencias.licenses_from_reate(viviendas, [])}
    new = by_id["vut_licenses_new"].values
    cum = by_id["vut_licenses_cumulative"].values
    assert [new[y]["value"] for y in ("2016", "2017", "2018", "2019")] == [1.0, 0.0, 0.0, 2.0]
    assert [cum[y]["value"] for y in ("2016", "2017", "2018", "2019")] == [1.0, 1.0, 1.0, 3.0]


def test_cumulative_plazas_sums_capacity_skipping_unparseable():
    viviendas = [
        _unit("01/01/2016", capacidad="5"),
        _unit("01/01/2017", capacidad="3"),
        _unit("02/01/2017", capacidad="no consta"),
    ]
    by_id = {i.id: i for i in reate_licencias.licenses_from_reate(viviendas, [])}
    plazas = by_id["vut_plazas_cumulative"].values
    assert plazas["2016"]["value"] == 5.0
    assert plazas["2017"]["value"] == 8.0


def test_other_municipalities_are_filtered_out():
    viviendas = [_unit("01/01/2016"), _unit("01/01/2016", municipio="Bilbao")]
    by_id = {i.id: i for i in reate_licencias.licenses_from_reate(viviendas, [])}
    assert by_id["vut_licenses_new"].values["2016"]["value"] == 1.0


def test_missing_or_malformed_fecha_is_skipped():
    viviendas = [
        _unit("01/01/2016"),
        {"Municipio": "Donostia / San Sebastián", "Capacidad": "2"},  # sin fecha
        _unit("2016"),  # malformada
    ]
    by_id = {i.id: i for i in reate_licencias.licenses_from_reate(viviendas, [])}
    assert by_id["vut_licenses_new"].values["2016"]["value"] == 1.0
    assert len(by_id["vut_licenses_new"].values) == 1


def test_indicators_have_expected_metadata():
    by_id = {i.id: i for i in reate_licencias.licenses_from_reate([_unit("01/01/2016")], [])}
    assert set(by_id) == {"vut_licenses_new", "vut_licenses_cumulative", "vut_plazas_cumulative"}
    for ind in by_id.values():
        assert ind.theme == "tourism"
        assert "REATE" in ind.source
        assert "bajas" in ind.source  # the survivorship caveat travels with the data
    assert by_id["vut_licenses_new"].unit == "licenze"
    assert by_id["vut_plazas_cumulative"].unit == "posti letto"


def test_build_indicators_reads_cached_files(tmp_path: Path):
    (tmp_path / reate_licencias.RAW_VIVIENDAS).write_text(
        json.dumps([_unit("01/01/2016")]), encoding="utf-8")
    (tmp_path / reate_licencias.RAW_HABITACIONES).write_text(
        json.dumps([_unit("01/01/2016")]), encoding="utf-8")
    by_id = {i.id: i for i in reate_licencias.build_indicators(tmp_path)}
    assert by_id["vut_licenses_new"].values["2016"]["value"] == 2.0


def test_build_indicators_missing_files_return_empty(tmp_path: Path):
    assert reate_licencias.build_indicators(tmp_path) == []
    # one of the two present is still incomplete → also empty, never half a curve
    (tmp_path / reate_licencias.RAW_VIVIENDAS).write_text("[]", encoding="utf-8")
    assert reate_licencias.build_indicators(tmp_path) == []
