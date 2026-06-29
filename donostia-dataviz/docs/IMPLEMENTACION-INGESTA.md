# Guía de implementación para Claude Code — ingesta de datos (REC-1..4)

> **Para quién.** Esta guía es para ejecutar en un entorno con **acceso a red y a
> los datos** (Claude Code), donde se puede descargar, construir y testear el
> pipeline. Aquí *no* se escribió el código de ingesta porque no se puede
> verificar sin los datos crudos; en cambio se especifica con precisión qué hacer,
> siguiendo los patrones que ya existen en `data-pipeline/`.
>
> Fuentes verificadas (URLs, formato, granularidad) en `PLAN-RECOLECCION.md`.
> Backlog en `GAP-ANALYSIS.md`. La parte de análisis (Sprint A) ya está hecha y
> testeable en `analysis/sprint_a.py`.

## Patrón del pipeline (recordatorio)

Cada fuente = un módulo en `data-pipeline/src/donostia_pipeline/datasets/` que
expone una de estas firmas:

- **Métrica por barrio** → `build(ctx) -> list[Metric]` (modelo: `demografia.py`).
- **Indicador anual ciudad** → `build_indicators(raw_dir) -> list[Indicator]`
  (modelo: `residuos.py`).
- **Métrica GIS** (puntos/rejilla → barrio) → `build(ctx) -> list[Metric]` usando
  `ctx.barrio_index` (modelo: `educacion_gis.py`).

Registro en `build.py`: añadir el fichero crudo a `RAW_DOWNLOADS` (nombre→URL) y
el módulo a `DATASETS` (métricas) o a la línea de `indicators` en `run()`.
`validate()` (en `model.py`) impone los invariantes; los tests viven en
`data-pipeline/tests/` como **tests de transformación pura** (modelo:
`test_demografia.py`, `test_residuos.py`, `test_educacion_gis.py`).

Verificación tras cada módulo:

```bash
cd data-pipeline && python -m donostia_pipeline.build      # reconstruye JSON+CSV
pytest                                                      # 66 tests + los nuevos
```

Y comprobar que la métrica aparece en `web/src/data/metrics.json` y en
`data/metrics_long.csv` (sin tocar el frontend: aparece sola).

---

## REC-1 — Edad / envejecimiento por barrio  ·  métrica por barrio

**Fuente:** `https://www.donostia.eus/datosabiertos/recursos/demografia-piramideedad/demografiapiramideedadbarrio.csv`
(CSV, barrio, anual, tramos quinquenales por sexo). **Confirmar columnas reales
al descargar** (esperado: año, `AuzoKodea`, tramo de edad, sexo, nº personas).

**Crear** `datasets/edad.py` siguiendo `demografia.py`. Derivar al menos:

- `ageing_index` — `pob ≥65 / pob <15 × 100` (kind `sequential`, theme
  `demography`).
- `pct_young_adults` — `pob 25–39 / pob total × 100` (proxy de atractivo para
  familias jóvenes; idea Gemini/Perplexity).
- opcional `median_age`.

Esqueleto:

```python
# datasets/edad.py
from ..model import BuildContext, Metric
CSV_NAME = "edad_barrio.csv"
SOURCE = "Donostia Open Data — pirámide de edad por barrio (Padrón)"

def build(ctx: BuildContext) -> list[Metric]:
    # acumular por (barrio_id, year): pob<15, pob>=65, pob 25-39, total
    # join: barrio_id = ctx.code_to_id.get(row["AuzoKodea"].strip())
    # parsear tramos de edad → bucket; saltar código en blanco (Ezezaguna)
    # ageing = p65 / p15 * 100  (None si p15==0)
    return [Metric(id="ageing_index", label="Índice de envejecimiento",
                   unit="%", kind="sequential", theme="demography", source=SOURCE,
                   geo_grain="barrio", time_grain="year", periods=periods, values=...)]
```

**Registro:** `RAW_DOWNLOADS["edad_barrio.csv"] = "<URL de arriba>"`;
añadir `edad` a `DATASETS`. **Tests:** `test_edad.py` con filas sintéticas
(p.ej. 100 jóvenes / 200 mayores → índice 200,0). **Sin join espacial.**

---

## REC-2 — Ruido por barrio  ·  métrica GIS (rejilla → areal)

**Fuente:** Donostia Open Data `ruido-noche` (y `ruido-total`), **SHP** en
EPSG:25830, snapshots **2008 / 2017 / 2022**. Ver `PLAN-RECOLECCION.md`.

**Patrón:** como `educacion_gis.py` pero con **polígonos + interpolación areal**,
no conteo de puntos. Usar:

- `gis_io.load_shapefile(path, source_crs="EPSG:25830")` → reproyecta a 4326.
- `ctx.barrio_index.areal_interpolate(features, mode="mean")` con
  `features = [(geom, valor_dB), ...]`.

