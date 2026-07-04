import { describe, expect, it } from "vitest";
import {
  MEASURES,
  displayName,
  streetRows,
  streetPointsGeoJSON,
  radiusFor,
} from "../src/lib/streets";
import type { StreetVutData } from "../src/lib/types";

const data: StreetVutData = {
  source: "test",
  totalRows: 10,
  matchedRows: 9,
  matchRate: 90,
  streetCount: 3,
  streets: [
    { code: "1", nameEs: "Zabaleta, Calle de", nameEu: "Zabaleta Kalea", lon: -1.97, lat: 43.32, units: 35, vut: 30, hut: 5, beds: 155 },
    { code: "2", nameEs: "Fe, Paseo de la", nameEu: "La Fe Pasealekua", lon: -2.0, lat: 43.31, units: 6, vut: 6, hut: 0, beds: 40 },
    { code: "3", nameEs: "Aispua, Calle de", nameEu: "Aispua Kalea", lon: -1.99, lat: 43.29, units: 6, vut: 4, hut: 2, beds: 20 },
  ],
};

describe("displayName (de-invert the official ES name)", () => {
  it("turns 'Zabaleta, Calle de' into 'Calle de Zabaleta'", () => {
    expect(displayName(data.streets[0])).toBe("Calle de Zabaleta");
  });
  it("handles 'Fe, Paseo de la' → 'Paseo de la Fe'", () => {
    expect(displayName(data.streets[1])).toBe("Paseo de la Fe");
  });
  it("falls back to the EU name when there is no ES name", () => {
    expect(displayName({ ...data.streets[0], nameEs: "" })).toBe("Zabaleta Kalea");
  });
});

describe("streetRows (mirror table)", () => {
  it("sorts by the chosen measure descending, ties broken by name", () => {
    const rows = streetRows(data, "units");
    expect(rows.map((r) => r.code)).toEqual(["1", "3", "2"]); // 35, then 6/6 tie → Aispua < Fe
    expect(rows[0].name).toBe("Calle de Zabaleta");
    expect(rows[0].value).toBe(35);
  });
  it("switches the ranked value when the measure changes", () => {
    const rows = streetRows(data, "beds");
    expect(rows.map((r) => r.value)).toEqual([155, 40, 20]);
  });
});

describe("radiusFor (area-proportional, sqrt)", () => {
  it("maps 0 to the minimum radius and the max value to the max radius", () => {
    expect(radiusFor(0, 35)).toBeCloseTo(MEASURES.units.rMin ?? 4);
    expect(radiusFor(35, 35)).toBeCloseTo(22);
  });
  it("is monotonic and area-proportional (value 1/4 of max → ~half radius span)", () => {
    const rMin = 4, rMax = 22;
    const mid = radiusFor(35 / 4, 35);
    expect(mid).toBeCloseTo(rMin + (rMax - rMin) * 0.5, 5);
  });
});

describe("streetPointsGeoJSON", () => {
  it("emits one Point feature per street decorated with color, radius and label", () => {
    const fc = streetPointsGeoJSON(data, "units");
    expect(fc.features).toHaveLength(3);
    const f0 = fc.features[0];
    expect(f0.geometry.type).toBe("Point");
    expect(f0.geometry.coordinates).toEqual([-1.97, 43.32]);
    expect(typeof f0.properties.__color).toBe("string");
    expect(f0.properties.__radius).toBeGreaterThan(0);
    expect(f0.properties.name).toBe("Calle de Zabaleta");
    expect(f0.properties.__valueLabel).toContain("35");
  });
});
