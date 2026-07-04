import { useMemo, useState } from "react";
import { buildColorScale } from "../lib/colorScale";
import { streetVut } from "../lib/data";
import {
  MEASURES,
  type MeasureKey,
  streetPointsGeoJSON,
  streetRows,
} from "../lib/streets";
import { Legend } from "./Legend";
import { StreetMap } from "./StreetMap";

/** Touristic housing at **street** granularity — the one view in the app that
 *  stops below the barrio. A proportional-symbol map (one circle per street,
 *  sized by touristic units or beds) plus its accessible mirror table. */
export function StreetVutSection() {
  const [measure, setMeasure] = useState<MeasureKey>("units");
  const data = streetVut;
  const m = MEASURES[measure];
  const fc = useMemo(() => streetPointsGeoJSON(data, measure), [data, measure]);
  const rows = useMemo(() => streetRows(data, measure), [data, measure]);
  const scale = useMemo(
    () => buildColorScale(data.streets.map((s) => s[m.key]), "sequential", "warm"),
    [data, m.key],
  );

  if (!data || data.streets.length === 0) return null;

  const totalUnits = data.streets.reduce((acc, s) => acc + s.units, 0);
  const top = rows[0];

  return (
    <section className="street-vut">
      <h2>Viviendas turísticas, calle a calle</h2>
      <p className="street-vut-sub">
        Il resto dell'app aggrega tutto ai 19 barrios; questa vista scende un
        livello. Il censo VUT porta l'indirizzo (<code>helbidea</code>), e il{" "}
        callejero municipale dà un codice di via stabile e un punto per ogni
        strada: uniti, contano le <strong>{totalUnits}</strong> viviendas
        turísticas per via. Emerge ciò che la media di barrio nasconde — gli assi
        della Parte Vieja e i paseos, non un barrio «medio».
      </p>

      <div className="street-vut-controls" role="group" aria-label="Misura mostrata">
        {(Object.keys(MEASURES) as MeasureKey[]).map((k) => (
          <button
            key={k}
            type="button"
            className={k === measure ? "active" : ""}
            aria-pressed={k === measure}
            onClick={() => setMeasure(k)}
          >
            {MEASURES[k].label}
          </button>
        ))}
      </div>

      <div
        className="map-area"
        role="img"
        aria-label={`Mappa a simboli proporzionali: ${m.label} per via a Donostia. Ogni cerchio è una via, più grande e più caldo dove ci sono più unità. Via con più ${m.unit}: ${top ? `${top.name}, ${top.valueLabel}` : "n/d"}. Dati completi nella tabella qui sotto.`}
      >
        <StreetMap data={fc} />
        <Legend scale={scale} unit={m.unit} />
      </div>

      <details className="map-data-table">
        <summary>
          Tabella dati: {m.label} per via ({data.streetCount} vie)
        </summary>
        <p className="street-vut-note">
          Fonte: {data.source}. Match indirizzo→via: {data.matchedRows}/
          {data.totalRows} righe del censo ({data.matchRate}%). Il punto è
          l'ancora dell'etichetta della via (non il suo asse); censo istantaneo,
          senza serie storica.
        </p>
        <table>
          <caption className="sr-only">
            {m.label} per via a Donostia, in {m.unit}, ordinate dal più alto al
            più basso.
          </caption>
          <thead>
            <tr>
              <th scope="col">Via</th>
              <th scope="col">{m.label}</th>
              <th scope="col">{measure === "units" ? "Posti letto" : "Unità"}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.code}>
                <th scope="row">{r.name}</th>
                <td>{r.valueLabel}</td>
                <td>{r.otherLabel}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </section>
  );
}
