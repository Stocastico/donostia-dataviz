// TypeScript mirror of the pipeline data contract (docs/DATA-CONTRACT.md).

export type MetricKind = "sequential" | "diverging" | "categorical";
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
  /** Ordered category labels; present only for kind === "categorical". */
  categories?: string[];
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
  /** For categorical metrics each value is the 0-based index into categories. */
  values: Record<string, Record<string, number | null>>;
  /** Ordered category labels; present only for kind === "categorical". */
  categories?: string[];
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

/** Annual city indicator (e.g. MICE) from indicators.json. */
export interface IndicatorData {
  id: string;
  label: string;
  unit: string;
  theme: string;
  source: string;
  years: string[];
  values: Record<string, { value: number; source: string }>;
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
