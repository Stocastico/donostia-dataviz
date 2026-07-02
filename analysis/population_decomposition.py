"""AN-12 — Descomponer el cambio de población por barrio: ¿vegetativo o migratorio?

No existe dataset abierto de saldo vegetativo/migratorio por barrio (ver
BACKLOG AN-12), así que se estima con el método clásico del **residuo por
cohortes** sobre la pirámide quinquenal del padrón (`edad_barrio.csv`,
2000–2025) y las tablas de mortalidad provinciales del INE
(`ine_mortalidad_gipuzkoa.json`, ₅qx 1991–2024):

    ΔP  =  nacimientos_proxy  −  defunciones_esperadas  +  migración_neta

Por ventana de 5 años cada cohorte envejece exactamente un grupo; las
defunciones esperadas salen de aplicar las ₅qx de Gipuzkoa (promedio de los
años de la ventana) a la pirámide inicial, y la migración neta es el residuo
cohorte a cohorte. La identidad es exacta por construcción.

Lecturas honestas / límites del método:
- `nacimientos_proxy` = población 00-04 al cierre de la ventana: mezcla los
  nacimientos con la migración neta de menores de 5 (familias que entran o
  salen) y descuenta su mortalidad. El saldo TOTAL no se ve afectado, pero el
  reparto vegetativo/migratorio es aproximado en esa franja.
- Se aplican las ₅qx provinciales a todos los barrios: sin diferencial de
  mortalidad por barrio (no publicado). En 25–39 la mortalidad es ~1–3‰ por
  quinquenio, así que el residuo joven es prácticamente migración pura.
- El grupo abierto 95+ usa ₅q=1 (tabla INE): sobreestima algo sus
  defunciones e infla en la misma cuantía la migración estimada del grupo
  que lo recibe; irrelevante para la pregunta (cohortes jóvenes).
- El padrón de Oarain no aparece en `edad_barrio.csv` (18 de 19 barrios) y
  las filas "Ezezaguna" (2–3 personas) se descartan.

Solo pandas + numpy. Requiere los crudos (bash datos/input/descargar_raw.sh).
Uso:
    python analysis/population_decomposition.py [--save]
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "datos" / "input" / "raw"
PYRAMID_CSV = RAW / "edad_barrio.csv"
QX_JSON = RAW / "ine_mortalidad_gipuzkoa.json"
OUTDIR = Path(__file__).resolve().parent / "output"

# Grupos quinquenales de la pirámide del padrón: 00-04, 05-09, …, 95->=.
AGE_LOS_PYR = list(range(0, 100, 5))          # 20 límites inferiores
N_GROUPS = len(AGE_LOS_PYR)
# Edades de las tablas de mortalidad INE: 0, 1-4, 5-9, …, 90-94, 95+.
AGE_LOS = [0, 1] + list(range(5, 100, 5))

WINDOWS = [(2000, 2005), (2005, 2010), (2010, 2015), (2015, 2020), (2020, 2025)]
YOUTH_LOS = (25, 30, 35)                      # cohortes 25-39 al inicio

_INE_AGE_RE = re.compile(r"De (\d+) a \d+ años|(\d+) años|(\d+) y más años")


def slug(auzoa: str) -> str:
    """'ATEGORRIETA - ULIA' → 'ategorrieta-ulia' (como los barrio_id del repo)."""
    s = unicodedata.normalize("NFKD", auzoa).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", "", s).lower()


# --------------------------------------------------------------- carga ----
def load_pyramid(path: Path = PYRAMID_CSV) -> pd.DataFrame:
    """Pirámide larga [barrio, year, age_idx, pop] desde el CSV del padrón."""
    if not path.exists():
        raise FileNotFoundError(
            f"falta {path} — ejecuta `bash datos/input/descargar_raw.sh`")
    df = pd.read_csv(path)
    df = df[df["Auzoa"] != "Ezezaguna"].copy()
    df["barrio"] = df["Auzoa"].map(slug)
    df["age_idx"] = df["AdinTartea"].str.slice(0, 2).astype(int) // 5
    out = (df.rename(columns={"Urtea": "year", "PertsonenKop": "pop"})
             [["barrio", "year", "age_idx", "pop"]])
    out["pop"] = out["pop"].astype(float)
    return out


def parse_qx(payload: list[dict]) -> pd.DataFrame:
    """JSON del INE (Tempus 67235 filtrado) → [sexo, year, age_lo, qx].

    Los valores vienen en ‰ y son ₅qx (probabilidad de morir en el tramo).
    El grupo antiguo "90 y más" (solapa con 90-94 + 95+) se descarta.
    """
    rows = []
    for serie in payload:
        parts = [p.strip() for p in serie["Nombre"].split(".")]
        sexo, edad = parts[1], parts[2]
        if edad == "90 y más años":
            continue
        m = _INE_AGE_RE.fullmatch(edad)
        if not m:
            continue
        age_lo = int(next(g for g in m.groups() if g is not None))
        for punto in serie["Data"]:
            rows.append({"sexo": sexo, "year": punto["Anyo"],
                         "age_lo": age_lo, "qx": punto["Valor"] / 1000.0})
    return pd.DataFrame(rows)


def load_qx(path: Path = QX_JSON) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"falta {path} — ejecuta `bash datos/input/descargar_raw.sh`")
    return parse_qx(json.loads(path.read_text(encoding="utf-8")))


# ------------------------------------------------- mortalidad esperada ----
def window_q5(qx: pd.DataFrame, t0: int, t1: int, sexo: str = "Total") -> np.ndarray:
    """₅q por grupo de la pirámide, promediando los años [t0, t1).

    El grupo 00-04 combina las filas INE '0' y '1-4':
    q = 1 − (1−q0)(1−q1_4). El resto de grupos coincide 1:1.
    """
    g = qx[(qx.sexo == sexo) & (qx.year >= t0) & (qx.year < t1)]
    mean = g.groupby("age_lo")["qx"].mean()
    q5 = np.empty(N_GROUPS)
    q5[0] = 1.0 - (1.0 - mean.loc[0]) * (1.0 - mean.loc[1])
    for i, lo in enumerate(AGE_LOS_PYR[1:], start=1):
        q5[i] = mean.loc[lo]
    return q5


# --------------------------------------------------------- descomponer ----
def _panels(pyr: pd.DataFrame, t0: int, t1: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pirámides barrio × age_idx en t0 y t1 (solo barrios presentes en ambas)."""
    p0 = (pyr[pyr.year == t0].pivot_table(index="barrio", columns="age_idx",
                                          values="pop", aggfunc="sum")
          .reindex(columns=range(N_GROUPS)).fillna(0.0))
    p1 = (pyr[pyr.year == t1].pivot_table(index="barrio", columns="age_idx",
                                          values="pop", aggfunc="sum")
          .reindex(columns=range(N_GROUPS)).fillna(0.0))
    common = p0.index.intersection(p1.index)
    return p0.loc[common], p1.loc[common]


