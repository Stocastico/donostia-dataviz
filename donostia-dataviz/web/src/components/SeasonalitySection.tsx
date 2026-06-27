import { useEffect, useState } from "react";
import { loadSeries, seriesRegistry } from "../lib/data";
import { SeasonalityHeatmap } from "./SeasonalityHeatmap";
import type { SeriesData } from "../lib/types";

/** "Stagionalità" section: a city-grain month × year heatmap. Hidden if no
 * series have been built yet. */
export function SeasonalitySection() {
  const available = seriesRegistry;
  const [seriesId, setSeriesId] = useState(available[0]?.id ?? "");
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
        <h2>Stagionalità turistica</h2>
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
            Le colonne sono gli anni, le righe i mesi: l'estate in alto a colori
            caldi, la bassa stagione più chiara.
          </p>
          <SeasonalityHeatmap series={series} />
          <p className="source-note">Fonte: {series.source}</p>
        </>
      ) : (
        <p className="seasonality-sub">Caricamento serie…</p>
      )}
    </section>
  );
}
