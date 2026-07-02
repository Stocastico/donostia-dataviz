// Helpers for annual city indicators (e.g. MICE).

import type { IndicatorData } from "./types";

export interface IndicatorPoint {
  year: string;
  value: number;
  source: string;
}

/** Ordered {year, value, source} points for a bar/line chart. */
export function indicatorBarData(ind: IndicatorData): IndicatorPoint[] {
  return ind.years.map((year) => ({
    year,
    value: ind.values[year]?.value,
    source: ind.values[year]?.source ?? "",
  }));
}

/** The most recent year's value, or null if the indicator is empty. */
export function latestPoint(ind: IndicatorData): { year: string; value: number } | null {
  const year = ind.years[ind.years.length - 1];
  if (!year) return null;
  return { year, value: ind.values[year].value };
}