**Caveat clave:** los mapas de ruido suelen venir en **rangos** (p.ej. "60–65
dB"), no en un valor único. Mapear cada rango a su **punto medio** antes de
interpolar (documentarlo como supuesto → ficha de confianza MET-4). Y los SHP
llegan como **conjunto de ficheros** (.shp/.shx/.dbf, a veces en zip): confirmar
que `load_shapefile` recibe la ruta correcta (descomprimir si hace falta en
`ensure_raw`).

Crear `datasets/ruido.py` → `Metric(id="noise_night_db", kind="sequential",
theme="environment", geo_grain="barrio", time_grain="year",
periods=["2008","2017","2022"])`. Alto valor: cruzar con `vut_density` (relato
turismo↔ruido, Parte Vieja/Gros). **Tests:** `test_ruido.py` con 2 polígonos de
dB conocidos sobre 1 barrio → media esperada.

---

## REC-3 — Fiscalidad municipal  ·  indicador anual ciudad

**Fuente:** `https://www.donostia.eus/datosabiertos/recursos/impuestos_tipo/pfi_impuestos_tipo_ciudad_ckan.csv`
(y `tasas_tipo`, `subvenciones`). CSV, ciudad, por tipo. Delimitador probable
`;` (como `residuos.csv`). **Caveat:** `subvenciones` puede tener pocos años.

**Patrón:** como `residuos.py` → `build_indicators(raw_dir) -> list[Indicator]`.
Decidir el recorte: recibos totales por año, y/o un indicador por tipo principal
(IBI, plusvalía…). Reutiliza la viz genérica de indicadores (ya existe, sin
frontend nuevo).

```python
# datasets/fiscalidad.py
from ..model import Indicator
def build_indicators(raw_dir) -> list[Indicator]:
    # sumar importe/recibos por Año (y por tipo si se quiere desglose)
    return [Indicator(id="tax_receipts_total", label="Recibos de impuestos",
                      unit="€", theme="economy", source=SOURCE, values=...)]
```

**Registro:** `RAW_DOWNLOADS` + en `run()` añadir a la línea de indicadores:
`indicators = mice.build_indicators() + residuos.build_indicators(...) + fiscalidad.build_indicators(config.RAW_DIR)`.
**Tests:** `test_fiscalidad.py`.

---

## REC-4 — Inside Airbnb  ·  métrica GIS (puntos) + serie temporal

**Fuente:** `insideairbnb.com/euskadi/` → San Sebastián: `listings.csv`
(lat/lon + atributos), `reviews.csv`, `calendar.csv`. **No** es CKAN
auto-descargable: fijar la URL estable del snapshot o descargar a mano a `raw/`.
**Licencia:** Inside Airbnb (CC BY 4.0) — registrar en `SOURCES.md`.

Dos salidas:

1. **Densidad Airbnb por barrio** (métrica GIS, como `educacion_gis.py`):
   `point_coords` desde `listings` → `ctx.barrio_index.count_points` →
   `rate_per_1000(counts, ctx.population_latest)` → `Metric(id="airbnb_density",
   theme="tourism", geo_grain="barrio", time_grain="snapshot")`. Comparar con
   `vut_density` (los VUT legales son solo una fracción).
2. **Serie-proxy de ocupación por barrio** (desbloquea AN-6 lead/lag): contar
   `reviews` por mes y barrio (join espacial del listing) → aproximación a la
   actividad mensual. Modelar como conjunto de `Series` ciudad o como métrica
   barrio×mes. **Documentar como proxy** (reseñas ≠ ocupación; ficha MET-4).

**Tests:** `test_airbnb.py` (puntos sintéticos → densidad esperada).

---

## Tareas de código relacionadas (fuera de REC, si se quiere seguir)

- **MET-1 — `housing_tension` parametrizable.** Hacer el m²/persona
  seleccionable y añadir variantes (`z(rent)−z(income)`, percentiles). El módulo
  actual es `datasets/housing_tension.py` (`build_from_metrics`). La superficie
  construida real vendría de REC-8 (catastro foral).
- **AN-8 — Índice de Transformación Urbana.** Nuevo módulo `build_from_metrics`
  que combine renta + alquiler + % universitarios + densidad VUT (multi-
  definición, componentes visibles). Usar el clustering/velocidades de
  `analysis/sprint_a.py` como base. **Nunca llamarlo "gentrificación"** (decisión).
- **Visualizaciones (VIZ-1/2/3).** Son frontend (`web/`): mapa de velocidad,
  mapa de perfiles/clusters, coropleta bivariada. Los datos ya los produce el
  análisis del Sprint A.

## Checklist de cada PR de ingesta

1. Módulo en `datasets/` con la firma correcta y `source` explícito.
2. Registro en `build.py` (`RAW_DOWNLOADS` + `DATASETS`/indicadores).
3. Test de transformación pura en `tests/`.
4. `python -m donostia_pipeline.build` reproduce JSON+CSV sin error.
5. `pytest` en verde.
6. Actualizar `SOURCES.md` (fuente + estado) y `DATA-CONTRACT.md` (nueva métrica).
7. Normalizar conteos por población (tasa/1000); nunca valor absoluto en mapa.
