import { useEffect, useRef } from "react";
import maplibregl, { type LngLatBoundsLike, type Map as MlMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { BarriosGeoJSON } from "../lib/types";

const SOURCE_ID = "barrios";
// Blank style: no external tiles, so the map works offline and without keys.
const BLANK_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: "bg", type: "background", paint: { "background-color": "#f4f6f8" } }],
};

/** Compute the bounding box of all barrio polygons for the initial fit. */
function bounds(geojson: BarriosGeoJSON): LngLatBoundsLike {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  const visit = (coords: GeoJSON.Position[] | GeoJSON.Position[][] | GeoJSON.Position[][][] | GeoJSON.Position) => {
    if (typeof coords[0] === "number") {
      const [x, y] = coords as GeoJSON.Position;
      minX = Math.min(minX, x); minY = Math.min(minY, y);
      maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
    } else {
      for (const c of coords as GeoJSON.Position[]) visit(c);
    }
  };
  for (const f of geojson.features) visit((f.geometry as GeoJSON.Polygon | GeoJSON.MultiPolygon).coordinates as never);
  return [[minX, minY], [maxX, maxY]];
}

/** A maplibre choropleth over the barrio geometry. ``data`` is the geometry
 * already decorated with per-feature ``__color`` (fill) and ``__valueLabel`` /
 * optional ``__deltaLabel`` (tooltip). Keeping the rendering generic lets both
 * the single-metric map and the bivariate map share one map instance. */
export function BarrioMap({ data }: { data: BarriosGeoJSON }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MlMap | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);
  // Latest decorated data. The "load" handler reads it (not a captured value)
  // so a data change landing before the style finishes loading isn't lost;
  // bounds are fixed by the geometry, so any snapshot fits the same.
  const dataRef = useRef<BarriosGeoJSON>(data);

  // Create the map once.
  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BLANK_STYLE,
      bounds: bounds(dataRef.current),
      fitBoundsOptions: { padding: 24 },
      attributionControl: false,
    });
    mapRef.current = map;
    popupRef.current = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

    map.on("load", () => {
      map.addSource(SOURCE_ID, { type: "geojson", data: dataRef.current });
      map.addLayer({
        id: "barrios-fill",
        type: "fill",
        source: SOURCE_ID,
        paint: { "fill-color": ["get", "__color"], "fill-opacity": 0.85 },
      });
      map.addLayer({
        id: "barrios-line",
        type: "line",
        source: SOURCE_ID,
        paint: { "line-color": "#ffffff", "line-width": 1 },
      });

      map.on("mousemove", "barrios-fill", (e) => {
        map.getCanvas().style.cursor = "pointer";
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties as Record<string, string>;
        const delta = p.__deltaLabel ? `<span class="tt-delta">Δ ${p.__deltaLabel}</span>` : "";
        popupRef.current
          ?.setLngLat(e.lngLat)
          .setHTML(`<strong>${p.name}</strong><br/>${p.__valueLabel} ${delta}`)
          .addTo(map);
      });
      map.on("mouseleave", "barrios-fill", () => {
        map.getCanvas().style.cursor = "";
        popupRef.current?.remove();
      });
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Recolor whenever the decorated data changes. If the source doesn't exist
  // yet (style still loading), the "load" handler picks dataRef up instead.
  useEffect(() => {
    dataRef.current = data;
    const map = mapRef.current;
    if (!map) return;
    const source = map.getSource(SOURCE_ID) as maplibregl.GeoJSONSource | undefined;
    if (source) source.setData(data as never);
  }, [data]);

  return <div ref={containerRef} className="choropleth-map" />;
}
