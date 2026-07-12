// Street-granularity touristic housing (street_vut.json). Pure transforms for
// the StreetVutSection map + its accessible mirror table. The circle map is a
// WebGL canvas (opaque to screen readers), so — as with the barrio choropleth —
// the same numbers are exposed as an ordered text table via streetRows().

import { buildColorScale, type ColorScale } from "./colorScale";
import type { StreetVut, StreetVutData } from "./types";

/** Selectable measures. ``rMin``/``rMax`` bound the circle radius in pixels. */
export const MEASURES = {
  units: { key: "units" as const, label: "Viviendas turísticas", unit: "unidades", rMin: 4, rMax: 22 },
  beds: { key: "beds" as const, label: "Plazas turísticas", unit: "plazas", rMin: 4, rMax: 22 },
} satisfies Record<string, { key: keyof Pick<StreetVut, "units" | "beds">; label: string; unit: string; rMin: number; rMax: number }>;

export type MeasureKey = keyof typeof MEASURES;

/** De-invert the official ES street name ("Zabaleta, Calle de" → "Calle de
 *  Zabaleta"); fall back to the natural-order EU name when there is no ES one. */
export function displayName(s: Pick<StreetVut, "nameEs" | "nameEu">): string {
  const es = s.nameEs?.trim();
  if (es) {
    const comma = es.indexOf(",");
    if (comma > -1) {
      const core = es.slice(0, comma).trim();
      const type = es.slice(comma + 1).trim();
      if (core && type) return `${type} ${core}`;
    }
    return es;
  }
  return s.nameEu?.trim() ?? "";
}

/** Area-proportional radius (sqrt): value 0 → ``rMin``, ``max`` → ``rMax``. */
export function radiusFor(value: number, max: number, rMin = 4, rMax = 22): number {
  if (max <= 0) return rMin;
  const t = Math.sqrt(Math.max(0, value) / max);
  return rMin + (rMax - rMin) * t;
}

export interface StreetRow {
  code: string;
  name: string;
  value: number;
  valueLabel: string;
  /** Second measure shown alongside (units ↔ beds), for context in the table. */
  otherLabel: string;
}

/** One row per street, sorted by the chosen measure descending (ties by name). */
export function streetRows(data: StreetVutData, measure: MeasureKey): StreetRow[] {
  const m = MEASURES[measure];
  const other = measure === "units" ? MEASURES.beds : MEASURES.units;
  return data.streets
    .map((s) => ({
      code: s.code,
      name: displayName(s),
      value: s[m.key],
      valueLabel: `${s[m.key]} ${m.unit}`,
      otherLabel: `${s[other.key]} ${other.unit}`,
    }))
    .sort((a, b) => b.value - a.value || a.name.localeCompare(b.name, "es"));
}

export interface StreetFeature {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] };
  properties: {
    code: string;
    name: string;
    __value: number;
    __valueLabel: string;
    __color: string;
    __radius: number;
  };
}

export interface StreetFeatureCollection {
  type: "FeatureCollection";
  features: StreetFeature[];
}

/** Decorate each street as a Point feature carrying color (shared YlOrRd ramp,
 *  like the choropleths) and an area-proportional radius for the circle map.
 *  Pass ``scale`` to reuse one already built for the same measure (e.g. the
 *  legend's); omitted, an identical one is built here. */
export function streetPointsGeoJSON(
  data: StreetVutData,
  measure: MeasureKey,
  scale?: ColorScale,
): StreetFeatureCollection {
  const m = MEASURES[measure];
  const values = data.streets.map((s) => s[m.key]);
  const max = values.reduce((acc, v) => Math.max(acc, v), 0);
  scale ??= buildColorScale(values, "sequential", "warm");

  return {
    type: "FeatureCollection",
    features: data.streets.map((s) => {
      const value = s[m.key];
      const name = displayName(s);
      return {
        type: "Feature" as const,
        geometry: { type: "Point" as const, coordinates: [s.lon, s.lat] as [number, number] },
        properties: {
          code: s.code,
          name,
          __value: value,
          __valueLabel: `${value} ${m.unit}`,
          __color: scale.color(value),
          __radius: radiusFor(value, max, m.rMin, m.rMax),
        },
      };
    }),
  };
}
