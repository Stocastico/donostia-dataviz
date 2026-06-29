"""Índice de Transformación Urbana (AN-8) — multi-definición, transparente.

NO es un "índice de gentrificación": con los datos disponibles no se puede
demostrar desplazamiento/sustitución de población (falta rotación de residentes).
Mide *transformación* observable, con la definición explícita y **dos modos**:

  A) Modo socioeconómico  (estilo Freeman 2005, adaptado)
     - Susceptibilidad: renta del barrio < mediana de la ciudad en el año base.
     - Señal de transformación: crecimiento de % universitarios y de alquiler
       por encima de la mediana de la ciudad (componente *local*, ya neto del
       efecto macro/inflación común a toda la ciudad).
     - Clasificación categórica + score continuo (media de z-scores).

  B) Modo presión turística  (PROVISIONAL)
     - Componentes de NIVEL: densidad VUT y nivel de alquiler (la "ciudad
       turística-cara"). No se usa el *crecimiento* de alquiler porque penaliza
       a los centros ya caros en el año base (menos margen de subida). Se
       ampliará con ruido (REC-2) y Airbnb (REC-4) cuando lleguen.

Pesos iguales y componentes **a la vista** (no caja negra). Solo pandas + numpy.

Uso:
    python analysis/transformation_index.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "metrics_long.csv"
OUTDIR = Path(__file__).resolve().parent / "output"
BASE_YEAR = 2016


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df["period"] = df["period"].astype(str)
    return df


def series(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Tabla barrio×año (numérica) desde BASE_YEAR; ignora snapshots 'actual'."""
    g = df[df.metric_id == metric].copy()
    g = g[pd.to_numeric(g.period, errors="coerce").notna()]
    g["year"] = g.period.astype(int)
    g = g[g.year >= BASE_YEAR]
    return g.pivot_table(index="barrio_id", columns="year", values="value")


def snapshot(df: pd.DataFrame, metric: str) -> pd.Series:
    g = df[df.metric_id == metric].sort_values("period").groupby("barrio_id").tail(1)
    return g.set_index("barrio_id")["value"].rename(metric)


def annual_rate(row: pd.Series, kind: str) -> float:
    """Pendiente anualizada de una fila barrio (años en el índice)."""
    s = row.dropna()
    if len(s) < 3:
        return np.nan
    years = s.index.to_numpy(float)
    slope = np.polyfit(years, s.to_numpy(float), 1)[0]
    return slope if kind == "pp" else 100.0 * slope / s.to_numpy(float).mean()


def z(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std()


def build() -> pd.DataFrame:
    df = load()
    income = series(df, "income_total")
    rent = series(df, "rent_eur_m2")
    univ = series(df, "pct_university")
    pop = series(df, "population")

    out = pd.DataFrame(index=sorted(set(income.index) | set(rent.index)))

    # --- Año base e insumos de nivel ---
    base_col = BASE_YEAR if BASE_YEAR in income.columns else min(income.columns)
    out["renta_base"] = income[base_col]
    out["renta_ultima"] = income.ffill(axis=1).iloc[:, -1]
    out["alquiler_nivel"] = rent.ffill(axis=1).iloc[:, -1]
    out["vut_density"] = snapshot(df, "vut_density")

    # --- Tasas anualizadas (crecimiento) ---
    out["univ_rate"] = univ.apply(lambda r: annual_rate(r, "pp"), axis=1)      # pp/año
    out["rent_rate"] = rent.apply(lambda r: annual_rate(r, "level"), axis=1)   # %/año
    out["pop_rate"] = pop.apply(lambda r: annual_rate(r, "level"), axis=1)     # %/año (contexto)

    # --- Componente LOCAL: exceso sobre la mediana de la ciudad ---
    # (resta el componente común macro/inflación → idea shift-share)
    out["univ_excess"] = out["univ_rate"] - out["univ_rate"].median()
    out["rent_excess"] = out["rent_rate"] - out["rent_rate"].median()

    # ===== A) Modo socioeconómico (Freeman) =====
    city_median_income = out["renta_base"].median()
    out["susceptible"] = out["renta_base"] < city_median_income
    up_univ = out["univ_rate"] > out["univ_rate"].median()
    up_rent = out["rent_rate"] > out["rent_rate"].median()

    def classify(row):
        if pd.isna(row["renta_base"]) or pd.isna(row["rent_rate"]) or pd.isna(row["univ_rate"]):
            return "datos insuficientes"
        if not row["susceptible"]:
            return "consolidado / no susceptible"
        n = int(up_univ.get(row.name, False)) + int(up_rent.get(row.name, False))
        return {2: "en transformación", 1: "transformación incipiente",
                0: "estable / sin transformación"}[n]

    out["clase_socioeconomica"] = out.apply(classify, axis=1)
    # Score continuo (media de z de los dos componentes locales)
    out["score_socioeconomico"] = pd.concat(
        [z(out["univ_excess"]), z(out["rent_excess"])], axis=1
    ).mean(axis=1).round(2)

    # ===== B) Modo presión turística (niveles; provisional hasta ruido/Airbnb) =====
    out["score_presion_turistica"] = pd.concat(
        [z(out["vut_density"]), z(out["alquiler_nivel"])], axis=1
    ).mean(axis=1).round(2)

    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()
    out = build()

    print("=" * 78)
    print("ÍNDICE DE TRANSFORMACIÓN URBANA  ·  Donostia Dataviz  (AN-8)")
    print("=" * 78)
    print(f"\nAño base: {BASE_YEAR} · mediana renta base ciudad (umbral susceptibilidad): "
          f"{out['renta_base'].median():,.0f} €\n")

    print("## A) MODO SOCIOECONÓMICO (estilo Freeman)\n")
    a = out.dropna(subset=["renta_base", "rent_rate", "univ_rate"]).copy()
    a = a.sort_values("score_socioeconomico", ascending=False)
    print(a[["renta_base", "univ_rate", "rent_rate", "univ_excess", "rent_excess",
             "score_socioeconomico", "clase_socioeconomica"]].round(2).to_string())

    print("\n## B) MODO PRESIÓN TURÍSTICA\n")
    b = out.dropna(subset=["vut_density", "alquiler_nivel"]).copy()
    b = b.sort_values("score_presion_turistica", ascending=False)
    print(b[["vut_density", "alquiler_nivel",
             "score_presion_turistica"]].round(2).to_string())

    print("\n## Resumen por clase socioeconómica\n")
    print(a["clase_socioeconomica"].value_counts().to_string())

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        out.round(3).to_csv(OUTDIR / "transformation_index.csv")
        print(f"\n[guardado] {OUTDIR/'transformation_index.csv'}")


if __name__ == "__main__":
    main()
