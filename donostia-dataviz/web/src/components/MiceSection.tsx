import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { indicators } from "../lib/data";
import { indicatorBarData, latestPoint } from "../lib/indicators";
import { formatValue } from "../lib/format";
import type { IndicatorData } from "../lib/types";

function find(id: string): IndicatorData | undefined {
  return indicators.find((i) => i.id === id);
}

/** MICE (congresses & meetings) — curated annual indicators. Headline figures
 * for the latest Convention Bureau totals + a bar chart of the comparable ICCA
 * international-congress series. */
export function MiceSection() {
  const icca = find("mice_icca_congresses");
  const events = find("mice_events_total");
  const attendees = find("mice_attendees");
  if (!icca && !events && !attendees) return null;

  const evLatest = events ? latestPoint(events) : null;
  const atLatest = attendees ? latestPoint(attendees) : null;
  const barData = icca ? indicatorBarData(icca) : [];

  return (
    <section className="mice">
      <h2>Turismo MICE — congressi e riunioni</h2>
      <p className="mice-sub">
        Dati curati da fonti citate (memorias DSS Turismoa, Convention Bureau,
        ICCA): non esiste un dataset aperto strutturato. Ogni valore porta la sua
        fonte (vedi <code>data/indicators_long.csv</code>).
      </p>

      <div className="mice-cards">
        {evLatest && (
          <StatCard
            value={formatValue(evLatest.value, events!.unit)}
            label={`Eventi professionali (${evLatest.year})`}
            sub={events!.values[evLatest.year].source}
          />
        )}
        {atLatest && (
          <StatCard
            value={formatValue(atLatest.value, attendees!.unit)}
            label={`Partecipanti (${atLatest.year})`}
            sub={attendees!.values[atLatest.year].source}
          />
        )}
      </div>

      {icca && (
        <>
          <h3>{icca.label} per anno</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={barData} margin={{ top: 18, right: 16, bottom: 8, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" vertical={false} />
              <XAxis dataKey="year" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} width={36} allowDecimals={false} />
              <Tooltip
                cursor={{ fill: "rgba(0,0,0,0.04)" }}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const p = payload[0].payload as { year: string; value: number; source: string };
                  return (
                    <div className="scatter-tip">
                      <strong>{p.year}: {p.value} {icca.unit}</strong>
                      <div style={{ maxWidth: 260 }}>{p.source}</div>
                    </div>
                  );
                }}
              />
              <Bar dataKey="value" fill="#d62728" radius={[3, 3, 0, 0]}>
                <LabelList dataKey="value" position="top" style={{ fontSize: 11, fill: "#444" }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <p className="source-note">
            Nota: i congressi ICCA seguono criteri stretti (associazioni
            internazionali, rotazione tra paesi) — molto meno numerosi del totale
            di eventi professionali del Convention Bureau.
          </p>
        </>
      )}
    </section>
  );
}

function StatCard({ value, label, sub }: { value: string; label: string; sub: string }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      <div className="stat-sub">{sub}</div>
    </div>
  );
}
