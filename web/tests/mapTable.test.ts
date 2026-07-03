import { describe, expect, it } from "vitest";
import { barrioRows } from "../src/lib/mapTable";
import type { BarriosGeoJSON, MetricData } from "../src/lib/types";

const geo = {
  type: "FeatureCollection",
  features: [
    { type: "Feature", properties: { barrio_id: "a", name: "A", kod_auzo: "1" },
      geometry: { type: "Polygon", coordinates: [] } },
    { type: "Feature", properties: { barrio_id: "b", name: "B", kod_auzo: "2" },
      geometry: { type: "Polygon", coordinates: [] } },
    { type: "Feature", properties: { barrio_id: "c", name: "C", kod_auzo: "3" },
      geometry: { type: "Polygon", coordinates: [] } },
  ],
} as unknown as BarriosGeoJSON;

const metric: MetricData = {
  id: "m", label: "M", unit: "%", kind: "sequential", theme: "housing", source: "x",
  periods: ["2020", "2021"],
  values: {
    a: { "2020": 10, "2021": 12 },
    b: { "2020": 5, "2021": 4 },
    c: { "2020": 8, "2021": null }, // no data in current period
  },
};

describe("barrioRows (map mirror table)", () => {
  it("returns one row per barrio with formatted value and delta vs previous period", () => {
    const rows = barrioRows(geo, metric, "2021");
    expect(rows).toHaveLength(3);
    const a = rows.find((r) => r.id === "a")!;
    expect(a.name).toBe("A");
    expect(a.valueLabel).toContain("12");
    expect(a.deltaLabel).toContain("+2"); // 12 − 10
  });

  it("sorts by value descending with n/d (nulls) last", () => {
    const rows = barrioRows(geo, metric, "2021");
    expect(rows.map((r) => r.id)).toEqual(["a", "b", "c"]);
    expect(rows[2].valueLabel).toBe("n/d");
  });

  it("has no delta for the first period", () => {
    const rows = barrioRows(geo, metric, "2020");
    expect(rows.every((r) => r.deltaLabel === "")).toBe(true);
  });

  it("labels categorical metrics by category name, without a delta", () => {
    const cat: MetricData = {
      id: "k", label: "K", unit: "", kind: "categorical", theme: "x", source: "x",
      periods: ["2020"], categories: ["Basso", "Alto"],
      values: { a: { "2020": 1 }, b: { "2020": 0 }, c: { "2020": null } },
    };
    const rows = barrioRows(geo, cat, "2020");
    expect(rows.find((r) => r.id === "a")!.valueLabel).toBe("Alto");
    expect(rows.every((r) => r.deltaLabel === "")).toBe(true);
  });
});
