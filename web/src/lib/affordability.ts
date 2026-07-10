import type { AffordabilityData } from "./types";

export interface AffordabilityRow {
  year: number;
  [seriesId: string]: number | undefined;
}

/** Merge the indexed city series into per-year rows for recharts, from the base
 * year on (before it only one series has data, which reads as noise on a 4-way
 * index). A missing series-year stays `undefined` so recharts breaks the line. */
export function affordabilityRows(d: AffordabilityData): AffordabilityRow[] {
  const years = new Set<number>();
  for (const s of d.series) {
    for (const y of Object.keys(s.data)) {
      const yr = Number(y);
      if (yr >= d.baseYear) years.add(yr);
    }
  }
  return [...years]
    .sort((a, b) => a - b)
    .map((year) => {
      const row: AffordabilityRow = { year };
      for (const s of d.series) row[s.id] = s.data[String(year)];
      return row;
    });
}
