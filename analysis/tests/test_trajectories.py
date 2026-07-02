"""Tests de AN-18 — trayectorias de barrio (connected scatter 2000→2025).

Piezas: panel x/y por barrio-año, suavizado, estadísticas de recorrido
(desplazamiento neto, longitud de camino, tortuosidad, cuadrante) y
dispersión anual de la nube (¿los barrios convergen o se separan?).
"""
import numpy as np
import pandas as pd
import pytest

import trajectories as tj


def _long(rows):
    return pd.DataFrame(rows, columns=["barrio_id", "metric_id", "period", "value"])


def _line(barrio="egia", n=6, x0=0.0, y0=0.0, dx=1.0, dy=2.0):
    """Trayectoria en línea recta con paso constante."""
    rows = []
    for i in range(n):
        rows.append((barrio, "mx", str(2000 + i), x0 + dx * i))
        rows.append((barrio, "my", str(2000 + i), y0 + dy * i))
    return _long(rows)


# --------------------------------------------------------------- panel ----
def test_xy_panel_alinea_las_dos_metricas():
    panel = tj.xy_panel(_line(), "mx", "my")
    assert list(panel.columns) == ["x", "y"]
    assert panel.loc[("egia", 2003), "x"] == pytest.approx(3.0)
    assert panel.loc[("egia", 2003), "y"] == pytest.approx(6.0)


def test_xy_panel_descarta_anios_incompletos():
    df = _line()
    df = df[~((df.metric_id == "my") & (df.period == "2005"))]
    panel = tj.xy_panel(df, "mx", "my")
    assert (2005 not in
            panel.loc["egia"].index)


# ------------------------------------------------------------ recorrido ----
def test_linea_recta_tortuosidad_uno():
    panel = tj.xy_panel(_line(n=6), "mx", "my")
    st = tj.trajectory_stats(panel, smooth=1).loc["egia"]
    assert st["dx"] == pytest.approx(5.0)
    assert st["dy"] == pytest.approx(10.0)
    assert st["desplazamiento"] == pytest.approx(np.hypot(5.0, 10.0))
    assert st["tortuosidad"] == pytest.approx(1.0)


def test_zigzag_tortuosidad_mayor_que_uno():
    rows = []
    ys = [0, 5, 0, 5, 0, 5]           # sube y baja; neto pequeño
    for i, y in enumerate(ys):
        rows.append(("gros", "mx", str(2000 + i), float(i)))
        rows.append(("gros", "my", str(2000 + i), float(y)))
    panel = tj.xy_panel(_long(rows), "mx", "my")
    st = tj.trajectory_stats(panel, smooth=1).loc["gros"]
    assert st["tortuosidad"] > 2.0


def test_cuadrante_segun_signos():
    assert tj.quadrant(1.0, 1.0) == "x+ y+"
    assert tj.quadrant(-2.0, 0.5) == "x- y+"
    assert tj.quadrant(3.0, -1.0) == "x+ y-"
    assert tj.quadrant(-0.1, -0.1) == "x- y-"


def test_suavizado_reduce_la_tortuosidad_del_ruido():
    rng = np.random.default_rng(42)
    rows = []
    for i in range(20):
        rows.append(("aiete", "mx", str(2000 + i), i + rng.normal(0, 0.8)))
        rows.append(("aiete", "my", str(2000 + i), 2 * i + rng.normal(0, 0.8)))
    panel = tj.xy_panel(_long(rows), "mx", "my")
    raw = tj.trajectory_stats(panel, smooth=1).loc["aiete", "tortuosidad"]
    smooth = tj.trajectory_stats(panel, smooth=3).loc["aiete", "tortuosidad"]
    assert smooth < raw


# ------------------------------------------------------------ dispersión ----
def test_dispersion_convergencia_detectada():
    rows = []
    for i in range(10):
        gap = 10.0 - i                # dos barrios acercándose
        rows += [("a", "mx", str(2000 + i), -gap), ("a", "my", str(2000 + i), 0.0),
                 ("b", "mx", str(2000 + i), gap), ("b", "my", str(2000 + i), 0.0)]
    panel = tj.xy_panel(_long(rows), "mx", "my")
    disp = tj.dispersion_by_year(panel)
    assert disp.iloc[-1] < disp.iloc[0]
    assert tj.trend_slope(disp) < 0
