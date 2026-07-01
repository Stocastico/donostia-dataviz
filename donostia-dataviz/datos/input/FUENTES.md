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
| `vtur_censo.csv` | Donostia Open Data | `.../recursos/censo-viviendas-turisticas/urb_ckan_vtur_censo.csv` | `vut_count`, `vut_density`, `vut_plazas` | snapshot actual | Open Data DSS |
| `demo_barrio.csv` | Donostia Open Data | `.../recursos/demografia-origen/demografianacionalidadbarrio.csv` | `pct_foreign`, `population` | anual 2000–2025 | Open Data DSS |
| `edad_barrio.csv` | Donostia Open Data | `.../recursos/demografia-piramideedad/demografiapiramideedadbarrio.csv` | `ageing_index`, `pct_youth_adults` | anual 2000–2025 | Open Data DSS |
| `renta_barrio.csv` | Donostia Open Data (Eustat) | `.../recursos/eustat_renta/eustatrentabarrio.csv` | `income_total`, `income_gender_gap` | anual 2016–2023 | Open Data DSS / Eustat |
| `estudios_barrio.csv` | Donostia Open Data | `.../recursos/demografia-nivelestudios/demografianivelestudiosbarrio.csv` | `pct_university` | anual 2000–2025 | Open Data DSS |
| `ine_pernoct_esp.json` | INE EOH | `servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EOT2721?nult=600` | `overnight_stays` (residentes) | mensual 2005–2026 | INE (open) |
| `ine_pernoct_ext.json` | INE EOH | `servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EOT2722?nult=600` | `overnight_stays` (extranjero) | mensual 2005–2026 | INE (open) |
| `emal_barrios.xlsx` | Gobierno Vasco — EMA/EMAL | `euskadi.eus/.../opendata/EMAL.-Barrios-Municipios.-2016-2025_es.xlsx` (hoja **T8.3**) | `rent_eur_m2` | anual 2016–2024 | Gob. Vasco (open) |
| `educativos.json` | Donostia Open Data | `.../recursos/servicios-educativos/hezkuntzaekipamenduak.json` | `schools_per_1000` | actual (157 puntos) | Open Data DSS |
| `residuos.csv` | Donostia Open Data | `.../recursos/residuos/datos-residuos.csv` | `recycling_rate` | anual 2010–2024 | Open Data DSS |
| `ruido_noche_2022.zip` | Donostia Open Data (ruido-noche) | `.../ide/INGURUMENA-MEDIO_AMBIENTE/shp/Zarata_Ruido/2022_DSS_IZT_totala_gau.zip` (SHP, EPSG:25830) | `noise_night_pct55` | 2022 | Open Data DSS |
| `impuestos_ciudad.csv` | Donostia Open Data | `.../dataset/36ef69b9…/download/pfi_impuestos_tipo_ciudad_ckan.csv` | `tax_revenue` | anual 2011–2025 | Open Data DSS |
| `tasas_ciudad.csv` | Donostia Open Data | `.../dataset/7c0f2bf4…/download/pfi_tasas_tipo_ciudad_ckan.csv` | `fee_revenue` | anual 2011–2025 | Open Data DSS |
| `airbnb_listings.csv.gz` | Inside Airbnb | `data.insideairbnb.com/spain/pv/euskadi/2025-09-29/data/listings.csv.gz` | `airbnb_density` | **2025-09-29** | CC BY 4.0 |
| `airbnb_reviews.csv.gz` | Inside Airbnb | `data.insideairbnb.com/spain/pv/euskadi/2025-09-29/data/reviews.csv.gz` | `airbnb_reviews`, `airbnb_activity` | **2025-09-29** | CC BY 4.0 |
| `aemet_igeldo.json` | AEMET OpenData | REST `valores/climatologicos/mensualesanuales`, estación **1024E** | `temp_avg`, `temp_max`, `precip`, `hot_days_30` | mensual 1981–2025 | AEMET (**requiere clave** `AEMET_API_KEY`) |
| `eustat_modelos_linguisticos.json` | Eustat (PxWeb) | tabla `PX_040601_ceens_mun01`, municipio 20069, **POST** con filtro server-side (ver `descargar_raw.sh`) | `pct_language_model_a/b/d` | anual 1983/1984–2024/2025 | Eustat (open) |

## Inputs curados (versionados en el repo)

| Fichero | Contenido | Origen |
|---|---|---|
| `mice_donostia.csv` | Indicadores MICE (congresos ICCA; récord 2024: 188 eventos / 259k asistentes) | Curado de notas de prensa citadas por fila (DSS Convention Bureau / ICCA). Ampliar añadiendo filas. |

## Pendiente / manual (sin dataset abierto)

Precio de venta €/m² por barrio (Indomio/Eustat), gasto/segmento del visitante
(Eustat Ibiltur), satisfacción del visitante (Observatorio Turístico), catastro
foral (Diputación de Gipuzkoa). Detalle en `docs/SOURCES.md`.

## Cómo poblar `raw/`

```bash
# Opción A — script directo (este directorio)
bash datos/input/descargar_raw.sh            # AEMET necesita AEMET_API_KEY

# Opción B — pipeline (recomendado: mismo resultado, con validación)
cd data-pipeline && python -m donostia_pipeline.build
```
