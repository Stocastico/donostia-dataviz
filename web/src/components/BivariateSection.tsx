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
import type { BarrioRow } from "../lib/mapTable";
import type { BarriosGeoJSON, MetricData, MetricInfo } from "../lib/types";
import { BarrioMap } from "./BarrioMap";
import { MapDataTable } from "./MapDataTable";

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

  useEffect(() => {
    let active = true;
    loadMetric(xId).then((m) => active && setX(m));
    return () => {
      active = false;
    };
  }, [xId]);
  useEffect(() => {
    let active = true;
    loadMetric(yId).then((m) => active && setY(m));
    return () => {
      active = false;
    };
  }, [yId]);

  const xInfo = barrioMetrics.find((m) => m.id === xId) ?? null;
  const yInfo = barrioMetrics.find((m) => m.id === yId) ?? null;

  const { data, mapped, rows } = useMemo<{
    data: BarriosGeoJSON;
    mapped: number;
    rows: BarrioRow[];
  }>(() => {
    if (!x || !y) return { data: barriosGeoJSON, mapped: 0, rows: [] };
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
    const rows: BarrioRow[] = [];
    const features = barriosGeoJSON.features.map((f) => {
      const id = f.properties.barrio_id;
      const xVal = xv[id];
      const yVal = yv[id];
      const both = xVal != null && yVal != null;
      let color = NO_DATA_COLOR;
      let valueLabel = "n/d";
      let plain = "n/d";
      if (both) {
        const xc = classify(xVal as number, xBreaks);
        const yc = classify(yVal as number, yBreaks);
        color = biColor(xc, yc);
        valueLabel =
          `${xInfo?.label}: ${formatValue(xVal as number, xUnit)} (${CLASS_LABELS[xc]})` +
          `<br/>${yInfo?.label}: ${formatValue(yVal as number, yUnit)} (${CLASS_LABELS[yc]})`;
        // Plain-text twin (no HTML) for the accessible mirror table.
        plain =
          `${formatValue(xVal as number, xUnit)} (${CLASS_LABELS[xc]}) · ` +
          `${formatValue(yVal as number, yUnit)} (${CLASS_LABELS[yc]})`;
      }
      rows.push({ id, name: f.properties.name, value: null, valueLabel: plain, deltaLabel: "" });
      return {
        ...f,
        properties: { ...f.properties, __color: color, __valueLabel: valueLabel, __deltaLabel: "" },
      };
    });
    rows.sort((a, b) => a.name.localeCompare(b.name, "es"));
    return { data: { ...barriosGeoJSON, features } as BarriosGeoJSON, mapped: joint.length, rows };
  }, [x, y, xInfo, yInfo]);

  return (
    <section className="bivariate">
      <div className="scatter-head">
        <h2>Mapa bivariado (3×3)</h2>
        <div className="scatter-axes">
          <label>
            <span className="control-label">Eje X</span>
            <AxisSelect value={xId} onChange={setXId} />
          </label>
          <label>
            <span className="control-label">Eje Y</span>
            <AxisSelect value={yId} onChange={setYId} />
          </label>
        </div>
      </div>

      <p className="scatter-sub">
        Cada barrio se clasifica en terciles (bajo/medio/alto) en cada eje
        (último año disponible); el color combina las dos clases. Los barrios
        "anómalos" — altos en un eje y bajos en el otro — destacan. {mapped} barrios
        con datos en ambos ejes.
      </p>

      <div className="bivariate-body">
        <div
          className="map-area"
          role="img"
          aria-label={`Mapa bivariado: ${xInfo?.label ?? "X"} × ${yInfo?.label ?? "Y"}, último año. Datos en la tabla de abajo.`}
        >
          <BarrioMap data={data} />
        </div>
        <BivariateLegend xLabel={xInfo?.label ?? "X"} yLabel={yInfo?.label ?? "Y"} />
      </div>
      <MapDataTable
        rows={rows}
        label={`${xInfo?.label ?? "X"} × ${yInfo?.label ?? "Y"}`}
        period="último año"
      />

      <p className="source-note">
        Fuentes: {xInfo?.source}
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
