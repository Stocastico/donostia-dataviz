"""AN-13 — Beta-convergencia: ¿los barrios que partían más abajo suben más?

Regresión clásica de convergencia, adaptada al repo:

    tasa_anualizada(2016→último) ~ α + β · nivel_2016

para renta, alquiler €/m² y % universitarios. β<0 con IC95 % bootstrap
enteramente negativo → convergencia (los de abajo recortan); β>0 →
divergencia; IC que cruza 0 → compatible con la "brecha estable" que el Gini
territorial (AN-5) ya sugería, pero testeada con más rigor.

Las tasas son las mismas del Sprint A (`sprint_a.annualized_rate`): %/año para
niveles (renta, alquiler), puntos pct/año para porcentajes. N=13–17 barrios →
el IC bootstrap es la parte importante, no el punto.

Solo pandas + numpy. Uso:
    python analysis/beta_convergence.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import sprint_a
from sprint_a import annualized_rate

OUTDIR = Path(__file__).resolve().parent / "output"
BASE_YEAR = 2016
N_BOOT = 2000
SEED = 42
METRICS = {"income_total": "level", "rent_eur_m2": "level", "pct_university": "pp"}


def load() -> pd.DataFrame:
    return sprint_a.load()


def ols(x: pd.Series, y: pd.Series) -> dict:
    """OLS simple y ~ α + β·x sobre los pares completos."""
    j = pd.concat([x, y], axis=1).dropna()
    n = len(j)
    if n < 3:
        return {"beta": float("nan"), "alpha": float("nan"), "r2": float("nan"), "n": n}
    xv, yv = j.iloc[:, 0].to_numpy(float), j.iloc[:, 1].to_numpy(float)
    beta, alpha = np.polyfit(xv, yv, 1)
    resid = yv - (beta * xv + alpha)
    ss_tot = ((yv - yv.mean()) ** 2).sum()
    r2 = 1.0 - (resid @ resid) / ss_tot if ss_tot > 0 else float("nan")
    return {"beta": float(beta), "alpha": float(alpha), "r2": float(r2), "n": n}


def bootstrap_beta_ci(x: pd.Series, y: pd.Series, n_boot: int = N_BOOT,
                      seed: int = SEED, alpha: float = 0.05) -> tuple[float, float]:
    """IC bootstrap percentil para β (remuestreo de pares, como AN-10)."""
    j = pd.concat([x, y], axis=1).dropna()
    n = len(j)
    if n < 3:
        return float("nan"), float("nan")
    xv, yv = j.iloc[:, 0].to_numpy(float), j.iloc[:, 1].to_numpy(float)
    rng = np.random.default_rng(seed)
    betas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if xv[idx].std() == 0:
            continue
        betas.append(np.polyfit(xv[idx], yv[idx], 1)[0])
    if not betas:
        return float("nan"), float("nan")
    lo, hi = np.percentile(betas, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def _level0_and_rate(df: pd.DataFrame, metric: str, kind: str) -> tuple[pd.Series, pd.Series]:
    g = df[df.metric_id == metric].copy()
    g = g[pd.to_numeric(g.period, errors="coerce").notna()]
    g["year"] = g.period.astype(int)
    g = g[g.year >= BASE_YEAR]
    panel = g.pivot_table(index="barrio_id", columns="year", values="value")
    level0 = panel[BASE_YEAR] if BASE_YEAR in panel.columns else pd.Series(dtype=float)
    rate = panel.apply(
        lambda r: annualized_rate(r.dropna().index.to_numpy(float),
                                  r.dropna().to_numpy(float), kind), axis=1)
    return level0.rename("nivel_2016"), rate.rename("tasa")


def _read(lo: float, hi: float) -> str:
    if hi < 0:
        return "convergencia"
    if lo > 0:
        return "divergencia"
    return "compatible con brecha estable"


def convergence_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for metric, kind in METRICS.items():
        level0, rate = _level0_and_rate(df, metric, kind)
        fit = ols(level0, rate)
        lo, hi = bootstrap_beta_ci(level0, rate)
        rows[metric] = {
            "unidad_tasa": "%/año" if kind == "level" else "pp/año",
            "beta": round(fit["beta"], 5), "r2": round(fit["r2"], 3),
            "n": fit["n"],
            "ci95_lo": round(lo, 5), "ci95_hi": round(hi, 5),
            "lectura": _read(lo, hi),
        }
    return pd.DataFrame(rows).T


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    tab = convergence_table(load())
    print("=" * 74)
    print("AN-13 · BETA-CONVERGENCIA  tasa(2016→último) ~ α + β·nivel_2016")
    print("=" * 74)
    print(f"\nIC95% bootstrap percentil ({N_BOOT} remuestreos, semilla {SEED}).\n")
    print(tab.to_string())
    print("\nLectura: β<0 (IC completo bajo 0) = los que partían bajos suben más")
    print("(convergencia); IC cruzando 0 = compatible con brecha estable (H3).")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        tab.to_csv(OUTDIR / "beta_convergence.csv")
        print(f"\n[guardado] {OUTDIR / 'beta_convergence.csv'}")


if __name__ == "__main__":
    main()
