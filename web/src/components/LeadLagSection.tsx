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
  if (lag === 0) return "0 (stesso anno)";
  return lag > 0 ? `+${lag} (turismo prima)` : `${lag} (affitto prima)`;
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
        <h2>Turismo → affitto: chi precede chi? (AN-6)</h2>
      </div>

      <p className="scatter-sub">
        Correlazione di panel sui {" "}
        <strong>cambiamenti interanuali</strong> (prime differenze, che tolgono la
        tendenza comune al rialzo) tra l'attività Airbnb e l'affitto, a diversi
        sfasamenti. Un picco a destra (sfasamento positivo) indicherebbe che la
        pressione turistica <strong>precede</strong> l'aumento dell'affitto.
        {best && Number.isFinite(best.r) && (
          <>
            {" "}
            Il massimo è a <strong>{lagLabel(best.lag)}</strong>, r ={" "}
            <strong>{best.r.toFixed(2)}</strong> (n = {n}) — ma il segnale{" "}
            <strong>non sopravvive</strong> al controllo per gli shock comuni di
            città (AN-16): con effetti fissi di anno r scende a ≈0,10
            (p permutazione ≈0,30).
          </>
        )}
      </p>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 16, right: 24, bottom: 28, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11 }}
            label={{ value: "sfasamento (anni)", position: "bottom", fontSize: 12, offset: 12 }}
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
        ⚠️ <strong>Esplorativo</strong> (MET-3): correlazione ≠ causalità. L'affitto
        è annuale (pochi punti) e le recensioni sono un <em>proxy</em> dell'occupazione
        che cresce anche con la piattaforma — per questo si leggono le differenze,
        non i livelli. Il <strong>blindaggio AN-16</strong> (stazionarietà + effetti
        fissi di anno + permutazione) mostra che gran parte del r(+1)=0,27 era
        covariazione macro comune: resta una domanda aperta, non un indizio.
        Riproducibile in <code>analysis/lead_lag.py</code> ·{" "}
        <code>analysis/lead_lag_robustness.py</code> · <code>docs/ANALISIS-LEADLAG.md</code>.
      </p>
    </section>
  );
}
