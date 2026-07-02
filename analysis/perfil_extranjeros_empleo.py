"""AN-21 — Perfil migratorio y de empleo: ¿quién trabaja en qué en Donostia?

Dos preguntas encadenadas (petición de usuario, jul-2026): (1) la población
extranjera de Donostia — ¿de dónde viene, por barrio, y cómo ha evolucionado?
¿encaja con la intuición de "varios perfiles distintos" (trabajo en
hostelería/cuidados/comercio, pareja o trabajo cualificado europeo, sin
empleo estable, nómada digital)? (2) en qué trabaja la ciudad en general —
¿es cierto que Donostia tiene mucha más investigación que la media española?
¿qué barrios concentran los empleos "humildes" frente a los mejor pagados?

Fuentes (ver `docs/SOURCES.md` / `datos/input/FUENTES.md`, registro REC-21):

- **País de origen por barrio** (Donostia Open Data, `demografia-origen`,
  el mismo CSV que ya alimenta `pct_foreign` en el pipeline, pero aquí sin
  agregar a "extranjero sí/no": 57 países, 2000–2025, por barrio). Lo único
  granular a **barrio** de todo este análisis.
- **Actividad de la población extranjera por continente** (Eustat EMPA,
  `PX_050407_cempa_empa_pa16`) — ocupados/parados/inactivos por continente de
  nacionalidad, solo grano **Gipuzkoa** (Eustat no baja a municipio en microdatos
  de la EPA-EUS por tamaño muestral).
- **Tasas de actividad/ocupación/paro por nacionalidad** (Eustat PRA,
  `PX_050403_cpra_tab17`) — española vs. extranjera, Gipuzkoa, 2015–2026.
- **Ocupación (CNO-11, 10 grupos) de la población ocupada** (Eustat EMPA,
  `PX_050407_cempa_empa_po38`) — Gipuzkoa, 2021–2024. Sin cruce con
  nacionalidad (Eustat no lo publica a este grano).
- **Personal dedicado a I+D** (Eustat, `PX_043201_cid_res08c`) — Gipuzkoa,
  investigadores vs. técnicos vs. auxiliares, 2001–2024, para comparar con
  el dato nacional citado por el INE (13,6‰ ocupados en I+D, 8,5‰
  investigadores, España 2024).
- **Establecimientos por sector (A10) en Donostia** (Eustat DIRAE,
  `PX_200163_cdirae_est02c`) — municipio 20069, 2008–2025. Es *establecimientos*,
  no personas empleadas (Eustat solo publica empleo por sector a nivel de
  territorio histórico, no municipio) — proxy de composición sectorial, mismo
  tipo de limitación que REC-7 ya documentada.

**Lo que NO existe y por qué**: no hay ninguna tabla pública en España que
cruce nacionalidad × ocupación × salario a nivel municipal, ni siquiera
provincial — la EPA y la Agencatributaria solo publican esos cruces a nivel
CC.AA./estatal por tamaño muestral, y Eustat replica la misma limitación.
Tampoco hay salario por nacionalidad. Esta es una limitación de la
estadística pública, no del pipeline: se documenta como brecha, no se rellena
con proxies poco honestos (ver `docs/NOTA-METODOLOGICA.md`, MET-5 —
"% extranjeros no es proxy de gentrificación").

Uso:
    python analysis/perfil_extranjeros_empleo.py [--save]
Requiere los crudos descargados (ver cabecera de cada loader para la URL/query
exacta; no están en `descargar_raw.sh` todavía — añadir si se decide wirear).
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "datos" / "input" / "raw"
OUTDIR = Path(__file__).resolve().parent / "output"

DEMO_CSV = RAW / "demo_barrio_nacionalidad.csv"
SPAIN = "ESPAÑA"

# ---------------------------------------------------------------------------
# Barrio identity (mismo criterio que data-pipeline/config.py, sin depender
# de él para que este script corra sin instalar el paquete del pipeline).
# ---------------------------------------------------------------------------
BARRIO_NAMES: dict[str, str] = {
    "1": "Aiete", "2": "Altza", "3": "Amara Berri", "4": "Antiguo",
    "5": "Añorga", "6": "Ategorrieta-Ulia", "7": "Erdialdea", "8": "Egia",
    "9": "Gros", "10": "Ibaeta", "11": "Igeldo", "12": "Intxaurrondo",
    "13": "Loiola", "14": "Martutene", "15": "Mirakruz-Bidebieta",
    "16": "Miramón-Zorroaga", "17": "Zubieta", "18": "Landarbaso",
    "19": "Oarain",
}

# ---------------------------------------------------------------------------
# País -> grupo regional. Deliberadamente más fino que el "extranjero sí/no"
# del pipeline (`pct_foreign`), para poder leer los distintos perfiles
# migratorios que se mezclan en esa cifra agregada (ver NOTA-METODOLOGICA
# MET-5). Los grupos separan patrones de origen conocidos en la literatura
# migratoria española, no destino laboral (que no está en los datos):
# económico reciente (América Latina, Magreb, África subsahariana, Europa
# del Este) vs. cualificado/rentista (Europa occidental, Norteamérica/Oceanía)
# vs. Oriente Medio (patrón mixto, con componente de asilo).
COUNTRY_TO_REGION: dict[str, str] = {
    # América Latina
    "ARGENTINA": "América Latina", "BOLIVIA": "América Latina",
    "BRASIL": "América Latina", "CHILE": "América Latina",
    "COLOMBIA": "América Latina", "COSTA RICA": "América Latina",
    "CUBA": "América Latina", "ECUADOR": "América Latina",
    "EL SALVADOR": "América Latina", "GUATEMALA": "América Latina",
    "HONDURAS": "América Latina", "MEXICO": "América Latina",
    "NICARAGUA": "América Latina", "PARAGUAY": "América Latina",
    "PERU": "América Latina", "REPUBLICA DOMINICANA": "América Latina",
    "URUGUAY": "América Latina", "VENEZUELA": "América Latina",
    # Norte de África (Magreb)
    "MARRUECOS": "Norte de África", "ARGELIA": "Norte de África",
    # África subsahariana
    "SENEGAL": "África subsahariana", "MALI": "África subsahariana",
    "CAMERUN": "África subsahariana", "GHANA": "África subsahariana",
    "GUINEA ECUATORIAL": "África subsahariana",
    "NIGERIA": "África subsahariana", "MAURITANIA": "África subsahariana",
    # Europa occidental / nórdica (renta alta, libre circulación UE)
    "ALEMANIA": "Europa occidental", "FRANCIA": "Europa occidental",
    "ITALIA": "Europa occidental", "PAISES BAJOS": "Europa occidental",
    "REINO UNIDO": "Europa occidental", "IRLANDA": "Europa occidental",
    "SUECIA": "Europa occidental", "GRECIA": "Europa occidental",
    "PORTUGAL": "Europa occidental",
    # Europa del este / ex-URSS (patrón migratorio económico, distinto del
    # anterior aunque ambos sean "Europa")
    "RUMANIA": "Europa del Este", "BULGARIA": "Europa del Este",
    "POLONIA": "Europa del Este", "MOLDAVIA": "Europa del Este",
    "UCRANIA": "Europa del Este", "RUSIA": "Europa del Este",
    "GEORGIA": "Europa del Este", "ARMENIA": "Europa del Este",
    # Oriente Medio (patrón mixto, componente de asilo notable en Siria)
    "IRAN": "Oriente Medio", "SIRIA": "Oriente Medio",
    # Asia oriental / meridional
    "CHINA": "Asia oriental/meridional", "FILIPINAS": "Asia oriental/meridional",
    "INDIA": "Asia oriental/meridional", "JAPON": "Asia oriental/meridional",
    "COREA": "Asia oriental/meridional", "VIETNAM": "Asia oriental/meridional",
    "NEPAL": "Asia oriental/meridional", "PAKISTAN": "Asia oriental/meridional",
    "MONGOLIA": "Asia oriental/meridional",
    # Norteamérica / Oceanía (renta alta)
    "ESTADOS UNIDOS DE AMERICA": "Norteamérica/Oceanía",
    "AUSTRALIA": "Norteamérica/Oceanía",
}

REGION_ORDER = [
    "España", "América Latina", "Norte de África", "África subsahariana",
    "Europa occidental", "Europa del Este", "Oriente Medio",
    "Asia oriental/meridional", "Norteamérica/Oceanía",
]

# Grupos "económicos recientes" vs. "renta alta" para el resumen de
# hipótesis — una lectura, no una etiqueta impuesta a cada persona.
ECONOMIC_MIGRATION = {"América Latina", "Norte de África", "África subsahariana",
                       "Europa del Este", "Oriente Medio", "Asia oriental/meridional"}
HIGH_INCOME_MIGRATION = {"Europa occidental", "Norteamérica/Oceanía"}


def miles(n: float) -> str:
    """Entero con separador de miles "." (formato español), aislado del resto
    del texto — evitar `.replace(",", ".")` sobre cadenas completas: corrompe
    etiquetas con comas de verdad (p.ej. "Comercio, transporte y hostelería")."""
    return f"{n:,.0f}".replace(",", ".")


def region_of(country: str) -> str:
    country = country.strip().upper()
    if country == SPAIN:
        return "España"
    return COUNTRY_TO_REGION.get(country, "Otros/no clasificado")


# ---------------------------------------------------------------------------
# 1. País de origen por barrio (única fuente a grano barrio de este script)
# ---------------------------------------------------------------------------
def load_origen_barrio(path: Path = DEMO_CSV) -> pd.DataFrame:
    """Filas (year, barrio_id, barrio_name, country, region, people)."""
    if not path.exists():
        raise FileNotFoundError(f"falta {path} — descárgalo de Donostia Open Data "
                                 "(demografia-origen/demografianacionalidadbarrio.csv)")
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            code = row["AuzoKodea"].strip()
            if code not in BARRIO_NAMES:
                continue  # "Ezezaguna" (barrio desconocido), ~0.12% de la población
            try:
                people = int(row["PertsonenKop"])
            except (TypeError, ValueError):
                continue
            country = row["Jatorria"].strip()
            rows.append({
                "year": int(row["Urtea"]),
                "barrio_id": code,
                "barrio_name": BARRIO_NAMES[code],
                "country": country,
                "region": region_of(country),
                "people": people,
            })
    return pd.DataFrame(rows)


def city_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """year × region -> people, pct sobre población total, pct sobre extranjeros."""
    by_region = df.groupby(["year", "region"])["people"].sum().reset_index()
    total = df.groupby("year")["people"].sum().rename("total_pop")
    foreign_total = (df[df.region != "España"].groupby("year")["people"].sum()
                      .rename("total_foreign"))
    out = by_region.merge(total, on="year").merge(foreign_total, on="year", how="left")
    out["pct_of_population"] = (out["people"] / out["total_pop"] * 100).round(3)
    out["pct_of_foreign"] = None
    mask = out.region != "España"
    out.loc[mask, "pct_of_foreign"] = (out.loc[mask, "people"]
                                        / out.loc[mask, "total_foreign"] * 100).round(3)
    return out[["year", "region", "people", "pct_of_population", "pct_of_foreign"]]


def barrio_by_region_latest(df: pd.DataFrame, year: int | None = None) -> pd.DataFrame:
    """barrio × region -> people y % del barrio, para el año más reciente disponible."""
    year = year or df.year.max()
    sub = df[df.year == year]
    by_region = sub.groupby(["barrio_id", "barrio_name", "region"])["people"].sum().reset_index()
    total = sub.groupby("barrio_id")["people"].sum().rename("barrio_pop")
    out = by_region.merge(total, on="barrio_id")
    out["pct_of_barrio"] = (out["people"] / out["barrio_pop"] * 100).round(2)
    return out.sort_values(["barrio_id", "people"], ascending=[True, False])


def top_countries(df: pd.DataFrame, year: int | None = None, n: int = 15) -> pd.DataFrame:
    """Top-n países extranjeros por población en el año más reciente, con
    comparación a 10 años antes cuando existe (evolución)."""
    year = year or df.year.max()
    past_year = year - 10 if (year - 10) in set(df.year) else df.year.min()
    latest = (df[(df.year == year) & (df.country != SPAIN)]
              .groupby("country")["people"].sum().rename("people_latest"))
    past = (df[(df.year == past_year) & (df.country != SPAIN)]
            .groupby("country")["people"].sum().rename(f"people_{past_year}"))
    out = pd.concat([latest, past], axis=1).fillna(0).astype(int)
    out["region"] = [region_of(c) for c in out.index]
    out = out.sort_values("people_latest", ascending=False).head(n)
    out.index.name = "country"
    return out.reset_index()


# ---------------------------------------------------------------------------
# 2. Eustat PxWeb (JSON-stat) — helpers compartidos + un loader por tabla.
#    Grano Gipuzkoa/Donostia según tabla (documentado en cada función).
# ---------------------------------------------------------------------------
def _pxweb_frame(path: Path, dim_names: list[str]) -> pd.DataFrame:
    """JSON-stat PxWeb -> DataFrame largo (una columna por dimensión + value).

    Mismo formato que ya parsea `movilidad_laboral.py` en el pipeline
    (``key``/``values`` por fila); aquí se generaliza a N dimensiones en vez
    de asumir una tabla concreta.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for rec in payload["data"]:
        try:
            value = float(rec["values"][0])
        except (TypeError, ValueError):
            continue  # ":" = dato no disponible en PxWeb
        row = dict(zip(dim_names, rec["key"]))
        row["value"] = value
        rows.append(row)
    return pd.DataFrame(rows)


