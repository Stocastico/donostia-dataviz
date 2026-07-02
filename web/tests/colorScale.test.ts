import { describe, expect, it } from "vitest";
import {
  buildColorScale,
  CATEGORICAL_PALETTE,
  NO_DATA_COLOR,
  legendStops,
} from "../src/lib/colorScale";

describe("buildColorScale", () => {
  it("maps null/undefined to the no-data color", () => {
    const s = buildColorScale([1, 2, 3], "sequential");
    expect(s.color(null)).toBe(NO_DATA_COLOR);
    expect(s.color(undefined)).toBe(NO_DATA_COLOR);
  });

  it("uses the data extent as the sequential domain", () => {
    const s = buildColorScale([5, 10, 2, null], "sequential");
    expect(s.domain).toEqual([2, 10]);
    expect(s.color(2)).not.toBe(s.color(10));
  });

  it("centres the diverging scale on zero and is symmetric", () => {
    const s = buildColorScale([-3, 1, 2], "diverging");
    expect(s.domain).toEqual([-3, 3]);
    // zero sits at the neutral midpoint
    expect(s.color(0)).toBeTruthy();
  });

  it("maps categorical indices to distinct palette colors and exposes labels", () => {
    const cats = ["A", "B", "C"];
    const s = buildColorScale([0, 1, 2], "categorical", "warm", cats);
    expect(s.kind).toBe("categorical");
    expect(s.categories).toEqual(cats);
    expect(s.color(0)).toBe(CATEGORICAL_PALETTE[0]);
    expect(s.color(1)).toBe(CATEGORICAL_PALETTE[1]);
    expect(s.color(0)).not.toBe(s.color(1));
    expect(s.color(null)).toBe(NO_DATA_COLOR);
  });

  it("produces n legend stops spanning the domain", () => {
    const s = buildColorScale([0, 100], "sequential");
    const stops = legendStops(s, 5);
    expect(stops).toHaveLength(5);
    expect(stops[0].value).toBe(0);
    expect(stops[4].value).toBe(100);
  });
});
