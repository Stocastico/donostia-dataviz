import type { MetricInfo } from "../lib/types";

interface Props {
  metrics: MetricInfo[];
  selectedId: string;
  onSelect: (id: string) => void;
}

const THEME_LABELS: Record<string, string> = {
  tourism: "Turismo",
  demography: "Demografía",
  economy: "Economía",
  education: "Educación",
  health: "Salud",
  housing: "Vivienda",
  climate: "Clima",
  change: "Velocidad de cambio",
  environment: "Medio ambiente",
  security: "Seguridad",
  transformation: "Transformación (AN-8)",
};

/** Dropdown over the metric registry, grouped by theme. Planned (not-yet-built)
 * metrics render disabled with a "(próximamente)" hint so the catalog is visible. */
export function MetricPicker({ metrics, selectedId, onSelect }: Props) {
  const byTheme = new Map<string, MetricInfo[]>();
  for (const m of metrics) {
    const list = byTheme.get(m.theme) ?? [];
    list.push(m);
    byTheme.set(m.theme, list);
  }

  return (
    <label className="metric-picker">
      <span className="control-label">Métrica</span>
      <select value={selectedId} onChange={(e) => onSelect(e.target.value)}>
        {[...byTheme.entries()].map(([theme, list]) => (
          <optgroup key={theme} label={THEME_LABELS[theme] ?? theme}>
            {list.map((m) => (
              <option key={m.id} value={m.id} disabled={m.status === "planned"}>
                {m.label}
                {m.status === "planned" ? " (próximamente)" : ""}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </label>
  );
}
