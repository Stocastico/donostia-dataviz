"""Sprint A — análisis sobre los datos existentes (sin datos nuevos).

Reproducible con la única dependencia del pipeline: pandas + numpy
(sin scipy/sklearn). Lee el indicator store `data/metrics_long.csv` y produce:

  1. Correlaciones robustas (Pearson + Spearman[rangos] + leave-one-out).
  2. Velocidad de cambio por barrio (tasas anualizadas 2016→último año).
  3. Tipología de barrios (k-means k=4, semilla fija) — perfiles descriptivos.

Uso:
    python analysis/sprint_a.py            # imprime el informe
    python analysis/sprint_a.py --save     # además vuelca CSVs a analysis/output/

Nota metodológica: N=19 barrios (menos en varias métricas). Los resultados son
descriptivos, no inferenciales; el clustering se presenta como perfiles, no como
verdad. Ver docs/ANALISIS-SPRINT-A.md.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "metrics_long.csv"
OUTDIR = Path(__file__).resolve().parent / "output"

# Outliers conocidos (centro turístico) para el leave-one-out.
OUTLIERS = ["erdialdea", "gros"]

# Métricas de corte transversal (último valor disponible por barrio).
CROSS_METRICS = [
    "income_total", "rent_eur_m2", "pct_university", "pct_foreign",
    "vut_density", "housing_tension", "schools_per_1000",
]
# Variables para el perfil/cluster (las 4 que sugiere el feedback).
CLUSTER_VARS = ["income_total", "pct_university", "vut_density", "rent_eur_m2"]
# Métricas con serie temporal para velocidad de cambio.
TREND_METRICS = {
    "income_total": "level", "rent_eur_m2": "level", "population": "level",
    "pct_university": "pp", "pct_foreign": "pp",
}
TREND_WINDOW_START = 2016  # ventana reciente comparable entre métricas


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df["period"] = df["period"].astype(str)
    return df


def latest_cross(df: pd.DataFrame, metric: str) -> pd.Series:
    """Último valor disponible por barrio (maneja el snapshot 'actual')."""
    g = df[df.metric_id == metric].sort_values("period").groupby("barrio_id").tail(1)
    return g.set_index("barrio_id")["value"].rename(metric)


def spearman(x: pd.Series, y: pd.Series) -> float:
    """Spearman = Pearson sobre rangos (evita la dependencia de scipy)."""
    return x.rank().corr(y.rank())


# ---------------------------------------------------------------------------
# 1. Correlaciones robustas
# ---------------------------------------------------------------------------
def correlations(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    cols = {m: latest_cross(df, m) for m in CROSS_METRICS}
    X = pd.concat(cols.values(), axis=1)
    pear = X.corr(method="pearson")
    spear = X.apply(lambda c: X.apply(lambda d: spearman(c, d)))

    key_pairs = [
        ("vut_density", "rent_eur_m2"),
        ("income_total", "pct_foreign"),
        ("vut_density", "income_total"),
        ("rent_eur_m2", "income_total"),
        ("pct_university", "income_total"),
        ("housing_tension", "income_total"),
    ]
    robustness = []
    for a, b in key_pairs:
        j = pd.concat([cols[a], cols[b]], axis=1).dropna()
        row = {
            "pair": f"{a} ~ {b}", "n": len(j),
            "pearson": round(j[a].corr(j[b]), 3),
            "spearman": round(spearman(j[a], j[b]), 3),
        }
        jj = j.drop(index=OUTLIERS, errors="ignore")
        row["pearson_sin_outliers"] = round(jj[a].corr(jj[b]), 3)
        row["n_sin_outliers"] = len(jj)
        robustness.append(row)
    return pear.round(3), spear.round(3), robustness


# ---------------------------------------------------------------------------
# 2. Velocidad de cambio
# ---------------------------------------------------------------------------
def annualized_rate(years: np.ndarray, vals: np.ndarray, kind: str) -> float:
    """Pendiente anualizada por regresión lineal sobre la ventana.

    kind='level' -> %/año (sobre la media); kind='pp' -> puntos pct/año.
    """
    if len(years) < 3:
        return np.nan
    slope = np.polyfit(years, vals, 1)[0]
    if kind == "pp":
        return round(slope, 3)               # puntos porcentuales / año
    return round(100.0 * slope / np.mean(vals), 3)  # %/año relativo a la media


def velocity(df: pd.DataFrame) -> pd.DataFrame:
    out: dict[str, dict[str, float]] = {}
    for metric, kind in TREND_METRICS.items():
        g = df[(df.metric_id == metric)].copy()
        g = g[pd.to_numeric(g.period, errors="coerce") >= TREND_WINDOW_START]
        g["year"] = g.period.astype(int)
        for bid, gb in g.groupby("barrio_id"):
            gb = gb.sort_values("year")
            out.setdefault(bid, {})[metric] = annualized_rate(
                gb.year.to_numpy(float), gb.value.to_numpy(float), kind
            )
    vel = pd.DataFrame(out).T.sort_index()
    # Composite: media de |z-score| de las tasas (cuánto se mueve el barrio).
    z = (vel - vel.mean()) / vel.std()
    vel["speed_index"] = z.abs().mean(axis=1).round(3)
    return vel.sort_values("speed_index", ascending=False)


# ---------------------------------------------------------------------------
# 3. Tipología de barrios (k-means numpy, semilla fija)
# ---------------------------------------------------------------------------
def kmeans(X: np.ndarray, k: int, seed: int = 42, n_init: int = 50,
           max_iter: int = 300) -> np.ndarray:
    rng = np.random.default_rng(seed)
    best_labels, best_inertia = None, np.inf
    for _ in range(n_init):
        centers = X[rng.choice(len(X), k, replace=False)]
        for _ in range(max_iter):
            d = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
            labels = d.argmin(1)
            new = np.array([X[labels == j].mean(0) if (labels == j).any()
                            else centers[j] for j in range(k)])
            if np.allclose(new, centers):
                break
            centers = new
        inertia = ((X - centers[labels]) ** 2).sum()
        if inertia < best_inertia:
            best_inertia, best_labels = inertia, labels
    return best_labels


def profiles(df: pd.DataFrame, k: int = 4) -> tuple[pd.DataFrame, pd.DataFrame]:
    X = pd.concat([latest_cross(df, m) for m in CLUSTER_VARS], axis=1).dropna()
    Z = (X - X.mean()) / X.std()
    labels = kmeans(Z.to_numpy(float), k=k)
    X = X.assign(cluster=labels)
    # Etiqueta legible según el centroide (z-score) de cada cluster.
    cent = Z.assign(cluster=labels).groupby("cluster").mean()
    names = {}
    for c, row in cent.iterrows():
        if row["vut_density"] > 0.6 and row["rent_eur_m2"] > 0.3:
            names[c] = "Central turístico de renta alta"
        elif row["income_total"] > 0.5 and row["vut_density"] < 0.2:
            names[c] = "Residencial acomodado, poco turístico"
        elif row["income_total"] < -0.3:
            names[c] = "Popular / en tensión"
        else:
            names[c] = "Transicional / mixto"
    X["perfil"] = X.cluster.map(names)
    return X.sort_values("cluster"), cent.round(2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true", help="vuelca CSVs a analysis/output/")
    args = ap.parse_args()
    df = load()

    print("=" * 72)
    print("SPRINT A — análisis sobre datos existentes  ·  Donostia Dataviz")
    print("=" * 72)

    pear, spear, robust = correlations(df)
    print("\n## 1. CORRELACIONES (corte transversal, último año por métrica)\n")
    print("Matriz de Pearson:\n", pear.to_string(), sep="")
    print("\nRobustez de los pares clave (Pearson, Spearman, sin outliers centro):\n")
    rob = pd.DataFrame(robust)
    print(rob.to_string(index=False))

    print("\n## 2. VELOCIDAD DE CAMBIO (tasas anualizadas, 2016→último año)\n")
    vel = velocity(df)
    print("level=%/año · pp=puntos pct/año · speed_index=media |z| de las tasas\n")
    print(vel.round(2).to_string())

    print("\n## 3. TIPOLOGÍA DE BARRIOS (k-means k=4, vars estandarizadas)\n")
    clusters, cent = profiles(df)
    print("Centroides (z-score) por cluster:\n", cent.to_string(), sep="")
    print("\nAsignación de barrios:\n")
    print(clusters[["income_total", "rent_eur_m2", "vut_density",
                    "pct_university", "perfil"]].round(1).to_string())

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        pear.to_csv(OUTDIR / "corr_pearson.csv")
        spear.to_csv(OUTDIR / "corr_spearman.csv")
        rob.to_csv(OUTDIR / "corr_robustness.csv", index=False)
        vel.to_csv(OUTDIR / "velocity.csv")
        clusters.to_csv(OUTDIR / "clusters.csv")
        print(f"\n[guardado] CSVs en {OUTDIR}")


if __name__ == "__main__":
    main()
