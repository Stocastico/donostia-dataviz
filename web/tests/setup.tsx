// Shared test setup for component tests under jsdom.
//
// jsdom has no WebGL and no ResizeObserver, so the two browser-native pieces
// the app leans on are stubbed here: maplibre-gl (the choropleth canvas) and
// ResizeObserver (recharts' ResponsiveContainer). The stubs keep the public
// surface the components actually touch, nothing more.
import { vi } from "vitest";

class FakeMap {
  on = vi.fn();
  addSource = vi.fn();
  addLayer = vi.fn();
  getSource = vi.fn(() => undefined);
  getCanvas = vi.fn(() => ({ style: {} }));
  remove = vi.fn();
}

class FakePopup {
  setLngLat = vi.fn(() => this);
  setHTML = vi.fn(() => this);
  addTo = vi.fn(() => this);
  remove = vi.fn();
}

vi.mock("maplibre-gl", () => ({
  default: { Map: FakeMap, Popup: FakePopup },
  Map: FakeMap,
  Popup: FakePopup,
}));

// recharts' ResponsiveContainer measures itself with ResizeObserver.
class FakeResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver ??= FakeResizeObserver as unknown as typeof ResizeObserver;
