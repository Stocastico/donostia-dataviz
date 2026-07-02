import { describe, expect, it } from "vitest";
import { linearRegression } from "../src/lib/stats";

describe("linearRegression", () => {
  it("recovers slope/intercept of a perfect line", () => {
    const fit = linearRegression([
      { x: 0, y: 1 },
      { x: 1, y: 3 },
      { x: 2, y: 5 },
    ]);
    expect(fit).not.toBeNull();
    expect(fit!.slope).toBeCloseTo(2);
    expect(fit!.intercept).toBeCloseTo(1);
    expect(fit!.r2).toBeCloseTo(1);
  });

  it("gives a positive slope and 0<r2<1 for noisy increasing data", () => {
    const fit = linearRegression([
      { x: 2000, y: 13 },
      { x: 2010, y: 13.5 },
      { x: 2020, y: 14.6 },
    ])!;
    expect(fit.slope).toBeGreaterThan(0);
    expect(fit.r2).toBeGreaterThan(0);
    expect(fit.r2).toBeLessThanOrEqual(1);
  });

  it("returns null with fewer than two points or no x-variance", () => {
    expect(linearRegression([{ x: 1, y: 2 }])).toBeNull();
    expect(linearRegression([{ x: 5, y: 1 }, { x: 5, y: 9 }])).toBeNull();
  });
});
