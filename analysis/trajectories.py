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
    python analysis/trajectories.py [--save] [--svg]

`--svg` regenera el connected scatter estático de la historia #6
(`analysis/output/trajectories_an18.svg`): mismo marco, paleta y marcadores
que el SVG inline publicado en `output/historias.html` (jul-2026), con
Egia/Antiguo/Loiola/Miramón destacados y Zubieta/Landerbaso fuera (ruido de
denominador — "no leer sus trazas").
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


# ------------------------------------------------------------- SVG AN-18 ----
# Marco canónico del gráfico publicado (historias.html #6): viewBox 680×500,
# área de trazado x∈[56,562] px ↔ envejecimiento [40,400], y∈[454,18] px ↔
# % universitarios [0,40]. Si el padrón se sale del marco algún año, ampliar
# aquí (y re-embeber el SVG en historias).
VIEW_W, VIEW_H = 680, 500
_PX = (56.0, 562.0)
_PY = (454.0, 18.0)
X_DOMAIN, X_STEP = (40.0, 400.0), 50
Y_DOMAIN, Y_STEP = (0.0, 40.0), 10
# Paleta de la página; el resto de trazas va en gris #c9d2de.
HIGHLIGHTS = {
    "egia": ("Egia", "#d1495b"),
    "antigua": ("Antiguo", "#e0902f"),
    "miramon-zorroaga": ("Miramón-Zorroaga", "#2a9d6f"),
    "loiola": ("Loiola", "#1f6f8b"),
}
# Las etiquetas de texto usan una variante más oscura (contraste AA 4,5:1
# sobre blanco); las líneas mantienen la paleta de la página.
LABEL_COLORS = {
    "egia": "#c03a4c",
    "antigua": "#9c5f0e",
    "miramon-zorroaga": "#1f7a54",
    "loiola": "#1f6f8b",
}
# Desplazamiento (dx, dy) de cada etiqueta respecto al punto final.
_LABEL_OFFSET = {"egia": (8, 4), "antigua": (8, -6),
                 "miramon-zorroaga": (8, 12), "loiola": (8, 4)}
EXCLUDE = {"zubieta", "landerbaso"}   # ruido de denominador (AN-18)
GRAY = "#c9d2de"
# Color de foco al pasar el ratón por una traza gris (distinto de los cuatro
# colores destacados): la traza «se enciende» sin necesidad de 17 colores fijos.
FOCUS = "#7a3ca6"
MARKER_YEARS = (2005, 2010, 2015, 2020)


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _sx(v: float) -> float:
    d0, d1 = X_DOMAIN
    return _PX[0] + (v - d0) / (d1 - d0) * (_PX[1] - _PX[0])


def _sy(v: float) -> float:
    d0, d1 = Y_DOMAIN
    return _PY[0] + (v - d0) / (d1 - d0) * (_PY[1] - _PY[0])


def _trace(g: pd.DataFrame, smooth: int) -> tuple[np.ndarray, np.ndarray, list[int]]:
    g = g.droplevel(0).sort_index()
    x = _smooth(g["x"], smooth).to_numpy(float)
    y = _smooth(g["y"], smooth).to_numpy(float)
    return x, y, list(g.index)


