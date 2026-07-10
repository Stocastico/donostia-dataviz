import { useEffect, useMemo, useState } from "react";
import { barriosGeoJSON, loadMetric } from "../lib/data";
import { valuesAtLatest } from "../lib/scatter";
import { pressureGaps, shareOfIncome } from "../lib/housing";
import { buildColorScale, NO_DATA_COLOR } from "../lib/colorScale";
import { formatValue } from "../lib/format";
import type { BarriosGeoJSON, MetricData, MetricKind } from "../lib/types";
import { BarrioMap } from "./BarrioMap";
import { Legend } from "./Legend";
import { MapDataTable } from "./MapDataTable";
import { rowsFromDecorated } from "../lib/mapTable";

const M2_OPTIONS = [20, 30, 40] as const;
type M2 = (typeof M2_OPTIONS)[number];
type MeasureId = "share" | "zgap" | "pctgap";

interface Measure {
  id: MeasureId;
  label: string;
  unit: string;
  kind: MetricKind;
  usesM2: boolean;
}
const MEASURES: Measure[] = [
  { id: "share", label: "Cuota de renta", unit: "%", kind: "sequential", usesM2: true },
  { id: "zgap", label: "Z-score (alquiler − renta)", unit: "z", kind: "diverging", usesM2: false },
  { id: "pctgap", label: "Percentil (alquiler − renta)", unit: "pp", kind: "diverging", usesM2: false },
];

const namesById: Record<string, string> = Object.fromEntries(
  barriosGeoJSON.features.map((f) => [f.properties.barrio_id, f.properties.name]),
);

/** Compute all three pressure measures over the joint sample (barrios with both
 * rent and income at their latest period), for a given m²/person. */
function computeMeasures(rentM: MetricData, incomeM: MetricData, m2: number) {
  const rv = valuesAtLatest(rentM);
  const iv = valuesAtLatest(incomeM);
  const ids = barriosGeoJSON.features
    .map((f) => f.properties.barrio_id)
    .filter((id) => rv[id] != null && iv[id] != null);
  const rent = ids.map((id) => rv[id] as number);
  const income = ids.map((id) => iv[id] as number);
  const { zGap, pctGap } = pressureGaps(rent, income);
  const out: Record<MeasureId, Record<string, number>> = { share: {}, zgap: {}, pctgap: {} };
  ids.forEach((id, k) => {
    out.share[id] = shareOfIncome(rent[k], income[k], m2);
    out.zgap[id] = zGap[k];
    out.pctgap[id] = pctGap[k];
  });
  return { ids, byMeasure: out };
}

/** Top-N barrios (most stressed = highest value) for a measure. */
function topN(values: Record<string, number>, n: number): string[] {
  return Object.entries(values)
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([id]) => id);
}

/** MET-1 / VIZ-4: housing pressure with a selectable m²/person assumption and a
 * "family of measures" that should agree on the most-stressed barrios. */
