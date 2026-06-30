// Color scales for the choropleth. Sequential (YlOrRd) for absolute values;
// diverging (RdBu, reversed → blue=down, red=up) centred at zero for deltas —
// matching the brief's color guidance.

import { extent } from "d3-array";
import { scaleSequential, scaleDiverging } from "d3-scale";
import {
  interpolateYlOrRd,
  interpolateRdBu,
  interpolateBlues,
} from "d3-scale-chromatic";
import type { MetricKind } from "./types";

export const NO_DATA_COLOR = "#e6e6e6";

/** Named sequential palettes selectable per metric/series. */
export const PALETTES: Record<string, (t: number) => string> = {
  warm: interpolateYlOrRd,
  cool: interpolateBlues,
};

/** Qualitative palette for categorical metrics (indexed by category). */
export const CATEGORICAL_PALETTE = [
  "#d6604d", // 0 — warm red
  "#4393c3", // 1 — blue
  "#f4a582", // 2 — amber
  "#5aae61", // 3 — green
  "#9970ab", // 4 — purple
  "#bf812d", // 5 — brown
];

export interface ColorScale {
  /** Map a value (or null) to a fill color. */
  color(value: number | null | undefined): string;
  /** [min, max] of the data that defined the scale (for the legend). */
  domain: [number, number];
  kind: MetricKind;
  /** Ordered category labels, present only for kind === "categorical". */
  categories?: string[];
}

/** Build a color scale for one set of values (typically one period).
 * ``palette`` selects the sequential ramp ("warm" default, "cool" for e.g. rain). */
export function buildColorScale(
  values: Array<number | null | undefined>,
  kind: MetricKind,
  palette: keyof typeof PALETTES = "warm",
  categories?: string[],
): ColorScale {
  const nums = values.filter((v): v is number => v != null && Number.isFinite(v));
  const [lo, hi] = extent(nums);
  const min = lo ?? 0;
  const max = hi ?? 0;

  if (kind === "categorical") {
    const labels = categories ?? [];
    return {
      color: (v) =>
        v == null || !Number.isFinite(v)
          ? NO_DATA_COLOR
          : CATEGORICAL_PALETTE[(v as number) % CATEGORICAL_PALETTE.length],
      domain: [0, Math.max(0, labels.length - 1)],
      kind,
      categories: labels,
    };
  }

  if (kind === "diverging") {
    const bound = Math.max(Math.abs(min), Math.abs(max)) || 1;
    const scale = scaleDiverging<string>(
      [-bound, 0, bound],
      // reverse RdBu so blue=negative, red=positive
      (t) => interpolateRdBu(1 - t),
    );
    return {
      color: (v) => (v == null || !Number.isFinite(v) ? NO_DATA_COLOR : scale(v)),
      domain: [-bound, bound],
      kind,
    };
  }

  const scale = scaleSequential<string>(
    [min, max === min ? min + 1 : max],
    PALETTES[palette],
  );
  return {
    color: (v) => (v == null || !Number.isFinite(v) ? NO_DATA_COLOR : scale(v)),
    domain: [min, max],
    kind,
  };
}

/** Evenly spaced sample stops for rendering a legend gradient/ticks. */
export function legendStops(scale: ColorScale, n = 5): Array<{ value: number; color: string }> {
  const [min, max] = scale.domain;
  return Array.from({ length: n }, (_, i) => {
    const value = min + ((max - min) * i) / (n - 1);
    return { value, color: scale.color(value) };
  });
}
