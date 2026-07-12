"""AN-14 — Estacionalidad turística por barrio: ¿quién depende del verano?

Las reseñas de Inside Airbnb fechadas ("modelo San Francisco": una reseña ≈
una estancia reseñada) permiten bajar la estacionalidad a barrio, cosa que
las pernoctaciones del INE (solo ciudad) no dan. Cada listing del snapshot
regional de Euskadi se asigna a barrio por punto-en-polígono contra
`barrios.geojson` (mismo principio que el pipeline, REC-4) y sus reseñas
heredan el barrio.

Medidas por barrio sobre el perfil mensual agregado (años completos):

- **ratio verano/invierno**: media mensual de reseñas jun–sep / nov–feb.
- **Gini mensual**: 0 = reparto uniforme, 11/12 ≈ todo en un mes.
- **% verano**: cuota de reseñas en jun–sep (uniforme = 33 %).
- perfil de 12 cuotas mensuales (la "rosa" de estacionalidad, para viz).

Lecturas honestas: proxy de estancias (no ocupación); el último año del
snapshot (parcial) se descarta; los barrios con pocas reseñas se filtran
(min_reviews) porque su perfil es ruido; la agregación 2011–2024 mezcla la
era pre y post COVID — el informe añade la ventana 2022–2024 como contraste.

Solo pandas + numpy (+ shapely, ya dependencia del pipeline). Requiere los
crudos (bash datos/input/descargar_raw.sh). Uso:
    python analysis/tourism_seasonality.py [--save]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "datos" / "input" / "raw"
LISTINGS_GZ = RAW / "airbnb_listings.csv.gz"
REVIEWS_GZ = RAW / "airbnb_reviews.csv.gz"
GEOJSON = ROOT / "web" / "src" / "data" / "barrios.geojson"
OUTDIR = Path(__file__).resolve().parent / "output"

# Snapshot Inside Airbnb 2026-06-30 → 2026 está incompleto.
LAST_COMPLETE_YEAR = 2025
VERANO = (6, 7, 8, 9)
INVIERNO = (11, 12, 1, 2)
MIN_REVIEWS = 300          # por debajo, el perfil mensual es ruido
RECENT = (2022, 2024)      # ventana de contraste post-COVID


# ------------------------------------------------------ punto → barrio ----
def assign_listings(listings: pd.DataFrame, features: list[dict]) -> pd.Series:
    """listing id → barrio_id por punto-en-polígono (fuera de Donostia: fuera)."""
    lon = listings["longitude"].to_numpy(float)
    lat = listings["latitude"].to_numpy(float)
    barrio = np.full(len(listings), None, dtype=object)
    for f in features:
        geom = shape(f["geometry"])
        inside = shapely.contains_xy(geom, lon, lat)
        barrio[inside] = f["properties"]["barrio_id"]
    out = pd.Series(barrio, index=listings["id"].to_numpy(), name="barrio")
    return out.dropna()


# ------------------------------------------------------ años completos ----
def complete_years_mask(dates: pd.Series,
                        last_complete: int = LAST_COMPLETE_YEAR) -> pd.Series:
    """True para las reseñas de años completos (el año del snapshot se corta)."""
    return dates.dt.year <= last_complete


# ------------------------------------------------------- perfil mensual ----
def monthly_profile(reviews: pd.DataFrame) -> pd.DataFrame:
    """Cuotas mensuales (12 columnas que suman 1) por barrio."""
    counts = (reviews.assign(month=reviews["date"].dt.month)
              .pivot_table(index="barrio", columns="month", values="date",
                           aggfunc="count")
              .reindex(columns=range(1, 13)).fillna(0.0))
    return counts.div(counts.sum(axis=1), axis=0)


def summer_winter_ratio(profile: pd.DataFrame) -> pd.Series:
    """Media mensual de cuota jun–sep / nov–feb (inf si el invierno es 0)."""
    verano = profile[list(VERANO)].mean(axis=1)
    invierno = profile[list(INVIERNO)].mean(axis=1)
    with np.errstate(divide="ignore"):
        return pd.Series(np.where(invierno > 0, verano / invierno, np.inf),
                         index=profile.index, name="ratio_verano_invierno")


def gini(shares: np.ndarray) -> float:
    """Gini de concentración mensual (0 = uniforme, 11/12 = un solo mes)."""
    x = np.sort(np.asarray(shares, dtype=float))
    n = len(x)
    if x.sum() == 0:
        return float("nan")
    cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def seasonality_table(reviews: pd.DataFrame,
                      min_reviews: int = MIN_REVIEWS) -> pd.DataFrame:
    """Tabla por barrio: n, ratio verano/invierno, Gini mensual, % verano."""
    n = reviews.groupby("barrio").size().rename("n_reviews")
    profile = monthly_profile(reviews)
    tab = pd.DataFrame({
        "n_reviews": n,
        "ratio_verano_invierno": summer_winter_ratio(profile),
        "gini_mensual": profile.apply(lambda r: gini(r.to_numpy()), axis=1),
        "pct_verano": profile[list(VERANO)].sum(axis=1),
    })
    return tab[tab.n_reviews >= min_reviews].sort_values(
        "ratio_verano_invierno", ascending=False)


# --------------------------------------------------------------- carga ----
def load_reviews() -> pd.DataFrame:
    """Reseñas de Donostia con barrio asignado y solo años completos."""
    for p in (LISTINGS_GZ, REVIEWS_GZ):
        if not p.exists():
            raise FileNotFoundError(
                f"falta {p} — ejecuta `bash datos/input/descargar_raw.sh`")
    listings = pd.read_csv(LISTINGS_GZ, usecols=["id", "latitude", "longitude"])
    features = json.loads(GEOJSON.read_text(encoding="utf-8"))["features"]
    barrio = assign_listings(listings, features)

    reviews = pd.read_csv(REVIEWS_GZ, usecols=["listing_id", "date"],
                          parse_dates=["date"])
    reviews["barrio"] = reviews["listing_id"].map(barrio)
    reviews = reviews.dropna(subset=["barrio"])
    return reviews[complete_years_mask(reviews["date"])].reset_index(drop=True)


# -------------------------------------------------------------- informe ----
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    reviews = load_reviews()
    years = reviews["date"].dt.year
    print("=" * 76)
    print("AN-14 · ESTACIONALIDAD TURÍSTICA POR BARRIO  (reseñas Inside Airbnb)")
    print("=" * 76)
    print(f"\n{len(reviews):,} reseñas de Donostia, {years.min()}–{years.max()}"
          f" (años completos), {reviews.barrio.nunique()} barrios con listings."
          .replace(",", "."))

    tab = seasonality_table(reviews)
    print(f"\nPor barrio (min {MIN_REVIEWS} reseñas; uniforme: ratio 1, "
          f"% verano 33 %):\n")
    print(tab.to_string(float_format=lambda v: f"{v:.2f}"))

    ciudad = seasonality_table(reviews.assign(barrio="(ciudad)"), 1)
    print("\nReferencia ciudad:\n")
    print(ciudad.to_string(float_format=lambda v: f"{v:.2f}"))

    recent = reviews[years.between(*RECENT)]
    tab_recent = seasonality_table(recent)
    print(f"\nVentana {RECENT[0]}–{RECENT[1]} (contraste post-COVID):\n")
    print(tab_recent.to_string(float_format=lambda v: f"{v:.2f}"))

    print("\nLectura: reseña ≈ estancia reseñada (proxy, no ocupación); el")
    print("perfil mensual agregado mezcla años — la ventana reciente contrasta.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        tab.to_csv(OUTDIR / "tourism_seasonality.csv")
        tab_recent.to_csv(OUTDIR / "tourism_seasonality_2022_2024.csv")
        monthly_profile(reviews).to_csv(OUTDIR / "seasonality_monthly.csv")
        print(f"\n[guardado] {OUTDIR / 'tourism_seasonality.csv'}")
        print(f"[guardado] {OUTDIR / 'tourism_seasonality_2022_2024.csv'}")
        print(f"[guardado] {OUTDIR / 'seasonality_monthly.csv'} (rosa mensual)")


if __name__ == "__main__":
    main()
