import { legendStops, NO_DATA_COLOR, type ColorScale } from "../lib/colorScale";
import { formatCompact } from "../lib/format";

interface Props {
  scale: ColorScale;
  unit: string;
}

/** Color-scale legend: a gradient bar with compact min/mid/max ticks, the unit
 * shown once, plus a no-data swatch. Categorical metrics get a swatch-per-label
 * list instead of a gradient. */
export function Legend({ scale, unit }: Props) {
  if (scale.kind === "categorical") {
    return (
      <div className="legend legend-categorical">
        {(scale.categories ?? []).map((label, i) => (
          <span key={label} className="legend-cat">
            <span className="swatch" style={{ background: scale.color(i) }} /> {label}
          </span>
        ))}
        <span className="legend-nodata">
          <span className="swatch" style={{ background: NO_DATA_COLOR }} /> n/d
        </span>
      </div>
    );
  }

  const stops = legendStops(scale, 5);
  const gradient = `linear-gradient(to right, ${stops
    .map((s) => s.color)
    .join(", ")})`;
  const mid = (scale.domain[0] + scale.domain[1]) / 2;

  return (
    <div className="legend">
      <div className="legend-bar" style={{ background: gradient }} />
      <div className="legend-ticks">
        <span>{formatCompact(scale.domain[0])}</span>
        <span>{formatCompact(mid)}</span>
        <span>{formatCompact(scale.domain[1])}</span>
      </div>
      <div className="legend-meta">
        <span className="legend-unit">{unit}</span>
        <span className="legend-nodata">
          <span className="swatch" style={{ background: NO_DATA_COLOR }} /> n/d
        </span>
      </div>
    </div>
  );
}
