"""HU-3 — Tipología comercial por barrio (OpenStreetMap): ¿el turismo cambia
qué tiendas hay?

La hipótesis del usuario: el turismo transforma la Parte Vieja y se nota en el
**cambio de tipología de tiendas** — suben souvenirs/chuches y hostelería,
cierran negocios históricos y de barrio (ferreterías, tiendas para el
residente).

Qué mide (foto **actual**, no evolución) con `shop=*` + `amenity=*` de OSM:

- **hosteleria** (bar, restaurant, cafe, pub, fast_food, ice_cream…): el
  consumo de visitante que en la Parte Vieja *no* es `shop=*` sino `amenity=*`.
- comercios en tres cubos (juicio curado, editable — ver `TURISTICO`/`COTIDIANO`):
  **turistico** (gift/souvenir/dulces/arte, orientado al visitante),
  **cotidiano** (alimentación diaria, ferretería, servicios de barrio,
  farmacia…), **otro** (retail general: ropa, calzado, joyería… sirve a ambos,
  no sesga).
- **vacant**: locales vacíos (señal lateral de REC-11).

Indicadores por barrio:
- `hosteleria_share` = hostelería / (hostelería + comercios activos).
- `turistico_share_shops` = turístico / (turístico + cotidiano) — el eje
  «visitante vs. residente» que pide la hipótesis, ignorando el retail neutro.
- `vacancy_rate` = vacíos / (activos + vacíos).

y se cruzan con la **densidad VUT** por barrio (`metrics_long`) para testear la
hipótesis: ¿más presión turística ↔ mezcla más hostelera/turística?

Lecturas honestas (importantes):
- **OSM es un snapshot y su completitud varía por barrio** (el centro está mejor
  mapeado que la periferia) → los *recuentos absolutos* están sesgados; las
  *proporciones intra-barrio* aguantan mejor, pero el sesgo de mapeo no
  desaparece. Coverage, no censo.
- **No hay dimensión temporal**: OSM da la *geografía actual* (qué barrios son
  hosteleros/turísticos hoy), no el *cambio* («cierran ferreterías»). La prueba
  temporal es la serie CNAE de ciudad (REC-7: retail 14,9→12,6 %, hostelería
  6,0→8,1 %, 2008–2025). Las dos se **triangulan**, no se sustituyen.
- La Parte Vieja no es un barrio propio (está en Erdialdea): se aísla por bbox
  declarado (`PARTE_VIEJA_BBOX`) como ficha aparte.
- Clasificación = juicio; correlación ≠ causalidad.

pandas + numpy + shapely. Carga de red (Overpass). Uso:
    python analysis/commercial_typology.py [--save]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import shapely
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
GEOJSON = ROOT / "web" / "src" / "data" / "barrios.geojson"
METRICS = ROOT / "datos" / "procesado" / "tablas" / "metrics_long.csv"
INDICATORS = ROOT / "datos" / "procesado" / "tablas" / "indicators_long.csv"
OUTDIR = Path(__file__).resolve().parent / "output"
CACHE = OUTDIR / "osm_commercial_raw.json"

OVERPASS = "https://overpass-api.de/api/interpreter"
UA = "donostia-dataviz/1.0 (research; contact stocastico@gmail.com)"
AREA = "Donostia / San Sebastián"

# Parte Vieja / Alde Zaharra (bbox declarado, no barrio oficial)
PARTE_VIEJA_BBOX = (43.3235, -1.9895, 43.3270, -1.9835)  # (lat0, lon0, lat1, lon1)

# --- clasificación (juicio curado a partir de la distribución OSM real) ------
HOSPITALITY = frozenset({
    "bar", "pub", "restaurant", "cafe", "fast_food", "biergarten",
    "food_court", "ice_cream", "nightclub",
})
TURISTICO = frozenset({
    "gift", "souvenir", "art", "antiques", "auction_house", "craft",
    "confectionery", "chocolate", "ice_cream",
})
COTIDIANO = frozenset({
    # alimentación diaria
    "bakery", "greengrocer", "butcher", "seafood", "supermarket", "convenience",
    "deli", "cheese", "dairy", "farm", "kiosk", "newsagent", "frozen_food",
    "pasta", "wine", "coffee", "tea", "health_food", "nutrition_supplements",
    "herbalist", "water", "beverages", "spices", "grocery",
    # ferretería / hogar / bricolaje
    "hardware", "doityourself", "paint", "building_materials", "electrical",
    "locksmith", "houseware", "appliance", "kitchen", "bathroom_furnishing",
    "trade", "garden_centre", "fireplace", "lighting", "glaziery", "tools",
    "hairdresser_supply",
    # automoción / reparación
    "car_repair", "car_parts", "tyres", "motorcycle_repair", "repair",
    # servicios personales de barrio / salud
    "hairdresser", "beauty", "laundry", "dry_cleaning", "optician",
    "medical_supply", "hearing_aids", "tailor", "sewing", "chemist",
    "pharmacy", "funeral_directors", "copyshop", "printer_ink", "pet_grooming",
    "veterinary", "cobbler",
})
VACANT_TAGS = ("vacant", "empty", "disused")


# ------------------------------------------------------------- clasificar ---
def classify(tags: dict) -> str | None:
    """Categoría de un local OSM: hosteleria / turistico / cotidiano / otro /
    vacant, o None si no es ni comercio ni hostelería."""
    amenity = tags.get("amenity")
    if amenity in HOSPITALITY:
        return "hosteleria"
    shop = tags.get("shop")
    disused = tags.get("disused:shop")
    if disused and disused != "no":
        return "vacant"
    if shop is None:
        return None
    if shop in VACANT_TAGS:
        return "vacant"
    if shop in TURISTICO:
        return "turistico"
    if shop in COTIDIANO:
        return "cotidiano"
    return "otro"


# ------------------------------------------------------------- parseo OSM ---
def _coord(el: dict) -> tuple[float | None, float | None]:
    if el["type"] == "node":
        return el.get("lon"), el.get("lat")
    c = el.get("center", {})
    return c.get("lon"), c.get("lat")


def parse_overpass(elements: list[dict]) -> pd.DataFrame:
    """Elementos Overpass → [osm_type, osm_id, lon, lat, category] (sin None)."""
    rows = []
    for el in elements:
        cat = classify(el.get("tags", {}))
        if cat is None:
            continue
        lon, lat = _coord(el)
        if lon is None or lat is None:
            continue
        rows.append({"osm_type": el["type"], "osm_id": el["id"],
                     "lon": float(lon), "lat": float(lat), "category": cat})
    return pd.DataFrame(rows,
                        columns=["osm_type", "osm_id", "lon", "lat", "category"])


# -------------------------------------------------- asignación a barrio ----
def assign_barrio(df: pd.DataFrame, features: list[dict]) -> pd.DataFrame:
    """Añade barrio_id por punto-en-polígono; descarta lo que cae fuera."""
    lon = df["lon"].to_numpy(float)
    lat = df["lat"].to_numpy(float)
    barrio = np.full(len(df), None, dtype=object)
    for f in features:
        geom = shape(f["geometry"])
        inside = shapely.contains_xy(geom, lon, lat)
        barrio[inside] = f["properties"]["barrio_id"]
    out = df.assign(barrio_id=barrio).dropna(subset=["barrio_id"])
    return out.reset_index(drop=True)


def in_parte_vieja(lon: float, lat: float,
                   bbox: tuple = PARTE_VIEJA_BBOX) -> bool:
    lat0, lon0, lat1, lon1 = bbox
    return lat0 <= lat <= lat1 and lon0 <= lon <= lon1


# ----------------------------------------------------- mezcla por barrio ----
def mix_by_barrio(df: pd.DataFrame) -> pd.DataFrame:
    """Recuentos por categoría + ratios (hostelería, turístico, vacío)."""
    counts = (df.groupby(["barrio_id", "category"]).size()
              .unstack(fill_value=0))
    for col in ("hosteleria", "turistico", "cotidiano", "otro", "vacant"):
        if col not in counts:
            counts[col] = 0
    counts["n_comercios"] = counts["turistico"] + counts["cotidiano"] + counts["otro"]
    total_locales = counts["n_comercios"] + counts["hosteleria"]
    counts["hosteleria_share"] = np.where(
        total_locales > 0, counts["hosteleria"] / total_locales, np.nan)
    tur_cot = counts["turistico"] + counts["cotidiano"]
    counts["turistico_share_shops"] = np.where(
        tur_cot > 0, counts["turistico"] / tur_cot, np.nan)
    activos_vac = counts["n_comercios"] + counts["vacant"]
    counts["vacancy_rate"] = np.where(
        activos_vac > 0, counts["vacant"] / activos_vac, np.nan)
    return counts.reset_index()


# --------------------------------------------------------- densidad VUT ----
def vut_density_by_barrio(path: Path = METRICS) -> pd.Series:
    df = pd.read_csv(path, usecols=["metric_id", "barrio_id", "value"])
    df = df[df["metric_id"] == "vut_density"]
    return df.set_index("barrio_id")["value"].astype(float)


def read_cnae_trend(path: Path = INDICATORS) -> dict[str, pd.Series]:
    """Eje TEMPORAL de ciudad (REC-7): cuotas CNAE de comercio y hostelería.

    OSM da la geografía *actual*; esta serie da el *cambio* que la hipótesis
    describe («cierran negocios de barrio»). Se triangulan.
    """
    df = pd.read_csv(path, usecols=["id", "year", "value"])
    out = {}
    for ind in ("retail_establishments_share", "hospitality_establishments_share"):
        sub = df[df["id"] == ind].copy()
        sub["year"] = sub["year"].astype(int)   # tras filtrar (otros ids traen '1983/1984')
        out[ind] = sub.set_index("year")["value"].astype(float).sort_index()
    return out


# --------------------------------------------------------------- carga ----
def fetch_shops(cache: Path = CACHE, use_cache: bool = True) -> list[dict]:
    """Comercios + hostelería de Donostia vía Overpass (cacheado en disco)."""
    if use_cache and cache.exists():
        return json.loads(cache.read_text())["elements"]
    query = f"""
    [out:json][timeout:180];
    area["boundary"="administrative"]["name"="{AREA}"]->.a;
    (
      nwr["shop"](area.a);
      nwr["amenity"~"^(bar|pub|restaurant|cafe|fast_food|biergarten|food_court|ice_cream|nightclub)$"](area.a);
    );
    out center tags;
    """
    r = requests.get(OVERPASS, params={"data": query},
                     headers={"User-Agent": UA}, timeout=200)
    r.raise_for_status()
    js = r.json()
    cache.parent.mkdir(exist_ok=True)
    cache.write_text(json.dumps(js))
    return js["elements"]


# -------------------------------------------------------------- informe ----
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()

    elements = fetch_shops(use_cache=not args.no_cache)
    df = parse_overpass(elements)
    features = json.loads(GEOJSON.read_text(encoding="utf-8"))["features"]
    df = assign_barrio(df, features)

    print("=" * 76)
    print("HU-3 · TIPOLOGÍA COMERCIAL POR BARRIO  (OpenStreetMap, snapshot)")
    print("=" * 76)
    print(f"\n{len(df):,} locales geolocalizados en barrio "
          f"({(df.category=='hosteleria').sum()} hostelería, "
          f"{(df.category!='hosteleria').sum()} comercios).".replace(",", "."))

    mix = mix_by_barrio(df)
    vut = vut_density_by_barrio()
    mix["vut_density"] = mix["barrio_id"].map(vut)

    show = mix.sort_values("hosteleria_share", ascending=False)
    cols = ["barrio_id", "hosteleria", "turistico", "cotidiano", "otro",
            "vacant", "n_comercios", "hosteleria_share",
            "turistico_share_shops", "vacancy_rate", "vut_density"]
    print("\nPor barrio (ordenado por intensidad hostelera):\n")
    print(show[cols].to_string(index=False, float_format=lambda v: f"{v:.2f}"))

    # correlación mezcla ↔ presión turística (barrios con VUT y ≥15 comercios)
    corr_df = mix[(mix["vut_density"].notna()) & (mix["n_comercios"] >= 15)]
    for col in ("hosteleria_share", "turistico_share_shops"):
        c = corr_df[col].corr(corr_df["vut_density"])
        print(f"\ncorr({col} ↔ vut_density) = {c:.2f}  "
              f"(n={len(corr_df)} barrios con ≥15 comercios)")

    # ficha Parte Vieja (bbox)
    pv = df[[in_parte_vieja(r.lon, r.lat) for r in df.itertuples()]]
    pv_mix = pv["category"].value_counts().to_dict()
    print(f"\nParte Vieja (bbox {PARTE_VIEJA_BBOX}): {len(pv)} locales — {pv_mix}")
    print("⚠️  OSM infra-mapea el casco viejo; leer como indicio, no censo.")

    # eje temporal: serie CNAE de ciudad (REC-7)
    print("\n— Triangulación temporal: cuota de locales por sector (CNAE, ciudad) —\n")
    trend = read_cnae_trend()
    retail, hosp = (trend["retail_establishments_share"],
                    trend["hospitality_establishments_share"])
    y0t, y1t = retail.index.min(), retail.index.max()
    print(f"  Comercio minorista: {retail[y0t]:.1f}% ({y0t}) → "
          f"{retail[y1t]:.1f}% ({y1t})  [{retail[y1t]-retail[y0t]:+.1f} pp]")
    print(f"  Hostelería:         {hosp[y0t]:.1f}% ({y0t}) → "
          f"{hosp[y1t]:.1f}% ({y1t})  [{hosp[y1t]-hosp[y0t]:+.1f} pp]")

    print("\nLectura: OSM da la GEOGRAFÍA actual (qué barrios son hosteleros/")
    print("turísticos); la serie CNAE da el CAMBIO de ciudad (comercio ↓,")
    print("hostelería ↑). Se triangulan: la Parte Vieja hostelera de hoy es el")
    print("estado final de esa deriva, no una prueba causal por sí sola.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        mix[cols].to_csv(OUTDIR / "commercial_typology_barrio.csv", index=False)
        print(f"\n[guardado] {OUTDIR / 'commercial_typology_barrio.csv'}")


if __name__ == "__main__":
    main()