def _expected_arrivals(p0: pd.DataFrame, q5: np.ndarray) -> pd.DataFrame:
    """Supervivientes esperados por grupo de destino en t1 (columna 0 = 0)."""
    surv = p0.to_numpy() * (1.0 - q5)
    arr = np.zeros_like(surv)
    arr[:, 1:] = surv[:, :-1]
    arr[:, -1] += surv[:, -1]           # el 95+ retiene a sus supervivientes
    return pd.DataFrame(arr, index=p0.index, columns=p0.columns)


def migration_by_age(pyr: pd.DataFrame, q5: np.ndarray, t0: int, t1: int) -> pd.DataFrame:
    """Residuo migratorio por grupo de DESTINO en t1 (columna 0 → NaN)."""
    p0, p1 = _panels(pyr, t0, t1)
    m = p1 - _expected_arrivals(p0, q5)
    m[0] = np.nan                        # los 00-04 son el proxy de nacimientos
    return m


def decompose(pyr: pd.DataFrame, q5: np.ndarray, t0: int, t1: int) -> pd.DataFrame:
    """Descomposición por barrio de la ventana t0→t1 (identidad exacta)."""
    p0, p1 = _panels(pyr, t0, t1)
    deaths = (p0 * q5).sum(axis=1)
    births = p1[0].astype(float)
    migration = (p1 - _expected_arrivals(p0, q5)).drop(columns=0).sum(axis=1)
    out = pd.DataFrame({
        "pop_t0": p0.sum(axis=1), "pop_t1": p1.sum(axis=1),
        "nacimientos_proxy": births, "defunciones_esperadas": deaths,
        "migracion_neta": migration,
    })
    out["delta"] = out.pop_t1 - out.pop_t0
    out["saldo_vegetativo"] = out.nacimientos_proxy - out.defunciones_esperadas
    return out


