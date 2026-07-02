"""AN-15 — Estadística espacial: Moran's I global y local (LISA).

¿Los barrios parecidos se agrupan en el espacio? Moran's I global con p-valor
por permutación (sin supuestos distribucionales, apropiado con N=13–19) y
Moran local por barrio, sobre las métricas clave del proyecto.

Pesos: contigüidad tipo queen derivada de `web/src/data/barrios.geojson`
(shapely, que ya es dependencia del pipeline; se consideran vecinos los
polígonos a <~10 m para tolerar pequeños huecos de digitalización), filas
estandarizadas.

Uso:
    python analysis/spatial_autocorrelation.py [--save]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import shape

import sprint_a
from sprint_a import latest_cross

ROOT = Path(__file__).resolve().parent.parent
GEOJSON = ROOT / "web" / "src" / "data" / "barrios.geojson"
OUTDIR = Path(__file__).resolve().parent / "output"
N_PERM = 999
SEED = 42
# ~1e-4 grados ≈ 10 m: tolera huecos de digitalización entre polígonos vecinos.
NEIGHBOUR_EPS = 1e-4
METRICS = ["income_total", "rent_eur_m2", "pct_university", "pct_foreign",
           "vut_density", "airbnb_density", "housing_tension"]


# ---------------------------------------------------------------------------
# pesos de contigüidad
# ---------------------------------------------------------------------------
def contiguity_from_features(features: list[dict],
                             eps: float = NEIGHBOUR_EPS) -> pd.DataFrame:
    """Matriz binaria simétrica de vecindad (queen) entre polígonos."""
    ids = [f["properties"]["barrio_id"] for f in features]
    geoms = [shape(f["geometry"]) for f in features]
    n = len(ids)
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if geoms[i].distance(geoms[j]) <= eps:
                W[i, j] = W[j, i] = 1.0
    return pd.DataFrame(W, index=ids, columns=ids)


def load_weights() -> pd.DataFrame:
    gj = json.loads(GEOJSON.read_text(encoding="utf-8"))
    return contiguity_from_features(gj["features"])


# ---------------------------------------------------------------------------
# Moran
# ---------------------------------------------------------------------------
def _align(values: pd.Series, W: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Recorta a los barrios con dato y con algún vecino; W row-standardized."""
    v = values.dropna()
    ids = [b for b in v.index if b in W.index]
    Wm = W.loc[ids, ids].to_numpy(float)
    keep = Wm.sum(axis=1) > 0
    ids = [b for b, k in zip(ids, keep) if k]
    Wm = W.loc[ids, ids].to_numpy(float)
    Wm = Wm / Wm.sum(axis=1, keepdims=True)
    return v.loc[ids].to_numpy(float), Wm


def _moran_stat(x: np.ndarray, Wr: np.ndarray) -> float:
    z = x - x.mean()
    denom = (z**2).sum()
    if denom == 0:
        return float("nan")
    n = len(x)
    return float(n / Wr.sum() * (z @ Wr @ z) / denom)


def morans_i(values: pd.Series, W: pd.DataFrame, n_perm: int = N_PERM,
             seed: int = SEED) -> tuple[float, float]:
    """(I global, p-valor de permutación a una cola sobre |desvío| de E[I])."""
    x, Wr = _align(values, W)
    if len(x) < 4:
        return float("nan"), float("nan")
    i_obs = _moran_stat(x, Wr)
    e_i = -1.0 / (len(x) - 1)  # esperanza bajo aleatoriedad
    rng = np.random.default_rng(seed)
    hits = sum(
        abs(_moran_stat(rng.permutation(x), Wr) - e_i) >= abs(i_obs - e_i)
        for _ in range(n_perm)
    )
    return i_obs, float((hits + 1) / (n_perm + 1))


def local_moran(values: pd.Series, W: pd.DataFrame) -> pd.DataFrame:
    """I_i = z_i · Σ_j w_ij z_j (z estandarizado, W row-standardized)."""
    x, Wr = _align(values, W)
    v = values.dropna()
    ids = [b for b in v.index if b in W.index and W.loc[b].sum() > 0]
    z = (x - x.mean()) / x.std()
    lag = Wr @ z
    return pd.DataFrame({"z": z.round(2), "lag_vecinos": lag.round(2),
                         "I_local": (z * lag).round(3)}, index=ids)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    W = load_weights()
    df = sprint_a.load()
    print("=" * 74)
    print("AN-15 · MORAN'S I — ¿los barrios parecidos se agrupan en el espacio?")
    print("=" * 74)
    print(f"\nPesos: contigüidad queen desde barrios.geojson (19 barrios), "
          f"p por permutación (n={N_PERM}).\n")

    rows = []
    for m in METRICS:
        vals = latest_cross(df, m)
        i, p = morans_i(vals, W)
        rows.append({"metrica": m, "moran_I": round(i, 3), "p_perm": round(p, 3),
                     "n": len(vals.dropna())})
    tab = pd.DataFrame(rows).sort_values("moran_I", ascending=False)
    print(tab.to_string(index=False))
    print("\nI>0 = los similares se tocan (clusters); I≈E[I]≈-0,06 = sin patrón.")

    sig = tab[tab.p_perm < 0.10]
    for m in sig.metrica:
        print(f"\n## Moran local — {m} (I_i>0: en cluster; los mayores):\n")
        loc = local_moran(latest_cross(df, m), W)
        print(loc.sort_values("I_local", ascending=False).head(5).to_string())

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        tab.to_csv(OUTDIR / "moran_global.csv", index=False)
        print(f"\n[guardado] {OUTDIR / 'moran_global.csv'}")


if __name__ == "__main__":
    main()
