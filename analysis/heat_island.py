"""REC-14 — Isla de calor superficial por barrio (Landsat C2 L2, banda térmica).

La historia #4 (clima) es la única sin dimensión espacial: las series de
Igeldo son de un punto. Este análisis baja la temperatura a barrio con la
**temperatura superficial** (LST) de Landsat 8/9 Collection 2 Level-2 (banda
``lwir11``/ST_B10, 30 m), vía el STAC de Microsoft Planetary Computer (acceso
anónimo con firma SAS, sin cuenta) — la única vía verificada sin credenciales
(USGS M2M y Copernicus Data Space piden cuenta; investigado jul-2026).

Método: escenas de verano (jun–sep, nubes <10 %), enmascaradas por píxel con
``qa_pixel`` (nube, sombra, cirro, dilatada); media zonal por barrio
(centros de píxel dentro del polígono, en el CRS UTM de la escena) y, por
escena, **anomalía respecto a la media de ciudad** — se promedian anomalías,
no temperaturas, para que días más o menos cálidos no pesen distinto. El
resultado es "cuánto más caliente que la media de Donostia es la superficie
de cada barrio en verano".

Lecturas honestas: LST es temperatura *de superficie* (tejados, asfalto), no
del aire que se respira; el paso de Landsat es ~10:50 UTC (media mañana), no
la noche tropical; los exclaves rurales salen fríos por cubierta vegetal, no
por microclima urbano.

Dependencias extra **solo de este script** (no del pipeline ni del CI):
``pip install rasterio pyproj``. Los recortes se cachean en
``datos/input/raw/heat_island/`` (npz, uno por escena). Uso:
    python analysis/heat_island.py [--save] [--years 2015 2025]
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from shapely.geometry import shape
from shapely.ops import transform as shp_transform

ROOT = Path(__file__).resolve().parent.parent
GEOJSON = ROOT / "web" / "src" / "data" / "barrios.geojson"
CACHE = ROOT / "datos" / "input" / "raw" / "heat_island"
OUTDIR = Path(__file__).resolve().parent / "output"

STAC_SEARCH = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS_TOKEN = "https://planetarycomputer.microsoft.com/api/sas/v1/token/landsateuwest/landsat-c2"

# Landsat C2 L2 ST: °C = DN * escala + offset − 273,15 K; DN 0 = nodata.
_SCALE, _OFFSET = 0.00341802, 149.0
# qa_pixel: bits que invalidan el píxel (dilated cloud, cirrus, cloud, shadow).
_QA_BAD_BITS = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4)
MAX_CLOUD = 10.0
SUMMER = ("06-01", "09-30")
MIN_PIXELS = 20


# ------------------------------------------------------- piezas puras ----
def dn_to_celsius(dn: np.ndarray) -> np.ndarray:
    out = dn.astype(float) * _SCALE + _OFFSET - 273.15
    out[dn == 0] = np.nan
    return out


def clear_mask(qa: np.ndarray) -> np.ndarray:
    """True donde el qa_pixel no marca nube/sombra/cirro."""
    return (qa & _QA_BAD_BITS) == 0


def zonal_means(lst: np.ndarray, grid: tuple[float, float, float, float],
                features: list[dict]) -> dict[str, tuple[float, int]]:
    """barrio_id → (media °C, n píxeles) sobre centros de píxel en el polígono.

    ``grid`` = (x0, dx, y0, dy) de una affine sin rotación, en el mismo CRS
    que las geometrías de ``features``.
    """
    x0, dx, y0, dy = grid
    rows, cols = lst.shape
    xs = x0 + (np.arange(cols) + 0.5) * dx
    ys = y0 + (np.arange(rows) + 0.5) * dy
    xx, yy = np.meshgrid(xs, ys)
    valid = ~np.isnan(lst)
    out = {}
    for f in features:
        inside = shapely.contains_xy(shape(f["geometry"]), xx, yy) & valid
        n = int(inside.sum())
        if n:
            out[f["properties"]["barrio_id"]] = (float(lst[inside].mean()), n)
    return out


def anomaly_table(per_scene: list[dict[str, tuple[float, int]]],
                  min_pixels: int = MIN_PIXELS) -> pd.DataFrame:
    """Anomalía media por barrio: (media barrio − media ciudad) por escena.

    La media de ciudad de cada escena pondera cada barrio por sus píxeles;
    los barrios con menos de ``min_pixels`` en una escena no puntúan en ella.
    """
    anomalies: dict[str, list[float]] = {}
    for scene in per_scene:
        ok = {b: (m, n) for b, (m, n) in scene.items() if n >= min_pixels}
        if not ok:
            continue
        total = sum(n for _, n in ok.values())
        city = sum(m * n for m, n in ok.values()) / total
        for b, (m, _) in ok.items():
            anomalies.setdefault(b, []).append(m - city)
    rows = [{"barrio_id": b, "lst_anomaly": float(np.mean(v)),
             "lst_anomaly_sd": float(np.std(v)), "n_scenes": len(v)}
            for b, v in anomalies.items()]
    columns = ["barrio_id", "lst_anomaly", "lst_anomaly_sd", "n_scenes"]
    return (pd.DataFrame(rows, columns=columns).set_index("barrio_id")
            .sort_values("lst_anomaly", ascending=False))


# --------------------------------------------------- red + ráster (lazy) ----
def _stac_scenes(years: tuple[int, int], bbox: list[float]) -> list[dict]:
    scenes = []
    for year in range(years[0], years[1] + 1):
        body = {
            "collections": ["landsat-c2-l2"],
            "bbox": bbox,
            "datetime": f"{year}-{SUMMER[0]}/{year}-{SUMMER[1]}",
            "query": {"eo:cloud_cover": {"lt": MAX_CLOUD},
                      "platform": {"in": ["landsat-8", "landsat-9"]}},
            "limit": 100,
        }
        req = urllib.request.Request(
            STAC_SEARCH, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            scenes.extend(json.load(resp)["features"])
    return scenes


def _fetch_scene_crop(item: dict, bbox: list[float], token: str):
    """Lee las ventanas lwir11+qa_pixel de una escena (cacheado en npz)."""
    import rasterio
    from rasterio.windows import from_bounds
    from pyproj import Transformer

    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{item['id']}.npz"
    if cached.exists():
        z = np.load(cached)
        return z["lwir11"], z["qa"], tuple(z["grid"]), str(z["crs"])

    with rasterio.open(item["assets"]["lwir11"]["href"] + "?" + token) as src:
        tr = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        x0, y0 = tr.transform(bbox[0], bbox[1])
        x1, y1 = tr.transform(bbox[2], bbox[3])
        win = from_bounds(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1),
                          src.transform)
        lwir = src.read(1, window=win)
        wt = src.window_transform(win)
        grid = (wt.c, wt.a, wt.f, wt.e)
        crs = str(src.crs)
    with rasterio.open(item["assets"]["qa_pixel"]["href"] + "?" + token) as src:
        qa = src.read(1, window=from_bounds(min(x0, x1), min(y0, y1),
                                            max(x0, x1), max(y0, y1),
                                            src.transform))
    np.savez_compressed(cached, lwir11=lwir, qa=qa, grid=np.array(grid),
                        crs=np.array(crs))
    return lwir, qa, grid, crs


def _features_in_crs(features: list[dict], crs: str) -> list[dict]:
    from pyproj import Transformer
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    out = []
    for f in features:
        geom = shp_transform(tr.transform, shape(f["geometry"]))
        out.append({"properties": f["properties"],
                    "geometry": geom.__geo_interface__})
    return out


# --------------------------------------------------------------- main ----
def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--years", nargs=2, type=int, default=(2015, 2025),
                        metavar=("INI", "FIN"))
    args = parser.parse_args(argv)

    gj = json.loads(GEOJSON.read_text(encoding="utf-8"))
    features = gj["features"]
    bounds = [shape(f["geometry"]).bounds for f in features]
    bbox = [min(b[0] for b in bounds), min(b[1] for b in bounds),
            max(b[2] for b in bounds), max(b[3] for b in bounds)]

    scenes = _stac_scenes(tuple(args.years), bbox)
    print(f"REC-14 — {len(scenes)} escenas de verano con <{MAX_CLOUD:.0f}% "
          f"de nubes ({args.years[0]}–{args.years[1]})")
    token = json.load(urllib.request.urlopen(SAS_TOKEN, timeout=30))["token"]

    per_scene, used = [], 0
    feats_by_crs: dict[str, list[dict]] = {}
    for item in scenes:
        try:
            lwir, qa, grid, crs = _fetch_scene_crop(item, bbox, token)
        except Exception as exc:                        # escena corrupta: fuera
            print(f"  · {item['id']} saltada ({exc})")
            continue
        lst = dn_to_celsius(lwir)
        lst[~clear_mask(qa)] = np.nan
        if np.isnan(lst).mean() > 0.5:                  # nubes locales: fuera
            continue
        feats = feats_by_crs.setdefault(crs, _features_in_crs(features, crs))
        means = zonal_means(lst, grid, feats)
        if means:
            per_scene.append(means)
            used += 1
    print(f"usadas {used} escenas (resto: >50% de píxeles no despejados en "
          "el recorte)\n")

    table = anomaly_table(per_scene)
    names = {f["properties"]["barrio_id"]: f["properties"]["name"]
             for f in features}
    table.insert(0, "name", [names.get(b, b) for b in table.index])
    print(table.to_string(float_format=lambda v: f"{v:+.2f}"))

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        table.to_csv(OUTDIR / "heat_island_barrio.csv")
        print(f"\n→ guardado en {OUTDIR}/heat_island_barrio.csv")


if __name__ == "__main__":
    main()
