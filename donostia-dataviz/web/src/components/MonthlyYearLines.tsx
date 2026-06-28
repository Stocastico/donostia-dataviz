import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { interpolateYlOrRd } from "d3-scale-chromatic";
import { monthlyYearRows } from "../lib/series";
import { formatCompact, formatValue } from "../lib/format";
import type { SeriesData } from "../lib/types";

const RECENT = 10; // how many trailing years get the warm gradient

/** "Monthly cycles" overlay: one line per year (x = month). Past years in grey,
 * the last RECENT years on a warm gradient, the latest year bold red — so the
 * eye sees recent years sitting higher (warmer) than the historical envelope. */
export function MonthlyYearLines({ series }: { series: SeriesData }) {
  const rows = monthlyYearRows(series);
  const years = series.years;
  const n = years.length;
  const last = years[n - 1];

  const style = (year: string, i: number) => {
    if (year === last) return { stroke: "#b30000", width: 3, opacity: 1 };
    if (i >= n - RECENT) {
      const t = (i - (n - RECENT)) / Math.max(1, RECENT - 1);
      return { stroke: interpolateYlOrRd(0.35 + 0.5 * t), width: 1.4, opacity: 0.9 };
    }
    return { stroke: "#d6d6d6", width: 1, opacity: 0.6 };
  };

  return (
    <div className="cycles-chart">
      <h3>Cicli mensili per anno</h3>
      <p className="trend-caption">
        Ogni linea è un anno: in <span style={{ color: "#bbb" }}>grigio</span> il
        passato, sui toni caldi gli ultimi {RECENT} anni, in{" "}
        <strong style={{ color: "#b30000" }}>rosso</strong> il {last}. Più le linee
        recenti stanno in alto, più gli anni recenti sono caldi.
      </p>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={rows} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="month" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} width={44} tickFormatter={formatCompact} />
          <Tooltip
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null;
              const lastVal = payload.find((p) => p.dataKey === last)?.value as number | undefined;
              const nums = payload
                .map((p) => p.value)
                .filter((v): v is number => typeof v === "number");
              const min = nums.length ? Math.min(...nums) : null;
              const max = nums.length ? Math.max(...nums) : null;
              return (
                <div className="scatter-tip">
                  <strong>{label}</strong>
                  <div>{last}: {formatValue(lastVal, series.unit)}</div>
                  <div style={{ color: "#888" }}>
                    storico: {formatValue(min, series.unit)} – {formatValue(max, series.unit)}
                  </div>
                </div>
              );
            }}
          />
          {years.map((year, i) => {
            const s = style(year, i);
            return (
              <Line
                key={year}
                dataKey={year}
                type="monotone"
                stroke={s.stroke}
                strokeWidth={s.width}
                strokeOpacity={s.opacity}
                dot={false}
                isAnimationActive={false}
                connectNulls
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
