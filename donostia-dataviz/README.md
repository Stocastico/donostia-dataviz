# Donostia Dataviz

Interactive dashboard of the evolution of **Donostia / San Sebastián**, by
barrio — choropleth maps with a time slider, plus comparative charts. Built from
public open data (Donostia Open Data, INE, AEMET, …).

This is one experiment in the `Experiments` repo; it lives entirely under
`donostia-dataviz/` on its own branch.

## What's here

```
donostia-dataviz/
  docs/            # PROJECT-BRIEF.md, SOURCES.md, DATA-CONTRACT.md
  data-pipeline/   # Python: raw public sources -> cleaned JSON
  web/             # React + Vite + TS app (MapLibre choropleth + Recharts)
```

The pipeline writes cleaned JSON into `web/src/data/` (committed), so **the site
builds with no Python and no live network calls** — it loads static JSON/GeoJSON.

## Current status (first milestone)

A working choropleth dashboard over the 19 official barrios, with these **live**
metrics from Donostia Open Data:

- **Viviendas turísticas (VUT/HUT)** and **posti letto** — touristic-housing
  census (current snapshot).
- **Popolazione residente** and **Popolazione straniera (%)** — annual series
  **2000–2025** (this drives the time slider and the barrio-comparison line
  chart, with a COVID-19 marker at 2020).

Further metrics (rent €/m², VUT density, AEMET climate, INE seasonality, MICE,
Ibiltur spend) are registered as **planned** and appear disabled in the metric
picker. See `docs/SOURCES.md` for each source's access status and
`docs/PROJECT-BRIEF.md` for the full roadmap.

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
