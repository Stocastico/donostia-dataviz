# Donostia Dataviz

Interactive dashboard of the evolution of **Donostia / San Sebastián**, by
barrio — choropleth maps with a time slider, plus comparative charts. Built from
public open data (Donostia Open Data, INE, AEMET, …).

This is one experiment in the `Experiments` repo; it lives entirely under
`donostia-dataviz/` on its own branch.

## What's here

```
donostia-dataviz/
  docs/            # PROJECT-BRIEF*.md, SOURCES.md, DATA-CONTRACT.md, INSIGHTS.md, GAP-ANALYSIS.md
  data-pipeline/   # Python: raw public sources -> cleaned JSON
  web/             # React + Vite + TS app (MapLibre choropleth + Recharts)
```

The pipeline writes cleaned JSON into `web/src/data/` (committed), so **the site
builds with no Python and no live network calls** — it loads static JSON/GeoJSON.
It also exports the same numbers as **tidy CSV tables** in `data/` (see
`data/README.md`), so the data can be reused in any stack/language without the
app.

## Current status

A working choropleth dashboard over the 19 official barrios, with **8 live**
metrics from Donostia Open Data, grouped by theme in the picker:

- **Turismo** — Viviendas turísticas (VUT/HUT) and posti letto (census
  snapshot); **Densità VUT per 1000 ab.** (derived: VUT / population).
- **Demografia** — Popolazione residente and Popolazione straniera (%), annual
  **2000–2025** (drives the time slider + the barrio-comparison line chart with
  a COVID-19 marker at 2020).
- **Economia** — Renta disponibile pro capite (€, 2016–2023) and the
  **divario di reddito di genere** (%).
- **Istruzione** — Popolazione con studi universitari (%), 2000–2025; **Centri
  educativi per 1000 ab.** (joined to barrios by point-in-polygon — the first
  GIS spatial-join metric).
- **Abitazioni** — Affitto medio €/m² (2016–2024), official Gobierno Vasco EMA
  rental-market statistics by barrio (real registered contracts, not listings);
  **Sforzo per l'affitto (% del reddito)** — a derived rent-to-income housing
  stress index, heaviest on the working-class barrios.

It also has **3 city-grain monthly time series**, shown as a month × year
heatmap in the "Serie temporali" section:

- **Pernottamenti hotel** (INE EOH, 2005–2026) — seasonality and its evolution.
- **Temperatura media**, **massima assoluta**, **Precipitazioni** and **giorni
  caldi (≥30°C)** (AEMET Igeldo `1024E`, 1981–2025) — each shown as a month×year
  heatmap, a monthly-cycles overlay (recent years highlighted) and an annual
  trend; together they read the warming + more frequent heat extremes.

Plus annual city indicators (MICE record + ICCA congresses; **recycling rate**
2010–2023, shown as a generic indicator line chart).

Remaining roadmap items (sale prices, MICE, Ibiltur spend) are city-grain or
need manual extraction; see `docs/SOURCES.md` for each source's access status
and `docs/PROJECT-BRIEF.md` for the full roadmap.

### Build phases

- **Phase 1** — pipeline + generic MapLibre choropleth + slider/legend/tooltip;
  first metrics (VUT census, demographics).
- **Phase 2** — renta (+ gender gap), education, and the derived VUT density;
  theme-grouped metric picker.
- **Phase 3** — city-grain monthly time series + seasonality heatmap: INE EOH
  overnight stays, AEMET Igeldo temperature & precipitation.
- **Housing** — rent €/m² per barrio from the official Gobierno Vasco EMA
  statistics (no scraping).
- **Phase 4** — per-barrio scatter/correlation view: pick any two metrics
  (latest period each), points sized by population, with the live Pearson
  correlation. Headline pairs: VUT density ↔ rent (r≈0.64) and income ↔ %
  foreign (r≈−0.58).
- **MICE + tables** — curated MICE annual indicators (ICCA congresses + the
  2024 Convention Bureau record), shown as a bar chart + stat cards; plus the
  full tidy-CSV export under `data/`. *(current)*

## Run it

### Frontend

```bash
cd web
npm install
npm run dev        # http://localhost:5173
npm test           # vitest (color scale, formatting)
npm run build      # type-check + production build
```

### Data pipeline (only needed to refresh data)

```bash
cd data-pipeline
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m donostia_pipeline.build          # download + rebuild web/src/data
python -m donostia_pipeline.build --offline # rebuild from cached raw/ only
pytest                                      # contract + join-integrity tests
```

Adding a metric = add a module in `data-pipeline/src/donostia_pipeline/datasets/`
exposing `build(ctx) -> list[Metric]`, register it in `build.DATASETS`, rerun the
pipeline. No frontend change is needed — it appears via `metrics.json`.

The AEMET dataset needs a free API key in the `AEMET_API_KEY` environment
variable (request at <https://opendata.aemet.es>); without it that dataset is
skipped and stays `planned`.

## Data contract

One stable shape per choropleth metric keeps the map generic — see
`docs/DATA-CONTRACT.md`. Every dataset joins to a single reference geometry
(`barrios.geojson`) on a stable `barrio_id` slug, which is how we deal with the
fact that barrio subdivisions differ between council datasets.
