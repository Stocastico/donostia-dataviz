import {
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { annualAggregate, isPartialYear } from "../lib/series";
import { linearRegression } from "../lib/stats";
import { formatCompact } from "../lib/format";
import type { SeriesData } from "../lib/types";

interface Props {
  series: SeriesData;
  /** "mean" for temperature, "sum" for precipitation / counts. */
  mode: "mean" | "sum";
  color: string;
}

const DEC = new Intl.NumberFormat("es-ES", { maximumFractionDigits: 2 });

/** Annual aggregate line + OLS linear-regression trend, with the per-decade
 * slope — the brief's "temperatura media annuale con trend (regressione)". */
export function AnnualTrendChart({ series, mode, color }: Props) {
  const agg = annualAggregate(series, mode);
  if (agg.length < 2) return null;

  // A year still in progress (e.g. the current one, only its first few months
  // published) isn't comparable to a full year for mode="mean" — including it
  // in the regression would skew the fitted trend. Still plot its point (it's
  // real data), just leave it out of the fit itself.
  const lastYear = agg[agg.length - 1].year;
  const partial = isPartialYear(series, lastYear);
  const fitRows = partial ? agg.slice(0, -1) : agg;
  const fit = linearRegression(fitRows.map((d) => ({ x: Number(d.year), y: d.value })));
  const data = agg.map((d) => ({
    year: d.year,
    value: Math.round(d.value * 100) / 100,
    trend: fit ? Math.round((fit.intercept + fit.slope * Number(d.year)) * 100) / 100 : null,
  }));

  const perDecade = fit ? fit.slope * 10 : null;
  const sign = perDecade != null && perDecade >= 0 ? "+" : "−";
  const aggLabel = mode === "mean" ? "media anual" : "total anual";

  return (
    <div className="trend-chart">
      <h3>{mode === "mean" ? "Media anual y tendencia" : "Total anual y tendencia"}</h3>
      {fit && perDecade != null && (
        <p className="trend-caption">
          Tendencia lineal: <strong>{sign}{DEC.format(Math.abs(perDecade))} {series.unit}/década</strong>{" "}
          (R² = {DEC.format(fit.r2)}).
          {partial && ` El ${lastYear} es parcial (en curso) y no se incluye en el cálculo de la tendencia.`}
        </p>
      )}
      <ResponsiveContainer width="100%" height={240}>
        <ComposedChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="year" tick={{ fontSize: 11 }} minTickGap={28} />
          <YAxis
            tick={{ fontSize: 11 }}
            width={48}
            domain={["auto", "auto"]}
            tickFormatter={formatCompact}
          />
          <Tooltip
            formatter={(v: number, name) => [
              `${DEC.format(v)} ${series.unit}`,
              name === "trend" ? "tendencia" : aggLabel,
            ]}
          />
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} name={aggLabel} />
          <Line type="monotone" dataKey="trend" stroke="#666" strokeWidth={1.5} strokeDasharray="6 4" dot={false} name="tendencia" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
