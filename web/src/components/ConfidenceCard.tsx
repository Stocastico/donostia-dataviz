import type { Confidence } from "../lib/types";

interface Props {
  confidence: Confidence;
  assumptions?: string[];
}

const TIER: Record<Confidence, { label: string; hint: string }> = {
  observed: { label: "Observado", hint: "Medido directamente de la fuente." },
  derived: { label: "Derivado", hint: "Calculado a partir de métricas observadas." },
  proxy: { label: "Proxy", hint: "Aproximación que sustituye al dato real." },
};

/** MET-4 confidence card: a tier badge (observed/derived/proxy) plus the
 * metric's assumptions, so the dashboard's methodological care is visible. */
export function ConfidenceCard({ confidence, assumptions }: Props) {
  const tier = TIER[confidence];
  return (
    <div className="confidence-card">
      <span className={`confidence-badge conf-${confidence}`} title={tier.hint}>
        {tier.label}
      </span>
      {assumptions && assumptions.length > 0 && (
        <ul className="confidence-assumptions">
          {assumptions.map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
