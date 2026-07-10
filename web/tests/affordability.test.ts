import { describe, expect, it } from "vitest";
import { affordabilityRows } from "../src/lib/affordability";
import type { AffordabilityData } from "../src/lib/types";

const DATA: AffordabilityData = {
  baseYear: 2016,
  commonEnd: 2023,
  unit: "indice (2016 = 100)",
  source: "test",
  note: "test",
  series: [
    {
      id: "sale", label: "Prezzo di vendita", color: "#b5730f", confidence: "proxy",
      lastYear: 2026, data: { "2015": 92, "2016": 100, "2023": 130, "2026": 160 },
      growth: { common: 30, full: 60 },
    },
    {
      id: "rent", label: "Affitto", color: "#2166ac", confidence: "observed",
      lastYear: 2024, data: { "2016": 100, "2023": 125 },
      growth: { common: 25, full: 35 },
    },
  ],
};

describe("affordabilityRows", () => {
  const rows = affordabilityRows(DATA);

  it("starts at the base year, dropping earlier years", () => {
    expect(rows[0].year).toBe(2016);
    expect(rows.some((r) => r.year === 2015)).toBe(false);
  });

  it("spans the union of series years from the base on", () => {
    expect(rows.map((r) => r.year)).toEqual([2016, 2023, 2026]);
  });

  it("leaves missing series-years undefined so the line breaks", () => {
    const y2026 = rows.find((r) => r.year === 2026)!;
    expect(y2026.sale).toBe(160);
    expect(y2026.rent).toBeUndefined(); // rent stops in 2024
  });
});
