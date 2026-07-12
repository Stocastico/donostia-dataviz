import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { barriosGeoJSON, loadMetric, metricRegistry } from "../lib/data";
import { buildScatterPoints, pearson, valuesAtLatest } from "../lib/scatter";
import { formatCompact, formatValue } from "../lib/format";
import type { MetricData, MetricInfo } from "../lib/types";

const DEFAULT_X = "vut_density";
const DEFAULT_Y = "rent_eur_m2";

// Numeric per-barrio metrics only: a categorical metric's values are category
// indices, meaningless as scatter coordinates or in a Pearson correlation.
const barrioMetrics: MetricInfo[] = metricRegistry.filter(
  (m) => m.geoGrain === "barrio" && m.status === "live" && m.kind !== "categorical",
);

const namesById: Record<string, string> = Object.fromEntries(
  barriosGeoJSON.features.map((f) => [f.properties.barrio_id, f.properties.name]),
);

/** Scatter of barrios on two chosen metrics (latest period each), sized by
 * population, with the Pearson correlation — the brief's Phase 4. */
export function ScatterSection() {
  const [xId, setXId] = useState(DEFAULT_X);
  const [yId, setYId] = useState(DEFAULT_Y);
  const [x, setX] = useState<MetricData | null>(null);
  const [y, setY] = useState<MetricData | null>(null);
  const [pop, setPop] = useState<MetricData | null>(null);

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
  useEffect(() => {
    loadMetric("population").then(setPop).catch(() => setPop(null));
  }, []);

  const { points, r, xInfo, yInfo } = useMemo(() => {
    if (!x || !y) return { points: [], r: null, xInfo: null, yInfo: null };
    const sizeByBarrio = pop ? valuesAtLatest(pop) : {};
    const size: Record<string, number | undefined> = {};
    for (const [k, v] of Object.entries(sizeByBarrio)) size[k] = v ?? undefined;
    const pts = buildScatterPoints(x, y, namesById, size);
    return {
      points: pts,
      r: pearson(pts),
      xInfo: barrioMetrics.find((m) => m.id === xId) ?? null,
      yInfo: barrioMetrics.find((m) => m.id === yId) ?? null,
    };
  }, [x, y, pop, xId, yId]);

  const latestPeriod = (m: MetricData | null) =>
    m ? m.periods[m.periods.length - 1] : "";

  return (
    <section className="scatter">
      <div className="scatter-head">
        <h2>Correlaciones entre barrios</h2>
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
        Cada punto es un barrio (último año disponible: X {latestPeriod(x)}, Y{" "}
        {latestPeriod(y)}); el área es proporcional a la población.
        {r != null && (
          <>
            {" "}
            Correlación de Pearson <strong>r = {r.toFixed(2)}</strong>.
          </>
        )}
      </p>

      <ResponsiveContainer width="100%" height={420}>
        <ScatterChart margin={{ top: 16, right: 24, bottom: 36, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            type="number"
            dataKey="x"
            name={xInfo?.label}
            tick={{ fontSize: 11 }}
            tickFormatter={formatCompact}
            label={{ value: xInfo?.label, position: "bottom", fontSize: 12, offset: 12 }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name={yInfo?.label}
            tick={{ fontSize: 11 }}
            tickFormatter={formatCompact}
            width={56}
            label={{ value: yInfo?.label, angle: -90, position: "insideLeft", fontSize: 12 }}
          />
          <ZAxis type="number" dataKey="size" range={[60, 520]} name="población" />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const p = payload[0].payload as { name: string; x: number; y: number };
              return (
                <div className="scatter-tip">
                  <strong>{p.name}</strong>
                  <div>{xInfo?.label}: {formatValue(p.x, xInfo?.unit ?? "")}</div>
                  <div>{yInfo?.label}: {formatValue(p.y, yInfo?.unit ?? "")}</div>
                </div>
              );
            }}
          />
          <Scatter data={points} fill="#1f77b4" fillOpacity={0.65}>
            <LabelList dataKey="name" position="top" style={{ fontSize: 10, fill: "#444" }} />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <p className="source-note">
        Fuentes: {xInfo?.source}
        {yInfo && yInfo.source !== xInfo?.source ? ` · ${yInfo.source}` : ""}
      </p>
    </section>
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
