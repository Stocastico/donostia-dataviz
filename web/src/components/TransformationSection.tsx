import { useEffect, useMemo, useState, type ReactNode } from "react";
import { ChoroplethMap } from "./ChoroplethMap";
import { Legend } from "./Legend";
import { ConfidenceCard } from "./ConfidenceCard";
import { MapDataTable } from "./MapDataTable";
import { barrioRows } from "../lib/mapTable";
import { buildColorScale } from "../lib/colorScale";
import { barriosGeoJSON, loadMetric, metricRegistry } from "../lib/data";
import type { MetricData } from "../lib/types";

// Selectable component layers for the third map (the "components in plain sight"
// idea of the index): the two socioeconomic local-excess drivers + the two
// tourism-intensity layers.
const COMPONENT_OPTIONS = [
  "transform_univ_excess",
  "transform_rent_excess",
  "vut_density",
  "airbnb_density",
];

function useMetric(id: string): MetricData | null {
  const [metric, setMetric] = useState<MetricData | null>(null);
  useEffect(() => {
    let active = true;
    setMetric(null);
    loadMetric(id).then((m) => active && setMetric(m));
    return () => {
      active = false;
    };
  }, [id]);
  return metric;
}

/** One map of the VIZ-6 dashboard: a small choropleth + legend + confidence card,
 * driven by a single metric id (latest period). */
function MapCard({ metricId, title }: { metricId: string; title: ReactNode }) {
  const metric = useMetric(metricId);
  const info = metricRegistry.find((m) => m.id === metricId);
  const period = metric ? metric.periods[metric.periods.length - 1] : "";

  const scale = useMemo(() => {
    if (!metric) return null;
    const vals = Object.values(metric.values).map((byPeriod) => byPeriod[period]);
    return buildColorScale(vals, metric.kind, "warm", metric.categories);
  }, [metric, period]);

  return (
    <div className="transform-card">
      <h3>{title}</h3>
      {metric && scale ? (
        <div
          className="map-area"
          role="img"
          aria-label={`Mappa coropletica: ${metric.label}, ${period}. Dati nella tabella qui sotto.`}
        >
          <ChoroplethMap geojson={barriosGeoJSON} metric={metric} period={period} scale={scale} />
          <Legend scale={scale} unit={metric.unit} />
        </div>
      ) : (
        <div className="map-placeholder">Caricamento…</div>
      )}
      {metric && (
        <MapDataTable
          rows={barrioRows(barriosGeoJSON, metric, period)}
          label={metric.label}
          period={period}
          unit={metric.unit}
        />
      )}
      {info?.confidence && (
        <ConfidenceCard confidence={info.confidence} assumptions={info.assumptions} />
      )}
    </div>
  );
}

/** VIZ-6 — Urban Transformation Index dashboard: three parallel maps of the same
 * multi-definition index (socioeconomic class, tourism pressure, a selectable
 * component), with the components in plain sight. Never labelled "gentrification"
 * (project decision): it measures observable transformation, not displacement. */
export function TransformationSection() {
  const [component, setComponent] = useState(COMPONENT_OPTIONS[0]);
  const compInfo = metricRegistry.find((m) => m.id === component);
  const classInfo = metricRegistry.find((m) => m.id === "transform_class");

  // Render nothing if the index metrics aren't in the build yet.
  if (!classInfo) return null;

  return (
    <section className="transformation">
      <div className="scatter-head">
        <h2>Donostia in trasformazione (Indice AN-8)</h2>
      </div>

      <p className="scatter-sub">
        Tre mappe affiancate dello stesso indice multi-definizione, con i componenti
        a vista. <strong>Trasformazione, non «gentrificazione»</strong>: con i dati
        disponibili non si può dimostrare la sostituzione dei residenti (MET-2). Il
        dato chiave è che le due trasformazioni <strong>non coincidono</strong>: il
        turismo si concentra nel centro benestante (Erdialdea, Gros), il cambiamento
        sociale nella periferia interna suscettibile (Loiola, Egia).
      </p>

      <div className="transform-grid">
        <MapCard
          metricId="transform_class"
          title="1 · Trasformazione socioeconomica (classe)"
        />
        <MapCard
          metricId="transform_tourism_score"
          title="2 · Pressione turistica (livelli)"
        />
        <MapCard
          metricId={component}
          title={
            <>
              <span>3 · Componente</span>
              <select
                className="transform-select"
                value={component}
                onChange={(e) => setComponent(e.target.value)}
              >
                {COMPONENT_OPTIONS.map((id) => {
                  const info = metricRegistry.find((m) => m.id === id);
                  return (
                    <option key={id} value={id}>
                      {info?.label ?? id}
                    </option>
                  );
                })}
              </select>
            </>
          }
        />
      </div>

      <p className="source-note">
        Fonti: {classInfo.source}
        {compInfo && compInfo.source !== classInfo.source ? ` · ${compInfo.source}` : ""}
      </p>
    </section>
  );
}
