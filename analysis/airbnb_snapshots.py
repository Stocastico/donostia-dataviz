"""REC-13 — Serie de snapshots de anuncios activos Inside Airbnb (MET-7).

El proxy Airbnb del proyecto se construye desde las *reseñas* de un único
snapshot (2026-06-30), con el sesgo de adopción documentado en MET-7: las
reseñas miden actividad reseñada, no oferta. Este análisis trae la serie de
snapshots trimestrales de Inside Airbnb (anuncios *activos* en cada fecha) y
la contrasta con las reseñas de los 12 meses previos a cada snapshot sobre el
mismo universo de listings, para cuantificar cuánto divergen oferta activa y
actividad reseñada.

Fuente y alcance (investigado jul-2026): Euskadi tiene snapshots trimestrales
desde 2021-12-30, pero el servidor solo mantiene accesibles los últimos ~8
(desde 2023-12-29; los anteriores devuelven 403 y requieren una *data request*
a Inside Airbnb — las fechas exactas quedan en ``UNAVAILABLE_SNAPSHOTS`` por si
algún día se piden). Se usa el CSV resumen (``visualisations/listings.csv``,
uno por fecha): trae id, lat/lon, room_type, licencia y reseñas — suficiente
para contar activos por barrio (punto-en-polígono, como el pipeline) sin
descargar los ficheros completos.

Lecturas honestas: "activo" = presente en el scrape de esa fecha (criterio de
Inside Airbnb, no de Airbnb); la ventana comparable es corta (2023-12→2026-06,
con un hueco de tres trimestres: entre 2025-09-29 y 2026-06-30 no se publicó
ningún snapshot); el campo ``license`` es autodeclarado por el anfitrión.

Solo pandas + numpy (+ shapely vía tourism_seasonality). Requiere los crudos
(bash datos/input/descargar_raw.sh). Uso:
    python analysis/airbnb_snapshots.py [--save]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from tourism_seasonality import assign_listings

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "datos" / "input" / "raw"
REVIEWS_GZ = RAW / "airbnb_reviews.csv.gz"
GEOJSON = ROOT / "web" / "src" / "data" / "barrios.geojson"
OUTDIR = Path(__file__).resolve().parent / "output"

# Snapshots aún descargables (verificado 2026-07-12). Trimestrales hasta
# 2025-09-29; después la cadencia se interrumpió y el siguiente es 2026-06-30
# (sondeados todos los días de oct-2025…may-2026: ninguno publicado).
SNAPSHOTS = [
    "2023-12-29", "2024-03-31", "2024-06-30", "2024-09-29",
    "2024-12-31", "2025-03-27", "2025-06-28", "2025-09-29",
    "2026-06-30",
]
# Existieron pero el servidor ya no los sirve (403) — solo vía data request.
UNAVAILABLE_SNAPSHOTS = [
    "2021-12-30", "2022-03-31", "2022-06-27", "2022-09-26",
    "2022-12-30", "2023-03-31", "2023-06-30", "2023-09-24",
]

_ENTIRE = "Entire home/apt"


def snapshot_path(date: str) -> Path:
    return RAW / f"airbnb_snapshot_{date}.csv"


# ------------------------------------------------------------ medidas ----
def snapshot_summary(df: pd.DataFrame) -> dict:
    """Un snapshot (ya filtrado a Donostia) → activos, % entire, % con licencia."""
    licensed = df["license"].fillna("").astype(str).str.strip() != ""
    return {
        "n_active": int(len(df)),
        "pct_entire_home": float((df["room_type"] == _ENTIRE).mean() * 100.0),
        "pct_licensed": float(licensed.mean() * 100.0),
    }


def barrio_counts(df: pd.DataFrame, features: list[dict]) -> pd.Series:
    """Anuncios activos por barrio (punto-en-polígono, como el pipeline)."""
    barrio = assign_listings(df, features)
    return barrio.value_counts().sort_index()


def reviews_ltm(reviews: pd.DataFrame, universe: set,
                snapshot_dates: list[str]) -> dict[str, int]:
    """Reseñas en los 12 meses previos a cada fecha, solo listings del universo."""
    ours = reviews[reviews["listing_id"].isin(universe)].copy()
    dates = pd.to_datetime(ours["date"])
    out = {}
    for snap in snapshot_dates:
        end = pd.Timestamp(snap)
        start = end - pd.Timedelta(days=365)
        out[snap] = int(((dates > start) & (dates <= end)).sum())
    return out


def growth_comparison(active: dict[str, int], ltm: dict[str, int]) -> dict:
    """Crecimiento primera→última fecha de ambas series y ratio de divergencia.

    bias_ratio > 1: las reseñas crecen más que la oferta activa (el proxy de
    reseñas *exagera* el crecimiento); < 1: lo subestima.
    """
    first, last = min(active), max(active)
    active_g = active[last] / active[first]
    reviews_g = ltm[last] / ltm[first]
    return {
        "window": (first, last),
        "active_growth_pct": (active_g - 1.0) * 100.0,
        "reviews_growth_pct": (reviews_g - 1.0) * 100.0,
        "bias_ratio": reviews_g / active_g,
    }


# --------------------------------------------------------------- main ----
def _load_snapshot(date: str) -> pd.DataFrame:
    path = snapshot_path(date)
    if not path.exists():
        raise SystemExit(
            f"falta {path.name} — ejecuta: bash datos/input/descargar_raw.sh")
    return pd.read_csv(
        path, usecols=["id", "latitude", "longitude", "room_type", "license"])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", action="store_true",
                        help="escribe los CSV en analysis/output/")
    args = parser.parse_args(argv)

    features = json.loads(GEOJSON.read_text(encoding="utf-8"))["features"]
    city_rows, barrio_cols, universe = [], {}, set()
    donostia_by_date: dict[str, pd.DataFrame] = {}
    for date in SNAPSHOTS:
        df = _load_snapshot(date)
        barrio = assign_listings(df, features)          # solo Donostia
        dss = df[df["id"].isin(barrio.index)]
        donostia_by_date[date] = dss
        universe |= set(dss["id"])
        city_rows.append({"snapshot": date, **snapshot_summary(dss)})
        barrio_cols[date] = barrio.value_counts()
    city = pd.DataFrame(city_rows).set_index("snapshot")
    por_barrio = pd.DataFrame(barrio_cols).fillna(0).astype(int).sort_index()

    reviews = pd.read_csv(REVIEWS_GZ, usecols=["listing_id", "date"])
    ltm = reviews_ltm(reviews, universe, SNAPSHOTS)
    city["reviews_ltm"] = pd.Series(ltm)
    g = growth_comparison(
        dict(city["n_active"]), ltm)

    print("REC-13 — anuncios activos por snapshot (Donostia)\n")
    print(city.to_string(), "\n")
    print("activos por barrio (primera y última fecha):\n")
    print(por_barrio[[SNAPSHOTS[0], SNAPSHOTS[-1]]].to_string(), "\n")
    print(f"ventana {g['window'][0]} → {g['window'][1]}:")
    print(f"  oferta activa   {g['active_growth_pct']:+.1f}%")
    print(f"  reseñas 12m     {g['reviews_growth_pct']:+.1f}%")
    print(f"  bias_ratio      {g['bias_ratio']:.2f} "
          "(>1: el proxy de reseñas exagera el crecimiento de la oferta)")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        city.to_csv(OUTDIR / "airbnb_snapshots_city.csv")
        por_barrio.rename_axis("barrio_id").to_csv(
            OUTDIR / "airbnb_snapshots_barrio.csv")
        print(f"\n→ guardado en {OUTDIR}/airbnb_snapshots_*.csv")


if __name__ == "__main__":
    main()
