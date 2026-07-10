// TypeScript mirror of the pipeline data contract (docs/DATA-CONTRACT.md).

export type MetricKind = "sequential" | "diverging" | "categorical";
export type MetricStatus = "live" | "partial" | "planned";
/** MET-4 confidence tier: how the number relates to reality. */
export type Confidence = "observed" | "derived" | "proxy";

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
  /** MET-4 confidence tier + assumptions for the confidence card. */
  confidence?: Confidence;
  assumptions?: string[];
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

/** One street in the sub-barrio touristic-housing export (street_vut.json). */
export interface StreetVut {
  code: string;
  nameEs: string;
  nameEu: string;
  lon: number;
  lat: number;
  /** Touristic units on the street (VUT + HUT). */
  units: number;
  vut: number;
  hut: number;
  /** Licensed beds (plazas) summed over the street's units. */
  beds: number;
}

/** Payload of street_vut.json — touristic housing per street (calles_vut). */
export interface StreetVutData {
  source: string;
  totalRows: number;
  matchedRows: number;
  matchRate: number;
  streetCount: number;
  streets: StreetVut[];
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

/** One indexed city series in the affordability comparison (HU-7). */
export interface AffordabilitySeries {
  id: string;
  label: string;
  color: string;
  confidence: "observed" | "derived" | "proxy";
  dash?: boolean;
  lastYear: number;
  // index value (base year = 100) per year, e.g. { "2016": 100, "2024": 134.8 }
  data: Record<string, number>;
  growth: { common: number | null; full: number | null };
}

/** affordability_index.json — venta/alquiler/salario/IPC, city, base 2016 = 100. */
export interface AffordabilityData {
  baseYear: number;
  commonEnd: number;
  unit: string;
  series: AffordabilitySeries[];
  source: string;
  note: string;
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

/** One foreign country in a barrio's origin card (REC-21-web). */
export interface OriginCountry {
  country: string;
  region: string;
  peopleLatest: number;
  peoplePast: number;
  pctOfBarrio: number;
}

export interface BarrioOrigins {
  name: string;
  foreignLatest: number;
  top: OriginCountry[];
}

/** Payload of origen_paises_barrio.json. */
export interface OriginPaisesData {
  latestYear: string | null;
  pastYear: string | null;
  source: string;
  barrios: Record<string, BarrioOrigins>;
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
