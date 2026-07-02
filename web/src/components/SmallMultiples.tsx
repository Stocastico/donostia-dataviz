import { useMemo } from "react";
import { projectBarrios } from "../lib/miniMap";
import type { ColorScale } from "../lib/colorScale";
import { barriosGeoJSON } from "../lib/data";
import type { MetricData } from "../lib/types";

const CELL_W = 92;
const CELL_H = 72;

interface Props {
  metric: MetricData;
  scale: ColorScale;
  activeIndex: number;
  onSelect: (index: number) => void;
}

/** All periods of the current metric at a glance, one small choropleth per
 * year (VIZ-8). Plain SVG, not maplibre: a real map per period would blow
 * past the browser's concurrent-WebGL-context limit for metrics with 20+
 * years. Clicking a cell jumps the main map/slider to that period; the
 * active one (also driven by "▶ Play") gets a highlighted border. */
export function SmallMultiples({ metric, scale, activeIndex, onSelect }: Props) {
  const { paths } = useMemo(
    () => projectBarrios(barriosGeoJSON, CELL_W, CELL_H),
    [],
  );

  if (metric.periods.length <= 1) return null;

  return (
    <section className="small-multiples">
      <h2>Tutti gli anni in un colpo d'occhio</h2>
      <p className="scatter-sub">
        Un mini-mappa per periodo, stessa scala colore della mappa principale.
        Clicca un anno per saltarci; usa "▶ Riproduci" sopra per animarli in
        sequenza.
      </p>
      <div className="small-multiples-grid">
        {metric.periods.map((period, i) => (
          <button
            key={period}
            type="button"
            className={`mini-map-cell ${i === activeIndex ? "active" : ""}`}
            onClick={() => onSelect(i)}
            aria-label={`Vai all'anno ${period}`}
            aria-pressed={i === activeIndex}
          >
            <svg viewBox={`0 0 ${CELL_W} ${CELL_H}`} width={CELL_W} height={CELL_H}>
              {paths.map((p) => (
                <path
                  key={p.barrioId}
                  d={p.d}
                  fill={scale.color(metric.values[p.barrioId]?.[period])}
                  stroke="#fff"
                  strokeWidth={0.4}
                />
              ))}
            </svg>
            <span className="mini-map-label">{period}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
