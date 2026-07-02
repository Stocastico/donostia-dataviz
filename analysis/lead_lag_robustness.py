"""AN-16 — Blindaje del lead/lag AN-6 (turismo → alquiler).

El feedback externo (jul-2026) señala que r(+1)=0,27 podría ser un artefacto de
no-estacionariedad o de shocks macro comunes (IPC, tipos). Tres defensas, todas
con pandas + numpy (sin scipy/statsmodels, como el resto de analysis/):

1. **Estacionariedad del panel en diferencias**: Dickey-Fuller (modelo con
   constante, sin lags aumentados) y KPSS (nivel) por barrio sobre las series
   en primeras diferencias. ⚠️ Con T≈8 puntos por barrio estos tests casi no
   tienen potencia — se reportan como diagnóstico descriptivo, no como
   veredicto. Valores críticos: DF asintóticos del modelo con constante
   (−3,43/−2,86/−2,57); KPSS de Kwiatkowski et al. (1992).

2. **Control macro por efectos fijos de año**: en vez de restar un IPC/tipo de
   interés concreto (series que el repo no tiene), se demedia cada año del
   panel (within-year). Esto absorbe *cualquier* shock común de la ciudad —
   inflación, tipos, COVID — y deja solo la variación entre barrios. Si el
   lead/lag sobrevive, no lo genera un factor macro común.

3. **Test de permutación** para cada desfase: se permuta el orden temporal de
   Δactividad dentro de cada barrio (n_perm veces) y se recalcula la
   correlación de panel → p-valor empírico de dos colas sin supuestos
   distribucionales. Se aplica sobre el panel ya demediado por año.

Uso:
    python analysis/lead_lag_robustness.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import lead_lag
from lead_lag import LAGS, _panel, _diffs, _pearson

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "datos" / "procesado" / "tablas" / "metrics_long.csv"
OUTDIR = Path(__file__).resolve().parent / "output"
N_PERM = 5000
SEED = 42

# Valores críticos asintóticos del test DF, modelo con constante (rechazo si t < crit).
DF_CRIT = {"1%": -3.43, "5%": -2.86, "10%": -2.57}
# Valores críticos KPSS nivel (Kwiatkowski et al. 1992; rechazo estacionariedad si stat > crit).
KPSS_CRIT = {"10%": 0.347, "5%": 0.463, "2.5%": 0.574, "1%": 0.739}
MIN_T_DF = 6  # por debajo no hay grados de libertad defendibles


# ---------------------------------------------------------------------------
# 1. Estacionariedad
# ---------------------------------------------------------------------------
def df_tstat(y: np.ndarray) -> float:
    """t-stat de Dickey-Fuller (Δy_t = α + γ·y_{t−1}; H0: γ=0, raíz unitaria)."""
    y = np.asarray(y, float)
    y = y[~np.isnan(y)]
    if len(y) < MIN_T_DF:
        return float("nan")
    dy, ylag = np.diff(y), y[:-1]
    if ylag.std() == 0:  # serie constante → regresor degenerado (pasa en el panel real)
        return float("nan")
    X = np.column_stack([np.ones_like(ylag), ylag])
    beta, *_ = np.linalg.lstsq(X, dy, rcond=None)
    resid = dy - X @ beta
    dof = len(dy) - 2
    sigma2 = resid @ resid / dof
    if sigma2 <= 0:
        return float("nan")
    cov = sigma2 * np.linalg.inv(X.T @ X)
    return float(beta[1] / np.sqrt(cov[1, 1]))


def kpss_stat(y: np.ndarray) -> float:
    """Estadístico KPSS de estacionariedad en nivel (H0: estacionaria).

    Varianza de largo plazo con ventana de Bartlett, truncamiento l4 estándar.
    """
    y = np.asarray(y, float)
    y = y[~np.isnan(y)]
    T = len(y)
    if T < 4:
        return float("nan")
    e = y - y.mean()
    S = np.cumsum(e)
    lag = int(4 * (T / 100.0) ** 0.25)
    s2 = e @ e / T
    for j in range(1, lag + 1):
        s2 += 2.0 * (1.0 - j / (lag + 1.0)) * (e[j:] @ e[:-j]) / T
    if s2 <= 0:
        return float("nan")
    return float(S @ S / (T**2 * s2))


def stationarity_table(panel: pd.DataFrame, name: str) -> pd.DataFrame:
    """DF y KPSS por barrio sobre las filas del panel (ya en diferencias)."""
    rows = []
    for bid, row in panel.iterrows():
        y = row.dropna().to_numpy(float)
        t, k = df_tstat(y), kpss_stat(y)
        rows.append({
            "serie": name, "barrio": bid, "T": len(y),
            "df_t": round(t, 2) if not np.isnan(t) else np.nan,
            "df_rechaza_raiz_5pct": bool(t < DF_CRIT["5%"]) if not np.isnan(t) else None,
            "kpss": round(k, 3) if not np.isnan(k) else np.nan,
            "kpss_rechaza_estac_5pct": bool(k > KPSS_CRIT["5%"]) if not np.isnan(k) else None,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Efectos fijos de año (control macro)
# ---------------------------------------------------------------------------
def demean_by_year(panel: pd.DataFrame) -> pd.DataFrame:
    """Resta la media de cada año (columna): absorbe cualquier shock macro común."""
    return panel - panel.mean(axis=0)


def panel_corr_at_lag(act: pd.DataFrame, rent: pd.DataFrame, lag: int) -> float:
    """Correlación de panel Δact(t−lag) ~ Δrent(t), como lead_lag.lead_lag."""
    r, _ = _corr_and_n(act, rent, lag)
    return r


def _corr_and_n(act: pd.DataFrame, rent: pd.DataFrame, lag: int) -> tuple[float, int]:
    barrios = sorted(set(act.index) & set(rent.index))
    xs, ys = [], []
    for year in rent.columns:
        src = year - lag
        if src not in act.columns:
            continue
        for b in barrios:
            xs.append(act.at[b, src])
            ys.append(rent.at[b, year])
    return _pearson(np.array(xs, float), np.array(ys, float))


# ---------------------------------------------------------------------------
# 3. Test de permutación
# ---------------------------------------------------------------------------
def permutation_pvalue(act: pd.DataFrame, rent: pd.DataFrame, lag: int,
                       n_perm: int = N_PERM, seed: int = SEED) -> float:
    """p-valor empírico de dos colas: ¿|r| observado es raro si se rompe el
    orden temporal de Δactividad dentro de cada barrio?"""
    barrios = sorted(set(act.index) & set(rent.index))
    A = act.loc[barrios]
    R = rent.loc[barrios]
    r_obs = panel_corr_at_lag(A, R, lag)
    if np.isnan(r_obs):
        return float("nan")
    rng = np.random.default_rng(seed)
    a_np = A.to_numpy(float)
    hits = 0
    for _ in range(n_perm):
        perm = pd.DataFrame(rng.permuted(a_np, axis=1),
                            index=A.index, columns=A.columns)
        r_p = panel_corr_at_lag(perm, R, lag)
        if not np.isnan(r_p) and abs(r_p) >= abs(r_obs):
            hits += 1
    return float((hits + 1) / (n_perm + 1))


# ---------------------------------------------------------------------------
# informe
# ---------------------------------------------------------------------------
def robustness_table(d_act: pd.DataFrame, d_rent: pd.DataFrame,
                     n_perm: int = N_PERM, seed: int = SEED) -> pd.DataFrame:
    """Para cada desfase: r naive, r con FE de año, N y p-valor de permutación
    (sobre el panel demediado)."""
    fe_act, fe_rent = demean_by_year(d_act), demean_by_year(d_rent)
    rows = []
    for k in LAGS:
        r_naive, n = _corr_and_n(d_act, d_rent, k)
        r_fe, _ = _corr_and_n(fe_act, fe_rent, k)
        p = permutation_pvalue(fe_act, fe_rent, k, n_perm=n_perm, seed=seed)
        rows.append({"lag_anni": k, "n": n,
                     "r_naive": round(r_naive, 3), "r_fe_anno": round(r_fe, 3),
                     "p_perm_fe": round(p, 4)})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    df = pd.read_csv(DATA)
    df["period"] = df["period"].astype(str)
    d_act = _diffs(_panel(df, "airbnb_activity"))
    d_rent = _diffs(_panel(df, "rent_eur_m2"))

    print("=" * 74)
    print("AN-16 · BLINDAJE DEL LEAD/LAG AN-6  (estacionariedad + macro + permutación)")
    print("=" * 74)

    print("\n## 1. Estacionariedad del panel en diferencias (diagnóstico, T pequeño)\n")
    stat = pd.concat([
        stationarity_table(d_act, "Δairbnb_activity"),
        stationarity_table(d_rent, "Δrent_eur_m2"),
    ], ignore_index=True)
    print(stat.to_string(index=False))
    ok = stat.dropna(subset=["df_t"])
    print(f"\nResumen: DF rechaza raíz unitaria (5%) en "
          f"{int(ok.df_rechaza_raiz_5pct.sum())}/{len(ok)} series con T suficiente; "
          f"KPSS rechaza estacionariedad (5%) en "
          f"{int(stat.kpss_rechaza_estac_5pct.dropna().sum())}/{int(stat.kpss.notna().sum())}.")
    print("⚠️ Con T≈8 por serie, DF casi no tiene potencia: diagnóstico, no veredicto.")

    print(f"\n## 2+3. Lead/lag naive vs. FE de año, con p-valor de permutación "
          f"(n={N_PERM}, semilla {SEED})\n")
    tab = robustness_table(d_act, d_rent)
    print(tab.to_string(index=False))
    print("\nLectura: r_fe_anno quita cualquier shock común de ciudad (IPC, tipos,")
    print("COVID). p_perm_fe = prob. de un |r| así al romper el orden temporal de")
    print("Δactividad dentro de cada barrio (dos colas, sin supuestos).")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        stat.to_csv(OUTDIR / "lead_lag_stationarity.csv", index=False)
        tab.to_csv(OUTDIR / "lead_lag_robustness.csv", index=False)
        print(f"\n[guardado] {OUTDIR/'lead_lag_stationarity.csv'} · "
              f"{OUTDIR/'lead_lag_robustness.csv'}")


if __name__ == "__main__":
    main()
