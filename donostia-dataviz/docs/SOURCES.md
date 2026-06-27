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
| Education level | Donostia Open Data | recursos/demografia-nivelestudios/**demografianivelestudiosbarrio.csv** (year, AuzoKodea, level, Ehuneko_Totala 0–1; annual 2000–2025) | **wired ✓** | code ✓ |
| Renta | Donostia Open Data (Eustat) | recursos/eustat_renta/**eustatrentabarrio.csv** (Anyo, CodBarrio, RentaPer_Total + by gender/age/origin; annual 2016–2023) | **wired ✓** | code ✓ |
| Climate (temp / precip) | AEMET — Igeldo station | **station `1024E`**, OpenData REST API `opendata.aemet.es` (monthly values from 1981) | api (free key) | web ✓ |
| Hotel occupancy / overnight stays | INE EOH | San Sebastián is an INE "punto turístico"; INEbase EOH + datos.gob.es API ids `2074`/`2078` | api / csv | web ✓ |
| Airbnb listings (geolocated) | Inside Airbnb | https://insideairbnb.com/euskadi/ region page (San Sebastián) | download / request | web ✓ |
| Bus passengers / parking | Donostia Open Data | tema/transporte (annual from 2011; point snapshot) | direct | brief |
| Crime | Donostia Open Data (Guardia Municipal) | tema/seguridad (barrio, annual) | direct | brief |

## Derived metrics (computed in the pipeline from the sources above)

| Metric | Formula | Inputs | Status |
|---|---|---|---|
| `vut_density` — VUT per 1000 ab. | VUT units / population(latest year) × 1000 | VUT census + demographics | **wired ✓** |
| `income_gender_gap` — divario di genere | (RentaPer_Hombres − RentaPer_Mujeres) / RentaPer_Hombres × 100 | renta barrio | **wired ✓** |
| `vut_density` per anno, ageing index, Airbnb intensity | see brief | future sources | planned |

## Manual / planned (no structured open dataset — extraction needed)

| Theme | Source | Access | Plan |
|---|---|---|---|
| Sale & rent €/m² per barrio | Indomio | scrape | monthly 2023→; register `planned`, scrape later |
| Visit motive / gasto / segment | Eustat Ibiltur | tables / manual | annual; pull from Eustat tables |
| MICE events / attendees | DSS Convention Bureau / ICCA | PDF extraction | memorias on `press.sansebastianturismoa.eus`, ICCA reports |
| Visitor satisfaction, excursionism | Observatorio Turístico Donostia | manual | annual headline figures |

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
