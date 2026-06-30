// Helpers for the bivariate 3×3 choropleth (VIZ-3): cross two metrics into a
// low/mid/high class on each axis and a blended color. Classes are terciles of
// the joint sample (barrios that have a value on both metrics), so each axis is
// split into thirds over exactly the barrios shown on the map.

import { quantile } from "d3-array";

export type BiClass = 0 | 1 | 2; // 0 = low, 1 = mid, 2 = high

/** Tercile breakpoints (33rd, 66th percentile) of the values. */
export function terciles(values: number[]): [number, number] {
  const sorted = values.filter((v) => Number.isFinite(v)).sort((a, b) => a - b);
  const b1 = quantile(sorted, 1 / 3) ?? 0;
  const b2 = quantile(sorted, 2 / 3) ?? b1;
  return [b1, b2];
}

/** Place a value in its tercile: < b1 → low, < b2 → mid, else high. */
export function classify(value: number, [b1, b2]: [number, number]): BiClass {
  if (value < b1) return 0;
  if (value < b2) return 1;
  return 2;
}

/** Class names for tooltips/legend. */
export const CLASS_LABELS = ["Basso", "Medio", "Alto"] as const;

// Stevens "Blue (x) × Red (y)" 3×3 scheme, indexed [yClass][xClass]:
// x adds blue, y adds red, both-high is dark.
export const BIVARIATE_PALETTE: string[][] = [
  ["#e8e8e8", "#b0d5df", "#64acbe"], // y low
  ["#e4acac", "#ad9ea5", "#627f8c"], // y mid
  ["#c85a5a", "#985356", "#574249"], // y high
];

/** Blended color for a pair of axis classes. */
export function biColor(xClass: BiClass, yClass: BiClass): string {
  return BIVARIATE_PALETTE[yClass][xClass];
}
