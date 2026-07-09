import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { indicatorBarData, latestPoint } from "../lib/indicators";
import { formatCompact, formatValue } from "../lib/format";
import type { IndicatorData } from "../lib/types";

const THEME_COLOR: Record<string, string> = {
  environment: "#2ca02c",
  tourism: "#d62728",
  security: "#7c4dff",
};

/** Generic annual-indicator line chart (year → value), with a latest-value
 * callout. Reusable for any city indicator (recycling rate, taxes, …). */
export function IndicatorTrendChart({ indicator }: { indicator: IndicatorData }) {
  const data = indicatorBarData(indicator);
  const latest = latestPoint(indicator);
  const color = THEME_COLOR[indicator.theme] ?? "#1f77b4";

  return (
    <div className="indicator-chart">
      <div className="indicator-head">
        <h3>{indicator.label}</h3>
        {latest && (
          <span className="indicator-latest">
            {latest.year}: <strong>{formatValue(latest.value, indicator.unit)}</strong>
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="year" tick={{ fontSize: 11 }} minTickGap={24} />
          <YAxis tick={{ fontSize: 11 }} width={44} tickFormatter={formatCompact} />
          <Tooltip
            formatter={(v: number) => [formatValue(v, indicator.unit), indicator.label]}
          />
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
      <p className="source-note">Fonte: {indicator.source}</p>
    </div>
  );
}
