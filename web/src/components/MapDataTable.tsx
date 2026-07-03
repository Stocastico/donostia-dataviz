import { useMemo } from "react";
import { barrioRows } from "../lib/mapTable";
import type { BarriosGeoJSON, MetricData } from "../lib/types";

interface Props {
  geojson: BarriosGeoJSON;
  metric: MetricData;
  period: string;
  /** Whether the metric has a period-over-period delta column to show. */
  showDelta?: boolean;
}

/** A11y text alternative to the choropleth: a keyboard-reachable, screen-reader
 * friendly table of every barrio's value (and change) for the current metric and
 * period. Collapsed by default so it doesn't crowd the visual, but fully in the
 * tab order and announced — the data on the map is never color-only. */
export function MapDataTable({ geojson, metric, period, showDelta = true }: Props) {
  const rows = useMemo(
    () => barrioRows(geojson, metric, period),
    [geojson, metric, period],
  );
  const withDelta = showDelta && rows.some((r) => r.deltaLabel !== "");

  return (
    <details className="map-data-table">
      <summary>
        Tabella dati: {metric.label} ({period})
      </summary>
      <table>
        <caption className="sr-only">
          {metric.label} per barrio, {period}. In {metric.unit || "valore"}, ordinati dal
          più alto al più basso.
        </caption>
        <thead>
          <tr>
            <th scope="col">Barrio</th>
            <th scope="col">Valore</th>
            {withDelta && <th scope="col">Δ periodo prec.</th>}
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
