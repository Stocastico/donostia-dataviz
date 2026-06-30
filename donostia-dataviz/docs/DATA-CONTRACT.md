# Data contract — pipeline ↔ frontend boundary

The Python pipeline (`data-pipeline/`) writes static, cleaned JSON into
`web/src/data/`. The frontend loads only those files — it has **no runtime
dependency** on Python or live source APIs. One stable shape per choropleth
metric keeps the map/slider code generic: adding a dataset is "drop a JSON +
register a metric", with no map-component changes.

## Files

### `barrios.geojson` — the single reference geometry

Standard GeoJSON `FeatureCollection`, coordinates in **EPSG:4326**. Each feature:

```jsonc
{
  "type": "Feature",
  "properties": { "barrio_id": "amara-berri", "name": "Amara Berri" },
  "geometry": { "type": "Polygon", "coordinates": [ /* ... */ ] }
}
```

`barrio_id` is a stable slug (lowercased, accent-stripped, hyphenated). Every
metric joins on it.

### `metric_<id>.json` — one per choropleth metric

```jsonc
{
  "id": "vut_density",
  "label": "Densità VUT (per 1000 abitanti)",
  "unit": "per 1000 ab.",
  "kind": "sequential",          // "sequential" | "diverging" | "categorical"
  "theme": "tourism",
  "source": "Donostia Open Data — censo viviendas turísticas",
  "periods": ["2020", "2021", "2022", "2023", "2024"],
  "values": {
    "amara-berri": { "2020": 3.1, "2021": 3.4, "2022": null },
    "gros":        { "2020": 8.2, "2021": 9.0, "2022": 9.6 }
  }
}
```

- `periods` — ordered list of period labels (year `"YYYY"` or month `"YYYY-MM"`).
- `values[barrio_id][period]` — a `number`, or `null` when missing for that
  period (the map renders missing barrios in a neutral "no data" color).
- `kind` selects the color scale: `sequential` (D3 sequential for absolute
  values), `diverging` (blue=down / red=up, centered at 0, for deltas), or
  `categorical` (qualitative palette for class/profile metrics).
- `categories` — **only** for `kind: "categorical"`: an ordered list of class
  labels. Each `value` is then the **0-based index** into this list (e.g.
  `barrio_profile` carries the barrio-typology cluster). The legend renders one
  swatch per label and the tooltip shows the label, not the number.
- `confidence` — MET-4 provenance tier: `observed` (measured directly),
  `derived` (computed from observed metrics) or `proxy` (an approximation). Drives
  the UI's confidence badge.
- `assumptions` — optional list of short caveat strings shown on the confidence
  card (omitted when empty).

### `metrics.json` — the registry the UI reads

Array of lightweight descriptors used to build the metric dropdown without
loading every metric file up front:

```jsonc
[
  {
    "id": "vut_density",
    "label": "Densità VUT (per 1000 abitanti)",
    "theme": "tourism",
    "geoGrain": "barrio",
    "timeGrain": "year",
    "source": "Donostia Open Data — censo viviendas turísticas",
    "status": "live"            // "live" | "partial" | "planned"
  }
]
```

`status: "planned"` metrics appear in the UI disabled with a "data coming soon"
note (for manual/PDF sources not yet extracted — MICE, Ibiltur, Indomio).

## Invariants (enforced by pipeline tests)

1. Every `barrio_id` used in any `metric_*.json` exists in `barrios.geojson`.
2. Every metric in `metrics.json` with `status: "live"` has a matching
   `metric_<id>.json`, and vice-versa.
3. `periods` is sorted ascending and unique.
4. No negative values for count/density metrics; deltas may be negative.
5. Each `values` entry only uses keys present in `periods`.
