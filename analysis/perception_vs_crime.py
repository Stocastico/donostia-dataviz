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

- **Realidad — municipio** (parcial): infracciones penales conocidas y tasa/1000
  hab. de **Donostia** (Ertzaintza + Guardia Municipal, vía Balance de
  Criminalidad del Min. del Interior). Solo puntos sueltos de prensa
  (2019–2021 + Δ2024). Fuente curada: `datos/input/criminalidad_donostia.csv`.

- **Realidad — provincia** (completa): serie oficial anual del **Portal
  Estadístico de Criminalidad** (Min. del Interior), infracciones penales
  conocidas por tipología, **Gipuzkoa 2010–2024**. Fuente curada:
  `datos/input/criminalidad_gipuzkoa_mir.csv`. ⚠️ **Es la provincia, no la
  ciudad**: Donostia es ~⅓ de la población de Gipuzkoa y su mayor municipio, así
  que la serie vale como **telón de fondo regional** de la tendencia, no como el
  dato exacto de la ciudad — hay que decirlo así en cualquier relato.

La «tijera»: si la percepción de inseguridad **sube** mientras la criminalidad
real **baja/se estanca**, la hipótesis del usuario se sostiene. Si suben juntas,
no.

Hallazgo (con la serie oficial de Gipuzkoa ya en la mano, honesto):
- A **largo plazo** la percepción de inseguridad ha *mejorado* mucho: de ~35 %
  de familias con algún problema en 1989 a ~14–18 % en 2004–2019 → «ha bajado
  mucho la seguridad» es **falso** en perspectiva histórica.
- Pero hay un **repunte reciente 2019→2024** (14,6 %→21,5 %), coherente con la
  encuesta municipal 2026 (inseguridad 2ª preocupación). Y la criminalidad real
  de Gipuzkoa **también sube con fuerza** en esa ventana (+34 %, 25.016→33.425
  infracciones) tras una década plana → en el corto plazo percepción y realidad
  **coinciden**, no divergen: la «tijera» *no* se sostiene y el repunte de
  preocupación tiene **base real**.
- El titular queda en dos tiempos: la ciudad se percibe mucho más segura que en
  los 80/90 (la alarma «de siempre» es falsa), pero el empeoramiento de los
  últimos años es real, no solo una impresión.

Lecturas honestas: la percepción es de la **zona comarcal** Donostia-Bajo
Bidasoa (Eustat), cada 5 años; la criminalidad completa es de **Gipuzkoa
provincia** (Min. Interior), no del municipio (Donostia ≈ ⅓ de la provincia) →
telón de fondo regional, no el dato de la ciudad; la serie municipal es parcial
(prensa); correlación ≠ causalidad; N pequeño.

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
CRIME_GIPUZKOA = ROOT / "datos" / "input" / "criminalidad_gipuzkoa_mir.csv"
OUTDIR = Path(__file__).resolve().parent / "output"

DONOSTIA_ZONA = "70"
TOTAL_TIPOLOGIA = "TOTAL INFRACCIONES PENALES"


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


def read_crime_gipuzkoa(path: Path = CRIME_GIPUZKOA) -> pd.DataFrame:
    """Serie oficial del Portal Estadístico de Criminalidad (Gipuzkoa, provincia)."""
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    df["infracciones"] = df["infracciones"].astype(int)
    return df


def gipuzkoa_series(df: pd.DataFrame,
                    tipologia: str = TOTAL_TIPOLOGIA) -> pd.Series:
    """year → infracciones de una tipología (por defecto el total provincial)."""
    sub = df[df["tipologia"] == tipologia]
    return sub.set_index("year")["infracciones"].astype(float).sort_index()


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

    print("\n— Realidad (municipio, parcial): criminalidad de Donostia (prensa) —\n")
    counts = crime_series(crime_df, "infracciones_penales")
    rate = crime_series(crime_df, "tasa_criminalidad_1000")
    print("infracciones penales:", {int(y): int(v) for y, v in counts.items()})
    print("tasa/1000 hab.:", {int(y): v for y, v in rate.items()})
    print("Δ2024 vs 2023:", dict(zip(
        crime_series(crime_df, "var_interanual_pct").index.astype(int),
        crime_series(crime_df, "var_interanual_pct").values)), "% (total)")

    print("\n— Realidad (provincia, completa): Gipuzkoa 2010–2024 —")
    print("  (Portal Estadístico de Criminalidad, Min. Interior. ⚠️ provincia,")
    print("   no municipio: Donostia ≈ ⅓ de Gipuzkoa → telón de fondo regional)\n")
    gip_df = read_crime_gipuzkoa()
    total = gipuzkoa_series(gip_df)
    print("total infracciones:", {int(y): int(v) for y, v in total.items()})
    dec = (total[2019] / total[2010] - 1) * 100
    rec = (total[2024] / total[2019] - 1) * 100
    print(f"  década plana 2010→2019 ({dec:+.0f} %), salto reciente "
          f"2019→2024 ({rec:+.0f} %).")
    # tipologías que más tiran del repunte reciente
    tipos = ["5. PATRIMONIO", "5.1.-Hurtos", "3. LIBERTAD SEXUAL",
             "1. CONTRA LAS PERSONAS"]
    print("  variación 2019→2024 por bloque:")
    for t in tipos:
        s = gipuzkoa_series(gip_df, t)
        print(f"    {t:<28} {int(s[2019]):>6} → {int(s[2024]):>6} "
              f"({(s[2024] / s[2019] - 1) * 100:+.0f} %)")

    print("\n— La tijera (ventana 2019→2024) —")
    sc = scissors(share, total, 2019, 2024, threshold=1.0)
    print(f"  percepción {sc['perception']} ({sc['perc_delta']:+} pp) · "
          f"criminalidad real {sc['crime']} ({sc['crime_delta']:+.0f} infr.) "
          f"→ VEREDICTO: {sc['veredicto']}")
    print("  Percepción y realidad se mueven JUNTAS en 2019→2024: la 'tijera'")
    print("  NO se sostiene — el repunte de preocupación tiene base real. Pero a")
    print("  largo plazo 2024 (21,5 %) sigue MUY por debajo de 1989 (35,4 %):")
    print("  «la seguridad ha bajado mucho» es falso en perspectiva histórica.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        tab.to_csv(OUTDIR / "perception_insecurity_share.csv")
        total.rename("infracciones").to_csv(
            OUTDIR / "crime_gipuzkoa_total.csv")
        print(f"\n[guardado] {OUTDIR / 'perception_insecurity_share.csv'}")
        print(f"[guardado] {OUTDIR / 'crime_gipuzkoa_total.csv'}")


if __name__ == "__main__":
    main()
