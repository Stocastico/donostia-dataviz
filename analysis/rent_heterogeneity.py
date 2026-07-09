"""H7 — ¿La presión del alquiler es uniforme por barrio? ¿Y el «Zubieta barato»?

La hipótesis del usuario (`docs/HIPOTESIS-FUTURAS.md` §3): la preocupación por
la vivienda cara no sería uniforme — barrios pequeños o periféricos (el ejemplo
propuesto: **Zubieta, más barato**) tendrían dinámicas de precio propias,
distintas del este obrero.

Dato: alquiler `rent_eur_m2` por barrio (EMA — fianzas depositadas de contratos
nuevos), 2016–2024, en `metrics_long.csv`.

Dos preguntas:

1. **Cobertura.** ¿Se puede siquiera medir cada barrio? La EMA registra donde
   hay mercado de alquiler con suficientes contratos; los barrios de mercado
   fino no aparecen.
2. **Heterogeneidad.** Entre los que sí tienen serie, ¿el alquiler ha subido
   uniformemente o hay barrios con trayectoria propia?

Hallazgo (honesto, doble):

- **El «Zubieta barato» NO es verificable.** 6 de los 19 barrios **no tienen
  ningún dato** de alquiler (Zubieta, Igeldo, Añorga, Miramón-Zorroaga y los
  exclaves Landerbaso/Oarain) y 2 más solo parcial (Ategorrieta-Ulia,
  Martutene) — justo los pequeños/periféricos que plantea la hipótesis. Es el
  mismo problema de **registro parcial** que VPO/Etxebide (MET-5): sin muestra,
  no hay número; no se afirma que Zubieta sea más barato ni lo contrario.
- **Entre los 11 barrios con serie completa, la subida NO es uniforme, pero al
  revés del marco de la hipótesis**: el **este obrero barato subió más rápido**
  (Loiola +48 %, Intxaurrondo +44 %, Altza +35 %) y el **centro caro menos**
  (Erdialdea +29 %, Egia +28 %). corr(nivel 2016, crecimiento) ≈ −0,5:
  convergencia **en %** (los baratos se encarecen más deprisa), aunque la brecha
  **en €/m²** persiste (coherente con AN-13/H3). La presión de asequibilidad es
  mayor donde la renta es menor (une con HU-7), no en una periferia con vida
  propia. N pequeño; correlación ≠ causalidad.

Solo pandas + numpy. Uso:
    python analysis/rent_heterogeneity.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "datos" / "procesado" / "tablas" / "metrics_long.csv"

N_PERIODS_FULL = 9   # 2016–2024


# --------------------------------------------------------- funciones puras ----
def classify_coverage(n_periods: int, full: int = N_PERIODS_FULL) -> str:
    if n_periods == 0:
        return "sin dato"
    if n_periods >= full:
        return "completa"
    return "parcial"


def coverage(df: pd.DataFrame, universe: dict[str, str]) -> pd.DataFrame:
    """Por barrio del ``universe``: nº de periodos con dato, extremos y estado.

    ``universe`` = todos los barrios (barrio_id → name); los que no aparecen en
    ``df`` cuentan como «sin dato» (n_periods=0) — el punto de H7.
    """
    rows = {}
    for bid, name in universe.items():
        sub = df[df["barrio_id"] == bid]
        years = sorted(sub["period"].unique())
        rows[bid] = {
            "name": name,
            "n_periods": len(years),
            "first": years[0] if years else None,
            "last": years[-1] if years else None,
            "status": classify_coverage(len(years)),
        }
    return pd.DataFrame(rows).T


def rent_growth(df: pd.DataFrame, y0: int, y1: int) -> pd.DataFrame:
    """Crecimiento % y0→y1 por barrio (solo los que tienen ambos extremos)."""
    piv = df.pivot_table(index="barrio_id", columns="period", values="value")
    names = df.groupby("barrio_id")["barrio_name"].first()
    both = piv.dropna(subset=[y0, y1])
    out = pd.DataFrame({
        "name": names.reindex(both.index),
        "v0": both[y0], "v1": both[y1],
        "growth_pct": (both[y1] / both[y0] - 1) * 100,
    })
    return out.sort_values("growth_pct", ascending=False)


def level_growth_corr(df: pd.DataFrame, y0: int, y1: int) -> float:
    """corr(nivel inicial, crecimiento %): <0 = los baratos suben más."""
    g = rent_growth(df, y0, y1)
    return float(np.corrcoef(g["v0"], g["growth_pct"])[0, 1])


# --------------------------------------------------------------- lectura ----
def read_rent(path: Path = METRICS) -> pd.DataFrame:
    m = pd.read_csv(path)
    r = m[m["metric_id"] == "rent_eur_m2"].copy()
    r["period"] = r["period"].astype(int)
    r["value"] = r["value"].astype(float)
    return r[["barrio_id", "barrio_name", "period", "value"]]


def barrio_universe(path: Path = METRICS) -> dict[str, str]:
    """Todos los barrios del proyecto (barrio_id → name), desde metrics_long."""
    m = pd.read_csv(path)
    pairs = m[["barrio_id", "barrio_name"]].drop_duplicates()
    return dict(zip(pairs["barrio_id"], pairs["barrio_name"]))


# -------------------------------------------------------------- informe ----
def main() -> None:
    df = read_rent()
    cov = coverage(df, barrio_universe())

    print("=" * 66)
    print("H7 · ¿ES UNIFORME LA PRESIÓN DEL ALQUILER? ¿Y EL «ZUBIETA BARATO»?")
    print("=" * 66)

    print("\n— Cobertura EMA por barrio (fianzas de contratos nuevos) —")
    for status in ("completa", "parcial", "sin dato"):
        bs = cov[cov["status"] == status]
        names = ", ".join(sorted(bs["name"]))
        print(f"  {status:<9} ({len(bs):>2}): {names}")
    print("\n  → El «Zubieta más barato» NO es verificable: Zubieta (y 5 barrios")
    print("    más) no tienen dato EMA. Registro parcial, no universo (MET-5).")

    g = rent_growth(df, 2016, 2024)
    print("\n— Heterogeneidad 2016→2024 (11 barrios con serie completa) —")
    print(f"{'barrio':<22}{'2016':>7}{'2024':>7}{'crec%':>8}")
    for bid, row in g.iterrows():
        print(f"{row['name']:<22}{row['v0']:>7.1f}{row['v1']:>7.1f}"
              f"{row['growth_pct']:>7.1f}%")
    corr = level_growth_corr(df, 2016, 2024)
    print(f"\n  Rango de crecimiento: {g['growth_pct'].min():.0f}–"
          f"{g['growth_pct'].max():.0f}% (no uniforme).")
    print(f"  corr(nivel 2016, crecimiento) = {corr:+.2f}: el este obrero BARATO")
    print("  (Loiola, Intxaurrondo, Altza) sube MÁS que el centro caro → "
          "convergencia")
    print("  en % (la brecha en €/m² persiste, AN-13). La presión de "
          "asequibilidad")
    print("  es mayor donde la renta es menor (une con HU-7), no en una "
          "periferia aparte.")


if __name__ == "__main__":
    main()
