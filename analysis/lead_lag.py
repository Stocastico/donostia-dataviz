"""AN-6 — Lead/lag: ¿la presión turística precede a la subida del alquiler?

EXPLORATORIO. Cruza dos paneles barrio×año ya en el pipeline:

  * ``airbnb_activity`` — reseñas/año por 1000 ab. (proxy de presión turística;
    derivado de Inside Airbnb reviews, REC-4),
  * ``rent_eur_m2``     — alquiler medio €/m² (EMA, anual).

El problema metodológico que obliga a ser cautos:

  1. El alquiler es **anual** (2016→2024 ≈ 9 puntos) → poca resolución temporal.
  2. Las reseñas crecen con la **adopción de la plataforma**, no solo con la
     ocupación → tendencia común al alza que inflaría una correlación de niveles.

Por eso NO correlacionamos niveles. Trabajamos en **primeras diferencias**
(variación interanual), que quitan la tendencia común, y montamos un **panel** de
todos los barrios×años para ganar N. Reportamos la correlación de Pearson de
Δactividad(t−k) con Δalquiler(t) para varios desfases k (k>0 = turismo precede al
alquiler), con su N. Es una señal, no una prueba causal (MET-3).

Uso:
    python analysis/lead_lag.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "datos" / "procesado" / "tablas" / "metrics_long.csv"
OUTDIR = Path(__file__).resolve().parent / "output"
LAGS = range(-1, 3)  # k: alquiler precede (−1) … turismo precede (+1,+2)


def _panel(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Tabla barrio×año (numérica) para una métrica anual."""
    g = df[df.metric_id == metric].copy()
    g = g[pd.to_numeric(g.period, errors="coerce").notna()]
    g["year"] = g.period.astype(int)
    return g.pivot_table(index="barrio_id", columns="year", values="value")


def _diffs(panel: pd.DataFrame) -> pd.DataFrame:
    """Variación interanual (primeras diferencias) por barrio, año a año."""
    return panel.sort_index(axis=1).diff(axis=1)


def _pearson(x: np.ndarray, y: np.ndarray) -> tuple[float, int]:
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return float("nan"), len(x)
    return float(np.corrcoef(x, y)[0, 1]), len(x)


def lead_lag(d_act: pd.DataFrame, d_rent: pd.DataFrame, lags=LAGS) -> pd.DataFrame:
    """Para cada desfase k, apila (Δactividad[year−k], Δalquiler[year]) de todos
    los barrios y años solapados y calcula la correlación del panel."""
    rows = []
    rent_years = list(d_rent.columns)
    barrios = sorted(set(d_act.index) & set(d_rent.index))
    for k in lags:
        xs, ys = [], []
        for year in rent_years:
            src = year - k
            if src not in d_act.columns:
                continue
            for b in barrios:
                xs.append(d_act.at[b, src] if src in d_act.columns else np.nan)
                ys.append(d_rent.at[b, year])
        r, n = _pearson(np.array(xs, float), np.array(ys, float))
        rows.append({"lag_anni": k, "r": round(r, 3), "n": n,
                     "lectura": _read(k)})
    return pd.DataFrame(rows)


def _read(k: int) -> str:
    if k > 0:
        return f"turismo precede al alquiler en {k} año(s)"
    if k < 0:
        return f"alquiler precede al turismo en {abs(k)} año(s)"
    return "mismo año (contemporáneo)"


def city_series(df: pd.DataFrame) -> pd.DataFrame:
    """Serie ciudad: actividad total (suma) y alquiler medio por año."""
    act = _panel(df, "airbnb_activity").sum(axis=0, min_count=1)
    rent = _panel(df, "rent_eur_m2").mean(axis=0)
    return pd.DataFrame({"airbnb_activity_sum": act, "rent_mean": rent}).dropna()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    df = pd.read_csv(DATA)
    df["period"] = df["period"].astype(str)

    act = _panel(df, "airbnb_activity")
    rent = _panel(df, "rent_eur_m2")
    d_act, d_rent = _diffs(act), _diffs(rent)
    table = lead_lag(d_act, d_rent)

    print("=" * 74)
    print("AN-6 · LEAD/LAG turismo → alquiler  (Donostia Dataviz, EXPLORATORIO)")
    print("=" * 74)
    print(f"\nPanel: {len(set(act.index) & set(rent.index))} barrios · "
          f"años de alquiler {int(rent.columns.min())}–{int(rent.columns.max())}")
    print("Primeras diferencias (Δ interanual), correlación de panel:\n")
    print(table.to_string(index=False))

    best = table.loc[table.r.abs().idxmax()] if table.r.notna().any() else None
    if best is not None:
        print(f"\nDesfase con |r| máximo: lag={int(best.lag_anni)} → r={best.r} "
              f"(n={int(best.n)}) — {best.lectura}.")

    cs = city_series(df)
    print("\n— Contexto ciudad (niveles, SIN detrend — solo descriptivo) —")
    print(cs.round(2).to_string())

    print("\nAVISOS (MET-3): correlación ≠ causalidad; alquiler anual (pocos puntos); "
          "\nlas reseñas crecen con la plataforma → leído en diferencias, exploratorio.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        table.to_csv(OUTDIR / "lead_lag.csv", index=False)
        print(f"\n[guardado] {OUTDIR / 'lead_lag.csv'}")


if __name__ == "__main__":
    main()
