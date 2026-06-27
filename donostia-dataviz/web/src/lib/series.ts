// Helpers for city-grain monthly time series (seasonality heatmap + line).

import type { SeriesData } from "./types";

export const MONTH_LABELS = [
  "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
  "Lug", "Ago", "Set", "Ott", "Nov", "Dic",
];

/** All non-null values across every year/month — for building the color scale. */
export function flattenSeriesValues(series: SeriesData): number[] {
  const out: number[] = [];
  for (const byMonth of Object.values(series.values)) {
    for (const v of Object.values(byMonth)) {
      if (v != null && Number.isFinite(v)) out.push(v);
    }
  }
  return out;
}

/** Per-year totals (sum of months, ignoring nulls) for an annual trend line. */
export function annualTotals(series: SeriesData): Array<{ year: string; total: number }> {
  return series.years.map((year) => {
    const total = Object.values(series.values[year] ?? {}).reduce<number>(
      (acc, v) => acc + (v ?? 0),
      0,
    );
    return { year, total };
  });
}
