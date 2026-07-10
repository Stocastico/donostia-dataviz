import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { affordability } from "../lib/data";
import { affordabilityRows } from "../lib/affordability";

const fmtIdx = (v: number | undefined) =>
  v == null ? "" : v.toLocaleString("it-IT", { maximumFractionDigits: 0 });
const fmtPct = (v: number | null) => (v == null ? "—" : `${v > 0 ? "+" : ""}${v}%`);

/** HU-7 — comprare/affittare vs. salario vs. IPC, città, base 2016 = 100.
 * Porta nel dashboard ciò che l'analisi housing_affordability e la Storia 1
 * raccontano: casa e affitto corrono più del salario e dell'inflazione. */
export function AffordabilitySection() {
  const d = affordability;
  const rows = affordabilityRows(d);
  const byId = Object.fromEntries(d.series.map((s) => [s.id, s]));

  return (
    <section className="affordability">
      <div className="scatter-head">
        <h2>Comprare e affittare corrono più del salario</h2>
      </div>
      <p className="scatter-sub">
        Quattro serie di città indicizzate a <strong>2016 = 100</strong> (media dei
        barrios pesata per popolazione): il <strong>prezzo di vendita</strong>{" "}
        (idealista, offerta &mdash; <em>proxy</em>), l'<strong>affitto</strong> (EMA),
        il <strong>salario</strong> (reddito da lavoro, Eustat) e l'<strong>IPC</strong>{" "}
        (inflazione, linea di riferimento tratteggiata). Chi sta sopra l'IPC si
        incarisce in termini reali; chi sta sopra il salario, più veloce di quanto
        cresca lo stipendio.
      </p>

      <ResponsiveContainer width="100%" height={330}>
        <LineChart data={rows} margin={{ top: 8, right: 20, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="year" tick={{ fontSize: 11 }} minTickGap={20} />
          <YAxis
            tick={{ fontSize: 11 }}
            width={40}
            tickFormatter={fmtIdx}
            domain={["dataMin - 4", "dataMax + 4"]}
          />
          <Tooltip
            formatter={(v: number, name: string) => [fmtIdx(v), byId[name]?.label ?? name]}
            labelFormatter={(y) => `Anno ${y}`}
          />
          <Legend formatter={(value: string) => byId[value]?.label ?? value} />
          {d.series.map((s) => (
            <Line
              key={s.id}
              type="monotone"
              dataKey={s.id}
              name={s.id}
              stroke={s.color}
              strokeWidth={2.2}
              strokeDasharray={s.dash ? "5 4" : undefined}
              dot={false}
              connectNulls={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      <div className="mice-cards">
        {d.series.map((s) => (
          <div className="stat-card" key={s.id}>
            <div className="stat-value">{fmtPct(s.growth.common)}</div>
            <div className="stat-label">
              <span className="afford-dot" style={{ background: s.color }} aria-hidden />
              {s.label}
            </div>
            <div className="stat-sub">
              {s.growth.full != null && s.lastYear !== d.commonEnd
                ? `${fmtPct(s.growth.full)} accumulato al ${s.lastYear}`
                : `finestra comune ${d.baseYear}–${d.commonEnd}`}
            </div>
          </div>
        ))}
      </div>

      <p className="afford-take">
        Nella finestra comune <strong>{d.baseYear}–{d.commonEnd}</strong> l'ordine è
        netto: <strong>vendita &gt; affitto &gt; salario &gt; IPC</strong>. Comprare
        casa è la voce che è cresciuta di più &mdash; e, guardando oltre il 2023, il
        prezzo di vendita accumula un <strong>+{d.series.find((s) => s.id === "sale")?.growth.full}%</strong>{" "}
        al {d.series.find((s) => s.id === "sale")?.lastYear}, mentre il salario si è
        fermato molto prima. È la stessa asequibilità della Storia 1, vista in un
        indice unico.
      </p>

      <p className="source-note">
        Fonte: {d.source} {d.note}
      </p>
    </section>
  );
}
