"""Tests de AN-21 — perfil migratorio y de empleo.

Piezas: clasificación país -> región, agregación ciudad/barrio a partir del
CSV de origen, y el parser JSON-stat genérico de PxWeb (mismo formato que ya
usa `movilidad_laboral.py` en el pipeline, aquí generalizado a N dimensiones).
"""
import json

import pandas as pd
import pytest

import perfil_extranjeros_empleo as pe


# --------------------------------------------------- país -> región ----
def test_region_of_espana_es_caso_especial():
    assert pe.region_of("ESPAÑA") == "España"


def test_region_of_paises_conocidos():
    assert pe.region_of("Honduras") == "América Latina"
    assert pe.region_of("marruecos") == "Norte de África"
    assert pe.region_of("ALEMANIA") == "Europa occidental"


def test_region_of_pais_no_clasificado_no_se_descarta():
    assert pe.region_of("NARNIA") == "Otros/no clasificado"


# ------------------------------------------------- agregación ciudad ----
def _origen_df() -> pd.DataFrame:
    rows = [
        {"year": 2025, "barrio_id": "1", "barrio_name": "Aiete", "country": "ESPAÑA",
         "region": "España", "people": 900},
        {"year": 2025, "barrio_id": "1", "barrio_name": "Aiete", "country": "HONDURAS",
         "region": "América Latina", "people": 60},
        {"year": 2025, "barrio_id": "1", "barrio_name": "Aiete", "country": "MARRUECOS",
         "region": "Norte de África", "people": 40},
        {"year": 2025, "barrio_id": "2", "barrio_name": "Altza", "country": "ESPAÑA",
         "region": "España", "people": 500},
        {"year": 2025, "barrio_id": "2", "barrio_name": "Altza", "country": "HONDURAS",
         "region": "América Latina", "people": 100},
    ]
    return pd.DataFrame(rows)


def test_city_by_region_pct_sobre_poblacion_y_extranjeros():
    out = pe.city_by_region(_origen_df()).set_index("region")
    # ciudad: 1900 total, 300 extranjeros (160 AL + 40 NA... espera: 60+100=160 AL, 40 NA)
    assert out.loc["América Latina", "people"] == 160
    assert out.loc["América Latina", "pct_of_population"] == pytest.approx(
        160 / 1600 * 100, abs=0.01)
    assert out.loc["América Latina", "pct_of_foreign"] == pytest.approx(
        160 / 200 * 100, abs=0.01)
    assert out.loc["España", "pct_of_foreign"] is None


def test_barrio_by_region_latest_pct_del_barrio():
    out = pe.barrio_by_region_latest(_origen_df(), year=2025)
    altza_al = out[(out.barrio_id == "2") & (out.region == "América Latina")].iloc[0]
    assert altza_al.pct_of_barrio == pytest.approx(100 / 600 * 100, abs=0.01)


def test_top_countries_compara_con_hace_10_anios():
    df = pd.concat([
        _origen_df(),
        _origen_df().assign(year=2015, people=lambda d: d.people // 2),
    ])
    top = pe.top_countries(df, year=2025, n=5)
    honduras = top[top.country == "HONDURAS"].iloc[0]
    assert honduras.people_latest == 160  # 60 (Aiete) + 100 (Altza)
    assert honduras.people_2015 == 80     # mitad, por construcción del fixture


# --------------------------------------------------------- pxweb ----
def _write_pxweb(tmp_path, rows):
    payload = {"data": [{"key": k, "values": v} for k, v in rows]}
    p = tmp_path / "fixture.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_pxweb_frame_ignora_dato_no_disponible(tmp_path):
    path = _write_pxweb(tmp_path, [
        (["20", "10", "2024"], ["123"]),
        (["20", "20", "2024"], [":"]),  # PxWeb: dato no disponible
    ])
    df = pe._pxweb_frame(path, ["territorio", "nac_code", "year"])
    assert len(df) == 1
    assert df.iloc[0]["value"] == 123.0


def test_load_tasas_nacionalidad_mapea_codigos(tmp_path):
    path = _write_pxweb(tmp_path, [
        (["10", "20", "30", "10", "2024"], ["65.5"]),
    ])
    df = pe.load_tasas_nacionalidad(path)
    row = df.iloc[0]
    assert row.tasa == "Actividad"
    assert row.nacionalidad == "Extranjera"
    assert row.year == 2024
    assert row.value == pytest.approx(65.5)


def test_load_establecimientos_sector_filtra_solo_estrato_total(tmp_path):
    path = _write_pxweb(tmp_path, [
        (["20069", "04", "0", "00", "2024"], ["100"]),   # estrato total
        (["20069", "04", "0", "01", "2024"], ["40"]),    # estrato 0-2 (excluir)
    ])
    df = pe.load_establecimientos_sector(path)
    assert len(df) == 1
    assert df.iloc[0]["establecimientos"] == 100