def load_extranjeros_actividad(path: Path) -> pd.DataFrame:
    """Ocupados/parados/inactivos por continente de nacionalidad, Gipuzkoa
    (Eustat EMPA pa16, 2010–2024, "miles" salvo que la tabla ya venga en
    personas — Eustat pa16 está en personas, no miles, verificado por orden
    de magnitud: ~36 000 extranjeros en Gipuzkoa en 2010)."""
    df = _pxweb_frame(path, ["territorio", "continente_code", "actividad_code", "sexo", "year"])
    continente = {"10": "Total", "20": "Europa", "30": "África", "40": "América",
                  "50": "Asia", "60": "Oceanía"}
    actividad = {"10": "Total", "20": "Ocupada", "30": "Parada", "40": "Inactiva"}
    df["continente"] = df.continente_code.map(continente)
    df["actividad"] = df.actividad_code.map(actividad)
    df["year"] = df.year.astype(int)
    return df[["year", "continente", "actividad", "value"]]


def load_tasas_nacionalidad(path: Path) -> pd.DataFrame:
    """Tasas de actividad/ocupación/paro (%) por nacionalidad, Gipuzkoa,
    2015–2026 (Eustat PRA tab17, promedio anual; el año en curso puede venir
    incompleto)."""
    df = _pxweb_frame(path, ["tasa_code", "territorio", "nac_code", "trimestre", "year"])
    tasa = {"10": "Actividad", "20": "Ocupación", "30": "Paro"}
    nac = {"10": "Total", "20": "Española", "30": "Extranjera"}
    df["tasa"] = df.tasa_code.map(tasa)
    df["nacionalidad"] = df.nac_code.map(nac)
    df["year"] = df.year.astype(int)
    return df[["year", "tasa", "nacionalidad", "value"]]


