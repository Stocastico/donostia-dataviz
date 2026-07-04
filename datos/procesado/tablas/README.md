# Donostia Dataviz — data tables (CSV)

Language-agnostic **tidy CSV** exports of every dataset processed by the
pipeline. They carry the same numbers the web app shows, but in a plain "long"
format any tool can read (pandas, R, DuckDB, JS, spreadsheets) — so the data can
be regenerated in another stack without touching the app or its JSON.

Regenerate with `python -m donostia_pipeline.build` (see `../../../data-pipeline/`).
All files are UTF-8, comma-separated, with a header row.

## Files

### `barrios.csv`
The 19 official barrios (reference geometry keys).

| column | meaning |
|---|---|
| `barrio_id` | stable slug used as the join key everywhere |
| `name` | display name |
| `kod_auzo` | official auzoak code (1–19) |

### `metrics_long.csv`
Per-barrio metrics (choropleths), one row per barrio × period.

| column | meaning |
|---|---|
| `metric_id` | e.g. `rent_eur_m2`, `pct_foreign`, `vut_density` |
| `label`, `theme`, `unit` | metric metadata (theme: tourism/demography/economy/education/housing) |
| `barrio_id`, `barrio_name` | the barrio (join to `barrios.csv`) |
| `period` | year `YYYY`, or `actual` for snapshots |
| `value` | numeric value (blank = no data) |
| `source` | citation for the dataset |

### `series_long.csv`
City-grain monthly time series (seasonality / climate), one row per year × month.

| column | meaning |
|---|---|
| `series_id` | `overnight_stays`, `temp_avg`, `precip` |
| `label`, `theme`, `unit` | series metadata |
| `year` | `YYYY` |
| `month` | `1`–`12` |
| `value` | numeric value (blank = no data) |
| `source` | citation for the dataset |

### `indicators_long.csv`
Annual city indicators (e.g. MICE), one row per indicator × year. Each row keeps
its own `source` because these are curated from individual press releases.

| column | meaning |
|---|---|
| `id` | e.g. `mice_icca_congresses`, `mice_events_total` |
| `label`, `theme`, `unit` | indicator metadata |
| `year`, `value` | the observation |
| `source` | citation for that specific figure |

### `calles_vut.csv`
Touristic housing (VUT/HUT) at **street** granularity — the one table below the
barrio level. One row per street with ≥1 touristic unit (301 streets). Built by
matching the VUT census addresses to the municipal callejero (see
`datasets/calles_vut.py`); mirrors `web/src/data/street_vut.json`.

| column | meaning |
|---|---|
| `street_code` | stable callejero code (`KodKalea`) |
| `name_es`, `name_eu` | street name (Spanish / Basque) |
| `lon`, `lat` | representative label point (WGS84), *not* the street axis |
| `units` | touristic units on the street (`vut` + `hut`) |
| `vut`, `hut` | split into whole dwellings (VUT) and rooms (HUT) |
| `beds` | licensed beds (plazas) summed over the street's units |

## Provenance

Sources and access status for every dataset are documented in
`../../../docs/SOURCES.md`. Most come from official open data (Donostia Open Data,
INE, AEMET, Gobierno Vasco EMA); the MICE indicators are hand-curated from cited
press releases and ICCA reports.
