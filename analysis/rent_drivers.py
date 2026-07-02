"""AN-19 — Regresión múltiple exploratoria: alquiler ~ renta + universitarios + Airbnb.

Pregunta del feedback externo: ¿la densidad Airbnb aporta información sobre el
nivel de alquiler *controlando* por renta y capital educativo? Con N=13 esto
**nunca** es un modelo publicable (y así se dice); es una forma disciplinada de
hacer la pregunta. Variables estandarizadas (coeficientes comparables), IC
bootstrap por coeficiente y ΔR² al añadir Airbnb al modelo renta+universitarios.

Solo pandas + numpy. Uso:
    python analysis/rent_drivers.py [--save]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import sprint_a
from sprint_a import latest_cross

OUTDIR = Path(__file__).resolve().parent / "output"
N_BOOT = 2000
SEED = 42
TARGET = "rent_eur_m2"
PREDICTORS = ["income_total", "pct_university", "airbnb_density"]


def ols_multi(X: pd.DataFrame, y: pd.Series) -> dict:
    """OLS y ~ const + X sobre filas completas; coeficientes por columna."""
    j = pd.concat([X, y.rename("_y")], axis=1).dropna()
    n = len(j)
    k = X.shape[1]
    if n < k + 2:
        return {"coef": {c: float("nan") for c in X.columns},
                "r2": float("nan"), "n": n}
    Xm = np.column_stack([np.ones(n), j[X.columns].to_numpy(float)])
    yv = j["_y"].to_numpy(float)
    beta, *_ = np.linalg.lstsq(Xm, yv, rcond=None)
    resid = yv - Xm @ beta
    ss_tot = ((yv - yv.mean()) ** 2).sum()
    r2 = 1.0 - (resid @ resid) / ss_tot if ss_tot > 0 else float("nan")
    return {"coef": {c: float(b) for c, b in zip(X.columns, beta[1:])},
            "r2": float(r2), "n": n}


def bootstrap_coef_ci(X: pd.DataFrame, y: pd.Series, n_boot: int = N_BOOT,
                      seed: int = SEED, alpha: float = 0.05) -> dict:
    """IC bootstrap percentil por coeficiente (remuestreo de filas completas)."""
    j = pd.concat([X, y.rename("_y")], axis=1).dropna()
    n = len(j)
    rng = np.random.default_rng(seed)
    draws: dict[str, list[float]] = {c: [] for c in X.columns}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        fit = ols_multi(j.iloc[idx][list(X.columns)], j.iloc[idx]["_y"])
        if not np.isnan(fit["r2"]):
            for c in X.columns:
                draws[c].append(fit["coef"][c])
    out = {}
    for c, vals in draws.items():
        if vals:
            lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
            out[c] = (float(lo), float(hi))
        else:
            out[c] = (float("nan"), float("nan"))
    return out


def delta_r2(X: pd.DataFrame, y: pd.Series, add: str) -> float:
    """Ganancia de R² al añadir la columna `add` al modelo con el resto."""
    base_cols = [c for c in X.columns if c != add]
    base = ols_multi(X[base_cols], y)
    full = ols_multi(X, y)
    return float(full["r2"] - base["r2"])


def load_vars() -> tuple[pd.DataFrame, pd.Series]:
    """Predictores y objetivo (último valor por barrio), estandarizados."""
    df = sprint_a.load()
    cols = pd.concat([latest_cross(df, m) for m in PREDICTORS + [TARGET]], axis=1)
    cols = cols.dropna()
    z = (cols - cols.mean()) / cols.std()
    return z[PREDICTORS], z[TARGET]


def build_report() -> dict:
    X, y = load_vars()
    full = ols_multi(X, y)
    ci = bootstrap_coef_ci(X, y)
    return {
        "n": full["n"],
        "modelo_completo": full,
        "ci95": ci,
        "delta_r2_airbnb": round(delta_r2(X, y, add="airbnb_density"), 3),
        "r2_sin_airbnb": round(ols_multi(X[["income_total", "pct_university"]], y)["r2"], 3),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    rep = build_report()
    print("=" * 74)
    print("AN-19 · alquiler ~ renta + universitarios + Airbnb  (EXPLORATORIO, N pequeño)")
    print("=" * 74)
    print(f"\nVariables estandarizadas (z), último valor por barrio · N={rep['n']}")
    print(f"IC95% bootstrap ({N_BOOT} remuestreos, semilla {SEED}).\n")
    print(f"{'coef':>18}  {'beta_z':>7}  {'IC95%':>18}")
    for c, b in rep["modelo_completo"]["coef"].items():
        lo, hi = rep["ci95"][c]
        print(f"{c:>18}  {b:7.3f}  [{lo:7.3f}, {hi:7.3f}]")
    print(f"\nR² modelo completo: {rep['modelo_completo']['r2']:.3f} · "
          f"R² sin Airbnb: {rep['r2_sin_airbnb']:.3f} · "
          f"ΔR² de añadir Airbnb: {rep['delta_r2_airbnb']:.3f}")
    print("\n⚠️ N=13: pregunta exploratoria, nunca un modelo. Coeficientes en z")
    print("(comparables entre sí); IC anchos = la respuesta honesta.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        (OUTDIR / "rent_drivers.json").write_text(
            json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[guardado] {OUTDIR / 'rent_drivers.json'}")


if __name__ == "__main__":
    main()