def load_ocupacion_cno(path: Path) -> pd.DataFrame:
    """Ocupados por grupo CNO-11 (10 grupos), Gipuzkoa, 2021–2024 (Eustat
    EMPA po38, personas — a diferencia de PRA tab04, esta tabla NO viene en
    miles, verificado por magnitud: la suma de grupos cuadra con el total de
    ocupados de Gipuzkoa, ~335k). Sin cruce con nacionalidad — Eustat no lo
    publica a este grano."""
    df = _pxweb_frame(path, ["territorio", "cno_code", "rama_code", "sexo", "year"])
    cno = {
        "_T": "Total", "1": "Directores y gerentes",
        "2": "Técnicos y profesionales científicos e intelectuales",
        "3": "Técnicos y profesionales de apoyo",
        "4": "Empleados contables/administrativos/oficina",
        "5": "Servicios de restauración, personales, protección y vendedores",
        "6": "Cualificados agrario/ganadero/forestal/pesquero",
        "7": "Artesanos y cualificados de industrias manufactureras",
        "8": "Operadores de instalaciones y montadores",
        "9": "Ocupaciones elementales", "0": "Ocupaciones militares",
    }
    df["ocupacion"] = df.cno_code.map(cno)
    df["year"] = df.year.astype(int)
    return df[["year", "ocupacion", "value"]]