export function HousingPressureSection() {
  const [m2, setM2] = useState<M2>(30);
  const [measureId, setMeasureId] = useState<MeasureId>("share");
  const [rentM, setRentM] = useState<MetricData | null>(null);
  const [incomeM, setIncomeM] = useState<MetricData | null>(null);

  useEffect(() => { loadMetric("rent_eur_m2").then(setRentM); }, []);
  useEffect(() => { loadMetric("income_total").then(setIncomeM); }, []);

  const measure = MEASURES.find((m) => m.id === measureId)!;

  const computed = useMemo(
    () => (rentM && incomeM ? computeMeasures(rentM, incomeM, m2) : null),
    [rentM, incomeM, m2],
  );

  const { data, scale } = useMemo(() => {
    if (!computed) return { data: barriosGeoJSON, scale: null };
    const vById = computed.byMeasure[measureId];
    const s = buildColorScale(Object.values(vById), measure.kind);
    const features = barriosGeoJSON.features.map((f) => {
      const id = f.properties.barrio_id;
      const v = vById[id];
      const has = v != null && Number.isFinite(v);
      return {
        ...f,
        properties: {
          ...f.properties,
          __value: has ? v : null,
          __color: has ? s.color(v) : NO_DATA_COLOR,
          __valueLabel: has ? formatValue(v, measure.unit) : "n/d",
          __deltaLabel: "",
        },
      };
    });
    return { data: { ...barriosGeoJSON, features } as BarriosGeoJSON, scale: s };
  }, [computed, measureId, measure]);

  // Family-of-measures agreement: top-5 most stressed under each measure.
  const family = useMemo(() => {
    if (!computed) return null;
    const tops = {
      share: topN(computed.byMeasure.share, 5),
      zgap: topN(computed.byMeasure.zgap, 5),
      pctgap: topN(computed.byMeasure.pctgap, 5),
    };
    const all = new Set(tops.share);
    const common = new Set(
      [...all].filter((id) => tops.zgap.includes(id) && tops.pctgap.includes(id)),
    );
    return { tops, common };
  }, [computed]);

  return (
    <section className="housing">
      <div className="scatter-head">
        <h2>Presión del alquiler sobre el residente medio</h2>
        <div className="housing-controls">
          <div className="housing-measure">
            <span className="control-label">Medida</span>
            <select value={measureId} onChange={(e) => setMeasureId(e.target.value as MeasureId)}>
              {MEASURES.map((m) => (
                <option key={m.id} value={m.id}>{m.label}</option>
              ))}
            </select>
          </div>
          <div className="housing-m2">
            <span className="control-label" id="m2-label">m²/persona</span>
            <div className="m2-buttons" role="group" aria-labelledby="m2-label">
              {M2_OPTIONS.map((v) => (
                <button
                  key={v}
                  type="button"
                  className={`chip ${v === m2 ? "on" : ""}`}
                  aria-pressed={v === m2}
                  onClick={() => setM2(v)}
                  disabled={!measure.usesM2}
                  title={measure.usesM2 ? "" : "Solo influye en la cuota de renta"}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <p className="scatter-sub">
        No es "el porcentaje de renta que gasta un hogar", sino una{" "}
        <strong>presión teórica sobre el residente medio</strong>, comparable entre
        barrios. El parámetro m²/persona es <strong>explícito y regulable</strong>{" "}
        (20/30/40) en vez de estar oculto: cambia solo la <em>cuota de renta</em>; las
        otras dos medidas (z-score y percentil) no dependen de él. Las tres medidas
        miran cosas distintas: la <em>cuota de renta</em> mide el esfuerzo de
        accesibilidad (dominado por la renta baja → el este obrero); los{" "}
        <em>desajustes estandarizados</em> miden cuánto corre el alquiler por delante
        de la renta (e iluminan también el centro caro). Los barrios señalados por{" "}
        <strong>las tres</strong> son los que están bajo presión se mida como se
        mida.
      </p>

      <div className="bivariate-body">
        <div
          className="map-area"
          role="img"
          aria-label={`Mapa coroplético: ${measure.label}. Datos en la tabla de abajo.`}
        >
          {scale ? (
            <>
              <BarrioMap data={data} />
              <Legend scale={scale} unit={measure.unit} />
              <MapDataTable
                rows={rowsFromDecorated(data)}
                label={measure.label}
                unit={measure.unit}
              />
            </>
          ) : (
            <div className="map-placeholder">Cargando datos…</div>
          )}
        </div>
        {family && (
          <div className="housing-family">
            <span className="control-label">Barrios bajo más presión (top 5)</span>
            <div className="family-cols">
              {MEASURES.map((m) => (
                <div key={m.id} className="family-col">
                  <h4>{m.label}</h4>
                  <ol>
                    {family.tops[m.id].map((id) => (
                      <li key={id} className={family.common.has(id) ? "common" : ""}>
                        {namesById[id] ?? id}
                      </li>
                    ))}
                  </ol>
                </div>
              ))}
            </div>
            <p className="family-note">
              En <strong>negrita</strong>, los barrios en el top 5 de <em>las tres</em>
              medidas: la presión ahí no es un artefacto ni del parámetro m² ni
              de la fórmula elegida. Las listas no coinciden del todo — y ese es el punto:
              esfuerzo de renta y desajuste alquiler-renta no son lo mismo.
            </p>
          </div>
        )}
      </div>

      <p className="source-note">
        Fuentes: {rentM?.source}
        {incomeM && incomeM.source !== rentM?.source ? ` · ${incomeM.source}` : ""}
      </p>
    </section>
  );
}
