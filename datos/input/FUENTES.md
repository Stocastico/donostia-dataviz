# Datos de input — fuentes y snapshots

Registro de **todos los datos de entrada** del proyecto: de dónde salen, qué
alimentan y cómo obtenerlos. Los ficheros crudos grandes/binarios y los que
requieren clave o API **no se versionan aquí directamente**; se descargan con
`descargar_raw.sh` (o corriendo el pipeline) a `datos/input/raw/`. El único input
versionado en el repo es el **MICE curado** (`mice_donostia.csv`), porque no
existe dataset abierto estructurado.

> **Nota de entorno.** La descarga automática **no puede ejecutarse desde Cowork**
> (el portal de datos agota el tiempo de `web_fetch` y la política prohíbe usar
> `curl`/`wget` como alternativa). Ejecuta `descargar_raw.sh` en tu máquina o corre
> `python -m donostia_pipeline.build`, que descarga exactamente estos mismos
> ficheros a `data-pipeline/raw/`. Ver el BACKLOG (sección Code).

## Fuentes automáticas (→ `datos/input/raw/`)

| Fichero crudo | Fuente | URL | Alimenta | Snapshot / periodo | Licencia |
|---|---|---|---|---|---|
| `auzoak.json` | Donostia Open Data | `.../recursos/mapa_auzoak/auzoak.json` | geometría de referencia (barrios) | actual | Open Data DSS |
| `vtur_censo.csv` | Donostia Open Data | `.../recursos/censo-viviendas-turisticas/urb_ckan_vtur_censo.csv` | `vut_count`, `vut_density`, `vut_plazas` y (por **calle**, vía `helbidea`) `street_vut.json` / `calles_vut.csv` | snapshot actual | Open Data DSS |
| `callejero.zip` | Donostia Open Data (Nombres de calle) | `.../dataset/ce59dab6…/download/hiribarrukobideenizena.zip` (SHP de puntos-etiqueta, EPSG:25830, con `KodKalea` + nombres ES/EU) | callejero municipal → geometría de `street_vut.json` / `calles_vut.csv` (grano **calle**, sub-barrio) | actual (861 calles) | Open Data DSS |
| `demo_barrio.csv` | Donostia Open Data | `.../recursos/demografia-origen/demografianacionalidadbarrio.csv` | `pct_foreign`, `population`, `pct_origin_*` (8 métricas por región de origen, REC-21) y `origen_paises_barrio.json` (ficha top-5 países por barrio, REC-21-web) | anual 2000–2025 | Open Data DSS |
| `edad_barrio.csv` | Donostia Open Data | `.../recursos/demografia-piramideedad/demografiapiramideedadbarrio.csv` | `ageing_index`, `pct_youth_adults` | anual 2000–2025 | Open Data DSS |
| `renta_barrio.csv` | Donostia Open Data (Eustat) | `.../recursos/eustat_renta/eustatrentabarrio.csv` | `income_total`, `income_gender_gap` | anual 2016–2023 | Open Data DSS / Eustat |
| `estudios_barrio.csv` | Donostia Open Data | `.../recursos/demografia-nivelestudios/demografianivelestudiosbarrio.csv` | `pct_university` | anual 2000–2025 | Open Data DSS |
| `ine_pernoct_esp.json` | INE EOH | `servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EOT2721?nult=600` | `overnight_stays` (residentes) | mensual 2005–2026 | INE (open) |
| `ine_pernoct_ext.json` | INE EOH | `servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EOT2722?nult=600` | `overnight_stays` (extranjero) | mensual 2005–2026 | INE (open) |
| `emal_barrios.xlsx` | Gobierno Vasco — EMA/EMAL | `euskadi.eus/.../opendata/EMAL.-Barrios-Municipios.-2016-2025_es.xlsx` (hoja **T8.3**) | `rent_eur_m2` | anual 2016–2024 | Gob. Vasco (open) |
| `educativos.json` | Donostia Open Data | `.../recursos/servicios-educativos/hezkuntzaekipamenduak.json` | `schools_per_1000` | actual (157 puntos) | Open Data DSS |
| `salud.json` | Donostia Open Data | `.../recursos/servicios-salud/osasunekipamenduak.json` | `health_per_1000` (REC-18, join punto→barrio) | actual (29 puntos) | Open Data DSS |
| `residuos.csv` | Donostia Open Data | `.../recursos/residuos/datos-residuos.csv` | `recycling_rate` | anual 2010–2024 | Open Data DSS |
| `ruido_noche_2022.zip` | Donostia Open Data (ruido-noche) | `.../ide/INGURUMENA-MEDIO_AMBIENTE/shp/Zarata_Ruido/2022_DSS_IZT_totala_gau.zip` (SHP, EPSG:25830) | `noise_night_pct55` | 2022 | Open Data DSS |
| `promociones_etxebide.csv` | Open Data Euskadi | `opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.csv` (CSV `;`, latin-1, coords UTM EPSG:25830) | `vpo_dwellings_per_1000` (REC-15, join punto→barrio). ⚠️ Registro **parcial**: 1.120 viviendas en Donostia, ≤~⅓ del solo alquiler protegido (3.151 uds., memoria zona tensionada 2024); no incluye el patronato municipal (Etxegintza, 2.087) | snapshot cumulativo | Gob. Vasco / Etxebide |
| `impuestos_ciudad.csv` | Donostia Open Data | `.../dataset/36ef69b9…/download/pfi_impuestos_tipo_ciudad_ckan.csv` | `tax_revenue` | anual 2011–2025 | Open Data DSS |
| `tasas_ciudad.csv` | Donostia Open Data | `.../dataset/7c0f2bf4…/download/pfi_tasas_tipo_ciudad_ckan.csv` | `fee_revenue` | anual 2011–2025 | Open Data DSS |
| `airbnb_listings.csv.gz` | Inside Airbnb | `data.insideairbnb.com/spain/pv/euskadi/2025-09-29/data/listings.csv.gz` | `airbnb_density` | **2025-09-29** | CC BY 4.0 |
| `airbnb_reviews.csv.gz` | Inside Airbnb | `data.insideairbnb.com/spain/pv/euskadi/2025-09-29/data/reviews.csv.gz` | `airbnb_reviews`, `airbnb_activity` | **2025-09-29** | CC BY 4.0 |
| `aemet_igeldo.json` | AEMET OpenData | REST `valores/climatologicos/mensualesanuales`, estación **1024E** | `temp_avg`, `temp_max`, `precip`, `hot_days_30` | mensual 1981–actual (`AEMET_YEAR_RANGE` en `build.py`; el año en curso queda parcial hasta que AEMET publique el último mes) | AEMET (**requiere clave** `AEMET_API_KEY`) |
| `eustat_modelos_linguisticos.json` | Eustat (PxWeb) | tabla `PX_040601_ceens_mun01`, municipio 20069, **POST** con filtro server-side (ver `descargar_raw.sh`) | `pct_language_model_a/b/d` | anual 1983/1984–2024/2025 | Eustat (open) |
| `eustat_paro_donostia.json` | Eustat (PxWeb) | tabla `PX_050403_cpra_tab19`, capital Donostia/San Sebastián, **POST** con filtro server-side (ver `descargar_raw.sh`) | `unemployment_rate(_men/_women)` | anual 2015–2025 (promedio anual) | Eustat (open) |
| `eustat_comercio_donostia.json` | Eustat (PxWeb) | tabla `PX_200163_cdirae_est04b`, municipio 20069, ~630 códigos CNAE-2009 (agregados a `comercio`/`hostelería` en el pipeline), **POST** con filtro server-side (ver `descargar_raw.sh`) | `total_establishments`, `retail_establishments_share`, `hospitality_establishments_share` | anual 2008–2025 | Eustat (open) |
| `reate_viviendas.json` | Gob. Vasco — REATE (Open Data Euskadi) | `opendata.euskadi.eus/.../habitaciones_viviendas_turisti/opendata/viviendas.json` | `vut_licenses_new`, `vut_licenses_cumulative`, `vut_plazas_cumulative` | snapshot vivo; altas 2016–actual (⚠️ solo licencias supervivientes: las bajas no se publican) | Gob. Vasco (open) |
| `reate_habitaciones.json` | Gob. Vasco — REATE (Open Data Euskadi) | `opendata.euskadi.eus/.../habitaciones_viviendas_turisti/opendata/habitaciones.json` | (se suma a los indicadores anteriores: VUT+HUT) | ídem | Gob. Vasco (open) |
| `eustat_empa_movilidad.json` | Eustat (PxWeb) | tabla `PX_050407_cempa_empa_mt02`, municipio 20069, **POST** con filtro server-side (ver `descargar_raw.sh`) | `residents_work_in_city_pct`, denominador de `job_concentration_ratio` | anual 2021–2024 (lugar de trabajo **categórico**, no matriz O-D) | Eustat (open) |
| `eustat_eme_movilidad.json` | Eustat (PxWeb) | tabla `PX_040606_ceme_me02`, municipio 20069, **POST** con filtro server-side (ver `descargar_raw.sh`) | `residents_study_in_city_pct` | anual 2021–2024 (lugar de estudio **categórico**, no matriz O-D) | Eustat (open) |
| `eustat_dirae_empleo.json` | Eustat (PxWeb) | tabla `PX_200163_cdirae_est07`, municipio 20069, **POST** con filtro server-side (ver `descargar_raw.sh`) | `jobs_located`, numerador de `job_concentration_ratio` | anual 1995–2025 | Eustat (open) |
| `eustat_renta_trabajo.json` | Eustat (PxWeb) | tabla `PX_173402_crpf_rpf_rp22_2p`, barrios de Donostia + **tipo de renta 110 (renta del trabajo)**, **POST** server-side (`build.ensure_eustat_renta_trabajo`) | `income_labor` (salario/renta del trabajo per cápita por barrio, HU-7) | anual 2016–2023 | Eustat (open) |
| `eustat_tasas_nacionalidad_gipuzkoa.json` | Eustat (PxWeb) | tabla `PX_050403_cpra_tab17`, Gipuzkoa, **POST** con filtro server-side (ver `descargar_raw.sh`) | `unemployment_rate_spanish_gipuzkoa`, `unemployment_rate_foreign_gipuzkoa` (REC-21) | anual 2015–2026 (promedio anual) | Eustat (open) |
| `eustat_id_personal_gipuzkoa.json` | Eustat (PxWeb) | tabla `PX_043201_cid_res08c`, Gipuzkoa, **POST** con filtro server-side (ver `descargar_raw.sh`) | numerador de `randd_personnel_per_1000_employed_gipuzkoa` (REC-21) | anual 2001–2024 | Eustat (open) |
| `eustat_poblacion_ocupada_total.json` | Eustat (PxWeb) | tabla `PX_050403_cpra_tab04`, C.A. de Euskadi + Gipuzkoa, **POST** con filtro server-side (ver `descargar_raw.sh`) | denominador de `randd_personnel_per_1000_employed_gipuzkoa` (REC-21) | anual 1985–2026 (promedio anual) | Eustat (open) |
| `airbnb_snapshot_<fecha>.csv` (×8) | Inside Airbnb | `data.insideairbnb.com/spain/pv/euskadi/<fecha>/visualisations/listings.csv` | solo `analysis/` (REC-13: serie de anuncios activos vs. reseñas, MET-7; **no** alimenta el pipeline) | trimestral **2023-12-29 → 2025-09-29** (los snapshots 2021-12-30…2023-09-24 existieron pero dan 403; solo vía data request) | CC BY 4.0 |
| `ine_mortalidad_gipuzkoa.json` | INE Tablas de Mortalidad | tabla Tempus **67235**, filtro server-side prov. Gipuzkoa + función "Riesgo de muerte" (qx quinquenal, ‰, por sexo) | solo `analysis/` (AN-12: supervivencia esperada por cohorte; **no** alimenta el pipeline) | anual 1991–2024 | INE (open) |
| `demo_barrio_nacionalidad.csv` | Donostia Open Data | mismo recurso que `demo_barrio.csv` (`demografia-origen/demografianacionalidadbarrio.csv`) sin agregar por país — 57 países, por barrio | solo `analysis/` (AN-21: origen detallado por barrio; el pipeline solo consume el agregado `pct_foreign`) | anual 2000–2025 | Open Data DSS |

