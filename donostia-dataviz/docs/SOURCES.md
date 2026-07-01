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
| Climate (temp / precip / extremes) | AEMET — Igeldo station | **station `1024E`**, OpenData REST `valores/climatologicos/mensualesanuales` (monthly **1981–2025**; 36-month cap → 3-year windows). From the same records: `temp_avg` (tm_mes), `temp_max` (ta_max, picco assoluto), `precip` (p_mes), `hot_days_30` (nt_30, giorni ≥30 °C) | **wired ✓** (free key) | code ✓ |
| Hotel occupancy / overnight stays | INE EOH | wstempus table **2078**, series **EOT2721**+**EOT2722** (pernoctaciones España+extranjero) → `overnight_stays` series (2005–2026) | **wired ✓** | code ✓ |
| Airbnb listings (geolocated) | Inside Airbnb | region **Euskadi** snapshot **2025-09-29**: `data/listings.csv.gz` (lat/lon + attrs) + `data/reviews.csv.gz` (one row per review w/ date). Spatial-joined point→barrio (only Donostia kept) → `airbnb_density`; reviews/month → `airbnb_reviews` series. CC BY 4.0 | **wired ✓** | code ✓ |
| Educational facilities (GIS) | Donostia Open Data | recursos/servicios-educativos/**hezkuntzaekipamenduak.json** (GeoJSON, 157 punti; geometrie già in WGS84). Join spaziale punto→barrio (`spatial.py`) → `schools_per_1000` | **wired ✓** | code ✓ |
| Waste / recycling | Donostia Open Data | recursos/residuos/**datos-residuos.csv** (Año, Tipo de recogida, Ambito, kg; annual 2010–2024) → indicatore `recycling_rate` (ámbito urbano; 2024 incompleto escluso) | **wired ✓** | code ✓ |
| Municipal taxes / fees | Donostia Open Data | `impuestos_tipo`/`tasas_tipo` → **pfi_impuestos_tipo_ciudad_ckan.csv**, **pfi_tasas_tipo_ciudad_ckan.csv** (Urtea, Zerga/Tasa, Kopurua €; annual 2011–2025) → indicadores `tax_revenue`/`fee_revenue` (M€, importes **emitidos** nominales). `subvenciones` no en catálogo; existe versión por barrio | **wired ✓** | code ✓ |
| Bus passengers / parking | Donostia Open Data | tema/transporte (annual from 2011; point snapshot) | direct | brief |
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
| Visit motive / gasto / segment | Eustat Ibiltur | tables / manual | annual; pull from Eustat tables |
| MICE events / attendees | DSS Convention Bureau / ICCA | **curated ✓** | `data-pipeline/curated/mice_donostia.csv` — annual indicators (ICCA congresses 2018/19/23/25; 2024 record 188 events / 259k attendees), each value cited per-row. Extend by adding rows. |
| Visitor satisfaction, excursionism | Observatorio Turístico Donostia | manual | annual headline figures |
| Catastro (valore/dati immobili) | **Diputación Foral de Gipuzkoa** | bulk CSV | ⚠️ usare il catastro **foral** su `gipuzkoairekia.eus` (Bienes Inmuebles de Naturaleza Urbana, CC-BY), **NON** `sedecatastro.gob.es` (non copre i territori forali). Parcela-level → aggregare a barrio col join spaziale. |

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
- Donostia San Sebastián Turismoa — *Memorias anuales* (`press.sansebastianturi