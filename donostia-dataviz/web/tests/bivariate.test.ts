import { describe, expect, it } from "vitest";
import {
  BIVARIATE_PALETTE,
  biColor,
  classify,
  terciles,
} from "../src/lib/bivariate";

describe("bivariate terciles + classify", () => {
  it("splits a 1..9 range into balanced thirds", () => {
    const breaks = terciles([1, 2, 3, 4, 5, 6, 7, 8, 9]);
    // low {1,2,3}, mid {4,5,6}, high {7,8,9}
    expect(classify(1, breaks)).toBe(0);
    expect(classify(3, breaks)).toBe(0);
    expect(classify(5, breaks)).toBe(1);
    expect(classify(7, breaks)).toBe(2);
    expect(classify(9, breaks)).toBe(2);
  });

  it("ignores non-finite values when computing breaks", () => {
    const breaks = terciles([1, 2, 3, NaN, Infinity]);
    expect(Number.isFinite(breaks[0])).toBe(true);
    expect(Number.isFinite(breaks[1])).toBe(true);
  });

  it("classifies the smallest value as low and largest as high", () => {
    const vals = [10, 20, 30, 40, 50, 60];
    const breaks = terciles(vals);
    expect(classify(Math.min(...vals), breaks)).toBe(0);
    expect(classify(Math.max(...vals), breaks)).toBe(2);
  });
});

describe("biColor", () => {
  it("indexes the palette by [yClass][xClass]", () => {
    expect(biColor(0, 0)).toBe(BIVARIATE_PALETTE[0][0]); // both low → neutral
    expect(biColor(2, 2)).toBe(BIVARIATE_PALETTE[2][2]); // both high → dark corner
    expect(biColor(2, 0)).toBe(BIVARIATE_PALETTE[0][2]); // high X, low Y
    expect(biColor(0, 2)).toBe(BIVARIATE_PALETTE[2][0]); // low X, high Y
  });

  it("gives every class pair a distinct color", () => {
    const seen = new Set<string>();
    for (let y = 0; y < 3; y++) for (let x = 0; x < 3; x++) seen.add(biColor(x as 0, y as 0));
    expect(seen.size).toBe(9);
  });
});
