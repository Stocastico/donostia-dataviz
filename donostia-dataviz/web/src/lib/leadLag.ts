// AN-6 lead/lag, computed in-browser from two barrio×year metrics
// (airbnb_activity, rent_eur_m2). Mirrors analysis/lead_lag.py: first differences
// (to remove the common platform-growth/inflation trend) + panel correlation at
// several yearly lags. lag k > 0 means tourism activity *leads* rent by k years.

import type { MetricData } from "./types";

export interface LagPoint {
  lag: number;
  r: number;
  n: number;
}

/** barrio_id → (year → value), keeping only numeric (year) periods. */
function yearPanel(metric: MetricData): Map<string, Map<number, number>> {
  const out = new Map<string, Map<number, number>>();
  for (const [bid, byPeriod] of Object.entries(metric.values)) {
    const ys = new Map<number, number>();
    for (const [period, v] of Object.entries(byPeriod)) {
      const y = Number(period);
      if (v != null && Number.isFinite(v) && Number.isInteger(y)) ys.set(y, v);
    }
    if (ys.size) out.set(bid, ys);
  }
  return out;
}

/** Year-over-year first differences per barrio (Δ = value[y] − value[y−1]). */
function firstDiffs(
  panel: Map<string, Map<number, number>>,
): Map<string, Map<number, number>> {
  const out = new Map<string, Map<number, number>>();
  for (const [bid, ys] of panel) {
    const d = new Map<number, number>();
    for (const [y, v] of ys) {
      const prev = ys.get(y - 1);
      if (prev != null) d.set(y, v - prev);
    }
    if (d.size) out.set(bid, d);
  }
  return out;
}

/** Pearson correlation over (x, y) pairs; NaN if too few points or no variance. */
export function pearson(pairs: Array<[number, number]>): { r: number; n: number } {
  const n = pairs.length;
  if (n < 3) return { r: NaN, n };
  let mx = 0;
  let my = 0;
  for (const [x, y] of pairs) {
    mx += x;
    my += y;
  }
  mx /= n;
  my /= n;
  let sxy = 0;
  let sxx = 0;
  let syy = 0;
  for (const [x, y] of pairs) {
    const dx = x - mx;
    const dy = y - my;
    sxy += dx * dy;
    sxx += dx * dx;
    syy += dy * dy;
  }
  if (sxx === 0 || syy === 0) return { r: NaN, n };
  return { r: sxy / Math.sqrt(sxx * syy), n };
}

/** Panel lead/lag of first-differenced activity vs rent, at the given yearly lags.
 * For each lag k it stacks (Δactivity[year−k], Δrent[year]) over all barrios/years
 * and correlates. k > 0 → activity leads rent. */
export function leadLag(
  activity: MetricData,
  rent: MetricData,
  lags: number[] = [-1, 0, 1, 2],
): LagPoint[] {
  const dAct = firstDiffs(yearPanel(activity));
  const dRent = firstDiffs(yearPanel(rent));
  const barrios = [...dRent.keys()].filter((b) => dAct.has(b));

  return lags.map((k) => {
    const pairs: Array<[number, number]> = [];
    for (const b of barrios) {
      const a = dAct.get(b)!;
      const r = dRent.get(b)!;
      for (const [year, dr] of r) {
        const da = a.get(year - k);
        if (da != null) pairs.push([da, dr]);
      }
    }
    const { r, n } = pearson(pairs);
    return { lag: k, r, n };
  });
}

/** The lag with the largest |r| (the "best" alignment), or null if none valid. */
export function bestLag(points: LagPoint[]): LagPoint | null {
  let best: LagPoint | null = null;
  for (const p of points) {
    if (Number.isFinite(p.r) && (best === null || Math.abs(p.r) > Math.abs(best.r))) {
      best = p;
    }
  }
  return best;
}
