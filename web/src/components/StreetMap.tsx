import { useEffect, useRef } from "react";
import maplibregl, { type LngLatBoundsLike, type Map as MlMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { StreetFeatureCollection } from "../lib/streets";

const SOURCE_ID = "streets";
// Blank style: no external tiles, so the map works offline and without keys
// (same choice as BarrioMap).
const BLANK_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: "bg", type: "background", paint: { "background-color": "#f4f6f8" } }],
};

/** Bounding box of all street points for the initial fit. */
function bounds(fc: StreetFeatureCollection): LngLatBoundsLike {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const f of fc.features) {
    const [x, y] = f.geometry.coordinates;
    minX = Math.min(minX, x); minY = Math.min(minY, y);
    maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
  }
  if (!Number.isFinite(minX)) return [[-2.05, 43.28], [-1.94, 43.34]]; // Donostia fallback
  return [[minX, minY], [maxX, maxY]];
}

/** A maplibre proportional-symbol map: one circle per street, sized by
 *  ``__radius`` and colored by ``__color`` (both precomputed in
 *  streetPointsGeoJSON). Mirrors BarrioMap's lifecycle: create once, then
 *  setData when the decorated collection changes. */
export function StreetMap({ data }: { data: StreetFeatureCollection }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MlMap | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);
  // Latest decorated data; the "load" handler reads it so a data change that
  // lands before the style finishes loading isn't lost (same as BarrioMap).
  const dataRef = useRef<StreetFeatureCollection>(data);

  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BLANK_STYLE,
      bounds: bounds(dataRef.current),
      fitBoundsOptions: { padding: 28 },
      attributionControl: false,
    });
    mapRef.current = map;
    popupRef.current = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

    map.on("load", () => {
      map.addSource(SOURCE_ID, { type: "geojson", data: dataRef.current });
      map.addLayer({
        id: "streets-circle",
        type: "circle",
        source: SOURCE_ID,
        paint: {
          "circle-radius": ["get", "__radius"],
          "circle-color": ["get", "__color"],
          "circle-opacity": 0.85,
          "circle-stroke-color": "#5a3a1a",
          "circle-stroke-width": 0.6,
        },
      });

      map.on("mousemove", "streets-circle", (e) => {
        map.getCanvas().style.cursor = "pointer";
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties as Record<string, string>;
        popupRef.current
          ?.setLngLat(e.lngLat)
          .setHTML(`<strong>${p.name}</strong><br/>${p.__valueLabel}`)
          .addTo(map);
      });
      map.on("mouseleave", "streets-circle", () => {
        map.getCanvas().style.cursor = "";
        popupRef.current?.remove();
      });
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    dataRef.current = data;
    const map = mapRef.current;
    if (!map) return;
    const source = map.getSource(SOURCE_ID) as maplibregl.GeoJSONSource | undefined;
    if (source) source.setData(data as never);
  }, [data]);

  return <div ref={containerRef} className="choropleth-map" />;
}
