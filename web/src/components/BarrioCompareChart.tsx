import {
  CartesianGrid,
  Legend as RLegend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { BarriosGeoJSON, MetricData } from "../lib/types";

interface Props {
  geojson: BarriosGeoJSON;
  metric: MetricData;
  barrioIds: string[];
}

const LINE_COLORS = ["#1f77b4", "#d62728", "#2ca02c"];

/** Linked line chart comparing a few barrios across the metric's periods.
 * Annotates 2020 (COVID-19) when present, per the brief's Phase 2. */
export function BarrioCompareChart({ geojson, metric, barrioIds }: Props) {
  if (metric.periods.length <= 1 || barrioIds.length === 0) return null;

  const nameById = new Map(
    geojson.features.map((f) => [f.properties.barrio_id, f.properties.name]),
  );

  const data = metric.periods.map((period) => {
    const row: Record<string, string | number | null> = { period };
    for (const id of barrioIds) {
      row[nameById.get(id) ?? id] = metric.values[id]?.[period] ?? null;
    }
    return row;
  });

  return (
    <div className="compare-chart">
      <h3>Comparación de barrios — {metric.label}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="period" tick={{ fontSize: 11 }} minTickGap={24} />
          <YAxis tick={{ fontSize: 11 }} width={48} unit={metric.unit === "%" ? "%" : ""} />
          <Tooltip />
          <RLegend />
          {metric.periods.includes("2020") && (
            <ReferenceLine x="2020" stroke="#999" strokeDasharray="4 4" label={{ value: "COVID-19", fontSize: 10, fill: "#777" }} />
          )}
          {barrioIds.map((id, i) => (
            <Line
              key={id}
              type="monotone"
              dataKey={nameById.get(id) ?? id}
              stroke={LINE_COLORS[i % LINE_COLORS.length]}
              dot={false}
              strokeWidth={2}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
