// Helpers for per-barrio scatter/correlation views (Phase 4).

import type { MetricData } from "./types";

const DEFAULT_SIZE = 600;

export interface ScatterPoint {
  id: string;
  name: string;
  x: number;
  y: number;
  size: number;
}

/** Each barrio's value at the metric's most recent period (null if missing). */
export function valuesAtLatest(metric: MetricData): Record<string, number | null> {
  const period = metric.periods[metric.periods.length - 1];
  const out: Record<string, number | null> = {};
  for (const [barrioId, byPeriod] of Object.entries(metric.values)) {
    const v = byPeriod[period];
    out[barrioId] = v == null || !Number.isFinite(v) ? null : v;
  }
  return out;
}

/** Join two metrics at their latest period into scatter points (barrios with a
 * value for both). ``size`` comes from a per-barrio measure (e.g. population). */
export function buildScatterPoints(
  xMetric: MetricData,
  yMetric: MetricData,
  names: Record<string, string>,
  sizeByBarrio: Record<string, number | undefined>,
): ScatterPoint[] {
  const xv = valuesAtLatest(xMetric);
  const yv = valuesAtLatest(yMetric);
  const points: ScatterPoint[] = [];
  for (const id of Object.keys(names)) {
    const x = xv[id];
    const y = yv[id];
    if (x == null || y == null) continue;
    points.push({ id, name: names[id], x, y, size: sizeByBarrio[id] ?? DEFAULT_SIZE });
  }
  return points;
}

/** Pearson correlation coefficient; null if <2 points or no variance. */
export function pearson(points: Array<{ x: number; y: number }>): number | null {
  const n = points.length;
  if (n < 2) return null;
  let sx = 0, sy = 0;
  for (const p of points) {
    sx += p.x;
    sy += p.y;
  }
  const mx = sx / n;
  const my = sy / n;
  let cov = 0, vx = 0, vy = 0;
  for (const p of points) {
    const dx = p.x - mx;
    const dy = p.y - my;
    cov += dx * dy;
    vx += dx * dx;
    vy += dy * dy;
  }
  if (vx === 0 || vy === 0) return null;
  return cov / Math.sqrt(vx * vy);
}
