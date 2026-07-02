import { useEffect, useMemo, useState } from "react";
import { barriosGeoJSON, loadMetric, metricRegistry } from "../lib/data";
import { valuesAtLatest } from "../lib/scatter";
import {
  BIVARIATE_PALETTE,
  CLASS_LABELS,
  biColor,
  classify,
  terciles,
  type BiClass,
} from "../lib/bivariate";
import { NO_DATA_COLOR } from "../lib/colorScale";
import { formatValue } from "../lib/format";
import type { BarriosGeoJSON, MetricData, MetricInfo } from "../lib/types";
import { BarrioMap } from "./BarrioMap";

const DEFAULT_X = "income_total";
const DEFAULT_Y = "housing_tension";

// Numeric per-barrio metrics only (a categorical metric has no terciles).
const barrioMetrics: MetricInfo[] = metricRegistry.filter(
  (m) => m.geoGrain === "barrio" && m.status === "live" && m.kind !== "categorical",
);

/** Bivariate 3×3 choropleth (VIZ-3): cross two metrics into low/mid/high classes
 * per axis and color barrios by the blended class, surfacing the "anomalous"
 * barrios (e.g. low income × high housing tension) that a single map hides. */
export function BivariateSection() {
  const [xId, setXId] = useState(DEFAULT_X);
  const [yId, setYId] = useState(DEFAULT_Y);
  const [x, setX] = useState<MetricData | null>(null);
  const [y, setY] = useState<MetricData | null>(null);

  useEffect(() => { loadMetric(xId).then(setX); }, [xId]);
  useEffect(() => { loadMetric(yId).then(setY); }, [yId]);

  const xInfo = barrioMetrics.find((m) => m.id === xId) ?? null;
  const yInfo = barrioMetrics.find((m) => m.id === yId) ?? null;

  const { data, mapped } = useMemo<{ data: BarriosGeoJSON; mapped: number }>(() => {
    if (!x || !y) return { data: barriosGeoJSON, mapped: 0 };
    const xv = valuesAtLatest(x);
    const yv = valuesAtLatest(y);
    // Joint sample: barrios with a value on both axes → terciles over those.
    const joint = barriosGeoJSON.features
      .map((f) => f.properties.barrio_id)
      .filter((id) => xv[id] != null && yv[id] != null);
    const xBreaks = terciles(joint.map((id) => xv[id] as number));
    const yBreaks = terciles(joint.map((id) => yv[id] as number));

    const xUnit = xInfo?.unit ?? "";
    const yUnit = yInfo?.unit ?? "";
    const features = barriosGeoJSON.features.map((f) => {
      const id = f.properties.barrio_id;
      const xVal = xv[id];
      const yVal = yv[id];
      const both = xVal != null && yVal != null;
      let color = NO_DATA_COLOR;
      let valueLabel = "n/d";
      if (both) {
        const xc = classify(xVal as number, xBreaks);
        const yc = classify(yVal as number, yBreaks);
        color = biColor(xc, yc);
        valueLabel =
          `${xInfo?.label}: ${formatValue(xVal as number, xUnit)} (${CLASS_LABELS[xc]})` +
          `<br/>${yInfo?.label}: ${formatValue(yVal as number, yUnit)} (${CLASS_LABELS[yc]})`;
      }
      return {
        ...f,
        properties: { ...f.properties, __color: color, __valueLabel: valueLabel, __deltaLabel: "" },
      };
    });
    return { data: { ...barriosGeoJSON, features } as BarriosGeoJSON, mapped: joint.length };
  }, [x, y, xInfo, yInfo]);

  return (
    <section className="bivariate">
      <div className="scatter-head">
        <h2>Mappa bivariata (3×3)</h2>
        <div className="scatter-axes">
          <label>
            <span className="control-label">Asse X</span>
            <AxisSelect value={xId} onChange={setXId} />
          </label>
          <label>
            <span className="control-label">Asse Y</span>
            <AxisSelect value={yId} onChange={setYId} />
          </label>
        </div>
      </div>

      <p className="scatter-sub">
        Ogni barrio è classificato in terzili (basso/medio/alto) su ciascun asse
        (ultimo anno disponibile); il colore combina le due classi. I barrios
        "anomali" — alti su un asse e bassi sull'altro — spiccano. {mapped} barrios
        con dati su entrambi gli assi.
      </p>

      <div className="bivariate-body">
        <div className="map-area">
          <BarrioMap data={data} />
        </div>
        <BivariateLegend xLabel={xInfo?.label ?? "X"} yLabel={yInfo?.label ?? "Y"} />
      </div>

      <p className="source-note">
        Fonti: {xInfo?.source}
        {yInfo && yInfo.source !== xInfo?.source ? ` · ${yInfo.source}` : ""}
      </p>
    </section>
  );
}

/** 3×3 color key with axis arrows (→ more X, ↑ more Y). */
function BivariateLegend({ xLabel, yLabel }: { xLabel: string; yLabel: string }) {
  return (
    <div className="bivariate-legend">
      <span className="bivariate-ylabel">{yLabel} →</span>
      <div className="bivariate-grid">
        {/* render y high (top) to y low (bottom) so up = more */}
        {([2, 1, 0] as BiClass[]).map((yc) =>
          ([0, 1, 2] as BiClass[]).map((xc) => (
            <span
              key={`${xc}-${yc}`}
              className="bivariate-cell"
              style={{ background: BIVARIATE_PALETTE[yc][xc] }}
              title={`X ${CLASS_LABELS[xc]} · Y ${CLASS_LABELS[yc]}`}
            />
          )),
        )}
      </div>
      <span className="bivariate-xlabel">{xLabel} →</span>
    </div>
  );
}

function AxisSelect({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      {barrioMetrics.map((m) => (
        <option key={m.id} value={m.id}>
          {m.label}
        </option>
      ))}
    </select>
  );
}
