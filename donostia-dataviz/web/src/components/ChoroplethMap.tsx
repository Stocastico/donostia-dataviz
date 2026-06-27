import { useEffect, useRef } from "react";
import maplibregl, { type LngLatBoundsLike, type Map as MlMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { ColorScale } from "../lib/colorScale";
import { formatDelta, formatValue } from "../lib/format";
import type { BarriosGeoJSON, MetricData } from "../lib/types";

interface Props {
  geojson: BarriosGeoJSON;
  metric: MetricData;
  period: string;
  scale: ColorScale;
}

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

/** Build a recolored copy of the geometry carrying the current value/delta/color. */
function decorate(geojson: BarriosGeoJSON, metric: MetricData, period: string, scale: ColorScale): BarriosGeoJSON {
  const pIdx = metric.periods.indexOf(period);
  const prev = pIdx > 0 ? metric.periods[pIdx - 1] : null;
  return {
    ...geojson,
    features: geojson.features.map((f) => {
      const id = f.properties.barrio_id;
      const value = metric.values[id]?.[period] ?? null;
      const prevValue = prev ? metric.values[id]?.[prev] ?? null : null;
      return {
        ...f,
        properties: {
          ...f.properties,
          __value: value,
          __valueLabel: formatValue(value, metric.unit),
          __deltaLabel: prev ? formatDelta(value, prevValue) : "",
          __color: scale.color(value),
        },
      };
    }),
  } as BarriosGeoJSON;
}

export function ChoroplethMap({ geojson, metric, period, scale }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MlMap | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);

  // Create the map once.
  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BLANK_STYLE,
      bounds: bounds(geojson),
      fitBoundsOptions: { padding: 24 },
      attributionControl: false,
    });
    mapRef.current = map;
    popupRef.current = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

    map.on("load", () => {
      map.addSource(SOURCE_ID, { type: "geojson", data: decorate(geojson, metric, period, scale) });
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Recolor whenever the metric, period or scale changes.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const source = map.getSource(SOURCE_ID) as maplibregl.GeoJSONSource | undefined;
    if (source) source.setData(decorate(geojson, metric, period, scale) as never);
  }, [geojson, metric, period, scale]);

  return <div ref={containerRef} className="choropleth-map" />;
}
