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
  v == null ? "" : v.toLocaleString("es-ES", { maximumFractionDigits: 0 });
const fmtPct = (v: number | null) => (v == null ? "—" : `${v > 0 ? "+" : ""}${v}%`);

/** HU-7 — buying/renting vs. wages vs. CPI, city grain, base 2016 = 100.
 * Brings to the dashboard what the housing_affordability analysis and Story 1
 * tell: home prices and rents outrun wages and inflation. */
export function AffordabilitySection() {
  const d = affordability;
  const rows = affordabilityRows(d);
  const byId = Object.fromEntries(d.series.map((s) => [s.id, s]));

  return (
    <section className="affordability">
      <div className="scatter-head">
        <h2>Comprar y alquilar corren más que el salario</h2>
      </div>
      <p className="scatter-sub">
        Cuatro series de ciudad indexadas a <strong>2016 = 100</strong> (media de los
        barrios ponderada por población): el <strong>precio de venta</strong>{" "}
        (idealista, oferta &mdash; <em>proxy</em>), el <strong>alquiler</strong> (EMA),
        el <strong>salario</strong> (renta del trabajo, Eustat) y el <strong>IPC</strong>{" "}
        (inflación, línea de referencia discontinua). Lo que está por encima del IPC
        se encarece en términos reales; lo que está por encima del salario, más rápido
        de lo que crece el sueldo.
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
            labelFormatter={(y) => `Año ${y}`}
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
                ? `${fmtPct(s.growth.full)} acumulado a ${s.lastYear}`
                : `ventana común ${d.baseYear}–${d.commonEnd}`}
            </div>
          </div>
        ))}
      </div>

      <p className="afford-take">
        En la ventana común <strong>{d.baseYear}–{d.commonEnd}</strong> el orden es
        claro: <strong>venta &gt; alquiler &gt; salario &gt; IPC</strong>. Comprar
        vivienda es la partida que más ha crecido &mdash; y, mirando más allá de 2023, el
        precio de venta acumula un <strong>{fmtPct(d.series.find((s) => s.id === "sale")?.growth.full ?? null)}</strong>{" "}
        a {d.series.find((s) => s.id === "sale")?.lastYear}, mientras el salario se
        paró mucho antes. Es la misma asequibilidad de la Historia 1, vista en un
        índice único.
      </p>

      <p className="source-note">
        Fuente: {d.source} {d.note}
      </p>
    </section>
  );
}