### Fuentes analysis-only con descarga propia

| Origen | Vía | Alimenta | Notas |
|---|---|---|---|
| Landsat 8/9 Collection 2 Level-2 (banda térmica `lwir11` + `qa_pixel`) | STAC de Microsoft Planetary Computer (acceso anónimo, firma SAS) — descarga el propio `analysis/heat_island.py`, recortes cacheados en `raw/heat_island/` | REC-14 isla de calor (`analysis/output/heat_island_barrio.csv`) | requiere `pip install rasterio pyproj` (solo ese script); USGS M2M y Copernicus Data Space se descartaron por pedir cuenta |
| Eustat PxWeb — 4 tablas: extranjeros por continente×actividad (`pa16`), ocupados por CNO-11 (`empa_po38`), establecimientos por sector A10 en Donostia (`cdirae_est02c`), renta por profesión (`crpf_rp_a_03`) | POST server-side vía `www.eustat.eus/bankupx/api/v1/es/DB/<tabla>.px` (ver queries exactas en las docstrings de cada `load_*` de `perfil_extranjeros_empleo.py`) | REC-21 / AN-21 perfil migratorio y de empleo (`analysis/output/*.csv`) — el resto de tablas de REC-21 (paro por nacionalidad, personal I+D, población ocupada) ya está cableado al pipeline, ver tabla de arriba | Grano **Gipuzkoa** salvo `cdirae_est02c` (municipio 20069) y `crpf_rp_a_03` (C.A. de Euskadi). No encajan en el modelo Metric/Indicator (desglose multi-categoría por año, no un valor escalar) |

