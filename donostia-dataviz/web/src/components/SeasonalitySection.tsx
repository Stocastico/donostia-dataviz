import { useEffect, useState } from "react";
import { loadSeries, seriesRegistry } from "../lib/data";
import { SeasonalityHeatmap } from "./SeasonalityHeatmap";
import { AnnualTrendChart } from "./AnnualTrendChart";
import { PALETTES } from "../lib/colorScale";
import type { SeriesData } from "../lib/types";

// Per-series presentation: temperature is a mean in a warm ramp; precipitation
// is a sum in a cool (blue) ramp; counts default to a sum in the warm ramp.
function presentation(id: string, unit: string): {
  palette: keyof typeof PALETTES;
  mode: "mean" | "sum";
  trendColor: string;
} {
  if (id === "precip") return { palette: "cool", mode: "sum", trendColor: "#1f77b4" };
  if (unit === "°C") return { palette: "warm", mode: "mean", trendColor: "#d62728" };
  return { palette: "warm", mode: "sum", trendColor: "#d62728" };
}

/** "Stagionalità" section: a city-grain month × year heatmap. Hidden if no
 * series have been built yet. */
export function SeasonalitySection() {
  const available = seriesRegistry;
  // Default to temperature when present (shows the warming trend), else first.
  const defaultId =
    available.find((s) => s.id === "temp_avg")?.id ?? available[0]?.id ?? "";
  const [seriesId, setSeriesId] = useState(defaultId);
  const [series, setSeries] = useState<SeriesData | null>(null);

  useEffect(() => {
    if (!seriesId) return;
    let active = true;
    loadSeries(seriesId).then((s) => active && setSeries(s));
    return () => {
      active = false;
    };
  }, [seriesId]);

  if (available.length === 0) return null;

  return (
    <section className="seasonality">
      <div className="seasonality-head">
        <h2>Serie temporali — mese × anno</h2>
        {available.length > 1 && (
          <select value={seriesId} onChange={(e) => setSeriesId(e.target.value)}>
            {available.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        )}
      </div>
      {series ? (
        <>
          <p className="seasonality-sub">
            {series.label} — {series.years[0]}–{series.years[series.years.length - 1]}.
            Le colonne sono gli anni, le righe i mesi: i colori più intensi
            indicano i valori più alti. Rivela la stagionalità e la sua
            evoluzione nel tempo.
          </p>
          {(() => {
            const pres = presentation(series.id, series.unit);
            return (
              <>
                <SeasonalityHeatmap series={series} palette={pres.palette} />
                <AnnualTrendChart series={series} mode={pres.mode} color={pres.trendColor} />
              </>
            );
          })()}
          <p className="source-note">Fonte: {series.source}</p>
        </>
      ) : (
        <p className="seasonality-sub">Caricamento serie…</p>
      )}
    </section>
  );
}
