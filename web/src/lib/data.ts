// Data loaders. The pipeline writes static JSON into src/data; we import the
// registry + geometry eagerly (small) and lazy-load each metric on demand.

import type {
  BarriosGeoJSON,
  IndicatorData,
  MetricData,
  MetricInfo,
  OriginPaisesData,
  SeriesData,
  SeriesInfo,
  StreetVutData,
} from "./types";
import rawRegistry from "../data/metrics.json";
import rawSeriesRegistry from "../data/series.json";
import rawIndicators from "../data/indicators.json";
import rawOrigins from "../data/origen_paises_barrio.json";
import rawStreetVut from "../data/street_vut.json";
import rawGeo from "../data/barrios.geojson?raw";

export const metricRegistry: MetricInfo[] = rawRegistry as MetricInfo[];

export const seriesRegistry: SeriesInfo[] = rawSeriesRegistry as SeriesInfo[];

export const indicators: IndicatorData[] = rawIndicators as unknown as IndicatorData[];

export const originPaises: OriginPaisesData = rawOrigins as OriginPaisesData;

export const streetVut: StreetVutData = rawStreetVut as StreetVutData;

export const barriosGeoJSON: BarriosGeoJSON = JSON.parse(
  rawGeo,
) as BarriosGeoJSON;

// Vite turns this glob into a map of lazy importers, one per metric file.
const metricLoaders = import.meta.glob<{ default: MetricData }>(
  "../data/metric_*.json",
);

/** Lazy-load a single metric's full data by id. */
export async function loadMetric(id: string): Promise<MetricData> {
  const key = `../data/metric_${id}.json`;
  const loader = metricLoaders[key];
  if (!loader) throw new Error(`Unknown metric: ${id}`);
  const module = await loader();
  return module.default;
}

const seriesLoaders = import.meta.glob<{ default: SeriesData }>(
  "../data/series_*.json",
);

/** Lazy-load a single time series' full data by id. */
export async function loadSeries(id: string): Promise<SeriesData> {
  const key = `../data/series_${id}.json`;
  const loader = seriesLoaders[key];
  if (!loader) throw new Error(`Unknown series: ${id}`);
  const module = await loader();
  return module.default;
}
