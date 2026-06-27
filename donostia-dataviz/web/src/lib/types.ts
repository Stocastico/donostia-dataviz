// TypeScript mirror of the pipeline data contract (docs/DATA-CONTRACT.md).

export type MetricKind = "sequential" | "diverging";
export type MetricStatus = "live" | "partial" | "planned";

/** Lightweight descriptor from metrics.json — drives the metric picker. */
export interface MetricInfo {
  id: string;
  label: string;
  unit: string;
  theme: string;
  kind: MetricKind;
  geoGrain: string;
  timeGrain: "year" | "month" | "snapshot";
  source: string;
  status: MetricStatus;
  periods: string[];
}

/** Full metric payload from metric_<id>.json. */
export interface MetricData {
  id: string;
  label: string;
  unit: string;
  kind: MetricKind;
  theme: string;
  source: string;
  periods: string[];
  values: Record<string, Record<string, number | null>>;
}

/** Lightweight descriptor from series.json. */
export interface SeriesInfo {
  id: string;
  label: string;
  unit: string;
  theme: string;
  source: string;
  kind: "month-year";
  years: string[];
}

/** Full city-grain monthly time series from series_<id>.json. */
export interface SeriesData {
  id: string;
  label: string;
  unit: string;
  theme: string;
  source: string;
  kind: "month-year";
  years: string[];
  // values[year][month "1".."12"] -> number | null
  values: Record<string, Record<string, number | null>>;
}

export interface BarrioProperties {
  barrio_id: string;
  name: string;
  kod_auzo: string;
}

export type BarriosGeoJSON = GeoJSON.FeatureCollection<
  GeoJSON.Geometry,
  BarrioProperties
>;
