import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend as RLegend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { loadSeries, seriesRegistry } from "../lib/data";
import { annualAggregate } from "../lib/series";
import type { SeriesData } from "../lib/types";

const AIRBNB = "airbnb_reviews";
const HOTEL = "overnight_stays";
const BASE = "2016"; // index both to 100 here so the two units are comparable

/** Per-year totals indexed to BASE = 100 (null before a usable base). */
function indexed(series: SeriesData): Map<string, number> {
  const agg = annualAggregate(series, "sum");
  const base = agg.find((d) => d.year === BASE)?.value;
  if (!base) return new Map();
  return new Map(agg.map((d) => [d.year, (d.value / base) * 100]));
}

/** "Two tourisms": Airbnb (reviews, a proxy) vs hotel (INE overnight stays),
 * both indexed to {BASE}=100 to compare their *trajectory* despite the
 * different units. Stages story #5: touristic lodging grows much faster than
 * hotel capacity. */
export function TourismCompareSection() {
  const [airbnb, setAirbnb] = useState<SeriesData | null>(null);
  const [hotel, setHotel] = useState<SeriesData | null>(null);

  useEffect(() => {
    loadSeries(AIRBNB).then(setAirbnb).catch(() => setAirbnb(null));
    loadSeries(HOTEL).then(setHotel).catch(() => setHotel(null));
  }, []);

  const { data, lastYear } = useMemo(() => {
    if (!airbnb || !hotel) return { data: [], lastYear: "" };
    const ia = indexed(airbnb);
    const ih = indexed(hotel);
    const years = [...new Set([...ia.keys(), ...ih.keys()])]
      .filter((y) => y >= BASE)
      .sort();
    const rows = years.map((year) => ({
      year,
      airbnb: ia.get(year) ?? null,
      hotel: ih.get(year) ?? null,
    }));
    return { data: rows, lastYear: years[years.length - 1] ?? "" };
  }, [airbnb, hotel]);

  if (!seriesRegistry.some((s) => s.id === AIRBNB)) return null;

  const peak = data.reduce<number | null>(
    (mx, d) => (d.airbnb != null && (mx == null || d.airbnb > mx) ? d.airbnb : mx),
    null,
  );

  return (
    <section className="tourism-compare">
      <div className="scatter-head">
        <h2>Dos turismos: Airbnb vs hotel (desde {BASE})</h2>
      </div>

      <p className="scatter-sub">
        Pernoctaciones hoteleras (INE) y reseñas Airbnb, ambos{" "}
        <strong>indexados a {BASE} = 100</strong> para comparar la trayectoria
        pese a las unidades distintas.
        {peak != null && (
          <>
            {" "}
            La actividad Airbnb llega a <strong>~{Math.round(peak)}</strong> ({BASE} =
            100): crece <strong>mucho más rápido</strong> que la capacidad
            hotelera — la ciudad turística que se expande es la de los pisos,
            no la de los hoteles.
          </>
        )}
      </p>

      <ResponsiveContainer width="100%" height={340}>
        <LineChart data={data} margin={{ top: 16, right: 24, bottom: 28, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="year" tick={{ fontSize: 11 }} />
          <YAxis
            tick={{ fontSize: 11 }}
            label={{ value: `indice (${BASE}=100)`, angle: -90, position: "insideLeft", fontSize: 12 }}
          />
          <ReferenceLine y={100} stroke="#bbb" strokeDasharray="4 4" />
          <Tooltip
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null;
              return (
                <div className="scatter-tip">
                  <strong>{label}</strong>
                  {payload.map((p) => (
                    <div key={p.name}>
                      {p.name}: {p.value == null ? "n/d" : Math.round(p.value as number)}
                    </div>
                  ))}
                </div>
              );
            }}
          />
          <RLegend />
          <Line type="monotone" dataKey="airbnb" name="Airbnb (reseñas)" stroke="#d62728" strokeWidth={2} dot={false} connectNulls />
          <Line type="monotone" dataKey="hotel" name="Hotel (pernoctaciones)" stroke="#1f77b4" strokeWidth={2} dot={false} connectNulls />
        </LineChart>
      </ResponsiveContainer>

      <p className="scatter-sub leadlag-caveat">
        ⚠️ Base {BASE} pequeña para Airbnb → su crecimiento relativo se magnifica;
        las reseñas son un <em>proxy</em> de ocupación, no plazas. El último año
        ({lastYear}) puede estar incompleto. Hoteles: {hotel?.source}.
      </p>
    </section>
  );
}
