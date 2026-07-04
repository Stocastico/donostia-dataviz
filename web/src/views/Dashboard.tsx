import { useEffect, useMemo, useState } from "react";
import { ChoroplethMap } from "../components/ChoroplethMap";
import { Legend } from "../components/Legend";
import { MetricPicker } from "../components/MetricPicker";
import { SmallMultiples } from "../components/SmallMultiples";
import { TimeSlider } from "../components/TimeSlider";
import { BarrioCompareChart } from "../components/BarrioCompareChart";
import { SeasonalitySection } from "../components/SeasonalitySection";
import { ScatterSection } from "../components/ScatterSection";
import { BivariateSection } from "../components/BivariateSection";
import { TransformationSection } from "../components/TransformationSection";
import { TwoCitiesSection } from "../components/TwoCitiesSection";
import { TourismCompareSection } from "../components/TourismCompareSection";
import { StreetVutSection } from "../components/StreetVutSection";
import { LeadLagSection } from "../components/LeadLagSection";
import { HousingPressureSection } from "../components/HousingPressureSection";
import { MiceSection } from "../components/MiceSection";
import { IndicatorsSection } from "../components/IndicatorsSection";
import { MapDataTable } from "../components/MapDataTable";
import { barrioRows } from "../lib/mapTable";
import { BarrioOriginsSection } from "../components/BarrioOriginsSection";
import { ConfidenceCard } from "../components/ConfidenceCard";
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
  const [playing, setPlaying] = useState(false);

  // Load the selected metric; default the slider to its latest period.
  useEffect(() => {
    let active = true;
    setPlaying(false); // switching metric mid-animation would be jarring
    loadMetric(metricId).then((m) => {
      if (!active) return;
      setMetric(m);
      setPeriodIndex(Math.max(0, m.periods.length - 1));
    });
    return () => {
      active = false;
    };
  }, [metricId]);

  // "▶ Play" (VIZ-8): step through every period, looping back to the start.
  useEffect(() => {
    if (!playing || !metric || metric.periods.length <= 1) return;
    const periods = metric.periods;
    const id = setInterval(() => {
      setPeriodIndex((i) => (i + 1) % periods.length);
    }, 900);
    return () => clearInterval(id);
  }, [playing, metric]);

  const period = metric?.periods[periodIndex] ?? "";

  // Color scale is fixed over ALL periods, not just the one shown: otherwise the
  // per-year min/max would recolor a barrio whose value never changed (the legend
  // would shift under the slider). With a stable domain, color always means the
  // same value and only moves when the data does — so the slider shows real change.
  // (Categorical domains are period-independent anyway.)
  const scale = useMemo(() => {
    if (!metric) return null;
    const vals = Object.values(metric.values).flatMap((byPeriod) =>
      Object.values(byPeriod),
    );
    return buildColorScale(vals, metric.kind, "warm", metric.categories);
  }, [metric]);

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
          <TimeSlider
            periods={metric.periods}
            index={periodIndex}
            onChange={setPeriodIndex}
            playing={playing}
            onTogglePlay={() => setPlaying((p) => !p)}
          />
        )}
      </div>

      <div
        className="map-area"
        role="img"
        aria-label={
          metric
            ? `Mappa coropletica: ${metric.label}, ${period}. Dati completi nella tabella qui sotto.`
            : "Mappa in caricamento"
        }
      >
        {metric && scale ? (
          <>
            <ChoroplethMap geojson={barriosGeoJSON} metric={metric} period={period} scale={scale} />
            <Legend scale={scale} unit={metric.unit} />
          </>
        ) : (
          <div className="map-placeholder">Caricamento dati…</div>
        )}
      </div>

      {metric && (
        <MapDataTable
          rows={barrioRows(barriosGeoJSON, metric, period)}
          label={metric.label}
          period={period}
          unit={metric.unit}
        />
      )}

      {selectedInfo && (
        <div className="metric-meta">
          <p className="source-note">Fonte: {selectedInfo.source}</p>
          {selectedInfo.confidence && (
            <ConfidenceCard
              confidence={selectedInfo.confidence}
              assumptions={selectedInfo.assumptions}
            />
          )}
        </div>
      )}

      {metric && scale && (
        <SmallMultiples
          metric={metric}
          scale={scale}
          activeIndex={periodIndex}
          onSelect={(i) => {
            setPlaying(false);
            setPeriodIndex(i);
          }}
        />
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
      <TransformationSection />
      <TwoCitiesSection />
      <TourismCompareSection />
      <StreetVutSection />
      <LeadLagSection />
      <HousingPressureSection />
      <MiceSection />
      <IndicatorsSection />
      <BarrioOriginsSection />
    </div>
  );
}