def svg_connected_scatter(panel: pd.DataFrame, names: dict[str, str] | None = None,
                          smooth: int = SMOOTH) -> str:
    """El connected scatter de la historia #6 como SVG standalone.

    Cada traza se envuelve en un `<g class="traj" data-…>` con una banda de
    impacto transparente (`.hit`) más ancha que la línea y los datos de inicio
    y fin: la interactividad (resaltar al pasar el ratón, tooltip con nombre y
    cifras 2000→2025) la conecta el JS de `historias.html`, así que **todas**
    las trazas —no solo las cuatro destacadas— son identificables.
    """
    names = names or {}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" '
        'role="img" aria-label="Trayectorias de los barrios 2000–2025 en el '
        'plano envejecimiento × universitarios">'
    ]
    # rejilla + ejes (primera marca en el múltiplo de X_STEP dentro del dominio)
    import math
    v = math.ceil(X_DOMAIN[0] / X_STEP) * X_STEP
    while v < X_DOMAIN[1] + 1e-9:
        parts.append(f'<line x1="{_sx(v):.1f}" y1="{_PY[1]}" x2="{_sx(v):.1f}" '
                     f'y2="{_PY[0]}" stroke="#eef1f6"/>')
        parts.append(f'<text x="{_sx(v):.1f}" y="{_PY[0] + 16:.0f}" font-size="10.5" '
                     f'fill="#5f6e84" text-anchor="middle">{v:.0f}</text>')
        v += X_STEP
    v = Y_DOMAIN[0]
    while v < Y_DOMAIN[1] + 1e-9:
        parts.append(f'<line x1="{_PX[0]}" y1="{_sy(v):.1f}" x2="{_PX[1]}" '
                     f'y2="{_sy(v):.1f}" stroke="#eef1f6"/>')
        parts.append(f'<text x="{_PX[0] - 8:.0f}" y="{_sy(v) + 3.5:.1f}" font-size="10.5" '
                     f'fill="#5f6e84" text-anchor="end">{v:.0f}</text>')
        v += Y_STEP
    parts.append(f'<line x1="{_PX[0]}" y1="{_PY[0]}" x2="{_PX[1]}" y2="{_PY[0]}" '
                 'stroke="#d7dde7"/>')
    parts.append(f'<line x1="{_PX[0]}" y1="{_PY[1]}" x2="{_PX[0]}" y2="{_PY[0]}" '
                 'stroke="#d7dde7"/>')
    cx = (_PX[0] + _PX[1]) / 2
    cy = (_PY[0] + _PY[1]) / 2
    parts.append(f'<text x="{cx:.0f}" y="{VIEW_H - 8}" font-size="11.5" fill="#3a4a63" '
                 'text-anchor="middle" font-weight="600">Índice de envejecimiento '
                 '(≥65 / &lt;15 × 100) →</text>')
    parts.append(f'<text x="14" y="{cy:.0f}" font-size="11.5" fill="#3a4a63" '
                 'text-anchor="middle" font-weight="600" '
                 f'transform="rotate(-90 14 {cy:.0f})">% universitarios →</text>')

    barrios = [b for b in panel.index.get_level_values(0).unique()
               if b not in EXCLUDE]
    grays = sorted(b for b in barrios if b not in HIGHLIGHTS)
    colored = [b for b in HIGHLIGHTS if b in barrios]
    labels = []
    # grises primero, destacadas después (se dibujan encima); cada una es un
    # grupo con su banda de impacto para que sea fácil de señalar y su tooltip.
    for barrio in grays + colored:
        x, y, years = _trace(panel.loc[[barrio]], smooth)
        if len(x) < 2:
            continue
        hi = barrio in HIGHLIGHTS
        color = HIGHLIGHTS.get(barrio, (None, GRAY))[1]
        hover = color if hi else FOCUS
        name = HIGHLIGHTS[barrio][0] if hi else names.get(barrio, barrio.title())
        d = " L".join(f"{_sx(a):.1f},{_sy(b):.1f}" for a, b in zip(x, y))
        width, opacity = ("2.4", "1") if hi else ("1.1", "0.75")
        g = [f'<g class="traj" data-name="{_esc(name)}" data-color="{color}" '
             f'data-hover="{hover}" data-hi="{1 if hi else 0}" '
             f'data-xi="{x[0]:.0f}" data-xf="{x[-1]:.0f}" '
             f'data-yi="{y[0]:.1f}" data-yf="{y[-1]:.1f}" '
             f'data-yr0="{years[0]}" data-yr1="{years[-1]}">']
        g.append(f'<path class="line" d="M{d}" fill="none" stroke="{color}" '
                 f'stroke-width="{width}" stroke-linejoin="round" '
                 f'stroke-linecap="round" opacity="{opacity}"/>')
        if hi:
            for year in MARKER_YEARS:
                if year in years:
                    i = years.index(year)
                    g.append(f'<circle class="mk" cx="{_sx(x[i]):.1f}" '
                             f'cy="{_sy(y[i]):.1f}" r="2.2" fill="{color}"/>')
        r0, r1 = ("4.4", "4.6") if hi else ("2.6", "2.8")
        w0 = "2" if hi else "1.4"
        g.append(f'<circle class="p0" cx="{_sx(x[0]):.1f}" cy="{_sy(y[0]):.1f}" '
                 f'r="{r0}" fill="#fff" stroke="{color}" stroke-width="{w0}"/>')
        g.append(f'<circle class="p1" cx="{_sx(x[-1]):.1f}" cy="{_sy(y[-1]):.1f}" '
                 f'r="{r1}" fill="{color}"/>')
        # banda de impacto transparente, más ancha que la línea (fácil de señalar)
        g.append(f'<path class="hit" d="M{d}" fill="none" stroke="transparent" '
                 f'stroke-width="12" stroke-linejoin="round" stroke-linecap="round"/>')
        g.append('</g>')
        parts.append("".join(g))
        if hi:
            ox, oy = _LABEL_OFFSET.get(barrio, (8, 4))
            label_fill = LABEL_COLORS.get(barrio, color)
            labels.append(f'<text x="{_sx(x[-1]) + ox:.1f}" y="{_sy(y[-1]) + oy:.1f}" '
                          f'font-size="11.5" font-weight="700" '
                          f'fill="{label_fill}">{name}</text>')
    # capa superior (etiquetas fijas + leyenda): se mantiene por encima aunque
    # el JS suba una traza al frente al resaltarla.
    parts.append('<g class="overlay">')
    parts.extend(labels)
    # leyenda: círculo hueco = 2000, lleno = 2025
    parts.append('<circle cx="66" cy="28" r="4" fill="#fff" stroke="#5f6e84" '
                 'stroke-width="1.6"/><text x="75" y="31.5" font-size="10.5" '
                 'fill="#5f6e84">2000</text>')
    parts.append('<circle cx="118" cy="28" r="4" fill="#5f6e84"/>'
                 '<text x="127" y="31.5" font-size="10.5" fill="#5f6e84">2025 · '
                 'puntos intermedios = 2005/10/15/20</text>')
    parts.append('</g>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# -------------------------------------------------------------- informe ----
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--svg", action="store_true",
                    help="regenera analysis/output/trajectories_an18.svg")
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

    if args.svg:
        OUTDIR.mkdir(exist_ok=True)
        names = (df.drop_duplicates("barrio_id")
                 .set_index("barrio_id")["barrio_name"].to_dict())
        svg = svg_connected_scatter(panel, names)
        (OUTDIR / "trajectories_an18.svg").write_text(svg, encoding="utf-8")
        print(f"[guardado] {OUTDIR / 'trajectories_an18.svg'} "
              "(connected scatter de la historia #6)")


if __name__ == "__main__":
    main()
