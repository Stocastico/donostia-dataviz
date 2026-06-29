"""AN-4 y AN-5 — distribución y polarización entre barrios (solo datos existentes).

Reproducible con pandas + numpy (sin scipy/sklearn). Lee `data/metrics_long.csv`.

  AN-5  Polarización de la renta en el tiempo (2016–2023)
        - Gini inter-barrio (sin ponderar y ponderado por población).
        - Ratio P90/P10 y ratio max/min.
        - ¿Se ensancha la brecha territorial?

  AN-4  Matriz niveles vs. variaciones
        - Cada barrio en un cuadrante respecto a la MEDIANA de la ciudad.
          Insumo de la coropleta bivariada (VIZ-3).

Cautela: el Gini inter-barrio mide desigualdad TERRITORIAL (entre barrios), no
la total (ignora la dispersión intra-barrio) → cota inferior. N=17 con renta.
Outlier conocido: Miramón-Zorroaga 2022 (renta per cápita 59.243 €, barrio
pequeño y volátil) infla el Gini sin ponderar de 2022 → mirar el ponderado.

Uso:  python analysis/distribucion_barrios.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "metrics_long.csv"
OUTDIR = Path(__file__).resolve().parent / "output"


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df["period"] = df["period"].astype(str)
    return df


def panel(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    g = df[df.metric_id == metric].copy()
    g = g[pd.to_numeric(g.period, errors="coerce").notna()]
    g["year"] = g.period.astype(int)
    return g.pivot_table(index="barrio_id", columns="year", values="value")


def latest(df: pd.DataFrame, metric: str) -> pd.Series:
    g = df[df.metric_id == metric].sort_values("period").groupby("barrio_id").tail(1)
    return g.set_index("barrio_id")["value"].rename(metric)


def gini(x: np.ndarray, w: np.ndarray | None = None) -> float:
    x = np.asarray(x, float)
    if w is None:
        w = np.ones_like(x)
    w = np.asarray(w, float)
    mean_w = np.sum(w * x) / np.sum(w)
    num = np.sum(w[:, None] * w[None, :] * np.abs(x[:, None] - x[None, :]))
    return num / (2 * np.sum(w) ** 2 * mean_w)


def annual_rate(row: pd.Series, kind: str) -> float:
    s = row.dropna()
    if len(s) < 3:
        return np.nan
    years = s.index.to_numpy(float)
    slope = np.polyfit(years, s.to_numpy(float), 1)[0]
    return slope if kind == "pp" else 100.0 * slope / s.to_numpy(float).mean()


def an5_polarizacion(df: pd.DataFrame) -> pd.DataFrame:
    inc = panel(df, "income_total")
    pop = panel(df, "population")
    rows = []
    for year in inc.columns:
        x = inc[year].dropna()
        if len(x) < 5:
            continue
        w = pop[year].reindex(x.index) if year in pop.columns else None
        wok = w is not None and w.notna().all()
        rows.append({
            "year": int(year),
            "n": len(x),
            "gini": round(gini(x.to_numpy()), 4),
            "gini_pond_pob": round(gini(x.to_numpy(), w.to_numpy()), 4) if wok else np.nan,
            "p90_p10": round(np.percentile(x, 90) / np.percentile(x, 10), 3),
            "ratio_max_min": round(x.max() / x.min(), 3),
            "renta_max": int(x.max()),
            "renta_min": int(x.min()),
        })
    return pd.DataFrame(rows).set_index("year")


def quad(a: pd.Series, b: pd.Series, an: str, bn: str,
         awords=("alto", "bajo"), bwords=("rápido", "lento")) -> pd.DataFrame:
    """Clasifica cada barrio en 2×2 respecto a la mediana de la ciudad."""
    amed, bmed = a.median(), b.median()
    out = pd.DataFrame({an: a, bn: b}).dropna()
    def label(r):
        la = awords[0] if r[an] >= amed else awords[1]
        lb = bwords[0] if r[bn] >= bmed else bwords[1]
        return f"{an} {la} · {bn} {lb}"
    out["cuadrante"] = out.apply(label, axis=1)
    return out.sort_values(bn, ascending=False)


def an4_matriz(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rent = panel(df, "rent_eur_m2")
    inc = panel(df, "income_total")
    rent_level = rent.ffill(axis=1).iloc[:, -1]
    rent_growth = rent.apply(lambda r: annual_rate(r, "level"), axis=1)
    inc_level = inc.ffill(axis=1).iloc[:, -1]
    tension = latest(df, "housing_tension")
    return {
        # nivel × tasa de cambio → "rápido/lento"
        "alquiler_nivel_x_crecimiento": quad(
            rent_level, rent_growth, "alquiler", "crec"),
        # nivel × nivel → "alta/baja"
        "renta_nivel_x_tension": quad(
            inc_level, tension, "renta", "tension", bwords=("alta", "baja")),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()
    df = load()

    print("=" * 76)
    print("AN-5 · POLARIZACIÓN DE LA RENTA ENTRE BARRIOS (2016–2023)")
    print("=" * 76)
    pol = an5_polarizacion(df)
    print(pol.to_string())
    g0, g1 = pol["gini_pond_pob"].iloc[0], pol["gini_pond_pob"].iloc[-1]
    print(f"\nGini ponderado {pol.index[0]}→{pol.index[-1]}: {g0} → {g1}  "
          f"({'sube' if g1 > g0 else 'baja/estable'} {abs(g1-g0):.4f})")
    print("Nota: 2022 sin ponderar está inflado por Miramón-Zorroaga (outlier).")

    print("\n" + "=" * 76)
    print("AN-4 · MATRIZ NIVELES vs. VARIACIONES")
    print("=" * 76)
    mats = an4_matriz(df)
    for name, m in mats.items():
        print(f"\n## {name}\n")
        print(m.round(2).to_string())
        print("\n  recuento por cuadrante:")
        print(m["cuadrante"].value_counts().to_string())

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        pol.to_csv(OUTDIR / "an5_polarizacion.csv")
        for name, m in mats.items():
            m.round(3).to_csv(OUTDIR / f"an4_{name}.csv")
        print(f"\n[guardado] CSVs en {OUTDIR}")


if __name__ == "__main__":
    main()
