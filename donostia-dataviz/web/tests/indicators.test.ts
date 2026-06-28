import { describe, expect, it } from "vitest";
import { indicatorBarData, latestPoint } from "../src/lib/indicators";
import type { IndicatorData } from "../src/lib/types";

const IND: IndicatorData = {
  id: "mice_icca_congresses",
  label: "ICCA",
  unit: "congressi",
  theme: "tourism",
  source: "curated",
  years: ["2018", "2019", "2023", "2025"],
  values: {
    "2018": { value: 16, source: "ICCA 2018" },
    "2019": { value: 12, source: "ICCA 2019" },
    "2023": { value: 15, source: "ICCA 2023" },
    "2025": { value: 13, source: "ICCA 2025" },
  },
};

describe("indicatorBarData", () => {
  it("maps each year to a {year,value,source} point in order", () => {
    const data = indicatorBarData(IND);
    expect(data).toHaveLength(4);
    expect(data[0]).toEqual({ year: "2018", value: 16, source: "ICCA 2018" });
    expect(data.map((d) => d.year)).toEqual(["2018", "2019", "2023", "2025"]);
  });
});

describe("latestPoint", () => {
  it("returns the most recent year's value", () => {
    expect(latestPoint(IND)).toEqual({ year: "2025", value: 13 });
  });
  it("returns null for an empty indicator", () => {
    expect(latestPoint({ ...IND, years: [], values: {} })).toBeNull();
  });
});
