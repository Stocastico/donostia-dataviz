// Lightweight SVG projection for small-multiples maps (VIZ-8).
//
// The main dashboard map is a full maplibre-gl instance, which is too heavy
// to repeat once per year (browsers cap concurrent WebGL contexts well below
// the ~20+ periods some metrics have). Small multiples instead render plain
// SVG paths from a single shared projection computed once per viewport size.
//
// Equirectangular with a cos(latitude) correction on X is enough at Donostia's
// scale (a few km across) — no measurable distortion, and it avoids pulling in
// a full projection library for one small feature.

import type { BarriosGeoJSON } from "./types";

export interface MiniPath {
  barrioId: string;
  d: string;
}

export interface Projected {
  paths: MiniPath[];
  width: number;
  height: number;
}

type Ring = GeoJSON.Position[];

function ringsOf(geometry: GeoJSON.Geometry): Ring[][] {
  if (geometry.type === "Polygon") return [geometry.coordinates as Ring[]];
  if (geometry.type === "MultiPolygon") return geometry.coordinates as Ring[][];
  return [];
}

/** Project every barrio polygon into an SVG `d` path fitted to `width`×`height`. */
export function projectBarrios(
  geojson: BarriosGeoJSON,
  width: number,
  height: number,
  padding = 2,
): Projected {
  let minLon = Infinity, maxLon = -Infinity, minLat = Infinity, maxLat = -Infinity;
  for (const f of geojson.features) {
    for (const polygon of ringsOf(f.geometry)) {
      for (const ring of polygon) {
        for (const [lon, lat] of ring) {
          if (lon < minLon) minLon = lon;
          if (lon > maxLon) maxLon = lon;
          if (lat < minLat) minLat = lat;
          if (lat > maxLat) maxLat = lat;
        }
      }
    }
  }

  const cosLat = Math.cos(((minLat + maxLat) / 2) * (Math.PI / 180));
  const spanX = (maxLon - minLon) * cosLat || 1;
  const spanY = maxLat - minLat || 1;
  const innerW = width - 2 * padding;
  const innerH = height - 2 * padding;
  const scale = Math.min(innerW / spanX, innerH / spanY);
  const offsetX = padding + (innerW - spanX * scale) / 2;
  const offsetY = padding + (innerH - spanY * scale) / 2;

  const project = ([lon, lat]: GeoJSON.Position): [number, number] => [
    offsetX + (lon - minLon) * cosLat * scale,
    // SVG y grows downward; latitude grows northward — flip it.
    offsetY + (maxLat - lat) * scale,
  ];

  const paths: MiniPath[] = geojson.features.map((f) => {
    const d = ringsOf(f.geometry)
      .flatMap((polygon) => polygon.map((ring) => {
        const points = ring.map(project);
        return `M${points.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join("L")}Z`;
      }))
      .join(" ");
    return { barrioId: f.properties.barrio_id, d };
  });

  return { paths, width, height };
}
