// Helpers for city-grain monthly time series (seasonality heatmap + line).

import type { SeriesData } from "./types";

export const MONTH_LABELS = [
  "Ene", "Feb", "Mar", "Abr", "May", "Jun",
  "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
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

/** Reshape a month×year series into 12 month rows, each keyed by year — for a
 * "monthly cycles" overlay (one line per year, x = month). Missing → null. */
export function monthlyYearRows(
  series: SeriesData,
): Array<Record<string, string | number | null>> {
  return MONTH_LABELS.map((label, m) => {
    const row: Record<string, string | number | null> = { month: label };
    for (const year of series.years) {
      const v = series.values[year]?.[String(m + 1)];
      row[year] = v == null || !Number.isFinite(v) ? null : v;
    }
    return row;
  });
}

/** Annual mean of each year minus the overall baseline mean — the input for
 * "warming stripes" (anomaly per year vs the series average). */
export function temperatureAnomalies(
  series: SeriesData,
): Array<{ year: string; value: number; anomaly: number }> {
  const means = annualAggregate(series, "mean");
  if (means.length === 0) return [];
  const baseline = means.reduce((a, d) => a + d.value, 0) / means.length;
  return means.map((d) => ({
    year: d.year,
    value: d.value,
    anomaly: Math.round((d.value - baseline) * 100) / 100,
  }));
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

/** Whether `year` is still in progress (1-11 populated months) rather than a
 * finished calendar year (12) or simply absent (0). A partial year averaged
 * as if complete can mislead — e.g. only the cooler months published so far
 * would understate an annual temperature mean, not overstate it. Callers
 * that compute year-over-year trends/anomalies should caption or exclude it
 * rather than silently treat it as equivalent to a full year. */
export function isPartialYear(series: SeriesData, year: string): boolean {
  const count = Object.values(series.values[year] ?? {}).filter(
    (v) => v != null && Number.isFinite(v),
  ).length;
  return count > 0 && count < 12;
}

/** Per-year aggregate (sum or mean of the months present), skipping years with
 * no data at all. ``sum`` suits precipitation/overnight stays, ``mean`` suits
 * temperature. */
export function annualAggregate(
  series: SeriesData,
  mode: "sum" | "mean",
): Array<{ year: string; value: number }> {
  const out: Array<{ year: string; value: number }> = [];
  for (const year of series.years) {
    const nums = Object.values(series.values[year] ?? {}).filter(
      (v): v is number => v != null && Number.isFinite(v),
    );
    if (nums.length === 0) continue;
    const sum = nums.reduce((a, b) => a + b, 0);
    out.push({ year, value: mode === "mean" ? sum / nums.length : sum });
  }
  return out;
}
