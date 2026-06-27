"""Pipeline entry point: raw sources → cleaned JSON in ``web/src/data/``.

Run with ``python -m donostia_pipeline.build`` (optionally ``--offline`` to skip
network and use whatever is already in ``raw/``). Deterministic: re-running with
the same raw inputs reproduces byte-identical outputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

from . import config, geometry
from .datasets import demografia, estudios, renta, vut, vut_density
from .model import BuildContext, Metric, validate

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
}

# Dataset modules to run (each exposes build(ctx) -> list[Metric]).
# vut_density is derived and reads both the VUT census and demographics, so it
# runs after the sources it depends on are present in raw/.
DATASETS = [vut, demografia, renta, estudios, vut_density]

# Roadmap: metrics whose sources are known but not yet wired (manual/PDF/API).
# They appear in the UI disabled ("in arrivo") so the catalogue shows intent.
PLANNED_METRICS = [
    {
        "id": "rent_eur_m2",
        "label": "Affitto €/m²",
        "unit": "€/m²",
        "theme": "housing",
        "kind": "sequential",
        "geoGrain": "barrio",
        "timeGrain": "month",
        "source": "Indomio (scraping, in arrivo)",
        "status": "planned",
        "periods": [],
    },
    {
        "id": "temp_avg",
        "label": "Temperatura media",
        "unit": "°C",
        "theme": "climate",
        "kind": "sequential",
        "geoGrain": "city",
        "timeGrain": "month",
        "source": "AEMET — stazione Igeldo 1024E (API key, in arrivo)",
        "status": "planned",
        "periods": [],
    },
]


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

    # 2. Datasets → metrics.
    ctx = BuildContext(raw_dir=config.RAW_DIR, barrio_ids=valid_ids, code_to_id=code_to_id)
    metrics: list[Metric] = []
    for module in DATASETS:
        metrics.extend(module.build(ctx))

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

    return {"barrios": len(valid_ids), "metrics": len(registry)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Donostia Dataviz datasets.")
    parser.add_argument(
        "--offline", action="store_true", help="use existing raw/ files only"
    )
    args = parser.parse_args(argv)
    print("Building Donostia Dataviz datasets…")
    summary = run(offline=args.offline)
    print(f"Done: {summary['barrios']} barrios, {summary['metrics']} metrics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