def load_id_personal(path: Path) -> pd.DataFrame:
    """Personal EDP (equivalente a dedicación plena) en I+D, Gipuzkoa,
    2001–2024 (Eustat cid res08c), por sector de ejecución y ocupación."""
    df = _pxweb_frame(path, ["territorio", "sector_code", "ocup_code", "sexo", "year"])
    sector = {"00": "Total", "10": "Empresas e IPSFL", "20": "Admón. pública",
              "30": "Enseñanza superior"}
    ocup = {"100": "Total", "200": "Investigadores", "300": "Técnicos", "400": "Auxiliares"}
    df["sector"] = df.sector_code.map(sector)
    df["ocupacion"] = df.ocup_code.map(ocup)
    df["year"] = df.year.astype(int)
    return df[["year", "sector", "ocupacion", "value"]]


def load_renta_por_profesion(path: Path) -> pd.DataFrame:
    """Renta personal media del trabajo (€/año) por profesión, C.A. de
    Euskadi, 2021–2023 (Eustat crpf_rp_a_03) — sin barrio ni nacionalidad,
    el grano más fino que publica Eustat para sueldo × ocupación."""
    df = _pxweb_frame(path, ["sexo", "tipo_renta", "prof_code", "year"])
    prof = {
        "100": "Total", "110": "Directores y gerentes",
        "120": "Técnicos y profesionales científicos e intelectuales",
        "130": "Técnicos y profesionales de apoyo",
        "140": "Empleados contables/administrativos/oficina",
        "150": "Servicios de restauración, personales, protección, vendedores y FFAA",
        "160": "Cualificados agrario/ganadero/forestal/pesquero",
        "170": "Artesanos y cualificados de manufactura/construcción",
        "180": "Operadores de instalaciones y montadores",
        "190": "Ocupaciones elementales",
    }
    df["profesion"] = df.prof_code.map(prof)
    df["year"] = df.year.astype(int)
    return df[["year", "profesion", "value"]].rename(columns={"value": "renta_trabajo_eur"})


