import { useMemo, useState } from "react";
import { originPaises } from "../lib/data";
import { barrioOptions, originDelta, regionInfo } from "../lib/origins";

/** REC-21-web — "chi vive nel barrio · origini": the top foreign nationalities
 * in a chosen barrio and how each has moved over the last decade.
 *
 * ⚠️ MET-5: country of origin is NOT a proxy for income, tourism or
 * transformation — it's descriptive. The copy says so, and the app already
 * separates the two migrant profiles as regional choropleths (pct_origin_*). */
export function BarrioOriginsSection() {
  const options = useMemo(() => barrioOptions(originPaises), []);
  const [barrioId, setBarrioId] = useState<string>(
    () => (options.find((o) => o.id === "erdialdea") ?? options[0])?.id ?? "",
  );

  const barrio = originPaises.barrios[barrioId];
  const maxPct = useMemo(
    () => (barrio ? Math.max(...barrio.top.map((c) => c.pctOfBarrio), 0.001) : 1),
    [barrio],
  );

  if (options.length === 0 || !barrio) return null;
  const { latestYear, pastYear } = originPaises;

  return (
    <section className="origins">
      <div className="scatter-head">
        <h2>Quién vive en el barrio · orígenes</h2>
        <div className="origins-select">
          <label className="control-label" htmlFor="origins-barrio">Barrio</label>
          <select
            id="origins-barrio"
            value={barrioId}
            onChange={(e) => setBarrioId(e.target.value)}
          >
            {options.map((o) => (
              <option key={o.id} value={o.id}>{o.name}</option>
            ))}
          </select>
        </div>
      </div>

      <p className="scatter-sub">
        Las primeras <strong>cinco nacionalidades extranjeras</strong> de {barrio.name} en{" "}
        {latestYear}, con la variación respecto a diez años antes ({pastYear}).
        El origen <strong>no es un indicador</strong> de renta, turismo o
        transformación (MET-5): es una fotografía de <em>quién</em> habita el barrio.
        Dentro de «población extranjera» conviven perfiles opuestos — la migración
        económica reciente y la Europa de renta alta — que el resto del mapa
        mantiene distintos en los niveles <em>pct_origin_*</em>.
      </p>

      <ol
        className="origins-list"
        role="img"
        aria-label={`Principales nacionalidades extranjeras de ${barrio.name} en ${latestYear}`}
      >
        {barrio.top.map((c, i) => {
          const region = regionInfo(c.region);
          const delta = originDelta(c.peopleLatest, c.peoplePast);
          return (
            <li key={c.country} className="origins-row">
              <span className="origins-rank">{i + 1}</span>
              <span className="origins-name">
                {c.country}
                <span className="origins-region">
                  <span
                    className="origins-dot"
                    style={{ background: region.color }}
                    aria-hidden="true"
                  />
                  {region.label}
                </span>
              </span>
              <span className="origins-bar-wrap">
                <span
                  className="origins-bar"
                  style={{
                    width: `${(c.pctOfBarrio / maxPct) * 100}%`,
                    background: region.color,
                  }}
                />
              </span>
              <span className="origins-figs">
                <span className="origins-people">{c.peopleLatest} pers.</span>
                <span className="origins-pct">{c.pctOfBarrio}%</span>
                <span className={`origins-delta d-${delta.direction}`}>
                  {delta.direction === "up" && "▲ "}
                  {delta.direction === "down" && "▼ "}
                  {delta.label}
                </span>
              </span>
            </li>
          );
        })}
      </ol>

      <p className="source-note">
        Fuente: {originPaises.source}. Variación {pastYear}→{latestYear}; «nuevo»
        = nacionalidad no presente (o no registrada) en el barrio diez años antes.
      </p>
    </section>
  );
}
