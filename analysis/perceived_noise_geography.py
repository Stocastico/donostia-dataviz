"""H6 — El ruido percibido, ¿coincide con la isla de calor y con la VUT?

La hipótesis (a partir de las encuestas de percepción, `docs/HIPOTESIS-FUTURAS.md`
§3): los barrios que la gente percibe como más ruidosos serían los mismos que
destacan en la **isla de calor superficial** (REC-14) y en la **densidad de
viviendas turísticas** (VUT). Cruce directo, sin datos nuevos de campo.

Tres señales por barrio, todas ya en el repo:

- **Ruido percibido** (subjetivo) — encuesta municipal de percepción del ruido
  2026 (`datos/input/percepcion_ruido_donostia.csv`). ⚠️ **Parcial**: la prensa
  solo publica 5 barrios «ruidosos» y 4 «tranquilos», con zonificación propia
  (Parte Vieja → Erdialdea; Aiete-Miramón → Aiete) y sin % para los ruidosos
  salvo la Parte Vieja. Se usa la **categoría** (ruidoso=1 / tranquilo=0), no el
  ranking fino.
- **Isla de calor** (`datos/input/isla_calor_barrio.csv`) — anomalía LST vs.
  media de ciudad, reproducción de REC-14 (`heat_island.py`).
- **Densidad VUT** y **ruido medido** (`noise_night_pct55`) — del pipeline
  (`metrics_long.csv`). El ruido medido entra como **control**: si el percibido
  es serio, debe correlacionar con él.

Método: correlación **punto-biserial** (Pearson de la etiqueta binaria contra
cada señal) sobre los 9 barrios de la encuesta, con Spearman y un leave-one-out
del centro como control de robustez (N pequeño, se dice).

Hallazgo (honesto): el ruido percibido coincide **fuerte** con la isla de calor
(r≈0,73) y con el ruido **medido** (r≈0,75) — la geometría del **este denso**;
con la **densidad turística** (VUT) el vínculo es **más flojo** (r≈0,47) y
**confundido**: solo se sostiene porque los dos barrios más turísticos
(Erdialdea, Gros) son también los más densos y calientes. Los barrios ruidosos
**sin** turismo (Amara Berri, Egia, Añorga: VUT baja, calor y ruido altos)
rompen el vínculo con la VUT. Coherente con la doctrina del proyecto —**el ruido
es de tráfico, no de turismo** (MET-5, VIZ-5)— y con la propia demanda de la
encuesta: «menos tráfico». No es causalidad y N=9.

Solo pandas + numpy. No necesita crudos. Uso:
    python analysis/perceived_noise_geography.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SURVEY = ROOT / "datos" / "input" / "percepcion_ruido_donostia.csv"
HEAT = ROOT / "datos" / "input" / "isla_calor_barrio.csv"
METRICS = ROOT / "datos" / "procesado" / "tablas" / "metrics_long.csv"


# --------------------------------------------------------- funciones puras ----
def point_biserial(y: np.ndarray, x: np.ndarray) -> float:
    """Correlación punto-biserial = Pearson de una etiqueta binaria vs. señal."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    return float(np.corrcoef(y, x)[0, 1])


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Correlación de rangos de Spearman (rho)."""
    ra = pd.Series(np.asarray(a, dtype=float)).rank().to_numpy()
    rb = pd.Series(np.asarray(b, dtype=float)).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def perceived_labels(survey: pd.DataFrame) -> pd.Series:
    """barrio_id → 1.0 (ruidoso) / 0.0 (tranquilo)."""
    return (survey.set_index("barrio_id")["category"]
            .eq("ruidoso").astype(float))


def align_signals(survey: pd.DataFrame, heat: pd.Series, vut: pd.Series,
                  mnoise: pd.Series) -> pd.DataFrame:
    """Tabla con una fila por barrio de la encuesta y sus tres señales."""
    y = perceived_labels(survey)
    df = pd.DataFrame({
        "barrio_id": y.index,
        "y": y.to_numpy(),
        "heat": [heat.get(b, np.nan) for b in y.index],
        "vut": [vut.get(b, np.nan) for b in y.index],
        "mnoise": [mnoise.get(b, np.nan) for b in y.index],
    })
    return df.reset_index(drop=True)


# --------------------------------------------------------------- lectura ----
def read_survey(path: Path = SURVEY) -> pd.DataFrame:
    return pd.read_csv(path)


def read_heat(path: Path = HEAT) -> pd.Series:
    df = pd.read_csv(path)
    return df.set_index("barrio_id")["lst_anomaly"]


def _latest_metric(metric_id: str, path: Path = METRICS) -> pd.Series:
    m = pd.read_csv(path)
    s = m[m["metric_id"] == metric_id]
    s = s[s["period"] == s["period"].max()]
    return s.set_index("barrio_id")["value"]


def build_frame() -> pd.DataFrame:
    """El cruce completo (9 barrios × 3 señales) desde los datos reales."""
    return align_signals(read_survey(), read_heat(),
                         _latest_metric("vut_density"),
                         _latest_metric("noise_night_pct55"))


def correlations(exclude: list[str] | None = None) -> dict[str, float]:
    """Punto-biserial percibido↔{heat,vut,mnoise}, opcionalmente sin barrios."""
    df = build_frame()
    if exclude:
        df = df[~df["barrio_id"].isin(exclude)]
    return {c: point_biserial(df["y"], df[c]) for c in ("heat", "vut", "mnoise")}


# -------------------------------------------------------------- informe ----
def main() -> None:
    df = build_frame()
    print("=" * 72)
    print("H6 · RUIDO PERCIBIDO vs. ISLA DE CALOR vs. DENSIDAD VUT")
    print("=" * 72)
    print("\nEncuesta municipal de percepción del ruido 2026 (parcial, 9 barrios)")
    print("cruzada con calor (REC-14), densidad VUT y ruido medido:\n")
    show = df.copy()
    show["cat"] = np.where(show["y"] == 1.0, "ruidoso", "tranquilo")
    print(show[["barrio_id", "cat", "heat", "vut", "mnoise"]]
          .to_string(index=False, float_format=lambda v: f"{v:.1f}"))

    full = correlations()
    drop = correlations(exclude=["erdialdea"])
    sp = {c: spearman(df["y"], df[c]) for c in ("heat", "vut", "mnoise")}
    print("\n— Correlación con el ruido percibido (ruidoso=1 / tranquilo=0) —")
    print(f"{'señal':<22}{'r (pt-biserial)':>16}{'Spearman':>11}"
          f"{'r sin Erdialdea':>18}")
    names = {"heat": "isla de calor", "mnoise": "ruido medido (control)",
             "vut": "densidad VUT (turismo)"}
    for c in ("heat", "mnoise", "vut"):
        print(f"{names[c]:<22}{full[c]:>+16.2f}{sp[c]:>+11.2f}{drop[c]:>+18.2f}")

    print("\n— Lectura —")
    print("  El ruido percibido va FUERTE con el calor y con el ruido MEDIDO: es")
    print("  la geografía del este denso. Con la densidad turística (VUT) el")
    print("  vínculo es más flojo y se apoya en el centro (Erdialdea/Gros, que")
    print("  además es el más denso y caliente): al quitarlo, la VUT cae y el")
    print("  calor aguanta. Amara Berri, Egia y Añorga son ruidosos SIN turismo.")
    print("  → el ruido es de densidad/tráfico, no de turismo (MET-5/VIZ-5); la")
    print("  encuesta misma pide «menos tráfico». Correlación ≠ causalidad; N=9.")


if __name__ == "__main__":
    main()
