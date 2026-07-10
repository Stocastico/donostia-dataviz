"""REC-25 — Precio de venta €/m² por barrio (idealista): serie y encarecimiento.

Reproduce las cifras que la Historia 1 de ``output/historias.html`` cuenta sobre
el mercado de **compra**, a partir del snapshot curado
``datos/input/precios_venta_idealista.csv`` (serie mensual de oferta por zona
idealista, ~2010–2026):

- **media anual** por zona (≥3 meses/año),
- **subida desde el suelo** post-crisis (mínimo → último dato) por zona,
- **subida de ciudad** en ventanas 2016→2023 y 2016→2026 (media de zonas con
  ambos años), para el cruce con la asequibilidad de HU-7 (el alquiler subió
  +24,8 %, el salario +21,8 % y el IPC +20,4 % en 2016–2023; ver
  ``housing_affordability.py``),
- **brecha de nivel** centro/este en el último año.

Lecturas honestas: son precios **de oferta** (anuncios idealista), no de
transacción → cota superior de lo que se paga. Las zonas idealista no son los 19
barrios oficiales (algunas agregadas); Miramón-Zorroaga y Loiola-Martutene se
excluyen al origen (serie duplicada que acaba en 2019). Descriptivo, no causal.

Solo pandas. No necesita crudos ni red. Uso:
    python analysis/precios_venta.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "datos" / "input" / "precios_venta_idealista.csv"
OUTDIR = Path(__file__).resolve().parent / "output"
MIN_MONTHS = 3
FIRST_YEAR = 2011
# Zona "techo" (centro) y "suelo" (este asequible) para la brecha de nivel.
CEIL, FLOOR = "Centro-Miraconcha", "Altza-Bidebieta"


def annual_means(df: pd.DataFrame) -> pd.DataFrame:
    """zona × año → media €/m² de los meses presentes (≥ MIN_MONTHS, ≥ FIRST_YEAR)."""
    d = df.copy()
    d["year"] = d["mes"].str.slice(0, 4).astype(int)
    d = d[d["year"] >= FIRST_YEAR]
    g = d.groupby(["zona_idealista", "year"])["precio_eur_m2"]
    means = g.mean().round().where(g.count() >= MIN_MONTHS).dropna()
    return means.unstack("year")  # index=zona, columns=year


def surge_from_trough(annual: pd.DataFrame) -> pd.DataFrame:
    """Por zona: año/valor del mínimo, último año/valor y % de subida mínimo→último."""
    rows = []
    for zona, row in annual.iterrows():
        s = row.dropna()
        if s.empty:
            continue
        tmin_y = int(s.idxmin())
        last_y = int(s.index.max())
        rows.append({
            "zona": zona, "min_year": tmin_y, "min": s.loc[tmin_y],
            "last_year": last_y, "last": s.loc[last_y],
            "surge_pct": round((s.loc[last_y] / s.loc[tmin_y] - 1) * 100, 1),
        })
    return pd.DataFrame(rows).sort_values("last", ascending=False).reset_index(drop=True)


def window_growth(annual: pd.DataFrame, y0: int, y1: int) -> pd.Series:
    """% de subida y0→y1 por zona (solo las que tienen ambos años)."""
    if y0 not in annual.columns or y1 not in annual.columns:
        return pd.Series(dtype=float)
    both = annual[[y0, y1]].dropna()
    return ((both[y1] / both[y0] - 1) * 100).round(1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--save", action="store_true", help="escribe CSVs en analysis/output/")
    args = ap.parse_args()

    df = pd.read_csv(CSV)
    annual = annual_means(df)

    surge = surge_from_trough(annual)
    print("— Subida desde el suelo post-crisis (media anual, €/m²) —\n")
    print(surge.to_string(index=False))
    print(f"\nRango de subida mínimo→último: "
          f"+{surge['surge_pct'].min():.0f} % a +{surge['surge_pct'].max():.0f} %")

    for y0, y1 in [(2016, 2023), (2016, 2026)]:
        w = window_growth(annual, y0, y1)
        if not w.empty:
            print(f"\n— Ciudad {y0}→{y1}: media +{w.mean():.0f} % "
                  f"(min +{w.min():.0f} {w.idxmin()} · max +{w.max():.0f} {w.idxmax()}) —")
    print("  · Referencia HU-7 (2016–2023): alquiler +24,8 % · salario +21,8 % · IPC +20,4 %.")
    print("    → comprar se encareció más deprisa que todo lo demás.")

    if CEIL in annual.index and FLOOR in annual.index:
        last = int(annual.columns.max())
        c, f = annual.loc[CEIL, last], annual.loc[FLOOR, last]
        print(f"\n— Brecha de nivel {last}: {CEIL} {c:.0f} / {FLOOR} {f:.0f} = {c / f:.1f}× —")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        annual.to_csv(OUTDIR / "precios_venta_anual.csv")
        surge.to_csv(OUTDIR / "precios_venta_subida.csv", index=False)
        print(f"\n[guardado] {OUTDIR / 'precios_venta_anual.csv'}")
        print(f"[guardado] {OUTDIR / 'precios_venta_subida.csv'}")


if __name__ == "__main__":
    main()
