import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { loadMetric, metricRegistry } from "../lib/data";
import { bestLag, leadLag } from "../lib/leadLag";
import type { MetricData } from "../lib/types";

const ACTIVITY = "airbnb_activity";
const RENT = "rent_eur_m2";
const LAGS = [-1, 0, 1, 2];

function lagLabel(lag: number): string {
  if (lag === 0) return "0 (mismo año)";
  return lag > 0 ? `+${lag} (turismo antes)` : `${lag} (alquiler antes)`;
}

/** AN-6 — lead/lag turismo→alquiler: ¿la presión turística precede a la subida del
 * alquiler? Panel de barrios en primeras diferencias (quita la tendencia común),
 * correlación a varios desfases. Exploratorio (datos anuales, proxy de reseñas). */
export function LeadLagSection() {
  const [activity, setActivity] = useState<MetricData | null>(null);
  const [rent, setRent] = useState<MetricData | null>(null);

  useEffect(() => {
    loadMetric(ACTIVITY).then(setActivity).catch(() => setActivity(null));
    loadMetric(RENT).then(setRent).catch(() => setRent(null));
  }, []);

  const points = useMemo(
    () => (activity && rent ? leadLag(activity, rent, LAGS) : []),
    [activity, rent],
  );
  const best = useMemo(() => bestLag(points), [points]);

  // Hidden until the Airbnb activity panel (REC-4) is in the build.
  if (!metricRegistry.some((m) => m.id === ACTIVITY)) return null;

  const data = points.map((p) => ({
    lag: p.lag,
    label: lagLabel(p.lag),
    r: Number.isFinite(p.r) ? Number(p.r.toFixed(3)) : 0,
  }));
  const n = points.find((p) => Number.isFinite(p.r))?.n ?? 0;

  return (
    <section className="leadlag">
      <div className="scatter-head">
        <h2>Turismo → alquiler: ¿quién precede a quién? (AN-6)</h2>
      </div>

      <p className="scatter-sub">
        Correlación de panel sobre los {" "}
        <strong>cambios interanuales</strong> (primeras diferencias, que quitan la
        tendencia común al alza) entre la actividad Airbnb y el alquiler, a distintos
        desfases. Un pico a la derecha (desfase positivo) indicaría que la
        presión turística <strong>precede</strong> a la subida del alquiler.
        {best && Number.isFinite(best.r) && (
          <>
            {" "}
            El máximo está en <strong>{lagLabel(best.lag)}</strong>, r ={" "}
            <strong>{best.r.toFixed(2)}</strong> (n = {n}) — pero la señal{" "}
            <strong>no sobrevive</strong> al control por los shocks comunes de
            ciudad (AN-16): con efectos fijos de año r baja a ≈0,10
            (p permutación ≈0,30).
          </>
        )}
      </p>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 16, right: 24, bottom: 28, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11 }}
            label={{ value: "desfase (años)", position: "bottom", fontSize: 12, offset: 12 }}
          />
          <YAxis
            type="number"
            domain={[-0.4, 0.4]}
            tick={{ fontSize: 11 }}
            label={{ value: "r (panel, Δ)", angle: -90, position: "insideLeft", fontSize: 12 }}
          />
          <ReferenceLine y={0} stroke="#999" />
          <Tooltip
            cursor={{ fill: "rgba(0,0,0,0.04)" }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const p = payload[0].payload as { label: string; r: number };
              return (
                <div className="scatter-tip">
                  <strong>{p.label}</strong>
                  <div>r = {p.r.toFixed(3)}</div>
                </div>
              );
            }}
          />
          <Bar dataKey="r" radius={[3, 3, 0, 0]}>
            {data.map((d) => (
              <Cell
                key={d.lag}
                fill={best && d.lag === best.lag ? "#d62728" : "#9ecae1"}
              />
            ))}
            <LabelList dataKey="r" position="top" style={{ fontSize: 11, fill: "#444" }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <p className="scatter-sub leadlag-caveat">
        ⚠️ <strong>Exploratorio</strong> (MET-3): correlación ≠ causalidad. El alquiler
        es anual (pocos puntos) y las reseñas son un <em>proxy</em> de la ocupación
        que crece también con la plataforma — por eso se leen las diferencias,
        no los niveles. El <strong>blindaje AN-16</strong> (estacionariedad + efectos
        fijos de año + permutación) muestra que gran parte del r(+1)=0,27 era
        covariación macro común: queda una pregunta abierta, no un indicio.
        Reproducible en <code>analysis/lead_lag.py</code> ·{" "}
        <code>analysis/lead_lag_robustness.py</code> · <code>docs/ANALISIS-LEADLAG.md</code>.
      </p>
    </section>
  );
}
