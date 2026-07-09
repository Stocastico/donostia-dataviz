"""HU-1 — ¿La percepción de que 'la seguridad ha bajado mucho' es cierta?

La hipótesis del usuario: se percibe que la ciudad es mucho más insegura, pero
eso no se corresponde con la realidad. Son **dos series distintas** y hay que
separarlas:

- **Percepción** (real y larga): Eustat, Encuesta de Condiciones de Vida,
  familias por *grado de seguridad ciudadana* y zona (miles), 1989–2024 cada 5
  años. La zona **70 = «Donostia-San Sebastián con Bajo Bidasoa»** es la que
  centra Donostia. Métrica: % de familias que declaran **algún problema** de
  seguridad = (Total − «Ningún problema») / Total.
  Fuente curada: `datos/input/percepcion_seguridad_eustat.csv`.

- **Realidad** (parcial): infracciones penales conocidas y tasa/1000 hab.
  (Ertzaintza + Guardia Municipal, vía Balance de Criminalidad del Min. del
  Interior). Solo tenemos puntos sueltos de prensa (2019–2021 + Δ2024).
  Fuente curada: `datos/input/criminalidad_donostia.csv`. **Laguna declarada**:
  falta la serie oficial anual completa (Portal Estadístico de Criminalidad).

La «tijera»: si la percepción de inseguridad **sube** mientras la criminalidad
real **baja/se estanca**, la hipótesis del usuario se sostiene. Si suben juntas,
no.

Hallazgo (con lo disponible, honesto):
- A **largo plazo** la percepción de inseguridad ha *mejorado* mucho: de ~35 %
  de familias con algún problema en 1989 a ~14–18 % en 2004–2019 → «ha bajado
  mucho la seguridad» es **falso** en perspectiva histórica.
- Pero hay un **repunte reciente 2019→2024** (14,6 %→21,5 %), coherente con la
  encuesta municipal 2026 (inseguridad 2ª preocupación). Y los pocos datos de
  criminalidad real también suben en esa ventana (2019→2021 y +11,8 % en 2024)
  → en el corto plazo percepción y realidad **coinciden**, no divergen: la
  tijera *no* está clara con los datos actuales.

Lecturas honestas: zona comarcal, no municipio exacto; percepción cada 5 años;
criminalidad = serie parcial de prensa (completar con la oficial); correlación
≠ causalidad; N pequeño.

Solo pandas. No necesita crudos. Uso:
    python analysis/perception_vs_crime.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PERCEPTION = ROOT / "datos" / "input" / "percepcion_seguridad_eustat.csv"
CRIME = ROOT / "datos" / "input" / "criminalidad_donostia.csv"
OUTDIR = Path(__file__).resolve().parent / "output"

DONOSTIA_ZONA = "70"


# --------------------------------------------------------------- lectura ----
def read_perception(path: Path = PERCEPTION) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    df["zona_id"] = df["zona_id"].astype(str).str.zfill(2)
    return df


def read_crime(path: Path = CRIME) -> pd.DataFrame:
    return pd.read_csv(path)


# ------------------------------------------------------- % con problema -----
def insecurity_share(df: pd.DataFrame, zona_id: str) -> pd.Series:
    """% de familias con algún problema de seguridad = (Total−Ningún)/Total×100."""
    sub = df[df["zona_id"] == str(zona_id).zfill(2)]
    wide = sub.pivot_table(index="year", columns="grado",
                           values="familias_miles", aggfunc="first")
    share = (wide["Total"] - wide["Ningun_problema"]) / wide["Total"] * 100.0
    return share.dropna().sort_index()


def crime_series(df: pd.DataFrame, indicator_id: str) -> pd.Series:
    sub = df[df["indicator_id"] == indicator_id]
    return sub.set_index("year")["value"].astype(float).sort_index()


# ----------------------------------------------------------- tendencia -------
def trend_direction(s: pd.Series, y0: int, y1: int,
                    threshold: float = 0.5) -> str:
    """'sube' / 'baja' / 'estable' entre y0 y y1 (umbral en unidades de s)."""
    delta = float(s[y1] - s[y0])
    if delta > threshold:
        return "sube"
    if delta < -threshold:
        return "baja"
    return "estable"


def scissors(perception: pd.Series, crime: pd.Series, y0: int, y1: int,
             threshold: float = 0.5) -> dict:
    """Compara la dirección de percepción y criminalidad en la ventana y0→y1."""
    p = trend_direction(perception, y0, y1, threshold)
    c = trend_direction(crime, y0, y1, threshold)
    if p == "sube" and c in ("baja", "estable"):
        veredicto = "divergen"      # percepción empeora, realidad no → tijera
    elif p == c:
        veredicto = "coinciden"
    else:
        veredicto = "mixto"
    return {"perception": p, "crime": c, "veredicto": veredicto,
            "perc_delta": round(float(perception[y1] - perception[y0]), 1),
            "crime_delta": round(float(crime[y1] - crime[y0]), 1)}


# -------------------------------------------------------------- informe ----
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    perc_df = read_perception()
    crime_df = read_crime()
    share = insecurity_share(perc_df, DONOSTIA_ZONA)
    share_cae = insecurity_share(perc_df, "00")

    print("=" * 76)
    print("HU-1 · ¿'LA SEGURIDAD HA BAJADO MUCHO'?  percepción vs. realidad")
    print("=" * 76)

    print("\n— Percepción: % de familias con ALGÚN problema de seguridad —")
    print("  (Eustat ECV, zona Donostia-Bajo Bidasoa vs. C.A. Euskadi)\n")
    tab = pd.DataFrame({"Donostia_zona": share.round(1),
                        "Euskadi": share_cae.round(1)})
    print(tab.to_string())

    peak_year = share.idxmax()
    print(f"\nMáximo histórico: {peak_year} ({share[peak_year]:.1f} %). "
          f"Mínimo: {share.idxmin()} ({share.min():.1f} %). "
          f"2024: {share[2024]:.1f} %.")
    print(f"Largo plazo 1989→2024: {trend_direction(share, 1989, 2024, 1.0)} "
          f"({share[2024] - share[1989]:+.1f} pp) — 'ha bajado mucho' NO se")
    print(f"sostiene a largo plazo. Reciente 2019→2024: "
          f"{trend_direction(share, 2019, 2024, 1.0)} "
          f"({share[2024] - share[2019]:+.1f} pp) — sí hay repunte.")

    print("\n— Realidad: criminalidad (serie parcial, prensa/oficial) —\n")
    counts = crime_series(crime_df, "infracciones_penales")
    rate = crime_series(crime_df, "tasa_criminalidad_1000")
    print("infracciones penales:", {int(y): int(v) for y, v in counts.items()})
    print("tasa/1000 hab.:", {int(y): v for y, v in rate.items()})
    print("Δ2024 vs 2023:", dict(zip(
        crime_series(crime_df, "var_interanual_pct").index.astype(int),
        crime_series(crime_df, "var_interanual_pct").values)), "% (total)")

    print("\n— La tijera (ventana 2019→2024) —")
    # criminalidad 2019→2024: sin 2024 absoluto, usamos la señal disponible
    # (tasa sube 2019→2021; +11,8 % en 2024) → dirección 'sube'
    crime_dir = pd.Series({2019: rate[2019], 2024: rate[2019] * 1.10})  # proxy ↑
    sc = scissors(share, crime_dir, 2019, 2024, 1.0)
    print(f"  percepción {sc['perception']} ({sc['perc_delta']:+} pp) · "
          f"criminalidad {sc['crime']} (proxy) → VEREDICTO: {sc['veredicto']}")
    print("  Con los datos actuales percepción y realidad se mueven JUNTAS en")
    print("  2019→2024: la 'tijera' no está demostrada. Lo robusto: 2024 sigue")
    print("  muy por debajo de 1989. Falta la serie oficial completa para cerrar.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        tab.to_csv(OUTDIR / "perception_insecurity_share.csv")
        print(f"\n[guardado] {OUTDIR / 'perception_insecurity_share.csv'}")


if __name__ == "__main__":
    main()
