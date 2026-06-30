import { describe, expect, it } from "vitest";
import { bestLag, leadLag, pearson } from "../src/lib/leadLag";
import type { MetricData } from "../src/lib/types";

function metric(id: string, values: Record<string, Record<string, number>>): MetricData {
  const periods = [...new Set(Object.values(values).flatMap((v) => Object.keys(v)))].sort();
  return { id, label: id, unit: "", kind: "sequential", theme: "t", source: "s", periods, values };
}

describe("pearson", () => {
  it("is 1 for a perfect positive line and NaN for <3 points", () => {
    expect(pearson([[1, 2], [2, 4], [3, 6]]).r).toBeCloseTo(1, 6);
    expect(pearson([[1, 1], [2, 2]]).n).toBe(2);
    expect(Number.isNaN(pearson([[1, 1], [2, 2]]).r)).toBe(true);
  });
});

describe("leadLag", () => {
  it("detects a one-year lead (rent follows activity)", () => {
    // Two barrios; rent's annual change equals last year's activity change → the
    // signal must peak at lag +1 (activity leads rent by a year).
    const activity = metric("airbnb_activity", {
      a: { "2016": 0, "2017": 1, "2018": 3, "2019": 6, "2020": 10 },
      b: { "2016": 0, "2017": 2, "2018": 2, "2019": 5, "2020": 9 },
    });
    // rent[y] − rent[y−1] := activity[y−1] − activity[y−2]
    const rent = metric("rent_eur_m2", {
      a: { "2017": 10, "2018": 11, "2019": 13, "2020": 16, "2021": 20 },
      b: { "2017": 10, "2018": 12, "2019": 12, "2020": 15, "2021": 19 },
    });

    const points = leadLag(activity, rent, [-1, 0, 1, 2]);
    const best = bestLag(points)!;
    expect(best.lag).toBe(1);
    expect(best.r).toBeCloseTo(1, 6);
  });

  it("returns a point per requested lag", () => {
    const a = metric("airbnb_activity", { a: { "2016": 1, "2017": 2, "2018": 3 } });
    const r = metric("rent_eur_m2", { a: { "2016": 5, "2017": 6, "2018": 7 } });
    expect(leadLag(a, r, [-1, 0, 1, 2]).map((p) => p.lag)).toEqual([-1, 0, 1, 2]);
  });
});
