import { useEffect, useMemo, useState } from "react";
import { barriosGeoJSON, loadMetric, metricRegistry } from "../lib/data";
import { buildColorScale } from "../lib/colorScale";
import type { MetricData, MetricInfo } from "../lib/types";
import { ChoroplethMap } from "./ChoroplethMap";
import { Legend } from "./Legend";
import { MetricPicker } from "./MetricPicker";

const TOURISM_IDS = ["airbnb_density", "vut_density", "vut_count"];
const RESIDENT_IDS = ["schools_per_1000", "population", "pct_youth_adults", "ageing_index", "noise_night_pct55"];
const DEFAULT_TOURISM = "airbnb_density";
const DEFAULT_RESIDENT = "schools_per_1000";

function usePanel(defaultId: string) {
  const [id, setId] = useState(defaultId);
  const [metric, setMetric] = useState<MetricData | null>(null);

  useEffect(() => {
    let active = true;
    loadMetric(id).then((m) => {
      if (active) setMetric(m);
    });
    return () => {
      active = false;
    };
  }, [id]);

  return { id, setId, metric };
}

/** Historia #5 ("la città turistica vs. la città vissuta") portata al dashboard
 * interattivo (VIZ-10): due mappe indipendenti affiancate — non una mappa
 * bivariata (VIZ-3), che fonde due assi in un'unica scala; qui ogni lato ha la
 * propria metrica e scala colore, per un confronto puramente geografico di
 * "dove sta cosa". */
export function TwoCitiesSection() {
  const tourismMetrics = useMemo(
    () => metricRegistry.filter((m) => TOURISM_IDS.includes(m.id) && m.status === "live"),
    [],
  );
  const residentMetrics = useMemo(
    () => metricRegistry.filter((m) => RESIDENT_IDS.includes(m.id) && m.status === "live"),
    [],
  );

  const left = usePanel(DEFAULT_TOURISM);
  const right = usePanel(DEFAULT_RESIDENT);

  if (tourismMetrics.length === 0 || residentMetrics.length === 0) return null;

  return (
    <section className="two-cities">
      <div className="scatter-head">
        <h2>La città turistica vs. la città vissuta</h2>
      </div>
      <p className="scatter-sub">
        Due Donostia sovrapposte ma <strong>geograficamente separate</strong>:
        l'alloggio turistico si concentra nel centro storico e a Gros, mentre i
        servizi e la popolazione residente si distribuiscono soprattutto in
        periferia. Le due mappe sono indipendenti — cambia la metrica in
        ciascun lato per esplorare.
      </p>
      <div className="two-cities-grid">
        <TwoCitiesPanel title="🧳 Città turistica" metrics={tourismMetrics} panel={left} />
        <TwoCitiesPanel title="🏠 Città vissuta" metrics={residentMetrics} panel={right} />
      </div>
      <p className="scatter-sub leadlag-caveat">
        ⚠️ Il rumore notturno (`noise_night_pct55`) è dominato dal traffico, non
        è un proxy di turismo — vedi la correzione in `NOTA-METODOLOGICA.md`
        (MET-5) e l'analisi in `intermedia/ANALISIS-SPRINT-A.md`.
      </p>
    </section>
  );
}

function TwoCitiesPanel({
  title,
  metrics,
  panel,
}: {
  title: string;
  metrics: MetricInfo[];
  panel: ReturnType<typeof usePanel>;
}) {
  const scale = useMemo(() => {
    if (!panel.metric) return null;
    const vals = Object.values(panel.metric.values).flatMap((byPeriod) =>
      Object.values(byPeriod),
    );
    return buildColorScale(vals, panel.metric.kind, "warm", panel.metric.categories);
  }, [panel.metric]);

  const period = panel.metric?.periods[panel.metric.periods.length - 1] ?? "";

  return (
    <div className="two-cities-panel">
      <h3>{title}</h3>
      <MetricPicker metrics={metrics} selectedId={panel.id} onSelect={panel.setId} />
      <div className="map-area two-cities-map">
        {panel.metric && scale ? (
          <>
            <ChoroplethMap geojson={barriosGeoJSON} metric={panel.metric} period={period} scale={scale} />
            <Legend scale={scale} unit={panel.metric.unit} />
          </>
        ) : (
          <div className="map-placeholder">Caricamento dati…</div>
        )}
      </div>
      {panel.metric && <p className="source-note">Fonte: {panel.metric.source}</p>}
    </div>
  );
}
