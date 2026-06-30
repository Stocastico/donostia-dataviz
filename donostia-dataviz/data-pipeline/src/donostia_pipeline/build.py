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

from . import config, export_tables, geometry, spatial
from .datasets import (
    aemet_climate,
    barrio_profiles,
    change_velocity,
    demografia,
    educacion_gis,
    estudios,
    housing_tension,
    ine_eoh,
    mice,
    rent,
    renta,
    residuos,
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
    # Educational facilities (GeoJSON points, WGS84) — joined to barrios spatially.
    "educativos.json": (
        "https://www.donostia.eus/datosabiertos/recursos/"
        "servicios-educativos/hezkuntzaekipamenduak.json"
    ),
    # Waste collection (annual, city) → recycling-rate indicator.
    "residuos.csv": (
        "https://www.donostia.eus/datosabiertos/recursos/residuos/datos-residuos.csv"
    ),
}

# Dataset modules to run (each exposes build(ctx) -> list[Metric]).
# vut_density is derived and reads both the VUT census and demographics, so it
# runs after the sources it depends on are present in raw/.
DATASETS = [vut, demografia, renta, estudios, vut_density, rent, educacion_gis]

# Derived metrics computed from other metrics (run after DATASETS). Each exposes
# build_from_metrics(metrics_by_id) -> list[Metric]. ``change_velocity`` reads
# the base metrics' time series, so it must run after they (and any derived
# inputs) are in the store.
DERIVED_METRICS = [housing_tension, change_velocity, barrio_profiles]

# City-grain time-series modules (each exposes build_series(ctx) -> list[Series]).
SERIES_DATASETS = [ine_eoh, aemet_climate]

# AEMET climate fetch: monthly endpoint caps each request at 36 months, so we
# pull the history in 3-year windows and cache the concatenation in raw/.
AEMET_RAW = "aemet_igeldo.json"
AEMET_YEAR_RANGE = (1981, 2025)
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
    metrics: list[Metric] = []
    for module in DATASETS:
        metrics.extend(module.build(ctx))
    # Derived metrics combine the base ones (no raw files).
    metrics_by_id = {m.id: m for m in metrics}
    for module in DERIVED_METRICS:
        metrics.extend(module.build_from_metrics(metrics_by_id))

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

    # 5. Annual city indicators (MICE — curated; recycling rate — from residuos).
    indicators = mice.build_indicators() + residuos.build_indicators(config.RAW_DIR)
    _write_json(out_dir / "indicators.json", [i.to_file() for i in indicators])
    print(f"  ✓ indicators.json ({len(indicators)} indicators)")

    # 6. Tidy CSV export (language-agnostic tables under data/).
    barrio_names = {f["properties"]["barrio_id"]: f["properties"]["name"]
                    for f in geojson["features"]}
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