## Inputs curados (versionados en el repo)

| Fichero | Contenido | Origen |
|---|---|---|
| `mice_donostia.csv` | Indicadores MICE (congresos ICCA; récord 2024: 188 eventos / 259k asistentes) | Curado de notas de prensa citadas por fila (DSS Convention Bureau / ICCA). Ampliar añadiendo filas. |
| `ibiltur_donostia.csv` | Indicadores IBILTUR Ocio 2023 (gasto/persona, gasto/persona/día, impacto económico) — solo turista de ocio que pernocta | Curado de la ficha de destino Donostia/San Sebastián de Basquetour (PDF). Ampliar cuando salga otra edición **Ocio** (anual) comparable — la de 2022 es "Verano" (otra ventana temporal) y no se mezcla. |
| `ipc_espana.csv` | IPC general nacional, índice base 2021 = 100, media anual 2016–2025 | **HU-7 (analysis-only)**. Curado de INE, tabla Tempus **50902** (`servicios.ine.es/wstempus/js/ES/DATOS_TABLA/50902`), serie «Nacional. Índice general. Índice.», promediada a media anual. Snapshot jul-2026. Deflactor de `analysis/housing_affordability.py`. |
| `percepcion_seguridad_eustat.csv` | Familias por grado de seguridad ciudadana y zona (miles), 1989–2024, zonas C.A. Euskadi (00) y Donostia-Bajo Bidasoa (70) | **HU-1**. Eustat, Encuesta de Condiciones de Vida, tabla PxWeb **PX_010901_cecv_ma04_3** (POST json-stat2, filtro zona 00+70). Snapshot jul-2026. Alimenta `analysis/perception_vs_crime.py` **y** los indicadores del pipeline `perception_insecurity_donostia/_euskadi` (`datasets/seguridad.py`). |
| `criminalidad_donostia.csv` | Infracciones penales conocidas y tasa/1000 hab. de **Donostia (municipio)** (**serie parcial**: 2019–2021 + Δ2024) | **HU-1**. Curado de prensa citada por fila (euskadi.eus 2022, Noticias de Gipuzkoa 2025; datos Ertzaintza+Guardia Municipal vía Balance de Criminalidad del Min. Interior). Alimenta `analysis/perception_vs_crime.py` **y** los indicadores `crime_infractions`/`crime_rate_1000` (`datasets/seguridad.py`). Complementada (no sustituida) por la serie provincial completa de abajo. |
| `criminalidad_gipuzkoa_mir.csv` | Infracciones penales conocidas por tipología penal, **Gipuzkoa (provincia)** 2010–2024 (44 tipologías + `TOTAL INFRACCIONES PENALES`) | **HU-1** (serie oficial completa, aportada por el usuario jul-2026). **Portal Estadístico de Criminalidad**, Ministerio del Interior (`estadisticasdecriminalidad.ses.mir.es`). Normalizado a UTF-8/tidy desde el TSV original. ⚠️ **Es provincia, no municipio**: Donostia ≈ ⅓ de Gipuzkoa → telón de fondo regional de la tendencia, no el dato exacto de la ciudad (declararlo así en cualquier relato). Alimenta `analysis/perception_vs_crime.py` (serie total + desglose) **y** el indicador `crime_infractions_gipuzkoa` (`datasets/seguridad.py`, etiqueta con «Gipuzkoa (provincia)»). Cierra la «laguna declarada» del total; el grano municipal sigue siendo parcial. |

