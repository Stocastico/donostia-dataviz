import { describe, expect, it } from "vitest";
import { MONTH_LABELS, flattenSeriesValues, annualTotals, annualAggregate } from "../src/lib/series";
import type { SeriesData } from "../src/lib/types";

const SERIES: SeriesData = {
  id: "x",
  label: "X",
  unit: "n",
  theme: "tourism",
  source: "s",
  kind: "month-year",
  years: ["2020", "2021"],
  values: {
    "2020": { "1": 100, "2": 200 },
    "2021": { "1": 150, "2": null },
  },
};

describe("series helpers", () => {
  it("has 12 month labels", () => {
    expect(MONTH_LABELS).toHaveLength(12);
    expect(MONTH_LABELS[0]).toBe("Gen");
    expect(MONTH_LABELS[11]).toBe("Dic");
  });

  it("flattens non-null values across all years/months", () => {
    expect(flattenSeriesValues(SERIES).sort((a, b) => a - b)).toEqual([100, 150, 200]);
  });

  it("sums each year's months, ignoring nulls", () => {
    expect(annualTotals(SERIES)).toEqual([
      { year: "2020", total: 300 },
      { year: "2021", total: 150 },
    ]);
  });

  it("annualAggregate sums or means each year, skipping years with no data", () => {
    const s = {
      ...SERIES,
      values: {
        "2020": { "1": 10, "2": 20 },
        "2021": { "1": 30, "2": null },
        "2022": { "1": null },
      },
    };
    expect(annualAggregate(s, "sum")).toEqual([
      { year: "2020", value: 30 },
      { year: "2021", value: 30 },
    ]);
    expect(annualAggregate(s, "mean")).toEqual([
      { year: "2020", value: 15 },
      { year: "2021", value: 30 },
    ]);
  });
});
