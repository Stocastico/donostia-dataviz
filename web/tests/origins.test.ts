import { describe, expect, it } from "vitest";
import {
  ORIGIN_REGIONS,
  barrioOptions,
  originDelta,
  regionInfo,
} from "../src/lib/origins";
import type { OriginPaisesData } from "../src/lib/types";

describe("originDelta (10-year evolution)", () => {
  it("computes signed percent change when both years have people", () => {
    const d = originDelta(200, 100);
    expect(d.direction).toBe("up");
    expect(d.pct).toBeCloseTo(100, 6);
    expect(d.label).toContain("100");
  });

  it("marks a group absent a decade ago as new (no percentage)", () => {
    const d = originDelta(50, 0);
    expect(d.direction).toBe("new");
    expect(d.pct).toBeNull();
  });

  it("is flat when the count did not change", () => {
    expect(originDelta(80, 80).direction).toBe("flat");
  });

  it("is down when the count fell", () => {
    const d = originDelta(60, 120);
    expect(d.direction).toBe("down");
    expect(d.pct).toBeCloseTo(-50, 6);
  });
});

describe("regionInfo", () => {
  it("gives a label and color for every known region", () => {
    for (const key of Object.keys(ORIGIN_REGIONS)) {
      const info = regionInfo(key);
      expect(info.label.length).toBeGreaterThan(0);
      expect(info.color).toMatch(/^#/);
    }
  });

  it("falls back gracefully for an unknown region", () => {
    const info = regionInfo("marte");
    expect(info.label.length).toBeGreaterThan(0);
    expect(info.color).toMatch(/^#/);
  });
});

describe("barrioOptions", () => {
  const data: OriginPaisesData = {
    latestYear: "2025",
    pastYear: "2015",
    source: "x",
    barrios: {
      gros: { name: "Gros", foreignLatest: 10, top: [] },
      aiete: { name: "Aiete", foreignLatest: 5, top: [] },
    },
  };

  it("lists barrios sorted by display name", () => {
    const opts = barrioOptions(data);
    expect(opts.map((o) => o.id)).toEqual(["aiete", "gros"]);
    expect(opts[0].name).toBe("Aiete");
  });
});
