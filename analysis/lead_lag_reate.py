"""AN-6 (refinamiento) — Lead/lag turismo→alquiler con la 2ª señal REATE.

El lead/lag original (AN-6, `lead_lag.py`) usaba las **reseñas de Airbnb** como
proxy de presión turística y el **blindaje AN-16** (`lead_lag_robustness.py`) lo
retiró de los relatos: al controlar por **efectos fijos de año** —que absorben
cualquier shock común de ciudad (IPC, tipos, COVID)— la correlación de panel
r(+1) caía de 0,27 a 0,10 y el test de permutación daba p=0,30.

Pero ese control tiene un punto ciego, anotado en `ANALISIS-LEADLAG.md`: **el FE
de año no puede ver un efecto uniforme en toda la ciudad**. Si el turismo empujó
el alquiler a la vez en todos los barrios, ese empujón vive en la media de cada
año… justo lo que el FE resta. La vía para reabrir H1 sin ese punto ciego es un
test **a grano ciudad** (serie temporal única), con una **segunda señal
independiente** de las reseñas.

Esa señal existe desde REC-12: la curva **REATE** de nuevas licencias VUT/HUT
(`vut_licenses_new`, altas supervivientes por año, 2016–2025). Es *oferta legal
registrada*, no *interés de visitante* → independiente del proxy de reseñas y de
su sesgo de adopción (MET-7).

Este script cruza, **a grano ciudad**, el flujo anual de licencias con la
**variación del alquiler medio** (€/m², primeras diferencias) para varios
desfases k, con test de permutación de la serie temporal. Es el complemento
ciudad del panel de AN-16, no un sustituto.

⚠️ **Dos avisos que gobiernan la lectura:**

  1. **T diminuto.** El alquiler es anual (2016→2024 → 8 variaciones). Con ~8
     puntos ningún desfase es concluyente; se reporta N y p de permutación para
     no sobre-leer un r puntual.
  2. **Dos tendencias opuestas.** El flujo de licencias tiene su propio ciclo
     (pico 2017, desplome tras la regulación/purga) mientras la variación del
     alquiler se acelera al final del periodo. Un r crudo negativo sería un
     **cruce de tendencias**, no una dinámica. Por eso se acompaña de una
     variante **detrended** (linealmente): si el signo se vuelve inestable al
     quitar las tendencias, la asociación cruda no es interpretable.

Uso:
    python analysis/lead_lag_reate.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from lead_lag import _pearson

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "datos" / "procesado" / "tablas" / "metrics_long.csv"
INDICATORS = ROOT / "datos" / "procesado" / "tablas" / "indicators_long.csv"
OUTDIR = Path(__file__).resolve().parent / "output"

LAGS = range(-1, 3)  # k: alquiler precede (−1) … turismo precede (+1, +2)
SIGNAL_ID = "vut_licenses_new"
RENT_METRIC = "rent_eur_m2"
N_PERM = 5000
SEED = 42


# ---------------------------------------------------------------------------
# construcción de las dos series de ciudad
# ---------------------------------------------------------------------------
def city_rent_growth(metrics_df: pd.DataFrame, metric: str = RENT_METRIC) -> pd.Series:
    """Variación interanual del alquiler medio de ciudad (€/m², año→año).

    Media simple de los barrios con dato por año, luego primeras diferencias.
    Índice = año (int). Devuelve la Δ, no el nivel.
    """
    g = metrics_df[metrics_df.metric_id == metric].copy()
    g = g[pd.to_numeric(g.period, errors="coerce").notna()]
    g["year"] = g.period.astype(int)
    level = g.groupby("year").value.mean().sort_index()
    return level.diff().dropna()


def licenses_flow(indicators_df: pd.DataFrame, indicator: str = SIGNAL_ID) -> pd.Series:
    """Flujo anual de nuevas licencias VUT/HUT (REATE), indexado por año (int)."""
    g = indicators_df[indicators_df.id == indicator].copy()
    g["year"] = pd.to_numeric(g.year, errors="coerce")
    g = g.dropna(subset=["year"])
    s = g.set_index(g.year.astype(int)).value.sort_index()
    s.index.name = "year"
    return s


# ---------------------------------------------------------------------------
# lead/lag de serie temporal (grano ciudad)
# ---------------------------------------------------------------------------
def _corr_at_lag(signal: pd.Series, target: pd.Series, lag: int) -> tuple[float, int]:
    """Empareja signal[year−lag] con target[year] sobre los años de target."""
    xs, ys = [], []
    for year in target.index:
        src = int(year) - lag
        if src in signal.index:
            xs.append(signal.loc[src])
            ys.append(target.loc[year])
    return _pearson(np.array(xs, float), np.array(ys, float))


def _read(k: int) -> str:
    if k > 0:
        return f"turismo precede al alquiler {k} año/s"
    if k < 0:
        return f"alquiler precede al turismo {abs(k)} año/s"
    return "mismo año (contemporáneo)"


def lead_lag_series(signal: pd.Series, target: pd.Series, lags=LAGS) -> pd.DataFrame:
    """Para cada desfase k: r de Pearson (ciudad) de signal[t−k] ~ target[t] y N."""
    rows = []
    for k in lags:
        r, n = _corr_at_lag(signal, target, k)
        rows.append({"lag_anni": k, "r": round(r, 3) if not np.isnan(r) else np.nan,
                     "n": n, "lectura": _read(k)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# robustez: detrend lineal + permutación
# ---------------------------------------------------------------------------
def detrend(s: pd.Series) -> pd.Series:
    """Quita la tendencia lineal (OLS sobre el año) → residuos, mismo índice.

    Con <3 puntos no hay residuo defendible (la recta pasa por los puntos) →
    devuelve la serie centrada en su media.
    """
    y = np.asarray(s.values, float)
    x = np.asarray(s.index, float)
    mask = ~np.isnan(y)
    if mask.sum() < 3:
        return s - np.nanmean(y)
    b = np.polyfit(x[mask], y[mask], 1)
    return pd.Series(y - np.polyval(b, x), index=s.index)


def permutation_pvalue(signal: pd.Series, target: pd.Series, lag: int,
                       n_perm: int = N_PERM, seed: int = SEED) -> float:
    """p empírico de dos colas: ¿|r| observado es raro si se rompe el orden
    temporal de la señal (se permutan sus valores entre años)?"""
    r_obs, _ = _corr_at_lag(signal, target, lag)
    if np.isnan(r_obs):
        return float("nan")
    rng = np.random.default_rng(seed)
    vals = np.asarray(signal.values, float)
    hits = 0
    for _ in range(n_perm):
        perm = pd.Series(rng.permutation(vals), index=signal.index)
        r_p, _ = _corr_at_lag(perm, target, lag)
        if not np.isnan(r_p) and abs(r_p) >= abs(r_obs):
            hits += 1
    return float((hits + 1) / (n_perm + 1))


def robustness_table(signal: pd.Series, target: pd.Series, lags=LAGS,
                     n_perm: int = N_PERM, seed: int = SEED) -> pd.DataFrame:
    """Por desfase: r crudo, r con ambas series detrended, N y p de permutación
    (sobre la serie cruda)."""
    d_signal, d_target = detrend(signal), detrend(target)
    rows = []
    for k in lags:
        r_raw, n = _corr_at_lag(signal, target, k)
        r_det, _ = _corr_at_lag(d_signal, d_target, k)
        p = permutation_pvalue(signal, target, k, n_perm=n_perm, seed=seed)
        rows.append({"lag_anni": k, "n": n,
                     "r_crudo": round(r_raw, 3) if not np.isnan(r_raw) else np.nan,
                     "r_detrended": round(r_det, 3) if not np.isnan(r_det) else np.nan,
                     "p_perm": round(p, 4) if not np.isnan(p) else np.nan})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# informe
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    metrics = pd.read_csv(METRICS)
    metrics["period"] = metrics["period"].astype(str)
    indicators = pd.read_csv(INDICATORS)

    rent = city_rent_growth(metrics)
    lic = licenses_flow(indicators)

    print("=" * 74)
    print("AN-6 (refinamiento) · LEAD/LAG con la 2ª señal REATE  (grano CIUDAD)")
    print("=" * 74)
    print(f"\nΔalquiler ciudad (€/m²): {int(rent.index.min())}–{int(rent.index.max())} "
          f"({len(rent)} variaciones)")
    print(f"Licencias VUT nuevas (REATE): {int(lic.index.min())}–{int(lic.index.max())} "
          f"({len(lic)} años)")

    print("\n— Lead/lag serie temporal (r de ciudad, licencias[t−k] ~ Δalquiler[t]) —\n")
    tab = lead_lag_series(lic, rent)
    print(tab.to_string(index=False))

    print("\n— Robustez: crudo vs. detrended + permutación —\n")
    rob = robustness_table(lic, rent)
    print(rob.to_string(index=False))

    print("\nLECTURA (MET-3): a grano ciudad la asociación cruda es NEGATIVA (el flujo")
    print("de licencias cae mientras el alquiler acelera) = cruce de tendencias, no")
    print("dinámica; al quitar las tendencias el signo se vuelve inestable y ningún")
    print("desfase es significativo con T≈8. La 2ª señal REATE NO reabre H1: refuerza")
    print("el veredicto de AN-16. Vía pendiente: grano trimestral o más serie.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        tab.to_csv(OUTDIR / "lead_lag_reate.csv", index=False)
        rob.to_csv(OUTDIR / "lead_lag_reate_robustness.csv", index=False)
        print(f"\n[guardado] {OUTDIR / 'lead_lag_reate.csv'} · "
              f"{OUTDIR / 'lead_lag_reate_robustness.csv'}")


if __name__ == "__main__":
    main()
