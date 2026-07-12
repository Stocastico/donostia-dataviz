// Component smoke tests: the lib/ helpers are covered unit-by-unit elsewhere;
// these check the React wiring on top of them — that controls render, fire
// their callbacks, and the Dashboard mounts end-to-end with real data.
import { describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach } from "vitest";
import { MetricPicker } from "../src/components/MetricPicker";
import { TimeSlider } from "../src/components/TimeSlider";
import { MapDataTable } from "../src/components/MapDataTable";
import { Legend } from "../src/components/Legend";
import { buildColorScale } from "../src/lib/colorScale";
import type { MetricInfo } from "../src/lib/types";
import type { BarrioRow } from "../src/lib/mapTable";

afterEach(cleanup);

const metrics: MetricInfo[] = [
  {
    id: "vut_count", label: "Viviendas turísticas", unit: "uds", theme: "tourism",
    kind: "sequential", geoGrain: "barrio", timeGrain: "year", source: "test",
    status: "live", periods: ["2023"],
  },
  {
    id: "population", label: "Población", unit: "hab", theme: "demography",
    kind: "sequential", geoGrain: "barrio", timeGrain: "year", source: "test",
    status: "live", periods: ["2023"],
  },
  {
    id: "future", label: "Futura", unit: "", theme: "demography",
    kind: "sequential", geoGrain: "barrio", timeGrain: "year", source: "test",
    status: "planned", periods: [],
  },
];

describe("MetricPicker", () => {
  it("groups by theme, disables planned metrics and fires onSelect", () => {
    const onSelect = vi.fn();
    render(<MetricPicker metrics={metrics} selectedId="vut_count" onSelect={onSelect} />);

    const select = screen.getByLabelText<HTMLSelectElement>("Métrica");
    expect(select.value).toBe("vut_count");
    expect(screen.getByRole("group", { name: "Turismo" })).toBeTruthy();
    const planned = screen.getByRole("option", { name: /próximamente/ });
    expect((planned as HTMLOptionElement).disabled).toBe(true);

    fireEvent.change(select, { target: { value: "population" } });
    expect(onSelect).toHaveBeenCalledWith("population");
  });
});

describe("TimeSlider", () => {
  const periods = ["2019", "2020", "2021"];

  it("shows the current period and reports slider moves", () => {
    const onChange = vi.fn();
    render(<TimeSlider periods={periods} index={1} onChange={onChange} />);
    expect(screen.getByText("2020")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Seleccionar año"), { target: { value: "2" } });
    expect(onChange).toHaveBeenCalledWith(2);
  });

  it("toggles play/pause through the button", () => {
    const onTogglePlay = vi.fn();
    render(
      <TimeSlider periods={periods} index={0} onChange={() => {}} playing={false} onTogglePlay={onTogglePlay} />,
    );
    fireEvent.click(screen.getByRole("button", { name: /Reproducir/ }));
    expect(onTogglePlay).toHaveBeenCalledOnce();
  });

  it("renders a static label for single-period metrics", () => {
    render(<TimeSlider periods={["2024"]} index={0} onChange={() => {}} />);
    expect(screen.queryByRole("slider")).toBeNull();
    expect(screen.getByText("2024")).toBeTruthy();
  });
});

describe("MapDataTable", () => {
  const rows: BarrioRow[] = [
    { id: "gros", name: "Gros", value: 10, valueLabel: "10 uds", deltaLabel: "+2" },
    { id: "aiete", name: "Aiete", value: null, valueLabel: "n/d", deltaLabel: "" },
  ];

  it("renders every barrio with value and delta (— when absent)", () => {
    render(<MapDataTable rows={rows} label="Viviendas turísticas" period="2023" unit="uds" />);
    expect(screen.getByText(/Tabla de datos: Viviendas turísticas \(2023\)/)).toBeTruthy();
    expect(screen.getByRole("rowheader", { name: "Gros" })).toBeTruthy();
    expect(screen.getByText("+2")).toBeTruthy();
    expect(screen.getByText("—")).toBeTruthy();
  });

  it("omits the delta column when no row has one", () => {
    const noDelta = rows.map((r) => ({ ...r, deltaLabel: "" }));
    render(<MapDataTable rows={noDelta} label="X" />);
    expect(screen.queryByText("Δ periodo ant.")).toBeNull();
  });
});

describe("Legend", () => {
  it("renders swatch-per-category for categorical scales", () => {
    const scale = buildColorScale([0, 1, 2], "categorical", "warm", ["Bajo", "Medio", "Alto"]);
    render(<Legend scale={scale} unit="" />);
    for (const label of ["Bajo", "Medio", "Alto", "n/d"]) {
      expect(screen.getByText(label)).toBeTruthy();
    }
  });

  it("renders min/mid/max ticks for sequential scales", () => {
    const scale = buildColorScale([0, 50, 100], "sequential");
    render(<Legend scale={scale} unit="%" />);
    expect(screen.getByText("0")).toBeTruthy();
    expect(screen.getByText("50")).toBeTruthy();
    expect(screen.getByText("100")).toBeTruthy();
  });
});

describe("Dashboard (smoke, real data)", () => {
  it("mounts, loads the default metric and fills the mirror table", async () => {
    const { Dashboard } = await import("../src/views/Dashboard");
    render(<Dashboard />);
    expect(screen.getByRole("heading", { name: "Donostia Dataviz" })).toBeTruthy();

    // The default metric loads async (import.meta.glob) → the map aria-label
    // and the data table appear once it lands.
    await waitFor(() => {
      expect(screen.getByRole("img", { name: /Mapa coroplético/ })).toBeTruthy();
    });
    expect(screen.getAllByRole("rowheader").length).toBeGreaterThan(10); // 19 barrios
  });
});
