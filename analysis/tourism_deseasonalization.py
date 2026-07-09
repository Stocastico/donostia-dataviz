"""HU-5 / HU-6 — ¿Se está desestacionalizando el turismo de Donostia?

Las hipótesis del usuario (`docs/HIPOTESIS-FUTURAS.md` §5):

- **HU-5** «turismo sostenible = desestacionalizar»: ¿las pernoctaciones se
  reparten más a lo largo del año que antes?
- **HU-6** «el turismo de congresos (MICE) es de más calidad»: el ángulo
  medible es si el **MICE rellena la temporada baja** (= desestacionalización).

Dato: pernoctaciones hoteleras **mensuales** de Donostia (INE EOH, tabla 2078),
2005–2026, en `datos/procesado/tablas/series_long.csv` (`overnight_stays`).

Tres medidas de estacionalidad por año (sobre los 12 meses):
- **summer_share** = % de pernoctaciones en jul+ago+sep (JAS).
- **peak_trough** = mes máximo / mes mínimo.
- **cv** = desviación típica / media mensual (coeficiente de variación).

Y el **mecanismo**: crecimiento por mes 2005→2025 (¿crece más la temporada baja
que agosto?).

Hallazgo (honesto): la estacionalidad **baja** de forma sostenida y se acelera
tras 2022 — el % de verano cae de ~37 % (2005) a ~32 % (2025) y el CV de ~0,35
a ~0,24 (2023–2025 son los años **menos** estacionales de la serie). El
mecanismo es que la **temporada baja crece más rápido que el pico**: los meses
valle (ene/feb/nov/dic) hacen ×2,9–3,3 (2005→2025) mientras agosto solo ×2,1.
HU-5 **confirmada**.

Sobre HU-6: **no** se puede cruzar MICE × mes — la serie MICE
(`mice_donostia.csv`) es **solo anual** (nº de congresos/asistentes, sin
distribución mensual). El MICE crece (récord 2024: 188 eventos, 259.000
asistentes) y encaja como **contribuyente plausible** a que suba la temporada
baja, pero **no se puede aislar** de otras causas (turismo urbano de todo el
año, city-breaks, clima) sin el calendario mensual de eventos → limitación
declarada. Años 2020 (COVID, meses ausentes), 2021 (rebote atípico solo-verano)
y 2026 (en curso) se excluyen por incompletos/atípicos. N pequeño en años;
correlación ≠ causalidad.

Solo pandas + numpy. Uso:
    python analysis/tourism_deseasonalization.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SERIES = ROOT / "datos" / "procesado" / "tablas" / "series_long.csv"
MICE = ROOT / "datos" / "input" / "mice_donostia.csv"

SUMMER = (7, 8, 9)   # jul-ago-sep


# --------------------------------------------------------- funciones puras ----
def seasonality_metrics(month_values: dict[int, float]) -> dict[str, float]:
    """Medidas de estacionalidad de un año (mapping mes 1..12 → pernoctaciones)."""
    vals = np.array([month_values[m] for m in range(1, 13)], dtype=float)
    total = vals.sum()
    return {
        "total": float(total),
        "summer_share": float(vals[[m - 1 for m in SUMMER]].sum() / total * 100),
        "peak_trough": float(vals.max() / vals.min()),
        "cv": float(vals.std() / vals.mean()),
    }


def complete_years(df: pd.DataFrame) -> list[int]:
    """Años con los 12 meses presentes (los demás no son comparables)."""
    counts = df.groupby("year")["month"].nunique()
    return sorted(int(y) for y, n in counts.items() if n == 12)


def month_growth(df: pd.DataFrame, y0: int, y1: int) -> pd.Series:
    """Ratio de crecimiento por mes entre dos años (mes → value[y1]/value[y0])."""
    a = df[df["year"] == y0].set_index("month")["value"]
    b = df[df["year"] == y1].set_index("month")["value"]
    return (b / a).sort_index()


def year_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla de estacionalidad por año completo, indexada por año."""
    rows = {}
    for y in complete_years(df):
        mv = df[df["year"] == y].set_index("month")["value"].to_dict()
        rows[y] = seasonality_metrics(mv)
    return pd.DataFrame(rows).T.sort_index()


# --------------------------------------------------------------- lectura ----
def read_overnight(path: Path = SERIES) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["series_id"] == "overnight_stays"].copy()
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    df["value"] = df["value"].astype(float)
    return df[["year", "month", "value"]]


def read_mice(path: Path = MICE) -> pd.DataFrame:
    return pd.read_csv(path)


# -------------------------------------------------------------- informe ----
def main() -> None:
    df = read_overnight()
    ym = year_metrics(df)

    print("=" * 68)
    print("HU-5/HU-6 · DESESTACIONALIZACIÓN DEL TURISMO (pernoctaciones INE)")
    print("=" * 68)
    print("\nEstacionalidad por año (años completos; 2020/2021/2026 fuera):\n")
    view = ym.drop(index=[y for y in (2021,) if y in ym.index])  # atípico
    print(f"{'año':<6}{'total':>10}{'%verano':>9}{'pico/valle':>12}{'CV':>7}")
    for y, r in view.iterrows():
        print(f"{int(y):<6}{int(r['total']):>10}{r['summer_share']:>8.1f}%"
              f"{r['peak_trough']:>12.2f}{r['cv']:>7.2f}")

    early = ym.loc[[2005, 2006, 2007]]
    late = ym.loc[[2023, 2024, 2025]]
    print("\n— Tendencia —")
    print(f"  %verano: {early['summer_share'].mean():.1f} % (2005–07) → "
          f"{late['summer_share'].mean():.1f} % (2023–25)")
    print(f"  CV:      {early['cv'].mean():.2f} (2005–07) → "
          f"{late['cv'].mean():.2f} (2023–25)  — menos estacional")

    g = month_growth(df, 2005, 2025)
    names = "Ene Feb Mar Abr May Jun Jul Ago Sep Oct Nov Dic".split()
    print("\n— Mecanismo: crecimiento por mes 2005→2025 —")
    print("  " + "  ".join(f"{names[m-1]} {g[m]:.1f}x" for m in range(1, 13)))
    valley = np.mean([g[1], g[2], g[11], g[12]])
    print(f"  valle (Ene/Feb/Nov/Dic) ×{valley:.2f}  vs  pico (Ago) ×{g[8]:.2f}"
          f"  → la temporada baja crece {valley / g[8] - 1:+.0%} más.")

    mice = read_mice()
    att = mice[mice["indicator_id"] == "mice_attendees"]
    print("\n— HU-6 (MICE): límite —")
    if not att.empty:
        row = att.sort_values("year").iloc[-1]
        print(f"  MICE crece (asistentes {int(row['value']):,} en {int(row['year'])}),"
              " pero la serie es SOLO ANUAL:")
    print("  no hay calendario mensual de eventos → el MICE encaja como causa")
    print("  plausible del relleno de temporada baja, pero NO se puede aislar.")


if __name__ == "__main__":
    main()
