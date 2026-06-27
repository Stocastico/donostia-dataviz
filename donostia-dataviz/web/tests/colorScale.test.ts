import { describe, expect, it } from "vitest";
import { buildColorScale, NO_DATA_COLOR, legendStops } from "../src/lib/colorScale";

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

  it("produces n legend stops spanning the domain", () => {
    const s = buildColorScale([0, 100], "sequential");
    const stops = legendStops(s, 5);
    expect(stops).toHaveLength(5);
    expect(stops[0].value).toBe(0);
    expect(stops[4].value).toBe(100);
  });
});
