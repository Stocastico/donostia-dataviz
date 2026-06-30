import { useEffect, useMemo, useState } from "react";
import { ChoroplethMap } from "../components/ChoroplethMap";
import { Legend } from "../components/Legend";
import { MetricPicker } from "../components/MetricPicker";
import { TimeSlider } from "../components/TimeSlider";
import { BarrioCompareChart } from "../components/BarrioCompareChart";
import { SeasonalitySection } from "../components/SeasonalitySection";
import { ScatterSection } from "../components/ScatterSection";
import { BivariateSection } from "../components/BivariateSection";
import { MiceSection } from "../components/MiceSection";
import { IndicatorsSection } from "../components/IndicatorsSection";
import { buildColorScale } from "../lib/colorScale";
import { barriosGeoJSON, loadMetric, metricRegistry } from "../lib/data";
import type { MetricData } from "../lib/types";

const DEFAULT_METRIC = "vut_count";
const MAX_COMPARE = 3;
const DEFAULT_COMPARE = ["erdialdea", "gros", "amaraberri"];

export function Dashboard() {
  const [metricId, setMetricId] = useState(DEFAULT_METRIC);
  const [metric, setMetric] = useState<MetricData | null>(null);
  const [periodIndex, setPeriodIndex] = useState(0);
  const [compare, setCompare] = useState<string[]>(DEFAULT_COMPARE);

  // Load the selected metric; default the slider to its latest period.
  useEffect(() => {
    let active = true;
    loadMetric(metricId).then((m) => {
      if (!active) return;
      setMetric(m);
      setPeriodIndex(Math.max(0, m.periods.length - 1));
    });
    return () => {
      active = false;
    };
  }, [metricId]);

  const period = metric?.periods[periodIndex] ?? "";

  // Color scale is rebuilt from the values of the currently shown period.
  const scale = useMemo(() => {
    if (!metric) return null;
    const vals = Object.values(metric.values).map((byPeriod) => byPeriod[period]);
    return buildColorScale(vals, metric.kind, "warm", metric.categories);
  }, [metric, period]);

  const toggleBarrio = (id: string) =>
    setCompare((cur) =>
      cur.includes(id)
        ? cur.filter((x) => x !== id)
        : cur.length < MAX_COMPARE
          ? [...cur, id]
          : cur,
    );

  const selectedInfo = metricRegistry.find((m) => m.id === metricId);

  return (
    <div className="dashboard">
      <header className="app-header">
        <h1>Donostia Dataviz</h1>
        <p>L'evoluzione di Donostia / San Sebastián per barrio.</p>
      </header>

      <div className="controls">
        <MetricPicker metrics={metricRegistry} selectedId={metricId} onSelect={setMetricId} />
        {metric && (
          <TimeSlider periods={metric.periods} index={periodIndex} onChange={setPeriodIndex} />
        )}
      </div>

      <div className="map-area">
        {metric && scale ? (
          <>
            <ChoroplethMap geojson={barriosGeoJSON} metric={metric} period={period} scale={scale} />
            <Legend scale={scale} unit={metric.unit} />
          </>
        ) : (
          <div className="map-placeholder">Caricamento dati…</div>
        )}
      </div>

      {selectedInfo && (
        <p className="source-note">Fonte: {selectedInfo.source}</p>
      )}

      {metric && metric.periods.length > 1 && (
        <section className="compare-area">
          <div className="barrio-select">
            <span className="control-label">Confronta barrios (max {MAX_COMPARE})</span>
            <div className="barrio-chips">
              {barriosGeoJSON.features.map((f) => {
                const id = f.properties.barrio_id;
                const on = compare.includes(id);
                return (
                  <button
                    key={id}
                    className={`chip ${on ? "on" : ""}`}
                    onClick={() => toggleBarrio(id)}
                    disabled={!on && compare.length >= MAX_COMPARE}
                  >
                    {f.properties.name}
                  </button>
                );
              })}
            </div>
          </div>
          <BarrioCompareChart geojson={barriosGeoJSON} metric={metric} barrioIds={compare} />
        </section>
      )}

      <SeasonalitySection />
      <ScatterSection />
      <BivariateSection />
      <MiceSection />
      <IndicatorsSection />
    </div>
  );
}