def load_poblacion_ocupada(path: Path) -> pd.DataFrame:
    """Población ocupada total (miles), CAE y Gipuzkoa, promedio anual
    (Eustat PRA tab04) — denominador para el ratio de personal I+D por mil
    ocupados, comparable con la cifra que publica el INE para España."""
    df = _pxweb_frame(path, ["actividad_code", "territorio", "sexo", "trimestre", "year"])
    terr = {"00": "C.A. de Euskadi", "20": "Gipuzkoa"}
    df["territorio_nombre"] = df.territorio.map(terr)
    df["year"] = df.year.astype(int)
    df["ocupados"] = df.value * 1000  # la tabla viene en miles
    return df[["year", "territorio_nombre", "ocupados"]]


def load_establecimientos_sector(path: Path) -> pd.DataFrame:
    """Establecimientos por sector A10, Donostia, 2008–2025 (Eustat DIRAE
    est02c). Solo "estrato total" (código '00') para no duplicar el conteo
    por tramo de empleo."""
    df = _pxweb_frame(path, ["municipio", "sector_code", "personalidad", "estrato", "year"])
    df = df[df.estrato == "00"]  # total, evita sumar los tramos y el total dos veces
    sector = {
        "0": "Total", "00": "No determinada",
        "01": "Agricultura, ganadería y pesca",
        "02": "Industria, energía y saneamiento", "03": "Construcción",
        "04": "Comercio, transporte y hostelería",
        "05": "Información y comunicaciones", "06": "Actividades financieras y seguros",
        "07": "Actividades inmobiliarias",
        "08": "Actividades profesionales, científicas y administrativas",
        "09": "Administración pública, educación, sanidad y otros servicios",
    }
    df["sector"] = df.sector_code.map(sector)
    df["year"] = df.year.astype(int)
    return df[["year", "sector", "value"]].rename(columns={"value": "establecimientos"})


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    print("=" * 78)
    print("AN-21 · PERFIL MIGRATORIO Y DE EMPLEO — Donostia")
    print("=" * 78)

    # --- 1. Origen por barrio (grano barrio, 2000-2025) ---
    origen = load_origen_barrio()
    latest_year = origen.year.max()
    ciudad = city_by_region(origen)
    print(f"\n[1] Población por región de origen, ciudad, {latest_year} "
          f"(vs. {latest_year - 10}):\n")
    tabla_actual = ciudad[ciudad.year == latest_year].sort_values("people", ascending=False)
    tabla_pasado = ciudad[ciudad.year == latest_year - 10].set_index("region")["pct_of_population"]
    for _, r in tabla_actual.iterrows():
        antes = tabla_pasado.get(r.region)
        delta = f"(hace 10a: {antes:.2f}%)" if antes is not None else ""
        print(f"  {r.region:<28} {miles(r.people):>7}  {r.pct_of_population:>5.2f}% pob. "
              f"{delta}")

    top = top_countries(origen, latest_year)
    print(f"\n[1b] Top-15 países extranjeros, ciudad, {latest_year}:\n")
    print(top.to_string(index=False))

    barrio_region = barrio_by_region_latest(origen, latest_year)
    print(f"\n[1c] Barrios con mayor cuota de 'América Latina' y de "
          f"'Norte de África', {latest_year}:\n")
    for region in ("América Latina", "Norte de África", "Europa occidental"):
        sub = (barrio_region[barrio_region.region == region]
               .sort_values("pct_of_barrio", ascending=False).head(5))
        print(f"  {region}:")
        for _, r in sub.iterrows():
            print(f"    {r.barrio_name:<22} {r.pct_of_barrio:>5.2f}% del barrio "
                  f"({r.people:.0f} personas)")

    # --- 2. Actividad de extranjeros por continente (Gipuzkoa) ---
    path = RAW / "eustat_extranjeros_continente_actividad.json"
    tasas_path = RAW / "eustat_tasas_nacionalidad_gipuzkoa.json"
    cno_path = RAW / "eustat_ocupacion_cno_gipuzkoa.json"
    id_path = RAW / "eustat_id_personal_gipuzkoa.json"
    ocupados_path = RAW / "eustat_poblacion_ocupada_total.json"
    estab_path = RAW / "eustat_establecimientos_sector_donostia.json"

    if path.exists():
        act = load_extranjeros_actividad(path)
        year2 = act.year.max()
        print(f"\n[2] Situación laboral de la población extranjera 16+ por "
              f"continente, Gipuzkoa, {int(year2)} (⚠ grano Gipuzkoa, no Donostia):\n")
        piv = act[act.year == year2].pivot_table(index="continente", columns="actividad",
                                                   values="value", aggfunc="sum")
        for continente in ("Europa", "África", "América", "Asia", "Oceanía"):
            if continente not in piv.index:
                continue
            row = piv.loc[continente]
            total = row.get("Total", row.sum())
            ocup_pct = row.get("Ocupada", 0) / total * 100 if total else 0
            parada_pct = row.get("Parada", 0) / total * 100 if total else 0
            print(f"  {continente:<10} ocupada {ocup_pct:>5.1f}%  parada {parada_pct:>5.1f}%  "
                  f"(n={miles(total)})")

    if tasas_path.exists():
        tasas = load_tasas_nacionalidad(tasas_path)
        year3 = tasas[tasas.value.notna()].year.max()
        print(f"\n[2b] Tasas de actividad/ocupación/paro, española vs. extranjera, "
              f"Gipuzkoa, {int(year3)}:\n")
        sub = tasas[tasas.year == year3]
        for nac in ("Española", "Extranjera"):
            row = sub[sub.nacionalidad == nac].set_index("tasa")["value"]
            print(f"  {nac:<12} actividad {row.get('Actividad', float('nan')):>5.1f}%  "
                  f"ocupación {row.get('Ocupación', float('nan')):>5.1f}%  "
                  f"paro {row.get('Paro', float('nan')):>5.1f}%")

    # --- 3. Ocupación general (CNO-11), Gipuzkoa ---
    if cno_path.exists():
        cno = load_ocupacion_cno(cno_path)
        year4 = cno.year.max()
        print(f"\n[3] Población ocupada por grupo de ocupación (CNO-11), "
              f"Gipuzkoa, {int(year4)} (personas):\n")
        sub = cno[(cno.year == year4) & (cno.ocupacion != "Total")].sort_values(
            "value", ascending=False)
        total = cno[(cno.year == year4) & (cno.ocupacion == "Total")]["value"].sum()
        for _, r in sub.iterrows():
            print(f"  {r.ocupacion:<58} {miles(r.value):>8}  {r.value/total*100:>5.1f}%")

    # --- 3b. Sueldo medio por ocupación (C.A. de Euskadi, sin barrio/nacionalidad) ---
    renta_prof_path = RAW / "eustat_renta_por_profesion.json"
    if renta_prof_path.exists():
        rp = load_renta_por_profesion(renta_prof_path)
        year4b = rp.year.max()
        print(f"\n[3b] Renta media del trabajo por profesión, C.A. de Euskadi, "
              f"{int(year4b)} (€/año; ⚠ sin barrio ni nacionalidad):\n")
        sub = rp[(rp.year == year4b) & (rp.profesion != "Total")].sort_values(
            "renta_trabajo_eur", ascending=False)
        for _, r in sub.iterrows():
            print(f"  {r.profesion:<70} {miles(r.renta_trabajo_eur):>7} €")

    # --- 4. I+D: Gipuzkoa vs. España ---
    if id_path.exists() and ocupados_path.exists():
        idp = load_id_personal(id_path)
        ocup = load_poblacion_ocupada(ocupados_path)
        year5 = idp.year.max()
        total_idp = idp[(idp.year == year5) & (idp.sector == "Total")
                        & (idp.ocupacion == "Total")]["value"].sum()
        investigadores = idp[(idp.year == year5) & (idp.sector == "Total")
                             & (idp.ocupacion == "Investigadores")]["value"].sum()
        gipuzkoa_ocupados = ocup[(ocup.year == year5)
                                 & (ocup.territorio_nombre == "Gipuzkoa")]["ocupados"].sum()
        print(f"\n[4] Personal en I+D, Gipuzkoa, {int(year5)}: {miles(total_idp)} EDP "
              f"({miles(investigadores)} investigadores)")
        if gipuzkoa_ocupados:
            ratio_total = total_idp / gipuzkoa_ocupados * 1000
            ratio_invest = investigadores / gipuzkoa_ocupados * 1000
            print(f"  = {ratio_total:.1f}‰ de los {miles(gipuzkoa_ocupados)} ocupados "
                  f"(investigadores: {ratio_invest:.1f}‰)")
            print("  España 2024 (INE, nota de prensa): 13.6‰ personal I+D, "
                  "8.5‰ investigadores — Gipuzkoa duplica ampliamente ambas cifras.")

    # --- 5. Composición sectorial de establecimientos, Donostia ---
    if estab_path.exists():
        estab = load_establecimientos_sector(estab_path)
        year6 = estab.year.max()
        print(f"\n[5] Establecimientos por sector (A10), Donostia, {int(year6)}:\n")
        sub = estab[(estab.year == year6) & ~estab.sector.isin(["Total", "No determinada"])]
        total_e = estab[(estab.year == year6) & (estab.sector == "Total")]["establecimientos"].sum()
        sub = sub.sort_values("establecimientos", ascending=False)
        for _, r in sub.iterrows():
            print(f"  {r.sector:<52} {miles(r.establecimientos):>6}  "
                  f"{r.establecimientos/total_e*100:>5.1f}%")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        ciudad.to_csv(OUTDIR / "extranjeros_origen_ciudad.csv", index=False)
        barrio_region.to_csv(OUTDIR / "extranjeros_origen_barrio.csv", index=False)
        top.to_csv(OUTDIR / "extranjeros_top_paises.csv", index=False)
        print(f"\n[guardado] {OUTDIR / 'extranjeros_origen_ciudad.csv'}")
        print(f"[guardado] {OUTDIR / 'extranjeros_origen_barrio.csv'}")
        print(f"[guardado] {OUTDIR / 'extranjeros_top_paises.csv'}")
        if path.exists():
            act.to_csv(OUTDIR / "extranjeros_actividad_continente_gipuzkoa.csv", index=False)
            print(f"[guardado] {OUTDIR / 'extranjeros_actividad_continente_gipuzkoa.csv'}")
        if tasas_path.exists():
            tasas.to_csv(OUTDIR / "tasas_actividad_nacionalidad_gipuzkoa.csv", index=False)
            print(f"[guardado] {OUTDIR / 'tasas_actividad_nacionalidad_gipuzkoa.csv'}")
        if cno_path.exists():
            cno.to_csv(OUTDIR / "ocupacion_cno_gipuzkoa.csv", index=False)
            print(f"[guardado] {OUTDIR / 'ocupacion_cno_gipuzkoa.csv'}")
        if id_path.exists():
            idp.to_csv(OUTDIR / "id_personal_gipuzkoa.csv", index=False)
            print(f"[guardado] {OUTDIR / 'id_personal_gipuzkoa.csv'}")
        if estab_path.exists():
            estab.to_csv(OUTDIR / "establecimientos_sector_donostia.csv", index=False)
            print(f"[guardado] {OUTDIR / 'establecimientos_sector_donostia.csv'}")
        if renta_prof_path.exists():
            rp.to_csv(OUTDIR / "renta_por_profesion_caev.csv", index=False)
            print(f"[guardado] {OUTDIR / 'renta_por_profesion_caev.csv'}")


if __name__ == "__main__":
    main()
