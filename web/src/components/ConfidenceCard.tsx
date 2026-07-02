import type { Confidence } from "../lib/types";

interface Props {
  confidence: Confidence;
  assumptions?: string[];
}

const TIER: Record<Confidence, { label: string; hint: string }> = {
  observed: { label: "Osservato", hint: "Misurato direttamente dalla fonte." },
  derived: { label: "Derivato", hint: "Calcolato da metriche osservate." },
  proxy: { label: "Proxy", hint: "Approssimazione che sostituisce il dato reale." },
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
