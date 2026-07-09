"""HU-7 — Asequibilidad de la vivienda: ¿el alquiler sube más que el IPC y que
la renta?

La hipótesis del usuario: los precios de la vivienda crecen por encima de la
inflación y **muy** por encima del sueldo, hasta hacer casi imposible que una
persona con trabajo viva sola en la ciudad.

Qué mide este script, solo con datos ya en el repo + IPC oficial:

- **Alquiler** €/m² por barrio (EMA, 2016–2024) y **renta** disponible per
  cápita por barrio (Eustat, 2016–2023), agregados a ciudad como **media
  ponderada por población** de los barrios que reportan cada métrica.
- **IPC** general nacional (INE, media anual, base 2021) como deflactor:
  `datos/input/ipc_espana.csv` (curado, snapshot etiquetado por fila).
- Series **indexadas a base 2016 = 100** para comparar alquiler vs. renta vs.
  IPC en la misma escala; alquiler **real** (deflactado por IPC).
- **Esfuerzo** de vivir solo: misma fórmula que la métrica del pipeline
  `housing_tension` — `alquiler €/m² × 12 × 30 m² / renta pc × 100` = cuota de
  la renta anual de una persona que absorbe alquilar sus 30 m² típicos.

Lecturas honestas (heredadas de MET-1 y de la TESIS):
- El alquiler viene de contratos nuevos (EMA) y la renta cubre a todos los
  residentes → el «esfuerzo» es una **presión teórica sobre el residente
  medio**, no el % que gasta un hogar real.
- Alquiler (→2024), renta (→2023) e IPC (→2025) tienen ventanas distintas: la
  comparación a tres bandas usa la **ventana común 2016–2023**; el alquiler vs.
  IPC se reporta además hasta 2024.
- Los paneles de barrio difieren (11 barrios con alquiler, 17 con renta): cada
  serie de ciudad pondera los barrios que reportan esa métrica.
- Precios de **venta** €/m² no entran (no hay fuente abierta por barrio; ver
  `BACKLOG`); el alquiler cubre el grueso del relato.
- Correlación/serie descriptiva, no causalidad.

Solo pandas + numpy. No necesita crudos (lee tablas procesadas). Uso:
    python analysis/housing_affordability.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "datos" / "procesado" / "tablas" / "metrics_long.csv"
IPC = ROOT / "datos" / "input" / "ipc_espana.csv"
OUTDIR = Path(__file__).resolve().parent / "output"

M2_PER_PERSON = 30           # misma hipótesis transparente que housing_tension
BASE_YEAR = 2016
COMMON_WINDOW = (2016, 2023)  # alquiler ∩ renta ∩ IPC
RENT_WINDOW = (2016, 2024)    # alquiler ∩ IPC (renta no llega)


# --------------------------------------------------------------- lectura ----
def read_metric(metric_id: str, path: Path = METRICS) -> pd.DataFrame:
    """Filas [barrio_id, barrio_name, year:int, value:float] de una métrica."""
    df = pd.read_csv(path, usecols=["metric_id", "barrio_id", "barrio_name",
                                    "period", "value"])
    df = df[df["metric_id"] == metric_id].copy()
    df["year"] = df["period"].astype(int)
    df["value"] = df["value"].astype(float)
    return df[["barrio_id", "barrio_name", "year", "value"]].reset_index(drop=True)


def read_ipc(path: Path = IPC) -> pd.Series:
    """Índice IPC general nacional por año (base 2021 = 100)."""
    df = pd.read_csv(path)
    s = df.set_index(df["year"].astype(int))["value"].astype(float)
    s.name = "ipc"
    return s.sort_index()


def series_by_year(metric_df: pd.DataFrame, barrio_id: str) -> pd.Series:
    """Serie año→valor de un barrio concreto."""
    sub = metric_df[metric_df["barrio_id"] == barrio_id]
    return sub.set_index("year")["value"].sort_index()


# ------------------------------------------------------ transformaciones ----
def rebase(s: pd.Series, base_year: int) -> pd.Series:
    """Reescala a base_year = 100 (KeyError si falta el año base)."""
    base = s[base_year]
    return s / base * 100.0


def cumulative_growth_pct(s: pd.Series, y0: int, y1: int) -> float:
    """Crecimiento acumulado y0→y1 en %."""
    return float((s[y1] / s[y0] - 1.0) * 100.0)


def cagr_pct(s: pd.Series, y0: int, y1: int) -> float:
    """Tasa de crecimiento anual compuesta y0→y1 en %."""
    return float(((s[y1] / s[y0]) ** (1.0 / (y1 - y0)) - 1.0) * 100.0)


def deflate_to_index(nominal: pd.Series, ipc: pd.Series,
                     base_year: int) -> pd.Series:
    """Serie real (euros constantes) indexada a base_year = 100.

    real_index(y) = (nominal[y]/nominal[base]) / (ipc[y]/ipc[base]) × 100
    """
    years = nominal.index.intersection(ipc.index)
    nom = rebase(nominal.loc[years], base_year)
    price = rebase(ipc.loc[years], base_year)
    return (nom / price * 100.0).sort_index()


def population_weighted_city(value_df: pd.DataFrame,
                            pop_df: pd.DataFrame) -> pd.Series:
    """Media ponderada por población, año a año (barrios sin población fuera)."""
    merged = value_df.merge(pop_df, on=["barrio_id", "year"],
                            suffixes=("", "_pop"))
    merged = merged.dropna(subset=["value", "value_pop"])

    def _wmean(g: pd.DataFrame) -> float:
        w = g["value_pop"].to_numpy(float)
        v = g["value"].to_numpy(float)
        return float(np.average(v, weights=w)) if w.sum() > 0 else float("nan")

    out = merged.groupby("year", group_keys=True).apply(_wmean)
    out.name = "city"
    return out.sort_index()


def effort_ratio(rent: pd.Series, income: pd.Series,
                 m2: int = M2_PER_PERSON) -> pd.Series:
    """Esfuerzo % = alquiler €/m² × 12 × m² / renta pc × 100 (años comunes)."""
    years = rent.index.intersection(income.index)
    r = rent.loc[years].astype(float)
    inc = income.loc[years].astype(float)
    return (r * 12 * m2 / inc * 100.0).sort_index()


# --------------------------------------------------------------- resumen ----
def compare_growth(series: dict[str, pd.Series], y0: int, y1: int) -> pd.DataFrame:
    """Tabla crecimiento acumulado + CAGR de varias series en la ventana y0→y1."""
    rows = {}
    for name, s in series.items():
        if y0 in s.index and y1 in s.index:
            rows[name] = {
                f"{y0}": round(float(s[y0]), 2),
                f"{y1}": round(float(s[y1]), 2),
                "crec_%": round(cumulative_growth_pct(s, y0, y1), 1),
                "cagr_%": round(cagr_pct(s, y0, y1), 2),
            }
    return pd.DataFrame(rows).T


def barrio_summary(rent: pd.DataFrame, income: pd.DataFrame, ipc: pd.Series,
                   y0: int, y1: int) -> pd.DataFrame:
    """Por barrio: crecimiento alquiler, renta, alquiler real y esfuerzo."""
    ipc_g = cumulative_growth_pct(ipc, y0, y1)
    rows = []
    for bid in sorted(set(rent["barrio_id"]) & set(income["barrio_id"])):
        r = series_by_year(rent, bid)
        inc = series_by_year(income, bid)
        if not {y0, y1} <= set(r.index) or not {y0, y1} <= set(inc.index):
            continue
        eff = effort_ratio(r, inc)
        rows.append({
            "barrio_id": bid,
            "alq_crec_%": round(cumulative_growth_pct(r, y0, y1), 1),
            "renta_crec_%": round(cumulative_growth_pct(inc, y0, y1), 1),
            "ipc_crec_%": round(ipc_g, 1),
            "alq_real_crec_%": round(
                cumulative_growth_pct(deflate_to_index(r, ipc, y0), y0, y1), 1),
            f"esfuerzo_{y0}": round(float(eff[y0]), 1) if y0 in eff.index else None,
            f"esfuerzo_{y1}": round(float(eff[y1]), 1) if y1 in eff.index else None,
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["esfuerzo_delta_pp"] = (out[f"esfuerzo_{y1}"]
                                    - out[f"esfuerzo_{y0}"]).round(1)
        out = out.sort_values("alq_crec_%", ascending=False).reset_index(drop=True)
    return out


# --------------------------------------------------------------- informe ----
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    rent = read_metric("rent_eur_m2")
    income = read_metric("income_total")
    labor = read_metric("income_labor")
    pop = read_metric("population")
    ipc = read_ipc()

    city_rent = population_weighted_city(rent, pop)
    city_income = population_weighted_city(income, pop)
    city_labor = population_weighted_city(labor, pop)

    print("=" * 76)
    print("HU-7 · ASEQUIBILIDAD  ¿el alquiler crece más que el IPC y el sueldo?")
    print("=" * 76)

    y0, y1 = COMMON_WINDOW
    print(f"\n— Ciudad (media ponderada por población), ventana común {y0}–{y1} —\n")
    table = compare_growth(
        {"Alquiler €/m²": city_rent, "Salario (renta trabajo)": city_labor,
         "Renta disponible pc": city_income, "IPC": ipc}, y0, y1)
    print(table.to_string())
    print("\nClave: el alquiler crece MÁS que el SALARIO (renta del trabajo) pero")
    print("MENOS que la renta disponible pc — que incluye pensiones/capital/")
    print("transferencias e infla la media. Para 'vivir de un sueldo' manda el salario.")

    ry0, ry1 = RENT_WINDOW
    print(f"\n— Alquiler vs. IPC, ventana ampliada {ry0}–{ry1} —\n")
    table_rent = compare_growth({"Alquiler €/m²": city_rent, "IPC": ipc}, ry0, ry1)
    print(table_rent.to_string())
    real = deflate_to_index(city_rent, ipc, ry0)
    print(f"\nAlquiler REAL (deflactado) {ry0}→{ry1}: "
          f"{cumulative_growth_pct(real, ry0, ry1):+.1f} %  "
          f"(nominal {cumulative_growth_pct(city_rent, ry0, ry1):+.1f} %)")

    print(f"\n— Por barrio (ventana común {y0}–{y1}; esfuerzo = alquiler de "
          f"30 m² / renta pc) —\n")
    bs = barrio_summary(rent, income, ipc, y0, y1)
    print(bs.to_string(index=False))

    print("\nLectura: 'crece más que la inflación' = alq_crec_% > ipc_crec_%; "
          "'más que el sueldo' = alq_crec_% > renta_crec_%. El esfuerzo (vivir")
    print("solo en 30 m²) sube donde la renta no acompaña. Venta €/m²: sin dato.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        table.to_csv(OUTDIR / "housing_affordability_city.csv")
        bs.to_csv(OUTDIR / "housing_affordability_barrio.csv", index=False)
        idx = pd.DataFrame({
            "alquiler_ciudad": rebase(city_rent, BASE_YEAR),
            "renta_ciudad": rebase(city_income, BASE_YEAR),
            "ipc": rebase(ipc, BASE_YEAR),
        })
        idx.to_csv(OUTDIR / "housing_affordability_indexed.csv")
        print(f"\n[guardado] {OUTDIR / 'housing_affordability_city.csv'}")
        print(f"[guardado] {OUTDIR / 'housing_affordability_barrio.csv'}")
        print(f"[guardado] {OUTDIR / 'housing_affordability_indexed.csv'}")


if __name__ == "__main__":
    main()
