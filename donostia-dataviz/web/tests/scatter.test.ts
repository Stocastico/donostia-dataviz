import { describe, expect, it } from "vitest";
import { buildScatterPoints, pearson, valuesAtLatest } from "../src/lib/scatter";
import type { MetricData } from "../src/lib/types";

function metric(id: string, periods: string[], values: MetricData["values"]): MetricData {
  return {
    id, label: id, unit: "u", kind: "sequential", theme: "t", source: "s",
    periods, values,
  };
}

const X = metric("x", ["2016", "2024"], {
  gros: { "2016": 1, "2024": 10 },
  egia: { "2016": 3, "2024": 20 },
  aiete: { "2016": 5, "2024": 30 },
  altza: { "2016": 9, "2024": null }, // missing at latest → excluded
});
const Y = metric("y", ["2024"], {
  gros: { "2024": 2 },
  egia: { "2024": 4 },
  aiete: { "2024": 6 },
  altza: { "2024": 8 },
});
const NAMES = { gros: "Gros", egia: "Egia", aiete: "Aiete", altza: "Altza" };
const POP = { gros: 1000, egia: 2000, aiete: 3000 };

describe("valuesAtLatest", () => {
  it("takes each barrio's value at the metric's last period", () => {
    expect(valuesAtLatest(X)).toEqual({ gros: 10, egia: 20, aiete: 30, altza: null });
  });
});

describe("buildScatterPoints", () => {
  it("joins X/Y at latest period, dropping barrios missing either", () => {
    const pts = buildScatterPoints(X, Y, NAMES, POP);
    expect(pts.map((p) => p.id).sort()).toEqual(["aiete", "egia", "gros"]);
    const gros = pts.find((p) => p.id === "gros")!;
    expect(gros).toMatchObject({ x: 10, y: 2, name: "Gros", size: 1000 });
  });

  it("defaults size when population is unknown", () => {
    const pts = buildScatterPoints(X, Y, NAMES, {});
    expect(pts[0].size).toBeGreaterThan(0);
  });
});

describe("pearson", () => {
  it("is +1 for a perfectly increasing relation", () => {
    expect(pearson([{ x: 1, y: 2 }, { x: 2, y: 4 }, { x: 3, y: 6 }])).toBeCloseTo(1);
  });
  it("is -1 for a perfectly decreasing relation", () => {
    expect(pearson([{ x: 1, y: 6 }, { x: 2, y: 4 }, { x: 3, y: 2 }])).toBeCloseTo(-1);
  });
  it("returns null when there are too few points or no variance", () => {
    expect(pearson([{ x: 1, y: 1 }])).toBeNull();
    expect(pearson([{ x: 1, y: 5 }, { x: 1, y: 9 }])).toBeNull();
  });
});
