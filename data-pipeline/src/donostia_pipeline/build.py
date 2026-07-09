"""Pipeline entry point: raw sources → cleaned JSON in ``web/src/data/``.

Run with ``python -m donostia_pipeline.build`` (optionally ``--offline`` to skip
network and use whatever is already in ``raw/``). Deterministic: re-running with
the same raw inputs reproduces byte-identical outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

from . import config, export_tables, geometry, provenance, spatial
from .datasets import (
    aemet_climate,
    airbnb,
    barrio_profiles,
    calles_vut,
    change_velocity,
    demografia,
    demografia_edad,
    demografia_origen_region,
    educacion_gis,
    empleo_nacionalidad_gipuzkoa,
    fiscalidad,
    estudios,
    housing_tension,
    ibiltur,
    ine_eoh,
    mice,
    modelos_linguisticos,
    movilidad_laboral,
    origen_paises_barrio,
    paro,
    reate_licencias,
    rent,
    renta,
    renta_trabajo,
    residuos,
    seguridad,
    ruido_gis,
    salud_gis,
    tejido_comercial,
    tipologia_comercial,
    transformation,
    vpo_etxebide,
    vut,
    vut_density,
)
from .model import BuildContext, Metric, Series, validate, validate_series

# Raw files to ensure present before building. (filename -> URL)
RAW_DOWNLOADS: dict[str, str] = {
    "auzoak.json": config.BARRIOS_GEOJSON_URL,
    "vtur_censo.csv": (
        "https://www.donostia.eus/datosabiertos/recursos/"
        "censo-viviendas-turisticas/urb_ckan_vtur_censo.csv"
    ),
    "demo_barrio.csv": (
        "https://www.donostia.eus/datosabiertos/recursos/"
        "demografia-origen/demografianacionalidadbarrio.csv"
    ),
    "edad_barrio.csv": (
        "https://www.donostia.eus/datosabiertos/recursos/"
        "demografia-piramideedad/demografiapiramideedadbarrio.csv"
    ),
    "renta_barrio.csv": (
        "https://www.donostia.eus/datosabiertos/recursos/"
        "eustat_renta/eustatrentabarrio.csv"
    ),
    "estudios_barrio.csv": (
        "https://www.donostia.eus/datosabiertos/recursos/"
        "demografia-nivelestudios/demografianivelestudiosbarrio.csv"
    ),
    # INE EOH monthly overnight stays, San Sebastián (full history via nult).
    "ine_pernoct_esp.json": (
        "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EOT2721?nult=600"
    ),
    "ine_pernoct_ext.json": (
        "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EOT2722?nult=600"
    ),
    # Gobierno Vasco EMA — rent by barrio (xlsx, sheet T8.3).
    "emal_barrios.xlsx": (
        "https://euskadi.eus/contenidos/estadistica/122417_emal_tablas_estad/"
        "opendata/EMAL.-Barrios-Municipios.-2016-2025_es.xlsx"
    ),
    # Municipal street directory (callejero, "Nombres de calle") — zipped SHP of
    # label points in EPSG:25830 with a stable street code (KodKalea) + ES/EU
    # names. Enables the street-granularity VUT map (calles_vut). Not joined to
    # barrios: this is the sub-barrio layer.
    calles_vut.RAW_ZIP: (
        "https://www.donostia.eus/datosabiertos/dataset/"
        "ce59dab6-0de6-47b9-b5d7-8b422a68b709/resource/"
        "74843ba4-16a4-487b-baf7-583f521c2368/download/hiribarrukobideenizena.zip"
    ),
    # Educational facilities (GeoJSON points, WGS84) — joined to barrios spatially.
    "educativos.json": (
        "https://www.donostia.eus/datosabiertos/recursos/"
        "servicios-educativos/hezkuntzaekipamenduak.json"
    ),
    # Health facilities (GeoJSON points, WGS84) — REC-18, joined to barrios.
    salud_gis.GEOJSON_NAME: (
        "https://www.donostia.eus/datosabiertos/recursos/"
        "servicios-salud/osasunekipamenduak.json"
    ),
    # Waste collection (annual, city) → recycling-rate indicator.
    "residuos.csv": (
        "https://www.donostia.eus/datosabiertos/recursos/residuos/datos-residuos.csv"
    ),
    # Strategic night-noise map (Lnight), zipped SHP in EPSG:25830 (2022).
    "ruido_noche_2022.zip": (
        "https://www.donostia.eus/ide/INGURUMENA-MEDIO_AMBIENTE/shp/"
        "Zarata_Ruido/2022_DSS_IZT_totala_gau.zip"
    ),
    # Municipal fiscality (annual, city) → tax/fee revenue indicators.
    "impuestos_ciudad.csv": (
        "https://www.donostia.eus/datosabiertos/dataset/"
        "36ef69b9-b2f9-4ebc-b5e9-a7e6e8f32d37/resource/"
        "8b821f48-2add-4d61-a0bc-98f1749925da/download/pfi_impuestos_tipo_ciudad_ckan.csv"
    ),
    "tasas_ciudad.csv": (
        "https://www.donostia.eus/datosabiertos/dataset/"
        "7c0f2bf4-00b6-44bf-bf24-c9bdbc9bd00c/resource/"
        "cde02a4c-8113-45b9-ba59-614855e18919/download/pfi_tasas_tipo_ciudad_ckan.csv"
    ),
    # Inside Airbnb — Euskadi region snapshot 2025-09-29 (gzipped CSV). The full
    # `data/` files carry coordinates + per-review dates; we spatial-join to barrios
    # and keep only Donostia. License: Inside Airbnb (CC BY 4.0).
    "airbnb_listings.csv.gz": (
        "https://data.insideairbnb.com/spain/pv/euskadi/2025-09-29/data/listings.csv.gz"
    ),
    "airbnb_reviews.csv.gz": (
        "https://data.insideairbnb.com/spain/pv/euskadi/2025-09-29/data/reviews.csv.gz"
    ),
    # Gobierno Vasco REATE registry — tourist homes (VUT) + rooms (HUT) with the
    # original registration date. Living snapshot: bajas are not published, so
    # the derived curves are of surviving licenses (see reate_licencias.py).
    reate_licencias.RAW_VIVIENDAS: (
        "https://opendata.euskadi.eus/contenidos/ds_recursos_turisticos/"
        "habitaciones_viviendas_turisti/opendata/viviendas.json"
    ),
    reate_licencias.RAW_HABITACIONES: (
        "https://opendata.euskadi.eus/contenidos/ds_recursos_turisticos/"
        "habitaciones_viviendas_turisti/opendata/habitaciones.json"
    ),
    # Etxebide protected-housing promotions (REC-15): UTM points + dwelling
    # counts, joined to barrios. Whole Basque Country; geometry keeps Donostia.
    vpo_etxebide.CSV_NAME: (
        "https://opendata.euskadi.eus/contenidos/ds_localizaciones/"
        "promociones_etxebide/opendata/promociones.csv"
    ),
}

# Dataset modules to run (each exposes build(ctx) -> list[Metric]).
# vut_density is derived and reads both the VUT census and demographics, so it
# runs after the sources it depends on are present in raw/.
DATASETS = [vut, demografia, demografia_edad, demografia_origen_region, renta,
            renta_trabajo, estudios, vut_density, rent, educacion_gis, salud_gis,
            ruido_gis, airbnb, vpo_etxebide, tipologia_comercial]

# Derived metrics computed from other metrics (run after DATASETS). Each exposes
# build_from_metrics(metrics_by_id) -> list[Metric]. ``change_velocity`` reads
# the base metrics' time series, so it must run after they (and any derived
# inputs) are in the store.
DERIVED_METRICS = [housing_tension, change_velocity, barrio_profiles, transformation]

# City-grain time-series modules (each exposes build_series(ctx) -> list[Series]).
SERIES_DATASETS = [ine_eoh, aemet_climate, airbnb]

# AEMET climate fetch: monthly endpoint caps each request at 36 months, so we
# pull the history in 3-year windows and cache the concatenation in raw/.
AEMET_RAW = "aemet_igeldo.json"
AEMET_YEAR_RANGE = (1981, 2026)
AEMET_DATOS_URL = (
    "https://opendata.aemet.es/opendata/api/valores/climatologicos/"
    "mensualesanuales/datos/anioini/{ini}/aniofin/{fin}/estacion/"
    + config.AEMET_IGELDO_STATION
)


def ensure_aemet(offline: bool) -> bool:
    """Fetch the Igeldo monthly climate history into raw/ (once).

    Needs a free key in ``AEMET_API_KEY``. Returns False (and skips, leaving the
    climate series unbuilt) when offline, keyless, or already cached-but-absent.
    """
    dest = config.RAW_DIR / AEMET_RAW
    if dest.exists():
        return True
    key = os.environ.get(config.AEMET_API_KEY_ENV)
    if offline or not key:
        print("  · AEMET skipped (no AEMET_API_KEY / offline)")
        return False

    records: list[dict] = []
    ini, fin = AEMET_YEAR_RANGE
    for start in range(ini, fin + 1, 3):
        end = min(start + 2, fin)
        chunk = _fetch_aemet_window(start, end, key)
        if chunk is None:
            raise RuntimeError(f"AEMET fetch failed for {start}-{end}")
        records.extend(chunk)
        time.sleep(2)  # space out windows; the free API throttles bursts

    dest.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    print(f"  ↓ AEMET Igeldo ({len(records)} monthly records)")
    return True


def _fetch_aemet_window(start: int, end: int, key: str) -> list[dict] | None:
    """Fetch one 3-year window, retrying on the free API's rate limiting.

    AEMET answers with a pointer JSON (``estado``/``datos``); ``estado`` 429
    means throttled. Returns the records list, or None if it never succeeds.
    """
    url = AEMET_DATOS_URL.format(ini=start, fin=end)
    for attempt in range(5):
        ptr = requests.get(url, params={"api_key": key}, timeout=60).json()
        datos = ptr.get("datos")
        if datos:
            resp = requests.get(datos, timeout=60)
            if resp.status_code == 200:
                resp.encoding = "latin-1"  # AEMET serves ISO-8859-15
                return json.loads(resp.text)
        # throttled or transient → exponential backoff (3, 6, 12, 24s)
        time.sleep(3 * 2**attempt)
    return None


# Eustat PxWeb table PX_040601_ceens_mun01, filtered server-side to Donostia
# (municipio 20069), all years, titularidad "Total", nivel "Enseñanzas de
# régimen general" (100), modelo lingüístico (Total/A/B/D/X), "Total alumnos".
EUSTAT_MODELOS_RAW = modelos_linguisticos.RAW_FILE
EUSTAT_MODELOS_URL = (
    "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_040601_ceens_mun01.px"
)
EUSTAT_MODELOS_QUERY = {
    "query": [
        {"code": "municipio", "selection": {"filter": "item", "values": ["20069"]}},
        {"code": "titularidad del centro", "selection": {"filter": "item", "values": ["10"]}},
        {"code": "nivel de enseñanza", "selection": {"filter": "item", "values": ["100"]}},
        {"code": "modelo lingüistico",
         "selection": {"filter": "item", "values": ["10", "20", "30", "40", "50"]}},
        {"code": "características", "selection": {"filter": "item", "values": ["10"]}},
    ],
    "response": {"format": "json"},
}


def _ensure_pxweb_table(offline: bool, raw_name: str, url: str, query: dict, label: str) -> bool:
    """Fetch a Eustat PxWeb query response into raw/ (once); shared by the
    modelos-lingüísticos and paro fetches (both single-request POST queries)."""
    dest = config.RAW_DIR / raw_name
    if dest.exists():
        return True
    if offline:
        print(f"  · {label} skipped (offline)")
        return False
    resp = requests.post(url, json=query, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print(f"  ↓ {raw_name}")
    return True


def ensure_eustat_modelos(offline: bool) -> bool:
    """Fetch the Donostia language-model schooling series into raw/ (once)."""
    return _ensure_pxweb_table(
        offline, EUSTAT_MODELOS_RAW, EUSTAT_MODELOS_URL, EUSTAT_MODELOS_QUERY,
        "Eustat modelos lingüísticos",
    )


# Eustat PxWeb table PX_050403_cpra_tab19, filtered server-side to capital
# Donostia/San Sebastián (30), tasa "Tasa de paro" (30), all years, sexo
# (Total/Hombres/Mujeres), trimestre "Promedio anual" (10).
EUSTAT_PARO_RAW = paro.RAW_FILE
EUSTAT_PARO_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_050403_cpra_tab19.px"
EUSTAT_PARO_QUERY = {
    "query": [
        {"code": "tasa (%)", "selection": {"filter": "item", "values": ["30"]}},
        {"code": "capital", "selection": {"filter": "item", "values": ["30"]}},
        {"code": "sexo", "selection": {"filter": "item", "values": ["10", "20", "30"]}},
        {"code": "trimestre", "selection": {"filter": "item", "values": ["10"]}},
    ],
    "response": {"format": "json"},
}


def ensure_eustat_paro(offline: bool) -> bool:
    """Fetch the Donostia unemployment-rate series into raw/ (once)."""
    return _ensure_pxweb_table(
        offline, EUSTAT_PARO_RAW, EUSTAT_PARO_URL, EUSTAT_PARO_QUERY, "Eustat paro",
    )


# Eustat PxWeb table PX_200163_cdirae_est04b, filtered server-side to
# municipio Donostia (20069), all ~630 CNAE-2009 activity codes (the source
# has no section/division rollup rows — tejido_comercial.py sums client-side),
# all years.
EUSTAT_COMERCIO_RAW = tejido_comercial.RAW_FILE
EUSTAT_COMERCIO_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_200163_cdirae_est04b.px"
EUSTAT_COMERCIO_QUERY = {
    "query": [
        {"code": "municipio", "selection": {"filter": "item", "values": ["20069"]}},
        {"code": "CNAE-2009", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "periodo", "selection": {"filter": "all", "values": ["*"]}},
    ],
    "response": {"format": "json"},
}


def ensure_eustat_comercio(offline: bool) -> bool:
    """Fetch the Donostia establishments-by-CNAE series into raw/ (once)."""
    return _ensure_pxweb_table(
        offline, EUSTAT_COMERCIO_RAW, EUSTAT_COMERCIO_URL, EUSTAT_COMERCIO_QUERY,
        "Eustat tejido comercial",
    )


# REC-17 — Eustat has no municipio×municipio OD matrix in PxWeb; we fetch the
# categorical mobility tables (EMPA lugar de trabajo / EME lugar de estudios,
# Donostia 20069, 2021–) plus DIRAE localized employment (est07, 1995–). See
# datasets/movilidad_laboral.py for how they close H4's activity half.
_MOVILIDAD_QUERY = {
    "query": [
        {"code": "ámbitos territoriales",
         "selection": {"filter": "item", "values": ["20069"]}},
    ],
    "response": {"format": "json"},
}
EUSTAT_EMPA_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_050407_cempa_empa_mt02.px"
EUSTAT_EME_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_040606_ceme_me02.px"
EUSTAT_DIRAE_EMPLEO_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_200163_cdirae_est07.px"


def ensure_eustat_movilidad(offline: bool) -> bool:
    """Fetch the Donostia work/study mobility tables into raw/ (once)."""
    ok_empa = _ensure_pxweb_table(
        offline, movilidad_laboral.RAW_EMPA, EUSTAT_EMPA_URL, _MOVILIDAD_QUERY,
        "Eustat EMPA movilidad laboral",
    )
    ok_eme = _ensure_pxweb_table(
        offline, movilidad_laboral.RAW_EME, EUSTAT_EME_URL, _MOVILIDAD_QUERY,
        "Eustat EME movilidad de estudios",
    )
    return ok_empa and ok_eme


def ensure_eustat_dirae_empleo(offline: bool) -> bool:
    """Fetch the Donostia localized-employment series into raw/ (once)."""
    return _ensure_pxweb_table(
        offline, movilidad_laboral.RAW_DIRAE, EUSTAT_DIRAE_EMPLEO_URL,
        _MOVILIDAD_QUERY, "Eustat DIRAE empleo localizado",
    )


# REC-21 — unemployment by nationality + R&D-personnel intensity, Gipuzkoa
# (no barrio grain exists for either; see datasets/empleo_nacionalidad_gipuzkoa.py).
EUSTAT_TASAS_NAC_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_050403_cpra_tab17.px"
EUSTAT_TASAS_NAC_QUERY = {
    "query": [
        {"code": "tasa (%)", "selection": {"filter": "item", "values": ["10", "20", "30"]}},
        {"code": "territorio histórico", "selection": {"filter": "item", "values": ["20"]}},
        {"code": "nacionalidad", "selection": {"filter": "item", "values": ["10", "20", "30"]}},
        {"code": "trimestre", "selection": {"filter": "item", "values": ["10"]}},
    ],
    "response": {"format": "json"},
}

EUSTAT_ID_PERSONAL_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_043201_cid_res08c.px"
EUSTAT_ID_PERSONAL_QUERY = {
    "query": [
        {"code": "territorio histórico", "selection": {"filter": "item", "values": ["20"]}},
        {"code": "sector de ejecución",
         "selection": {"filter": "item", "values": ["00", "10", "20", "30"]}},
        {"code": "ocupación",
         "selection": {"filter": "item", "values": ["100", "200", "300", "400"]}},
        {"code": "sexo", "selection": {"filter": "item", "values": ["10"]}},
    ],
    "response": {"format": "json"},
}

EUSTAT_OCUPADOS_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_050403_cpra_tab04.px"
EUSTAT_OCUPADOS_QUERY = {
    "query": [
        {"code": "relación con la actividad (OIT)",
         "selection": {"filter": "item", "values": ["30"]}},
        {"code": "territorio histórico", "selection": {"filter": "item", "values": ["00", "20"]}},
        {"code": "sexo", "selection": {"filter": "item", "values": ["10"]}},
        {"code": "trimestre", "selection": {"filter": "item", "values": ["10"]}},
    ],
    "response": {"format": "json"},
}


def ensure_eustat_empleo_nacionalidad(offline: bool) -> bool:
    """Fetch the three Gipuzkoa employment tables for REC-21 into raw/ (once)."""
    ok_tasas = _ensure_pxweb_table(
        offline, empleo_nacionalidad_gipuzkoa.RAW_TASAS, EUSTAT_TASAS_NAC_URL,
        EUSTAT_TASAS_NAC_QUERY, "Eustat tasas por nacionalidad",
    )
    ok_id = _ensure_pxweb_table(
        offline, empleo_nacionalidad_gipuzkoa.RAW_ID_PERSONAL, EUSTAT_ID_PERSONAL_URL,
        EUSTAT_ID_PERSONAL_QUERY, "Eustat personal I+D",
    )
    ok_ocup = _ensure_pxweb_table(
        offline, empleo_nacionalidad_gipuzkoa.RAW_OCUPADOS, EUSTAT_OCUPADOS_URL,
        EUSTAT_OCUPADOS_QUERY, "Eustat población ocupada",
    )
    return ok_tasas and ok_id and ok_ocup


# Eustat PxWeb table PX_173402_crpf_rpf_rp22_2p, filtered server-side to
# Donostia's barrios and tipo de renta 110 (renta del trabajo = wages), all
# years — the salary proxy for HU-7 (renta_trabajo.py → income_labor).
EUSTAT_RENTA_TRABAJO_URL = (
    "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp22_2p.px"
)
_DONOSTIA_BARRIO_CODES = ["20069"] + sorted(renta_trabajo.EUSTAT_BARRIO_TO_ID)
EUSTAT_RENTA_TRABAJO_QUERY = {
    "query": [
        {"code": "barrios",
         "selection": {"filter": "item", "values": _DONOSTIA_BARRIO_CODES}},
        {"code": "tipo de renta",
         "selection": {"filter": "item", "values": [renta_trabajo.LABOR_INCOME_CODE]}},
        {"code": "periodo", "selection": {"filter": "all", "values": ["*"]}},
    ],
    "response": {"format": "json"},
}


def ensure_eustat_renta_trabajo(offline: bool) -> bool:
    """Fetch the Donostia labor-income-by-barrio series into raw/ (once)."""
    return _ensure_pxweb_table(
        offline, renta_trabajo.RAW_FILE, EUSTAT_RENTA_TRABAJO_URL,
        EUSTAT_RENTA_TRABAJO_QUERY, "Eustat renta del trabajo",
    )


# Roadmap: per-barrio metrics whose sources are known but not yet wired. They
# render disabled ("in arrivo") in the picker. Currently empty — the remaining
# roadmap items (MICE, Ibiltur spend) are city-grain, not barrio choropleths.
PLANNED_METRICS: list[dict] = []


def ensure_raw(offline: bool) -> None:
    """Download any missing raw inputs (unless offline)."""
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in RAW_DOWNLOADS.items():
        dest = config.RAW_DIR / name
        if dest.exists():
            continue
        if offline:
            raise FileNotFoundError(f"missing raw input {name} and --offline set")
        print(f"  ↓ downloading {name}")
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        dest.write_bytes(resp.content)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def run(offline: bool = False) -> dict:
    ensure_raw(offline)
    out_dir = config.WEB_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Reference geometry.
    geojson = geometry.normalize_barrios(config.RAW_DIR / "auzoak.json")
    _write_json(out_dir / "barrios.geojson", geojson)
    valid_ids = geometry.barrio_ids(geojson)
    code_to_id = {
        f["properties"]["kod_auzo"]: f["properties"]["barrio_id"]
        for f in geojson["features"]
    }
    print(f"  ✓ barrios.geojson ({len(valid_ids)} barrios)")

    # 2. Datasets → metrics. The context also carries the spatial index (for
    #    GIS point/areal joins) and the latest-year population (per-capita
    #    normalization), both built once against the reference geometry.
    ctx = BuildContext(
        raw_dir=config.RAW_DIR,
        barrio_ids=valid_ids,
        code_to_id=code_to_id,
        barrio_index=spatial.BarrioIndex(geojson),
        population_latest=demografia.population_latest_by_barrio(config.RAW_DIR, code_to_id),
    )
    # renta_trabajo (income_labor) needs its Eustat PxWeb table in raw/ before
    # the DATASETS loop (the other Eustat fetches feed city indicators later).
    ensure_eustat_renta_trabajo(offline)

    metrics: list[Metric] = []
    for module in DATASETS:
        metrics.extend(module.build(ctx))
    # Derived metrics combine the base ones (no raw files).
    metrics_by_id = {m.id: m for m in metrics}
    for module in DERIVED_METRICS:
        metrics.extend(module.build_from_metrics(metrics_by_id))

    # Stamp confidence tier + assumptions on every metric (MET-4), centrally.
    provenance.apply(metrics)

    registry = []
    for metric in metrics:
        validate(metric, valid_ids)
        _write_json(out_dir / f"metric_{metric.id}.json", metric.to_metric_file())
        registry.append(metric.to_registry_entry())
        print(f"  ✓ metric_{metric.id}.json ({len(metric.periods)} period(s))")

    # 3. Registry (live datasets + planned roadmap stubs), ordered by theme
    #    then label for a stable dropdown.
    registry.extend(PLANNED_METRICS)
    registry.sort(key=lambda e: (e["theme"], e["label"]))
    _write_json(out_dir / "metrics.json", registry)
    print(f"  ✓ metrics.json ({len(registry)} metrics)")

    # 4. City-grain time series (seasonality heatmaps etc.).
    ensure_aemet(offline)
    series_list: list[Series] = []
    for module in SERIES_DATASETS:
        series_list.extend(module.build_series(ctx))
    series_registry = []
    for series in series_list:
        validate_series(series)
        _write_json(out_dir / f"series_{series.id}.json", series.to_series_file())
        series_registry.append(series.to_registry_entry())
        print(f"  ✓ series_{series.id}.json ({len(series.years)} years)")
    series_registry.sort(key=lambda e: (e["theme"], e["label"]))
    _write_json(out_dir / "series.json", series_registry)
    print(f"  ✓ series.json ({len(series_registry)} series)")

    # 5. Annual city indicators (MICE — curated; recycling rate — from residuos;
    #    language-model schooling share / unemployment rate / establishment
    #    mix — from Eustat; Ibiltur Ocio — curated).
    ensure_eustat_modelos(offline)
    ensure_eustat_paro(offline)
    ensure_eustat_comercio(offline)
    ensure_eustat_movilidad(offline)
    ensure_eustat_dirae_empleo(offline)
    ensure_eustat_empleo_nacionalidad(offline)
    indicators = (mice.build_indicators() + residuos.build_indicators(config.RAW_DIR)
                  + fiscalidad.build_indicators(config.RAW_DIR)
                  + modelos_linguisticos.build_indicators(config.RAW_DIR)
                  + ibiltur.build_indicators()
                  + paro.build_indicators(config.RAW_DIR)
                  + tejido_comercial.build_indicators(config.RAW_DIR)
                  + reate_licencias.build_indicators(config.RAW_DIR)
                  + movilidad_laboral.build_indicators(config.RAW_DIR)
                  + empleo_nacionalidad_gipuzkoa.build_indicators(config.RAW_DIR)
                  + seguridad.build_indicators())
    _write_json(out_dir / "indicators.json", [i.to_file() for i in indicators])
    print(f"  ✓ indicators.json ({len(indicators)} indicators)")

    barrio_names = {f["properties"]["barrio_id"]: f["properties"]["name"]
                    for f in geojson["features"]}

    # 5b. Per-barrio top countries of origin (REC-21-web). Not a Metric — its own
    #     JSON export from the same demo_barrio.csv (see the module docstring).
    origen = origen_paises_barrio.write_json(
        config.RAW_DIR / origen_paises_barrio.CSV_NAME,
        out_dir / "origen_paises_barrio.json",
        code_to_id,
        barrio_names,
    )
    print(f"  ✓ origen_paises_barrio.json ({len(origen['barrios'])} barrios)")

    # 5c. Touristic housing per **street** (sub-barrio). Not a Metric — street
    #     geometry, not barrio_id; its own JSON export (see the module docstring).
    #     Skipped gracefully if the callejero SHP or the census isn't present.
    calle_zip = config.RAW_DIR / calles_vut.RAW_ZIP
    calle_csv = config.RAW_DIR / calles_vut.CSV_NAME
    if calle_zip.exists() and calle_csv.exists():
        streets = calles_vut.write_json(calle_zip, calle_csv, out_dir / "street_vut.json")
        # Same numbers as a tidy CSV (project principle), under datos/procesado.
        export_tables.write_csv(
            config.TABLES_DIR / "calles_vut.csv",
            ["street_code", "name_es", "name_eu", "lon", "lat", "units", "vut", "hut", "beds"],
            [{"street_code": s["code"], "name_es": s["nameEs"], "name_eu": s["nameEu"],
              "lon": s["lon"], "lat": s["lat"], "units": s["units"], "vut": s["vut"],
              "hut": s["hut"], "beds": s["beds"]} for s in streets["streets"]],
        )
        print(
            f"  ✓ street_vut.json + calles_vut.csv ({streets['streetCount']} streets, "
            f"{streets['matchRate']}% of census rows matched)"
        )
    else:
        print("  · street_vut.json skipped (callejero.zip / vtur_censo.csv absent)")

    # 6. Tidy CSV export (language-agnostic tables under data/).
    tables = config.TABLES_DIR
    export_tables.write_csv(
        tables / "barrios.csv", export_tables.BARRIO_FIELDS,
        [{"barrio_id": f["properties"]["barrio_id"],
          "name": f["properties"]["name"],
          "kod_auzo": f["properties"]["kod_auzo"]} for f in geojson["features"]],
    )
    export_tables.write_csv(
        tables / "metrics_long.csv", export_tables.METRIC_FIELDS,
        export_tables.metric_long_rows(metrics, barrio_names),
    )
    export_tables.write_csv(
        tables / "series_long.csv", export_tables.SERIES_FIELDS,
        export_tables.series_long_rows(series_list),
    )
    export_tables.write_csv(
        tables / "indicators_long.csv", export_tables.INDICATOR_FIELDS,
        export_tables.indicator_long_rows(indicators),
    )
    print(f"  ✓ CSV tables → {tables.name}/ (barrios, metrics_long, series_long, indicators_long)")

    return {
        "barrios": len(valid_ids),
        "metrics": len(registry),
        "series": len(series_registry),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Donostia Dataviz datasets.")
    parser.add_argument(
        "--offline", action="store_true", help="use existing raw/ files only"
    )
    args = parser.parse_args(argv)
    print("Building Donostia Dataviz datasets…")
    summary = run(offline=args.offline)
    print(
        f"Done: {summary['barrios']} barrios, {summary['metrics']} metrics, "
        f"{summary['series']} series."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
