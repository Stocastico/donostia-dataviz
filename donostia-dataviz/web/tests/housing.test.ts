import { describe, expect, it } from "vitest";
import {
  percentileRanks,
  pressureGaps,
  shareOfIncome,
  zScores,
} from "../src/lib/housing";

describe("shareOfIncome", () => {
  it("is rent × 12 × m² ÷ income × 100 and scales with m²", () => {
    // 10 €/m² × 12 × 30 ÷ 20000 × 100 = 18%
    expect(shareOfIncome(10, 20000, 30)).toBeCloseTo(18, 6);
    // doubling m² doubles the share
    expect(shareOfIncome(10, 20000, 40)).toBeCloseTo(24, 6);
    expect(shareOfIncome(10, 20000, 20)).toBeCloseTo(12, 6);
  });
});

describe("zScores", () => {
  it("centres on zero and uses sample sd", () => {
    const z = zScores([1, 2, 3]);
    expect(z[0] + z[1] + z[2]).toBeCloseTo(0, 6);
    expect(z[1]).toBeCloseTo(0, 6); // the mean maps to 0
    expect(z[2]).toBeGreaterThan(0);
    expect(z[0]).toBeLessThan(0);
  });

  it("returns zeros when there is no spread", () => {
    expect(zScores([5, 5, 5])).toEqual([0, 0, 0]);
  });
});

describe("percentileRanks", () => {
  it("maps min→0, max→1 and the middle→0.5", () => {
    expect(percentileRanks([10, 20, 30])).toEqual([0, 0.5, 1]);
  });
});

describe("pressureGaps", () => {
  it("is positive where rent ranks above income (more pressure)", () => {
    // barrio A: low income, mid rent → rent runs ahead of income → positive gap
    const rent = [10, 12, 14];
    const income = [10000, 30000, 50000];
    const { zGap, pctGap } = pressureGaps(rent, income);
    // poorest barrio (index 0) has the highest pressure on both gaps
    expect(Math.max(...zGap)).toBe(zGap[0]);
    expect(Math.max(...pctGap)).toBe(pctGap[0]);
    // richest barrio (index 2) has the lowest
    expect(Math.min(...zGap)).toBe(zGap[2]);
  });
});
