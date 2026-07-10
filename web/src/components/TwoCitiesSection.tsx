import { useEffect, useMemo, useState } from "react";
import { barriosGeoJSON, loadMetric, metricRegistry } from "../lib/data";
import { buildColorScale } from "../lib/colorScale";
import type { MetricData, MetricInfo } from "../lib/types";
import { ChoroplethMap } from "./ChoroplethMap";
import { Legend } from "./Legend";
import { MapDataTable } from "./MapDataTable";
import { barrioRows } from "../lib/mapTable";
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
        <h2>La ciudad turística vs. la ciudad vivida</h2>
      </div>
      <p className="scatter-sub">
        Dos Donostia superpuestas pero <strong>geográficamente separadas</strong>:
        el alojamiento turístico se concentra en el casco viejo y en Gros, mientras
        que los servicios y la población residente se distribuyen sobre todo en la
        periferia. Los dos mapas son independientes — cambia la métrica en
        cada lado para explorar.
      </p>
      <div className="two-cities-grid">
        <TwoCitiesPanel title="🧳 Ciudad turística" metrics={tourismMetrics} panel={left} />
        <TwoCitiesPanel title="🏠 Ciudad vivida" metrics={residentMetrics} panel={right} />
      </div>
      <p className="scatter-sub leadlag-caveat">
        ⚠️ El ruido nocturno (`noise_night_pct55`) está dominado por el tráfico, no
        es un proxy de turismo — ver la corrección en `NOTA-METODOLOGICA.md`
        (MET-5) y el análisis en `intermedia/ANALISIS-SPRINT-A.md`.
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
      <div
        className="map-area two-cities-map"
        role="img"
        aria-label={
          panel.metric
            ? `Mapa coroplético: ${panel.metric.label}, ${period}. Datos en la tabla de abajo.`
            : "Mapa cargando"
        }
      >
        {panel.metric && scale ? (
          <>
            <ChoroplethMap geojson={barriosGeoJSON} metric={panel.metric} period={period} scale={scale} />
            <Legend scale={scale} unit={panel.metric.unit} />
          </>
        ) : (
          <div className="map-placeholder">Cargando datos…</div>
        )}
      </div>
      {panel.metric && (
        <MapDataTable
          rows={barrioRows(barriosGeoJSON, panel.metric, period)}
          label={panel.metric.label}
          period={period}
          unit={panel.metric.unit}
        />
      )}
      {panel.metric && <p className="source-note">Fuente: {panel.metric.source}</p>}
    </div>
  );
}
