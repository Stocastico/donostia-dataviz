import { legendStops, NO_DATA_COLOR, type ColorScale } from "../lib/colorScale";
import { formatValue } from "../lib/format";

interface Props {
  scale: ColorScale;
  unit: string;
}

/** Color-scale legend: a gradient bar with min/mid/max ticks + a no-data swatch. */
export function Legend({ scale, unit }: Props) {
  const stops = legendStops(scale, 5);
  const gradient = `linear-gradient(to right, ${stops
    .map((s) => s.color)
    .join(", ")})`;

  return (
    <div className="legend">
      <div className="legend-bar" style={{ background: gradient }} />
      <div className="legend-ticks">
        <span>{formatValue(scale.domain[0], unit)}</span>
        <span>{formatValue((scale.domain[0] + scale.domain[1]) / 2, unit)}</span>
        <span>{formatValue(scale.domain[1], unit)}</span>
      </div>
      <div className="legend-nodata">
        <span className="swatch" style={{ background: NO_DATA_COLOR }} /> n/d
      </div>
    </div>
  );
}
