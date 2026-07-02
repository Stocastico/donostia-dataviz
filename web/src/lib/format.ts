// Value/delta formatting shared by the tooltip, legend and charts.

const NUM = new Intl.NumberFormat("it-IT", { maximumFractionDigits: 1 });

export function formatValue(value: number | null | undefined, unit: string): string {
  if (value == null || !Number.isFinite(value)) return "n/d";
  const num = NUM.format(value);
  return unit === "%" ? `${num}%` : `${num} ${unit}`;
}

/** Compact number for axes/legends: 246k, 2,2 M, 500 (no unit). */
export function formatCompact(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return "n/d";
  const abs = Math.abs(value);
  if (abs >= 1_000_000) return `${NUM.format(value / 1_000_000)} M`;
  if (abs >= 10_000) return `${NUM.format(Math.round(value / 1_000))}k`;
  if (abs >= 1_000) return `${NUM.format(value / 1_000)}k`; // keep one decimal (1,5k)
  return NUM.format(value);
}

/** Signed delta vs the previous period, e.g. "+1.3" or "−0.4" (n/d if missing). */
export function formatDelta(
  current: number | null | undefined,
  previous: number | null | undefined,
): string {
  if (current == null || previous == null) return "n/d";
  const d = current - previous;
  const sign = d > 0 ? "+" : d < 0 ? "−" : "±";
  return `${sign}${NUM.format(Math.abs(d))}`;
}
