import { indicators } from "../lib/data";
import { IndicatorTrendChart } from "./IndicatorTrendChart";

/** Section for annual city indicators that aren't the MICE ones (which have
 * their own bespoke section) — e.g. the recycling rate. Each shown as a line
 * chart. Hidden if there are none. */
export function IndicatorsSection() {
  const generic = indicators.filter((i) => !i.id.startsWith("mice_"));
  if (generic.length === 0) return null;

  return (
    <section className="indicators">
      <h2>Altri indicatori cittadini</h2>
      <div className="indicators-grid">
        {generic.map((ind) => (
          <IndicatorTrendChart key={ind.id} indicator={ind} />
        ))}
      </div>
    </section>
  );
}
