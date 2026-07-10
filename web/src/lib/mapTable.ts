// A11y: the choropleth is a WebGL canvas (opaque to screen readers) with a
// mouse-only tooltip. barrioRows() turns the same metric/period into an ordered,
// text list — the data behind the map — for a keyboard-accessible mirror table.

import { formatDelta, formatValue } from "./format";
import type { BarriosGeoJSON, MetricData } from "./types";

export interface BarrioRow {
  id: string;
  name: string;
  /** null when there is no value in this period (sorted last). */
  value: number | null;
  valueLabel: string;
  /** "" when no delta applies (first period, or categorical). */
  deltaLabel: string;
}

/** One row per barrio for the map's mirror table, sorted by value descending
 *  (barrios with no data last). Mirrors ChoroplethMap's decorate() formatting. */
export function barrioRows(
  geojson: BarriosGeoJSON,
  metric: MetricData,
  period: string,
): BarrioRow[] {
  const pIdx = metric.periods.indexOf(period);
  const prev = pIdx > 0 ? metric.periods[pIdx - 1] : null;
  const categorical = metric.kind === "categorical";

  const rows = geojson.features.map((f) => {
    const id = f.properties.barrio_id;
    const value = metric.values[id]?.[period] ?? null;
    const prevValue = prev ? metric.values[id]?.[prev] ?? null : null;
    const valueLabel = categorical
      ? value != null
        ? metric.categories?.[value] ?? "n/d"
        : "n/d"
      : formatValue(value, metric.unit);
    return {
      id,
      name: f.properties.name,
      value,
      valueLabel,
      deltaLabel: prev && !categorical ? formatDelta(value, prevValue) : "",
    };
  });

  return sortRows(rows);
}

/** Rows for maps whose barrios were decorated with computed __value/__valueLabel
 *  (and optional __deltaLabel) rather than coming from a single MetricData —
 *  e.g. the housing-pressure and bivariate maps. */
export function rowsFromDecorated(geojson: BarriosGeoJSON): BarrioRow[] {
  const rows = geojson.features.map((f) => {
    const p = f.properties as unknown as {
      barrio_id: string;
      name: string;
      __value?: number | null;
      __valueLabel?: string;
      __deltaLabel?: string;
    };
    return {
      id: p.barrio_id,
      name: p.name,
      value: p.__value ?? null,
      valueLabel: p.__valueLabel ?? "n/d",
      deltaLabel: p.__deltaLabel ?? "",
    };
  });
  return sortRows(rows);
}

/** Sort by value descending, barrios with no value last (alpha among them). */
function sortRows(rows: BarrioRow[]): BarrioRow[] {
  return rows.sort((x, y) => {
    if (x.value == null && y.value == null) return x.name.localeCompare(y.name, "es");
    if (x.value == null) return 1;
    if (y.value == null) return -1;
    return y.value - x.value;
  });
}
