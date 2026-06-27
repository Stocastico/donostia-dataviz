import { describe, expect, it } from "vitest";
import { formatDelta, formatValue } from "../src/lib/format";

describe("formatValue", () => {
  it("renders n/d for missing values", () => {
    expect(formatValue(null, "%")).toBe("n/d");
    expect(formatValue(undefined, "unità")).toBe("n/d");
  });

  it("appends % without a space and units with a space", () => {
    expect(formatValue(9.91, "%")).toBe("9,9%");
    expect(formatValue(120, "unità")).toBe("120 unità");
  });
});

describe("formatDelta", () => {
  it("signs the difference vs the previous period", () => {
    expect(formatDelta(10, 8)).toBe("+2");
    expect(formatDelta(8, 10)).toBe("−2");
    expect(formatDelta(5, 5)).toBe("±0");
  });

  it("returns n/d when either side is missing", () => {
    expect(formatDelta(null, 5)).toBe("n/d");
    expect(formatDelta(5, null)).toBe("n/d");
  });
});