def youth_net_rate(pyr: pd.DataFrame, q5: np.ndarray, t0: int, t1: int) -> pd.Series:
    """Tasa neta de migración de las cohortes 25-39 en t0 (residuo/población)."""
    p0, p1 = _panels(pyr, t0, t1)
    m = p1 - _expected_arrivals(p0, q5)
    src = [AGE_LOS_PYR.index(lo) for lo in YOUTH_LOS]
    dst = [i + 1 for i in src]
    return (m[dst].sum(axis=1) / p0[src].sum(axis=1)).rename("tasa_neta_25_39")


# -------------------------------------------------------------- informe ----
def run_all(pyr: pd.DataFrame, qx: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Descomposición por ventana y tasas jóvenes; formato largo para CSV."""
    decs, youth = [], []
    for t0, t1 in WINDOWS:
        q5 = window_q5(qx, t0, t1)
        d = decompose(pyr, q5, t0, t1)
        d.insert(0, "ventana", f"{t0}-{t1}")
        decs.append(d.reset_index())
        y = youth_net_rate(pyr, q5, t0, t1).reset_index()
        y.insert(0, "ventana", f"{t0}-{t1}")
        youth.append(y)
    return pd.concat(decs, ignore_index=True), pd.concat(youth, ignore_index=True)


def _fmt(df: pd.DataFrame) -> str:
    return df.to_string(float_format=lambda v: f"{v:,.0f}".replace(",", "."))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    pyr, qx = load_pyramid(), load_qx()
    dec, youth = run_all(pyr, qx)

    print("=" * 76)
    print("AN-12 · ¿VEGETATIVO O MIGRATORIO?  residuo por cohortes 2000→2025")
    print("=" * 76)

    total = (dec.groupby("barrio")[["delta", "nacimientos_proxy",
                                    "defunciones_esperadas", "saldo_vegetativo",
                                    "migracion_neta"]]
             .sum().sort_values("delta"))
    print("\nAcumulado 2000→2025 por barrio (personas):\n")
    print(_fmt(total))

    print("\nCentro (erdialdea + gros) por ventana:\n")
    centro = (dec[dec.barrio.isin(["erdialdea", "gros"])]
              .groupby("ventana")[["delta", "saldo_vegetativo", "migracion_neta"]]
              .sum())
    print(_fmt(centro))

    print("\nTasa neta de migración de cohortes 25-39 (por ventana):\n")
    yt = youth.pivot_table(index="barrio", columns="ventana",
                           values="tasa_neta_25_39")
    print(yt.to_string(float_format=lambda v: f"{100 * v:+.1f}%"))

    print("\nLectura: migración_neta = residuo tras mortalidad esperada (₅qx")
    print("Gipuzkoa, INE); nacimientos_proxy = población 00-04 al cierre (ver")
    print("docstring para los límites del reparto vegetativo/migratorio).")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        dec.to_csv(OUTDIR / "population_decomposition.csv", index=False)
        youth.to_csv(OUTDIR / "youth_net_migration.csv", index=False)
        print(f"\n[guardado] {OUTDIR / 'population_decomposition.csv'}")
        print(f"[guardado] {OUTDIR / 'youth_net_migration.csv'}")


if __name__ == "__main__":
    main()
