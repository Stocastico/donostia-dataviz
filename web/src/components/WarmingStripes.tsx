import { buildColorScale } from "../lib/colorScale";
import { temperatureAnomalies, isPartialYear } from "../lib/series";
import { formatValue } from "../lib/format";
import type { SeriesData } from "../lib/types";

/** Ed Hawkins "warming stripes": one bar per year coloured by its temperature
 * anomaly vs the series mean (blue = cooler, red = warmer). The drift from blue
 * to red over time is the warming. */
export function WarmingStripes({ series }: { series: SeriesData }) {
  const data = temperatureAnomalies(series);
  if (data.length < 2) return null;
  const scale = buildColorScale(data.map((d) => d.anomaly), "diverging");
  const lastYear = data[data.length - 1].year;
  const partial = isPartialYear(series, lastYear);

  return (
    <div className="stripes-chart">
      <h3>Warming stripes — anomalía anual</h3>
      <p className="trend-caption">
        Una barra por año, color = desviación respecto a la media del periodo
        (<span style={{ color: "#3b6fb0" }}>azul</span> = más frío,{" "}
        <span style={{ color: "#b30000" }}>rojo</span> = más cálido). El
        desplazamiento hacia el rojo en las últimas décadas es el calentamiento.
        {partial && ` La última barra (${lastYear}) es un año parcial (en curso), aún no comparable con un año completo.`}
      </p>
      <div className="stripes" role="img" aria-label="Warming stripes">
        {data.map((d) => (
          <div
            key={d.year}
            className={`stripe ${d.year === lastYear && partial ? "stripe-partial" : ""}`}
            style={{ backgroundColor: scale.color(d.anomaly) }}
            title={`${d.year}${d.year === lastYear && partial ? " (parcial)" : ""}: ${formatValue(d.value, series.unit)} (${d.anomaly >= 0 ? "+" : ""}${d.anomaly} ${series.unit})`}
          />
        ))}
      </div>
      <div className="stripes-ends">
        <span>{data[0].year}</span>
        <span>{data[data.length - 1].year}</span>
      </div>
    </div>
  );
}
