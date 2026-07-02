import { useMemo } from "react";
import type { ColorScale } from "../lib/colorScale";
import { formatDelta, formatValue } from "../lib/format";
import type { BarriosGeoJSON, MetricData } from "../lib/types";
import { BarrioMap } from "./BarrioMap";

interface Props {
  geojson: BarriosGeoJSON;
  metric: MetricData;
  period: string;
  scale: ColorScale;
}

/** Build a recolored copy of the geometry carrying the current value/delta/color. */
function decorate(geojson: BarriosGeoJSON, metric: MetricData, period: string, scale: ColorScale): BarriosGeoJSON {
  const pIdx = metric.periods.indexOf(period);
  const prev = pIdx > 0 ? metric.periods[pIdx - 1] : null;
  return {
    ...geojson,
    features: geojson.features.map((f) => {
      const id = f.properties.barrio_id;
      const value = metric.values[id]?.[period] ?? null;
      const prevValue = prev ? metric.values[id]?.[prev] ?? null : null;
      const isCategorical = metric.kind === "categorical";
      const valueLabel = isCategorical
        ? (value != null ? metric.categories?.[value] ?? "n/d" : "n/d")
        : formatValue(value, metric.unit);
      return {
        ...f,
        properties: {
          ...f.properties,
          __value: value,
          __valueLabel: valueLabel,
          // No period-over-period delta for categorical (or single-period) metrics.
          __deltaLabel: prev && !isCategorical ? formatDelta(value, prevValue) : "",
          __color: scale.color(value),
        },
      };
    }),
  } as BarriosGeoJSON;
}

/** Single-metric choropleth: decorates the geometry from one metric/period/scale
 * and renders it on the shared ``BarrioMap``. */
export function ChoroplethMap({ geojson, metric, period, scale }: Props) {
  const data = useMemo(
    () => decorate(geojson, metric, period, scale),
    [geojson, metric, period, scale],
  );
  return <BarrioMap data={data} />;
}
