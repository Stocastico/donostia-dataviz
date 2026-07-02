import { useMemo, useState } from "react";
import { buildColorScale, NO_DATA_COLOR, PALETTES } from "../lib/colorScale";
import { Legend } from "./Legend";
import { flattenSeriesValues, MONTH_LABELS } from "../lib/series";
import { formatValue } from "../lib/format";
import type { SeriesData } from "../lib/types";

interface Props {
  series: SeriesData;
  palette?: keyof typeof PALETTES;
}

interface HoverCell {
  year: string;
  monthIdx: number;
  value: number | null;
}

/** Month × year heatmap (rows = months, columns = years). Reveals seasonality
 * and how it changes over time in a single view, per the brief's Phase 3. */
export function SeasonalityHeatmap({ series, palette = "warm" }: Props) {
  const scale = useMemo(
    () => buildColorScale(flattenSeriesValues(series), "sequential", palette),
    [series, palette],
  );
  const [hover, setHover] = useState<HoverCell | null>(null);

  const cell = (year: string, monthIdx: number): number | null =>
    series.values[year]?.[String(monthIdx + 1)] ?? null;

  return (
    <div className="heatmap">
      <div
        className="heatmap-grid"
        style={{ gridTemplateColumns: `2.5rem repeat(${series.years.length}, 1fr)` }}
      >
        {/* Header row: blank corner + years */}
        <div className="hm-corner" />
        {series.years.map((y) => (
          <div key={y} className="hm-col-label">
            {y.slice(2)}
          </div>
        ))}

        {/* One row per month */}
        {MONTH_LABELS.map((label, m) => (
          <Row
            key={label}
            label={label}
            monthIdx={m}
            years={series.years}
            cell={cell}
            scale={scale}
            onHover={setHover}
          />
        ))}
      </div>

      <div className="heatmap-footer">
        <Legend scale={scale} unit={series.unit} />
        <div className="hm-readout">
          {hover
            ? `${MONTH_LABELS[hover.monthIdx]} ${hover.year}: ${formatValue(hover.value, series.unit)}`
            : "Passa sul calendario per i valori"}
        </div>
      </div>
    </div>
  );
}

function Row({
  label,
  monthIdx,
  years,
  cell,
  scale,
  onHover,
}: {
  label: string;
  monthIdx: number;
  years: string[];
  cell: (year: string, monthIdx: number) => number | null;
  scale: ReturnType<typeof buildColorScale>;
  onHover: (c: HoverCell | null) => void;
}) {
  return (
    <>
      <div className="hm-row-label">{label}</div>
      {years.map((year) => {
        const value = cell(year, monthIdx);
        return (
          <div
            key={year}
            className="hm-cell"
            style={{ background: value == null ? NO_DATA_COLOR : scale.color(value) }}
            onMouseEnter={() => onHover({ year, monthIdx, value })}
            onMouseLeave={() => onHover(null)}
            title={`${label} ${year}`}
          />
        );
      })}
    </>
  );
}
