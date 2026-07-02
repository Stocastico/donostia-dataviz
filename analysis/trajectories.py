"""AN-18 — Trayectorias de barrio: el connected scatter 2000→2025 (MET-8).

La tercera lectura de MET-8 (estado ≠ cambio ≠ **trayectoria**): el recorrido
completo de cada barrio en un plano de dos métricas con serie 2000–2025. El
par canónico es **envejecimiento × % universitarios** (¿quién se transforma
socialmente mientras envejece / rejuvenece?); el CSV largo incluye las cinco
métricas con serie completa para que la viz pueda elegir ejes.

Estadísticas de recorrido por barrio (sobre el camino suavizado, media móvil
centrada de 3 años, para que el ruido anual del padrón no infle el camino):

- **Δx, Δy y desplazamiento** neto 2000→2025 (unidades nativas).
- **tortuosidad** = longitud del camino / desplazamiento neto (1 = recto:
  el barrio fue siempre en la misma dirección; >>1 = deambula o vuelve).
- **cuadrante** del movimiento (x± y±) para clasificar el relato.
- **dispersión anual** de la nube (distancia media al centroide, ejes
  estandarizados): ¿las trayectorias convergen o se abren? (contraste
  descriptivo de H3 en el plano trayectoria).

Solo pandas + numpy; lee `datos/procesado/tablas/metrics_long.csv`
(versionado — no requiere crudos). Uso:
    python analysis/trajectories.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import sprint_a

OUTDIR = Path(__file__).resolve().parent / "output"

# Métricas con serie completa 2000–2025 (padrón): candidatas a eje.
FULL_SERIES = ["ageing_index", "pct_university", "pct_foreign",
               "pct_youth_adults", "population"]
# Par canónico del BACKLOG: ciclo de vida × transformación social.
X_METRIC, Y_METRIC = "ageing_index", "pct_university"
SMOOTH = 3          # ventana de la media móvil centrada (años)


# --------------------------------------------------------------- panel ----
def xy_panel(df: pd.DataFrame, x_metric: str, y_metric: str) -> pd.DataFrame:
    """Panel (barrio, year) → [x, y]; solo años con ambas métricas."""
    g = df[df.metric_id.isin([x_metric, y_metric])].copy()
    g = g[pd.to_numeric(g.period, errors="coerce").notna()]
    g["year"] = g.period.astype(int)
    wide = g.pivot_table(index=["barrio_id", "year"], columns="metric_id",
                         values="value")
    wide = wide.rename(columns={x_metric: "x", y_metric: "y"})[["x", "y"]]
    return wide.dropna().sort_index()


def _smooth(series: pd.Series, window: int) -> pd.Series:
    if window <= 1:
        return series
    return series.rolling(window, center=True, min_periods=1).mean()


# ------------------------------------------------------------ recorrido ----
def quadrant(dx: float, dy: float) -> str:
    return f"x{'+' if dx >= 0 else '-'} y{'+' if dy >= 0 else '-'}"


def trajectory_stats(panel: pd.DataFrame, smooth: int = SMOOTH) -> pd.DataFrame:
    """Desplazamiento, camino, tortuosidad y cuadrante por barrio."""
    rows = {}
    for barrio, g in panel.groupby(level=0):
        g = g.droplevel(0).sort_index()
        x = _smooth(g["x"], smooth).to_numpy()
        y = _smooth(g["y"], smooth).to_numpy()
        if len(x) < 2:
            continue
        dx, dy = x[-1] - x[0], y[-1] - y[0]
        net = float(np.hypot(dx, dy))
        path = float(np.hypot(np.diff(x), np.diff(y)).sum())
        rows[barrio] = {
            "anio_ini": int(g.index[0]), "anio_fin": int(g.index[-1]),
            "x_ini": x[0], "x_fin": x[-1], "y_ini": y[0], "y_fin": y[-1],
            "dx": dx, "dy": dy, "desplazamiento": net,
            "tortuosidad": path / net if net > 0 else float("inf"),
            "cuadrante": quadrant(dx, dy),
        }
    return pd.DataFrame(rows).T.astype(
        {c: float for c in ["x_ini", "x_fin", "y_ini", "y_fin", "dx", "dy",
                            "desplazamiento", "tortuosidad"]})


# ------------------------------------------------------------ dispersión ----
def dispersion_by_year(panel: pd.DataFrame) -> pd.Series:
    """Distancia media al centroide por año, con ejes estandarizados
    (z-scores globales barrio-año) para que las unidades no manden."""
    z = panel.copy()
    for c in ("x", "y"):
        sd = z[c].std(ddof=0)
        z[c] = (z[c] - z[c].mean()) / sd if sd > 0 else 0.0
    def _d(g: pd.DataFrame) -> float:
        cx, cy = g["x"].mean(), g["y"].mean()
        return float(np.hypot(g["x"] - cx, g["y"] - cy).mean())
    return (z.groupby(level=1).apply(_d)
            .rename("dispersion").sort_index())


def trend_slope(series: pd.Series) -> float:
    """Pendiente OLS de la serie sobre el tiempo (unidades/año)."""
    x = series.index.to_numpy(float)
    return float(np.polyfit(x, series.to_numpy(float), 1)[0])


# -------------------------------------------------------------- informe ----
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    df = sprint_a.load()
    panel = xy_panel(df, X_METRIC, Y_METRIC)
    stats = trajectory_stats(panel).sort_values("desplazamiento",
                                                ascending=False)
    disp = dispersion_by_year(panel)

    print("=" * 76)
    print(f"AN-18 · TRAYECTORIAS  {X_METRIC} (x) × {Y_METRIC} (y), 2000→2025")
    print("=" * 76)
    print(f"\nCamino suavizado (media móvil centrada {SMOOTH} años); "
          "tortuosidad 1 = recto.\n")
    cols = ["x_ini", "x_fin", "dx", "y_ini", "y_fin", "dy",
            "desplazamiento", "tortuosidad", "cuadrante"]
    print(stats[cols].to_string(float_format=lambda v: f"{v:.1f}"))

    print(f"\nDispersión de la nube (z, distancia media al centroide): "
          f"{disp.iloc[0]:.2f} ({disp.index[0]}) → {disp.iloc[-1]:.2f} "
          f"({disp.index[-1]}); pendiente {trend_slope(disp):+.4f}/año.")
    print("\nLectura: dx>0 envejece, dy>0 se universitariza; tortuosidad alta")
    print("= el barrio deambula o revierte (mirar la traza, no la flecha).")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        largo = df[df.metric_id.isin(FULL_SERIES)].copy()
        largo = largo[pd.to_numeric(largo.period, errors="coerce").notna()]
        largo["year"] = largo.period.astype(int)
        (largo[["barrio_id", "year", "metric_id", "value"]]
         .sort_values(["metric_id", "barrio_id", "year"])
         .to_csv(OUTDIR / "trajectories_long.csv", index=False))
        stats.to_csv(OUTDIR / "trajectory_stats.csv")
        disp.to_csv(OUTDIR / "trajectory_dispersion.csv")
        print(f"\n[guardado] {OUTDIR / 'trajectories_long.csv'} (viz-ready, "
              f"{len(FULL_SERIES)} métricas)")
        print(f"[guardado] {OUTDIR / 'trajectory_stats.csv'}")
        print(f"[guardado] {OUTDIR / 'trajectory_dispersion.csv'}")


if __name__ == "__main__":
    main()
