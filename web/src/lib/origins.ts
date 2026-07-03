// REC-21-web — helpers for the per-barrio country-of-origin card.
// Pure logic only (delta over a decade, region labels/colors, barrio options);
// the component in BarrioOriginsSection.tsx renders on top of these.

import type { OriginPaisesData } from "./types";

/** Region key → { short Italian label, colour }. Same grouping as the
 *  pct_origin_* choropleth metrics; colour is a *secondary* channel — the card
 *  always prints the region name too, so it reads without colour (a11y). */
export const ORIGIN_REGIONS: Record<string, { label: string; color: string }> = {
  latam: { label: "America Latina", color: "#4393c3" },
  norte_africa: { label: "Nord Africa", color: "#d6604d" },
  africa_subsahariana: { label: "Africa subsahariana", color: "#bf812d" },
  europa_occidental: { label: "Europa occidentale", color: "#5aae61" },
  europa_este: { label: "Europa dell'Est", color: "#9970ab" },
  oriente_medio: { label: "Medio Oriente", color: "#e08214" },
  asia: { label: "Asia", color: "#762a83" },
  norteamerica_oceania: { label: "Nord America / Oceania", color: "#2166ac" },
  otros: { label: "Altro", color: "#878787" },
};

const FALLBACK = { label: "Altro", color: "#878787" };

export function regionInfo(region: string): { label: string; color: string } {
  return ORIGIN_REGIONS[region] ?? FALLBACK;
}

export type Direction = "up" | "down" | "flat" | "new";

export interface OriginDelta {
  /** Signed percent change vs a decade ago, or null when it can't be computed
   *  (the group was absent then). */
  pct: number | null;
  direction: Direction;
  /** Human label, e.g. "+100%", "−50%", "nuovo" (new), "=" (flat). */
  label: string;
}

/** Evolution of one country's headcount over the last decade. */
export function originDelta(latest: number, past: number): OriginDelta {
  if (past === 0) {
    return latest === 0
      ? { pct: 0, direction: "flat", label: "=" }
      : { pct: null, direction: "new", label: "nuovo" };
  }
  if (latest === past) return { pct: 0, direction: "flat", label: "=" };
  const pct = ((latest - past) / past) * 100;
  const sign = pct > 0 ? "+" : "−";
  return {
    pct,
    direction: pct > 0 ? "up" : "down",
    label: `${sign}${Math.round(Math.abs(pct))}%`,
  };
}

/** Barrios present in the payload, as {id, name}, sorted by display name. */
export function barrioOptions(data: OriginPaisesData): Array<{ id: string; name: string }> {
  return Object.entries(data.barrios)
    .map(([id, b]) => ({ id, name: b.name }))
    .sort((a, b) => a.name.localeCompare(b.name, "it"));
}
