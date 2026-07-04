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
        El resto de la app lo agrega todo a los 19 barrios; esta vista baja un
        nivel. El censo VUT trae la dirección (<code>helbidea</code>) y el{" "}
        callejero municipal da un código de calle estable y un punto por calle:
        cruzados, cuentan las <strong>{totalUnits}</strong> viviendas turísticas
        por calle. Aflora lo que la media de barrio esconde — los ejes del centro
        y los paseos, no un barrio «medio».
      </p>

      <div className="street-vut-controls" role="group" aria-label="Medida mostrada">
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
        aria-label={`Mapa de símbolos proporcionales: ${m.label} por calle en Donostia. Cada círculo es una calle, más grande y más cálido donde hay más unidades. Calle con más ${m.unit}: ${top ? `${top.name}, ${top.valueLabel}` : "n/d"}. Datos completos en la tabla de abajo.`}
      >
        <StreetMap data={fc} />
        <Legend scale={scale} unit={m.unit} />
      </div>

      <details className="map-data-table">
        <summary>
          Tabla de datos: {m.label} por calle ({data.streetCount} calles)
        </summary>
        <p className="street-vut-note">
          Fuente: {data.source}. Emparejamiento dirección→calle:{" "}
          {data.matchedRows}/{data.totalRows} filas del censo ({data.matchRate}%).
          El punto es el ancla de la etiqueta de la calle (no su eje); censo
          instantáneo, sin serie histórica.
        </p>
        <table>
          <caption className="sr-only">
            {m.label} por calle en Donostia, en {m.unit}, ordenadas de mayor a
            menor.
          </caption>
          <thead>
            <tr>
              <th scope="col">Calle</th>
              <th scope="col">{m.label}</th>
              <th scope="col">{measure === "units" ? "Plazas" : "Unidades"}</th>
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
