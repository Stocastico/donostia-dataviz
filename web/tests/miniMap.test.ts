import { describe, expect, it } from "vitest";
import { projectBarrios } from "../src/lib/miniMap";
import type { BarriosGeoJSON } from "../src/lib/types";

// Two unit squares, side by side: "west" at x∈[0,1], "east" at x∈[2,3] (lon),
// both y∈[0,1] (lat). Simple enough to reason about the projected coordinates.
function square(barrioId: string, x0: number, y0: number): GeoJSON.Feature {
  return {
    type: "Feature",
    properties: { barrio_id: barrioId, name: barrioId, kod_auzo: "1" },
    geometry: {
      type: "Polygon",
      coordinates: [[
        [x0, y0], [x0 + 1, y0], [x0 + 1, y0 + 1], [x0, y0 + 1], [x0, y0],
      ]],
    },
  };
}

const GEO: BarriosGeoJSON = {
  type: "FeatureCollection",
  features: [square("west", 0, 0), square("east", 2, 0)] as never,
};

describe("projectBarrios", () => {
  it("returns one SVG path per feature, keyed by barrio_id", () => {
    const { paths } = projectBarrios(GEO, 100, 80);
    expect(paths.map((p) => p.barrioId).sort()).toEqual(["east", "west"]);
    for (const p of paths) {
      expect(p.d.startsWith("M")).toBe(true);
      expect(p.d).toContain("Z");
    }
  });

  it("preserves relative east/west ordering (more lon -> more x)", () => {
    const { paths } = projectBarrios(GEO, 100, 80);
    const firstX = (d: string) => Number(d.slice(1).split(/[ ,]/)[0]);
    const west = paths.find((p) => p.barrioId === "west")!;
    const east = paths.find((p) => p.barrioId === "east")!;
    expect(firstX(east.d)).toBeGreaterThan(firstX(west.d));
  });

  it("fits within the requested viewport", () => {
    const { paths, width, height } = projectBarrios(GEO, 100, 80);
    expect(width).toBe(100);
    expect(height).toBe(80);
    for (const p of paths) {
      const nums = p.d.slice(1, -1).trim().split(/[ ,LM]+/).filter(Boolean).map(Number);
      for (let i = 0; i < nums.length; i += 2) {
        expect(nums[i]).toBeGreaterThanOrEqual(0);
        expect(nums[i]).toBeLessThanOrEqual(width);
        expect(nums[i + 1]).toBeGreaterThanOrEqual(0);
        expect(nums[i + 1]).toBeLessThanOrEqual(height);
      }
    }
  });

  it("handles MultiPolygon geometries", () => {
    const multi: BarriosGeoJSON = {
      type: "FeatureCollection",
      features: [{
        type: "Feature",
        properties: { barrio_id: "split", name: "split", kod_auzo: "2" },
        geometry: {
          type: "MultiPolygon",
          coordinates: [
            [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            [[[2, 0], [3, 0], [3, 1], [2, 1], [2, 0]]],
          ],
        },
      }] as never,
    };
    const { paths } = projectBarrios(multi, 100, 80);
    expect(paths).toHaveLength(1);
    // two subpaths (one per polygon), each with its own M...Z
    expect(paths[0].d.match(/M/g)?.length).toBe(2);
  });
});
