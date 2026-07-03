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
        <h2>Chi vive nel barrio · origini</h2>
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
        Le prime <strong>cinque nazionalità straniere</strong> di {barrio.name} nel{" "}
        {latestYear}, con la variazione rispetto a dieci anni prima ({pastYear}).
        L'origine <strong>non è un indicatore</strong> di reddito, turismo o
        trasformazione (MET-5): è una fotografia di <em>chi</em> abita il barrio.
        Dentro «popolazione straniera» convivono profili opposti — la migrazione
        economica recente e l'Europa ad alto reddito — che il resto della mappa
        tiene distinti nei livelli <em>pct_origin_*</em>.
      </p>

      <ol
        className="origins-list"
        role="img"
        aria-label={`Prime nazionalità straniere di ${barrio.name} nel ${latestYear}`}
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
        Fonte: {originPaises.source}. Variazione {pastYear}→{latestYear}; «nuovo»
        = nazionalità non presente (o non registrata) nel barrio dieci anni prima.
      </p>
    </section>
  );
}
