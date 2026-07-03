# Source registry — Donostia Dataviz

Consolidated and verified data sources. The brief (`PROJECT-BRIEF.md`) is the
origin; this file pins down the vague references and records **access status**,
which drives build sequencing. We build first on `direct` sources, then `api`,
then `download`, and register `manual`/`planned` sources so the UI degrades
gracefully (shows "data coming soon") until their extraction lands.

## Reference geometry (everything joins to this)

| Resource | URL | Access | Notes |
|---|---|---|---|
| Barrios polygons (`mapa_auzoak`) | https://www.donostia.eus/datosabiertos/catalogo/mapa_auzoak | direct | 17 official barrios. Reproject to EPSG:4326, assign stable `barrio_id` slug. **Single reference geometry.** |
| Census tracts | https://www.donostia.eus/datosabiertos/catalogo/delimitaciones_censales | direct | Finer grain, optional |
| Unidades menores | Donostia Open Data | direct | Sub-barrio grain, optional |

> ⚠️ Barrio subdivisions differ between datasets from the same council. We pick
> `mapa_auzoak` as the one reference geometry and join every dataset onto its
> `barrio_id`. Datasets whose barrio names don't match get an explicit alias map
> in the pipeline (`config.py`), never a silent drop.

## Confirmed sources

| Theme | Source | Handle / endpoint | Access | Verified |
|---|---|---|---|---|
| VUT (viviendas uso turístico) | Donostia Open Data | recursos/censo-viviendas-turisticas/**urb_ckan_vtur_censo.csv** (Auzoa, helbidea, Mota, plazak — current *snapshot*, no time field) | **wired ✓** | code ✓ |
| Demographics / origin | Donostia Open Data | recursos/demografia-origen/**demografianacionalidadbarrio.csv** (Urtea, AuzoKodea, Jatorria, PertsonenKop; annual 2000–2025) | **wired ✓** | code ✓ |
| Demographics / age | Donostia Open Data | recursos/demografia-piramideedad/**demografiapiramideedadbarrio.csv** (Urtea, AuzoKodea, AdinTartea 5-year bands `00 - 04`…`95 - >=`, PertsonenKop; annual 2000–2025) → `ageing_index`, `pct_youth_adults` | **wired ✓** | code ✓ |
| Education level | Donostia Open Data | recursos/demografia-nivelestudios/**demografianivelestudiosbarrio.csv** (year, AuzoKodea, level, Ehuneko_Totala 0–1; annual 2000–2025) | **wired ✓** | code ✓ |
| Renta | Donostia Open Data (Eustat) | recursos/eustat_renta/**eustatrentabarrio.csv** (Anyo, CodBarrio, RentaPer_Total + by gender/age/origin; annual 2016–2023) | **wired ✓** | code ✓ |
| Rent €/m² per barrio | Gobierno Vasco — EMA/EMAL | **EMAL.-Barrios-Municipios.-2016-2025_es.xlsx**, sheet **T8.3** (renta media €/m² construido, annual 2016–2024). EMA barrio codes 001–017 = auzoak codes 1–17 → join by code | **wired ✓** | code ✓ |
| Climate (temp / precip / extremes) | AEMET — Igeldo station | **station `1024E`**, OpenData REST `valores/climatologicos/mensualesanuales` (monthly **1981–current**, `AEMET_YEAR_RANGE` in `build.py`; 36-month cap → 3-year windows). From the same records: `temp_avg` (tm_mes), `temp_max` (ta_max, picco assoluto), `precip` (p_mes), `hot_days_30` (nt_30, giorni ≥30 °C). The in-progress current year is flagged as partial in the UI (`isPartialYear`) — excluded from the trend fit, hatched in the warming stripes | **wired ✓** (free key) | code ✓ |
| Hotel occupancy / overnight stays | INE EOH | wstempus table **2078**, series **EOT2721**+**EOT2722** (pernoctaciones España+extranjero) → `overnight_stays` series (2005–2026) | **wired ✓** | code ✓ |
| Mortality risk ₅qx, Gipuzkoa (AN-12) | INE — Tablas de mortalidad | wstempus table **67235**, server-side filter prov. Gipuzkoa + "Riesgo de muerte" (qx ‰, quinquenal, por sexo), 1991–2024 → `ine_mortalidad_gipuzkoa.json` | **analysis-only** (AN-12; no alimenta el pipeline) | code ✓ (jul-2026) |
| Airbnb listings (geolocated) | Inside Airbnb | region **Euskadi** snapshot **2025-09-29**: `data/listings.csv.gz` (lat/lon + attrs) + `data/reviews.csv.gz` (one row per review w/ date). Spatial-joined point→barrio (only Donostia kept) → `airbnb_density`; reviews/month → `airbnb_reviews` series. CC BY 4.0 | **wired ✓** | code ✓ |
| Educational facilities (GIS) | Donostia Open Data | recursos/servicios-educativos/**hezkuntzaekipamenduak.json** (GeoJSON, 157 punti; geometrie già in WGS84). Join spaziale punto→barrio (`spatial.py`) → `schools_per_1000` | **wired ✓** | code ✓ |
| Waste / recycling | Donostia Open Data | recursos/residuos/**datos-residuos.csv** (Año, Tipo de recogida, Ambito, kg; annual 2010–2024) → indicatore `recycling_rate` (ámbito urbano; 2024 incompleto escluso) | **wired ✓** | code ✓ |
| Municipal taxes / fees | Donostia Open Data | `impuestos_tipo`/`tasas_tipo` → **pfi_impuestos_tipo_ciudad_ckan.csv**, **pfi_tasas_tipo_ciudad_ckan.csv** (Urtea, Zerga/Tasa, Kopurua €; annual 2011–2025) → indicadores `tax_revenue`/`fee_revenue` (M€, importes **emitidos** nominales). `subvenciones` no en catálogo; existe versión por barrio | **wired ✓** | code ✓ |
| Language model (euskera) schooling (REC-9) | Eustat (PxWeb) | table **PX_040601_ceens_mun01**, municipio **20069** (Donostia), server-side filtered via POST (titularidad Total, nivel "Enseñanzas de régimen general", modelo A/B/D/X; annual **1983/1984–2024/2025**) → `pct_language_model_a/b/d` (% of enrolled students) | **wired ✓** | code ✓ |
| Unemployment rate (REC-5) | Eustat (PxWeb) | table **PX_050403_cpra_tab19**, capital **Donostia/San Sebastián** (not aggregated with other municipalities), server-side filtered via POST (tasa de paro, sexo Total/Hombres/Mujeres, trimestre "Promedio anual"; annual **2015–2025**) → `unemployment_rate(_men/_women)` (%) | **wired ✓** | code ✓ |
| Commercial fabric proxy (REC-7) | Eustat (PxWeb) — CDIRAE business directory | table **PX_200163_cdirae_est04b**, municipio **20069** (Donostia), ~630 CNAE-2009 4-digit codes summed client-side into retail (47xx) / hospitality (55xx+56xx) since the source has no section/division rollup; annual **2008–2025** → `total_establishments`, `retail_establishments_share`, `hospitality_establishments_share` (%). **Proxy, not causal**: retail share 14.9%→12.6%, hospitality 6.0%→8.1% — consistent with, not proof of, tourist substitution (e-commerce erosion of retail isn't ruled out). No open dataset of commercial *licenses* by category+barrio exists (the brief's original ask); this is city-grain only | **wired ✓** | code ✓ |
| VUT/HUT license history (REC-12) | Gobierno Vasco — REATE (Open Data Euskadi) | dataset "Viviendas y habitaciones de vivienda particular para uso turístico": **viviendas.json** + **habitaciones.json**, one record per *currently registered* unit with `FechainscripcionREATE` (dd/mm/yyyy) → `vut_licenses_new`, `vut_licenses_cumulative`, `vut_plazas_cumulative` (annual 2016–2025, city). ⚠️ **Living-registry snapshot**: bajas are not published, so every curve is of *surviving* licenses (a floor of legal supply). No barrio/coords (street addresses only — same callejero limit as REC-8) | **wired ✓** | code ✓ (jul-2026) |
| Labor/study mobility + localized jobs (REC-17) | Eustat (PxWeb) — EMPA / EME / DIRAE | **no municipio×municipio OD matrix exists in the PxWeb bank** (full catalog checked, 2,321 tables). Wired instead: **PX_050407_cempa_empa_mt02** (employed residents by categorical *lugar de trabajo*, 2021–2024 → `residents_work_in_city_pct`), **PX_040606_ceme_me02** (students by *lugar de estudios*, 2021–2024 → `residents_study_in_city_pct`), **PX_200163_cdirae_est07** (persons employed in establishments located in Donostia, 1995–2025 → `jobs_located`) + derived `job_concentration_ratio` (jobs/employed residents; 1.20 in 2024 → the city imports workers). Closes H4's "concentrar actividad" half | **wired ✓** | code ✓ (jul-2026) |
| Migration profile by region of origin (REC-21) | Donostia Open Data (same `demografianacionalidadbarrio.csv` as `pct_foreign`, unaggregated) | 57 countries grouped into 8 regions of origin (Latin America, North Africa, Sub-Saharan Africa, Western Europe, Eastern Europe, Middle East, East/South Asia, North America/Oceania) → `pct_origin_*` (8 metrics, annual 2000–2025, barrio). Splits the single `pct_foreign` aggregate into populations that move in *opposite* directions with barrio income (Latin America r=-0.69, Western Europe r=+0.24) | **wired ✓** | code ✓ (jul-2026) |
| Employment stability by nationality + R&D intensity (REC-21) | Eustat (PxWeb) — PRA / R&D-personnel survey | **PX_050403_cpra_tab17** (unemployment rate by nationality, Gipuzkoa, 2015–2026 → `unemployment_rate_spanish_gipuzkoa`/`_foreign_gipuzkoa`; foreign roughly doubles Spanish) + **PX_043201_cid_res08c** ÷ **PX_050403_cpra_tab04** (R&D personnel per 1000 employed, Gipuzkoa → `randd_personnel_per_1000_employed_gipuzkoa`, 31‰ vs. Spain's 13.6‰, INE 2024). **Grain is Gipuzkoa, not Donostia** — Eustat's Basque Labour Force Survey and R&D-personnel stats don't go below territorio histórico. Occupation-by-CNO-11 breakdown, establishments-by-A10-sector (Donostia) and income-by-profession stay **analysis-only** (`analysis/perfil_extranjeros_empleo.py`) — they don't fit the Metric/Indicator shape (multi-category breakdown, not a single per-year value) | **wired ✓ (partial)** | code ✓ (jul-2026) |
| Airbnb active-listings snapshots (REC-13) | Inside Airbnb | quarterly Euskadi snapshots `visualisations/listings.csv`, **8 accessible** (2023-12-29 → 2025-09-29); the 8 older ones (back to 2021-12-30) return 403 — archived-data request only. Active listings per barrio (point-in-polygon) vs reviews-LTM on the same listing universe → MET-7 quantified: supply +2.0% vs reviews +20.2% (bias ×1.18); declared-license share 58→85% with a −10% active drop in 2025 (purge footprint). CC BY 4.0 | **analysis-only** (`analysis/airbnb_snapshots.py`) | code ✓ (jul-2026) |
| Surface heat island (REC-14) | Landsat 8/9 C2 L2 via Microsoft Planetary Computer STAC | thermal band `lwir11` (30 m) + `qa_pixel` cloud mask, 45 summer scenes 2015–2025, anonymous SAS access (USGS M2M / Copernicus need accounts). Zonal LST anomaly vs city mean per barrio → `analysis/output/heat_island_barrio.csv`: Gros +4.8 °C, Amara Berri +4.3, Egia +4.1; green ring −3…−5 °C. Needs `pip install rasterio pyproj` (that script only) | **analysis-only** (`analysis/heat_island.py`) | code ✓ (jul-2026) |
| Bus passengers / parking (REC-6) | Donostia Open Data | ⚠️ the `dbus_utilizacion` dataset linked from Open Data Euskadi is **gone** from Donostia's CKAN catalog (403, zero `package_search`/`resource_search` hits) — likely discontinued, same pattern as Crime below | not available | web ✓ (jul-2026) |
| Crime | Donostia Open Data (Guardia Municipal) | ⚠️ **non più nel catalogo**: `delitos-guardia`/`gua_delitosbarrio_ckan.csv` (brief) dà 403/404 e non è in `package_list` (138 dataset) — probabile rimozione/riorganizzazione (collaborazione Ertzaintza↔Guardia Municipal, 2026). Ripiego: serie municipio Ertzaintza/MIR. | non disponibile (barrio) | web ✓ |

## Derived metrics (computed in the pipeline from the sources above)

| Metric | Formula | Inputs | Status |
|---|---|---|---|
| `vut_density` — VUT per 1000 ab. | VUT units / population(latest year) × 1000 | VUT census + demographics | **wired ✓** |
| `income_gender_gap` — divario di genere | (RentaPer_Hombres − RentaPer_Mujeres) / RentaPer_Hombres × 100 | renta barrio | **wired ✓** |
| `schools_per_1000` — centri educativi | #scuole(join spaziale) / popolazione × 1000 | educativos GeoJSON + demographics | **wired ✓** |
| `airbnb_density` — annunci Airbnb per 1000 ab. | #annunci(join spaziale) / popolazione × 1000 | Inside Airbnb listings + demographics | **wired ✓** (REC-4) |
| `housing_tension` — sforzo affitto/reddito (%) | affitto €/m² × 12 × 30 m²/persona / reddito pro capite × 100 | rent EMA + income | **wired ✓** (idea #4; assunzione 30 m²/persona) |
| `transform_class` / `transform_*_score` / `transform_*_excess` — Indice di Trasformazione (AN-8) | modo Freeman (suscettibilità + crescita laureati/affitto) e modo pressione turistica; z-score, componenti a vista | income + rent + % university + VUT density | **wired ✓** (VIZ-6; cfr. intermedia/INDICE-TRANSFORMACION.md) |
| ageing index | pop ≥65 / <15 × 100 | pirámide de edad por barrio | **wired ✓** (REC-1) |

## Manual / planned (no structured open dataset — extraction needed)

| Theme | Source | Access | Plan |
|---|---|---|---|
| Sale price €/m² per barrio | Indomio / Eustat | scrape / tables | sale prices still pending; rent is now covered by the official EMA below |
| Visit motive / gasto / segment (REC-10) | Basquetour — IBILTUR Ocio | **curated ✓** | `datos/input/ibiltur_donostia.csv` — 2023 destination-level "ficha" for Donostia (spend/person, spend/person/day, economic impact), each cited. Not in Eustat's PxWeb bank at municipio grain — Basquetour publishes it as a per-edition destination PDF instead, not all editions comparable (e.g. 2022's is "Verano"/summer-only, not "Ocio"/full-year, so it's excluded rather than mixed in). Excursionist and MICE-business segments only exist Euskadi-wide, not Donostia-specific — not represented. |
| MICE events / attendees | DSS Convention Bureau / ICCA | **curated ✓** | `datos/input/mice_donostia.csv` — annual indicators (ICCA congresses 2018/19/23/25; 2024 record 188 events / 259k attendees), each value cited per-row. Extend by adding rows. |
| Visitor satisfaction, excursionism | Observatorio Turístico Donostia | manual | annual headline figures |
| Catastro (valore/dati immobili) | **Diputación Foral de Gipuzkoa** | bulk CSV | ⚠️ usare il catastro **foral** su `gipuzkoairekia.eus` (Bienes Inmuebles de Naturaleza Urbana, CC-BY, mirror funzionante: `api.gipuzkoairekia.eus/dataset/recurso/<id>/descargar`), **NON** `sedecatastro.gob.es` (non copre i territori forali). Verificato (jul-2026): **nessuno dei due CSV porta coordinate o barrio** — `parcelas` solo una `Refer` catastale interna a 7 cifre (serve geometria INSPIRE WFS/GML non confermata); `locales` porta via+portale (geocodificabile, ma senza stradario→barrio nel progetto). Non è il quick-win che sembrava; join spaziale ancora da risolvere. |

## Spatial join (GIS sources)

GIS datasets without a barrio field (points/grids/polygons) are assigned to the
reference geometry by `spatial.py` (point-in-polygon + area-weighted
interpolation) at ingestion — the same "join once" principle as attribute data.
Donostia's GeoJSON resources are already WGS84. **SHP-only** sources (e.g. the
noise grids `ruido-total`/`ruido-noche`, served in EPSG:25830) are handled by
`gis_io.load_shapefile` / `gis_io.load_shapefile_zip` (pyshp) +
`gis_io.reproject_geometry` (pyproj), which reproject 25830→4326 on load — no
external `ogr2ogr` step needed.

| Theme | Source | Handle / endpoint | Access | Verified |
|---|---|---|---|---|
| Night noise (Lnight) | Donostia Open Data — `ruido-noche` | `.../shp/Zarata_Ruido/**2022_DSS_IZT_totala_gau.zip**` (zipped SHP, EPSG:25830; nested iso-contours Lnight ≥50/55/60/65/70 dB, field `Isovalue`). Areal overlap → `noise_night_pct55` (% barrio area ≥55 dB). **Transport-dominated**, not nightlife | **wired ✓** | code ✓ |

## AEMET access note

The Igeldo monthly climatological series uses station index `1024E`. The
OpenData REST API requires a **free API key** (request at `opendata.aemet.es`).
The pipeline reads the key from the `AEMET_API_KEY` environment variable; if it
is absent, the AEMET dataset build is skipped and the metric is registered as
`planned` so the rest of the pipeline still runs.

## Academic references

- Aguado-Moralejo & Del Campo-Echeverría (2020) — *El fenómeno Airbnb en Donostia-San Sebastián* — CyTET 52(206)
- Etxezarreta-Etxarri et al. (2020) — *Urban touristification in Spanish cities: rental-housing sector in San Sebastian*
- Boletín AGE (2023) — *The touristification of urban spaces: measurement proposal*
- Eustat — *Ibiltur: Encuesta de Turismo Receptivo*
- ICCA — *International Congress Statistics Report* (Donostia pos. 221 world / 112 Europe, 2019)
- Donostia San Sebastián Turismoa — *Memorias anuales* (`press.sansebastianturismoa.eus`)
