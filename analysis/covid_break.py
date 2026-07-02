"""AN-20 — ¿2020 aceleró la turistificación o solo la interrumpió?

Idea RDD *con cautela por N*: se comparan las pendientes lineales de cada
serie **antes** (≤2019) y **después** (≥2021) del shock, excluyendo el cráter
de 2020, y el año en que cada serie recupera su nivel de 2019.

Series ciudad: actividad Airbnb (suma de barrios, anual), pernoctaciones
hoteleras (suma de meses completos, `series_long`), alquiler medio €/m².
Por barrio: pendientes pre/post de la actividad Airbnb — ¿cambió el mapa de
la presión turística, o solo su nivel?

⚠️ Tramos de 4–9 puntos: pendientes descriptivas, sin inferencia formal.

Solo pandas + numpy. Uso:
    python analysis/covid_break.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import lead_lag
from lead_lag import _panel

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "datos" / "procesado" / "tablas"
OUTDIR = Path(__file__).resolve().parent / "output"
BREAK_YEAR = 2020
MIN_POINTS = 3


def segmented_slopes(s: pd.Series) -> dict:
    """Pendientes lineales pre (≤2019) y post (≥2021); 2020 fuera de ambas."""
    s = s.dropna()
    years = s.index.to_numpy(float)
    pre = s[years < BREAK_YEAR]
    post = s[years > BREAK_YEAR]

    def slope(seg: pd.Series) -> float:
        if len(seg) < MIN_POINTS:
            return float("nan")
        return float(np.polyfit(seg.index.to_numpy(float), seg.to_numpy(float), 1)[0])

    sp, so = slope(pre), slope(post)
    acel = so / sp if np.isfinite(sp) and np.isfinite(so) and sp != 0 else float("nan")
    return {"slope_pre": sp, "slope_post": so,
            "n_pre": len(pre), "n_post": len(post), "aceleracion": acel}


def recovery_year(s: pd.Series) -> int | None:
    """Primer año >2020 en que la serie iguala o supera su valor de 2019."""
    s = s.dropna()
    if 2019 not in s.index:
        return None
    ref = s[2019]
    after = s[s.index > BREAK_YEAR]
    hit = after[after >= ref]
    return int(hit.index.min()) if len(hit) else None


# ---------------------------------------------------------------------------
# datos reales
# ---------------------------------------------------------------------------
def _city_series() -> dict[str, pd.Series]:
    df = pd.read_csv(TABLES / "metrics_long.csv")
    df["period"] = df["period"].astype(str)
    act = _panel(df, "airbnb_activity").sum(axis=0, min_count=1)
    rent = _panel(df, "rent_eur_m2").mean(axis=0)

    ser = pd.read_csv(TABLES / "series_long.csv")
    hotel = ser[ser.series_id == "overnight_stays"]
    by_year = hotel.groupby("year").agg(value=("value", "sum"), meses=("month", "nunique"))
    hotel_full = by_year[by_year.meses == 12]["value"]  # solo años completos

    out = {"airbnb_activity_city": act, "rent_city_mean": rent}
    if len(hotel_full):
        out["hotel_overnights_city"] = hotel_full
    return out


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(tabla ciudad, tabla por barrio de actividad Airbnb)."""
    city_rows = {}
    for name, s in _city_series().items():
        seg = segmented_slopes(s)
        seg["recuperacion"] = recovery_year(s)
        city_rows[name] = seg
    city = pd.DataFrame(city_rows).T

    df = pd.read_csv(TABLES / "metrics_long.csv")
    df["period"] = df["period"].astype(str)
    act = _panel(df, "airbnb_activity")
    rows = {bid: segmented_slopes(row) for bid, row in act.iterrows()}
    barrios = pd.DataFrame(rows).T.dropna(subset=["slope_pre", "slope_post"])
    return city, barrios


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    city, barrios = build_tables()
    print("=" * 74)
    print("AN-20 · RUPTURA COVID — pendientes pre (≤2019) vs post (≥2021), 2020 fuera")
    print("=" * 74)
    print("\n## Ciudad\n")
    print(city.round(3).to_string())
    print("\naceleracion = pendiente_post / pendiente_pre (>1 = se aceleró tras COVID)")
    print("recuperacion = primer año que iguala el nivel de 2019.")

    print("\n## Actividad Airbnb por barrio (reseñas/1000 hab·año)\n")
    b = barrios.sort_values("slope_post", ascending=False)
    b["aceleracion"] = b["aceleracion"].round(2)
    print(b.round(2).to_string())

    # Spearman = Pearson sobre rangos (sin scipy, como sprint_a.spearman)
    pre_rank = barrios["slope_pre"].rank(ascending=False)
    post_rank = barrios["slope_post"].rank(ascending=False)
    tau = pre_rank.corr(post_rank)
    print(f"\nCorrelación (Spearman) entre el ranking de crecimiento pre y post: {tau:.2f}")
    print("(alta = el mapa de la presión turística no cambió, solo su ritmo)")

    print("\n⚠️ Tramos de 4–9 puntos: descriptivo (idea RDD), sin inferencia formal.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        city.to_csv(OUTDIR / "covid_break_city.csv")
        barrios.to_csv(OUTDIR / "covid_break_barrios.csv")
        print(f"\n[guardado] {OUTDIR/'covid_break_city.csv'} · "
              f"{OUTDIR/'covid_break_barrios.csv'}")


if __name__ == "__main__":
    main()