## Fuentes analysis-only sin fichero versionado (descarga en tiempo de ejecución)

| Origen | Vía | Alimenta | Notas |
|---|---|---|---|
| OpenStreetMap (`shop=*` + `amenity` de hostelería) | Overpass API (`overpass-api.de`, GET con `User-Agent`), área administrativa «Donostia / San Sebastián` | **HU-3** tipología comercial (`analysis/commercial_typology.py`; cache en `analysis/output/osm_commercial_raw.json`, gitignored) | ODbL. Snapshot vivo (foto actual, sin histórico). Completitud OSM variable por barrio → proporciones intra-barrio más robustas que recuentos. |

## Pendiente / manual (sin dataset abierto)

Precio de venta €/m² por barrio (Indomio/Eustat), gasto de excursionistas y de
turismo de negocios/MICE por destino (solo hay cifras Euskadi-wide, no
Donostia-específicas), satisfacción del visitante (Observatorio Turístico),
catastro foral (Diputación de Gipuzkoa). Detalle en `docs/SOURCES.md`.

## Cómo poblar `raw/`

```bash
# Opción A — script directo (este directorio)
bash datos/input/descargar_raw.sh            # AEMET necesita AEMET_API_KEY

# Opción B — pipeline (recomendado: mismo resultado, con validación)
cd data-pipeline && python -m donostia_pipeline.build
```
