import type { BarrioRow } from "../lib/mapTable";

interface Props {
  rows: BarrioRow[];
  /** Metric/measure name for the summary + caption. */
  label: string;
  /** Period shown in the summary (e.g. "2024", "actual"). Omit when the map has
   *  no single period (e.g. a joint-latest computed measure). */
  period?: string;
  /** Unit for the caption; optional. */
  unit?: string;
}

/** A11y text alternative to a choropleth: a keyboard-reachable, screen-reader
 * friendly table of every barrio's value (and change) for the mapped metric —
 * so the data on the map is never color-only. Collapsed by default but fully in
 * the tab order and announced. Presentational: callers pass the rows (from
 * ``barrioRows`` for MetricData maps or ``rowsFromDecorated`` for computed ones). */
export function MapDataTable({ rows, label, period, unit }: Props) {
  const withDelta = rows.some((r) => r.deltaLabel !== "");

  return (
    <details className="map-data-table">
      <summary>
        Tabla de datos: {label}
        {period ? ` (${period})` : ""}
      </summary>
      <table>
        <caption className="sr-only">
          {label} por barrio{period ? `, ${period}` : ""}. En {unit || "valor"}, ordenados
          de mayor a menor.
        </caption>
        <thead>
          <tr>
            <th scope="col">Barrio</th>
            <th scope="col">Valor</th>
            {withDelta && <th scope="col">Δ periodo ant.</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <th scope="row">{r.name}</th>
              <td>{r.valueLabel}</td>
              {withDelta && <td>{r.deltaLabel || "—"}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  );
}
