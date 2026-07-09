"""H8 — La preocupación por el turismo sube justo cuando bajan las altas nuevas.

La hipótesis (contraintuitiva, `docs/HIPOTESIS-FUTURAS.md` §3): en la encuesta
municipal 2026 el **turismo entra nuevo al top-3 de preocupaciones** (82 % pide
«que no crezca más»), pero las **altas de licencias VUT/HUT nuevas** (el flujo de
presión bruta) llevan años cayendo — de 300/año en 2017 a 18 en 2025 (REC-12,
registro REATE). Lectura propuesta: lo que preocupa no es el **flujo** de nuevas
licencias, sino el **stock** acumulado y la masificación en volumen — ambos en
máximos.

Qué se puede medir (todo ya en el repo):

- **Flujo** — `vut_licenses_new` (altas REATE por año). Se ha desplomado.
- **Stock** — `vut_licenses_cumulative` y `vut_plazas_cumulative` (parque legal
  acumulado). En máximo histórico. ⚠️ REATE no publica bajas → el acumulado es
  un **suelo** (no resta cierres); aun así el flujo de altas sí es el ritmo de
  crecimiento bruto.
- **Volumen real** — pernoctaciones hoteleras anuales (INE), como presión
  efectivamente sentida. En récord (2,2 M en 2025).
- **Tasa de crecimiento del stock** = altas / stock previo → cuánto crece el
  parque cada año en términos relativos.

Hallazgo (honesto): el **flujo** de altas cae −94 % desde el pico de 2017
mientras el **stock** (1.329 licencias, 5.706 plazas) y el **volumen**
(pernoctaciones récord) están en máximos; la tasa de crecimiento del parque pasa
de >1 (2017, casi triplicaba) a ~0,01 (2025). Es decir, el parque turístico se
ha **estabilizado alto**, no reducido. La preocupación de 2026 encaja con el
**stock/masificación**, no con el (ya mínimo) flujo de altas — H8 respaldada de
forma **descriptiva**. Salvedades: la encuesta es **un único año** (2026), no una
serie, así que no se prueba una relación temporal; correlación ≠ causalidad;
REATE = licencias supervivientes.

Solo pandas. Uso:
    python analysis/tourism_concern_flow_stock.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INDICATORS = ROOT / "web" / "src" / "data" / "indicators.json"
SERIES = ROOT / "datos" / "procesado" / "tablas" / "series_long.csv"


# --------------------------------------------------------- funciones puras ----
def stock_growth_rate(new: pd.Series, cumulative: pd.Series) -> pd.Series:
    """Tasa de crecimiento del parque = altas[y] / stock[y-1]."""
    prev = cumulative.shift(1)
    return (new / prev).dropna().sort_index()


def change_sign(s: pd.Series, threshold: float = 0.0) -> str:
    """'sube' / 'baja' / 'estable' entre el primer y el último año de la serie."""
    lo, hi = s.index.min(), s.index.max()
    delta = float(s[hi] - s[lo])
    if delta > threshold:
        return "sube"
    if delta < -threshold:
        return "baja"
    return "estable"


def divergence(flow: pd.Series, stock: pd.Series, y0: int, y1: int) -> dict:
    """¿Van flujo y stock en sentidos opuestos entre y0 e y1?"""
    f = change_sign(flow.loc[[y0, y1]])
    s = change_sign(stock.loc[[y0, y1]])
    return {"flow": f, "stock": s,
            "diverge": {f, s} == {"sube", "baja"}}


# --------------------------------------------------------------- lectura ----
def read_indicator(indicator_id: str, path: Path = INDICATORS) -> pd.Series:
    data = json.loads(path.read_text(encoding="utf-8"))
    for ind in data:
        if ind["id"] == indicator_id:
            return pd.Series(
                {int(y): float(v["value"]) for y, v in ind["values"].items()}
            ).sort_index()
    raise KeyError(indicator_id)


def annual_overnight(path: Path = SERIES) -> pd.Series:
    """Pernoctaciones anuales (suma de meses), solo años completos (12 meses)."""
    df = pd.read_csv(path)
    df = df[df["series_id"] == "overnight_stays"]
    by_year = df.groupby("year")
    full = by_year["month"].nunique() == 12
    return by_year["value"].sum()[full].sort_index()


# -------------------------------------------------------------- informe ----
def main() -> None:
    flow = read_indicator("vut_licenses_new")
    stock = read_indicator("vut_licenses_cumulative")
    plazas = read_indicator("vut_plazas_cumulative")
    ov = annual_overnight()

    print("=" * 68)
    print("H8 · PREOCUPACIÓN POR TURISMO ↑  vs.  ALTAS DE LICENCIAS ↓")
    print("=" * 68)

    print("\n— Flujo vs. stock (licencias VUT/HUT, REATE) —")
    print(f"{'año':<6}{'altas/año':>10}{'stock':>8}{'plazas':>9}"
          f"{'crec.stock':>12}")
    g = stock_growth_rate(flow, stock)
    for y in flow.index:
        gr = f"{g[y]*100:.1f}%" if y in g.index else "—"
        print(f"{y:<6}{int(flow[y]):>10}{int(stock[y]):>8}{int(plazas[y]):>9}"
              f"{gr:>12}")

    peak = flow.idxmax()
    print(f"\n  El FLUJO se desploma: pico {int(flow[peak])} en {peak} → "
          f"{int(flow[flow.index.max()])} en {flow.index.max()} "
          f"({flow[flow.index.max()]/flow[peak]-1:+.0%}).")
    print(f"  El STOCK está en MÁXIMO: {int(stock.max())} licencias, "
          f"{int(plazas.max())} plazas. Tasa de crecimiento del parque: "
          f"{g[2017]*100:.0f}% (2017) → {g[2025]*100:.1f}% (2025).")

    d = divergence(flow, stock, 2017, 2025)
    print(f"\n— Divergencia 2017→2025 —")
    print(f"  flujo {d['flow']} · stock {d['stock']} → "
          f"{'DIVERGEN' if d['diverge'] else 'coinciden'}")
    print(f"  Volumen real (pernoctaciones): {int(ov[2017]):,} (2017) → "
          f"{int(ov.max()):,} (récord {ov.idxmax()}).")

    print("\n— Lectura —")
    print("  La presión BRUTA nueva (altas) casi ha desaparecido, pero el parque")
    print("  turístico se ha estabilizado ALTO y el volumen está en récord. La")
    print("  preocupación de 2026 encaja con el STOCK/masificación, no con el")
    print("  flujo de nuevas licencias. Salvedad: la encuesta es de un solo año")
    print("  (2026), no una serie → no se prueba relación temporal. REATE = suelo.")


if __name__ == "__main__":
    main()
