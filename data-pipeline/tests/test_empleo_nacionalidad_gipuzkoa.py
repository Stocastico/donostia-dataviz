"""TDD: REC-21 — unemployment by nationality + R&D-personnel intensity, Gipuzkoa.

Source shapes: PxWeb query responses.
- tasas nacionalidad (cpra_tab17): key = [tasa, territorio, nacionalidad, trimestre, periodo]
- personal I+D (cid_res08c): key = [territorio, sector, ocupación, sexo, periodo]
- población ocupada (cpra_tab04): key = [actividad, territorio, sexo, trimestre, periodo]
"""

import json
from pathlib import Path

from donostia_pipeline.datasets import empleo_nacionalidad_gipuzkoa as mod


def _tasa(tasa: str, nacionalidad: str, periodo: str, value: str) -> dict:
    return {"key": [tasa, "20", nacionalidad, "10", periodo], "values": [value]}


def _personal(periodo: str, value: str, sector: str = "00", ocupacion: str = "100") -> dict:
    return {"key": ["20", sector, ocupacion, "10", periodo], "values": [value]}


def _ocupados(periodo: str, value: str, territorio: str = "20") -> dict:
    return {"key": ["30", territorio, "10", "10", periodo], "values": [value]}


def test_paro_por_nacionalidad_separa_espanola_y_extranjera():
    payload = {"data": [
        _tasa("30", "20", "2024", "4.3"),
        _tasa("30", "30", "2024", "9.4"),
        _tasa("10", "20", "2024", "56.0"),  # tasa de actividad, debe ignorarse
    ]}
    by_id = {i.id: i for i in mod._paro_por_nacionalidad(payload)}
    assert by_id["unemployment_rate_spanish_gipuzkoa"].values["2024"]["value"] == 4.3
    assert by_id["unemployment_rate_foreign_gipuzkoa"].values["2024"]["value"] == 9.4


def test_paro_ignora_marcador_no_disponible():
    payload = {"data": [_tasa("30", "30", "2026", ":")]}
    by_id = {i.id: i for i in mod._paro_por_nacionalidad(payload)}
    assert "2026" not in by_id["unemployment_rate_foreign_gipuzkoa"].values


def test_randd_ratio_normaliza_por_mil_ocupados():
    id_payload = {"data": [_personal("2024", "10383")]}
    ocupados_payload = {"data": [_ocupados("2024", "335.3")]}  # tab04 en miles
    inds = mod._randd_ratio(id_payload, ocupados_payload)
    assert len(inds) == 1
    assert inds[0].id == "randd_personnel_per_1000_employed_gipuzkoa"
    assert round(inds[0].values["2024"]["value"], 1) == 31.0


def test_randd_ratio_filtra_sector_y_ocupacion_total():
    id_payload = {"data": [
        _personal("2024", "10383", sector="00", ocupacion="100"),  # total/total -> usar
        _personal("2024", "7050", sector="00", ocupacion="200"),   # investigadores -> ignorar
        _personal("2024", "9999", sector="10", ocupacion="100"),   # solo empresas -> ignorar
    ]}
    ocupados_payload = {"data": [_ocupados("2024", "335.3")]}
    inds = mod._randd_ratio(id_payload, ocupados_payload)
    assert round(inds[0].values["2024"]["value"], 1) == 31.0


def test_randd_ratio_solo_anios_solapados():
    id_payload = {"data": [_personal("2001", "3892.8"), _personal("2024", "10383")]}
    ocupados_payload = {"data": [_ocupados("2024", "335.3")]}  # sin 2001
    inds = mod._randd_ratio(id_payload, ocupados_payload)
    assert "2001" not in inds[0].values
    assert "2024" in inds[0].values


def test_randd_ratio_ignora_otro_territorio():
    id_payload = {"data": [_personal("2024", "10383")]}
    ocupados_payload = {"data": [_ocupados("2024", "999", territorio="00")]}  # CAE, no Gipuzkoa
    inds = mod._randd_ratio(id_payload, ocupados_payload)
    assert inds == []  # sin denominador de Gipuzkoa, ningún año calculable


def test_build_indicators_tolera_ficheros_ausentes(tmp_path: Path):
    assert mod.build_indicators(tmp_path) == []


def test_build_indicators_lee_ficheros_cacheados(tmp_path: Path):
    (tmp_path / mod.RAW_TASAS).write_text(
        json.dumps({"data": [_tasa("30", "30", "2024", "9.4")]}), encoding="utf-8")
    (tmp_path / mod.RAW_ID_PERSONAL).write_text(
        json.dumps({"data": [_personal("2024", "10383")]}), encoding="utf-8")
    (tmp_path / mod.RAW_OCUPADOS).write_text(
        json.dumps({"data": [_ocupados("2024", "335.3")]}), encoding="utf-8")
    by_id = {i.id: i for i in mod.build_indicators(tmp_path)}
    assert by_id["unemployment_rate_foreign_gipuzkoa"].values["2024"]["value"] == 9.4
    assert round(by_id["randd_personnel_per_1000_employed_gipuzkoa"].values["2024"]["value"], 1) == 31.0
