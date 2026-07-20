// Fact-check automatizado de output/historias.html.
//
// Cada cifra que el relato cita en texto (keynums, pasos del scrolly, párrafos)
// y que es derivable del blob embebido `window.DONO` se re-deriva aquí y se
// compara con el valor citado, redondeado a la precisión con que el texto lo
// cita. Si el pipeline regenera el blob y el texto se queda atrás, esta suite
// falla señalando la cifra exacta — es la red contra la desincronización
// dato↔narrativa (el modo de fallo real: el refresco del snapshot 2026-06 dejó
// rancios los scores de presión turística del cap. 7).
//
// Cobertura: solo afirmaciones derivables del blob. Las que salen de
// analysis/*.py sin datos en DONO (correlación −0,89 sin el centro, +29 % del
// alquiler de Erdialdea desde 2016, cifras EPA/REATE/Etxebide…) se verifican en
// los tests de sus scripts, no aquí.
import { beforeAll, describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const htmlPath = resolve(here, "../../output/historias.html");

interface MetricValue { v: number; period: string }
interface Dono {
  pressure_inputs: Record<string, { rent: number; income: number; income_labor: number; name: string }>;
  velocity: Record<string, Record<string, number>>;
  ageing_series: Record<string, Record<string, number>>;
  youth_series: Record<string, Record<string, number>>;
  airbnb_density: Record<string, number>;
  metrics: Record<string, Record<string, MetricValue>>;
  transform: { socio: Record<string, number>; tourism: Record<string, number> };
  tourism_index: { airbnb: Record<string, number>; hotel: Record<string, number> };
  climate: { reg: Record<string, number[]> };
  an5: { year: number; gini: number; gini_pond: number }[];
  leadlag: { lag: number; r: number }[];
  work: {
    jobs_located: Record<string, number>;
    concentration: Record<string, number>;
    resident_work_pct: Record<string, number>;
  };
}

let D: Dono;

// El texto cita valores redondeados: comparar a la precisión de la cita.
const r0 = (v: number) => Math.round(v);
const r1 = (v: number) => Math.round(v * 10) / 10;
const r2 = (v: number) => Math.round(v * 100) / 100;
// Esfuerzo teórico del cap. 1 (MET-1), mismo cálculo que renderPress().
const cuota = (k: string, m2 = 30) => {
  const o = D.pressure_inputs[k];
  return (o.rent * 12 * m2) / o.income * 100;
};
const pearson = (xs: number[], ys: number[]) => {
  const mean = (a: number[]) => a.reduce((s, v) => s + v, 0) / a.length;
  const mx = mean(xs), my = mean(ys);
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < xs.length; i++) {
    num += (xs[i] - mx) * (ys[i] - my);
    dx += (xs[i] - mx) ** 2;
    dy += (ys[i] - my) ** 2;
  }
  return num / Math.sqrt(dx * dy);
};

beforeAll(() => {
  const html = readFileSync(htmlPath, "utf-8");
  const m = html.match(/window\.DONO\s*=\s*(\{.*)/);
  if (!m) throw new Error("blob window.DONO no encontrado");
  const json = m[1].split("</script>")[0].trim().replace(/;$/, "");
  D = JSON.parse(json) as Dono;
});

describe("cap. 1 — la ciudad que se encarece", () => {
  it("esfuerzo con 30 m²: Altza 21,9 % · Egia 21,3 % · Intxaurrondo 20,9 %", () => {
    expect(r1(cuota("altza"))).toBe(21.9);
    expect(r1(cuota("egia"))).toBe(21.3);
    expect(r1(cuota("intxaurrondo"))).toBe(20.9);
  });

  it("el este obrero encabeza el ranking de esfuerzo (paso 1 del scrolly)", () => {
    const sorted = Object.keys(D.pressure_inputs).sort((a, b) => cuota(b) - cuota(a));
    expect(sorted.slice(0, 3).sort()).toEqual(["altza", "egia", "intxaurrondo"]);
  });

  // Blindaje MET-1: la renta per cápita total incluye pensiones y capital, muy
  // presentes en el centro envejecido. Re-derivar el esfuerzo con la renta *del
  // trabajo* invierte el ranking — el centro pasa a encabezarlo. El dato debe
  // estar embebido y el hallazgo debe mantenerse mientras el blob no cambie.
  const cuotaLabor = (k: string, m2 = 30) => {
    const o = D.pressure_inputs[k];
    return (o.rent * 12 * m2) / o.income_labor * 100;
  };
  it("embebe income_labor (renta del trabajo) para cada barrio con presión", () => {
    for (const k of Object.keys(D.pressure_inputs)) {
      expect(typeof D.pressure_inputs[k].income_labor, `income_labor de ${k}`).toBe("number");
      expect(D.pressure_inputs[k].income_labor).toBeGreaterThan(0);
      // La renta del trabajo es un subconjunto de la total.
      expect(D.pressure_inputs[k].income_labor).toBeLessThanOrEqual(D.pressure_inputs[k].income);
    }
  });
  it("con renta del trabajo el esfuerzo se invierte: Erdialdea y Gros encabezan", () => {
    const sorted = Object.keys(D.pressure_inputs).sort((a, b) => cuotaLabor(b) - cuotaLabor(a));
    expect(sorted.slice(0, 2).sort()).toEqual(["erdialdea", "gros"]);
    expect(r1(cuotaLabor("erdialdea"))).toBe(35.7);
    expect(r1(cuotaLabor("gros"))).toBe(34.9);
  });

  it("Gini ponderado «estable (~0,10)»", () => {
    const pond = D.an5.map((r) => r.gini_pond);
    expect(r2(pond[pond.length - 1])).toBeGreaterThanOrEqual(0.09);
    expect(r2(pond[pond.length - 1])).toBeLessThanOrEqual(0.11);
    expect(Math.max(...pond) - Math.min(...pond)).toBeLessThan(0.03); // «estable»
  });
});

describe("cap. 2 — velocidades", () => {
  it("alquiler: Loiola +4,3 %/año, la mayor", () => {
    expect(r1(D.velocity.loiola.rent_eur_m2)).toBe(4.3);
    const max = Math.max(...Object.values(D.velocity).map((v) => v.rent_eur_m2 ?? -Infinity));
    expect(D.velocity.loiola.rent_eur_m2).toBe(max);
  });

  it("población: Gros −0,60 · Antiguo −0,45 · Egia −0,33 %/año", () => {
    expect(r2(D.velocity.gros.population)).toBe(-0.6);
    expect(r2(D.velocity.antigua.population)).toBe(-0.45);
    expect(r2(D.velocity.egia.population)).toBe(-0.33);
  });

  it("% extranjeros: Intxaurrondo +0,92 pp/año, el más rápido", () => {
    expect(r2(D.velocity.intxaurrondo.pct_foreign)).toBe(0.92);
    const max = Math.max(...Object.values(D.velocity).map((v) => v.pct_foreign ?? -Infinity));
    expect(D.velocity.intxaurrondo.pct_foreign).toBe(max);
  });

  it("scatter VUT×alquiler: r = 0,64", () => {
    const vd = D.metrics.vut_density, rent = D.metrics.rent_eur_m2;
    const ks = Object.keys(vd).filter((k) => k in rent);
    expect(r2(pearson(ks.map((k) => vd[k].v), ks.map((k) => rent[k].v)))).toBe(0.64);
  });
});

describe("cap. 3 — quién vive Donostia", () => {
  it("índice de vejez 2025: Gros 370 · Erdialdea 350", () => {
    expect(r0(D.ageing_series.gros["2025"])).toBe(370);
    expect(r0(D.ageing_series.erdialdea["2025"])).toBe(350);
  });

  it("Antiguo sube +203 puntos entre 2000 y 2025", () => {
    expect(r0(D.ageing_series.antigua["2025"] - D.ageing_series.antigua["2000"])).toBe(203);
  });

  it("adultos jóvenes 2025: Intxaurrondo 21 %", () => {
    expect(r0(D.youth_series.intxaurrondo["2025"])).toBe(21);
  });
});

describe("cap. 4 — quién trabaja Donostia", () => {
  it("empleos localizados: crecen de ~66.000 (1995) a ~103.000 (2025)", () => {
    const w = D.work.jobs_located;
    const years = Object.keys(w).sort();
    expect(w[years[0]]).toBeGreaterThan(60000);
    expect(w[years[0]]).toBeLessThan(70000);
    expect(w[years[years.length - 1]]).toBe(103446);
  });

  it("ratio de concentración de empleo > 1 siempre y ~1,20 en 2024 (importa trabajadores)", () => {
    const c = D.work.concentration;
    for (const y of Object.keys(c)) expect(c[y], `ratio ${y}`).toBeGreaterThan(1);
    expect(r2(c["2024"])).toBe(1.2);
  });

  it("~66 % de los ocupados residentes trabajan en la propia ciudad (2024)", () => {
    expect(r0(D.work.resident_work_pct["2024"])).toBe(66);
  });

  it("brecha de renta de género (2023): mínima en los barrios densos y jóvenes, máxima en los pequeños/residenciales", () => {
    const g = D.metrics.income_gender_gap;
    const val = (k: string) => g[k].v;
    // El menor gap de toda la ciudad es Egia; Igeldo (rural, muestra pequeña) el mayor.
    const sorted = Object.keys(g).sort((a, b) => val(a) - val(b));
    expect(sorted[0]).toBe("egia");
    expect(sorted[sorted.length - 1]).toBe("igeldo");
    // Patrón robusto entre barrios urbanos: joven/mixto < acomodado/tradicional.
    expect(val("egia")).toBeLessThan(val("aiete"));
    expect(val("intxaurrondo")).toBeLessThan(val("antigua"));
  });
});

describe("cap. 4 — el clima (Igeldo)", () => {
  it("tendencia +0,31 °C/década (R²=0,39) y +0,81 días ≥30 °C/década", () => {
    expect(r2(D.climate.reg.temp_avg[0])).toBe(0.31);
    expect(r2(D.climate.reg.temp_avg[3])).toBe(0.39);
    expect(r2(D.climate.reg.hot_days[0])).toBe(0.81);
  });
});

describe("cap. 6 — las dos ciudades", () => {
  it("densidad Airbnb: Erdialdea ~33/1000 · Gros ~18/1000, y el máximo es Erdialdea", () => {
    expect(r0(D.airbnb_density.erdialdea)).toBe(33);
    expect(r0(D.airbnb_density.gros)).toBe(18);
    const max = Math.max(...Object.values(D.airbnb_density));
    expect(D.airbnb_density.erdialdea).toBe(max);
  });

  it("índice 2016=100: Airbnb ×6,6 en 2025; hotel ×1,7", () => {
    expect(r1(D.tourism_index.airbnb["2025"] / 100)).toBe(6.6);
    expect(r1(D.tourism_index.hotel["2025"] / 100)).toBe(1.7);
  });

  it("lead/lag: r≈0,27 con el turismo un año por delante, y es el máximo", () => {
    const plus1 = D.leadlag.find((d) => d.lag === 1)!;
    expect(r2(plus1.r)).toBe(0.27);
    expect(Math.max(...D.leadlag.map((d) => d.r))).toBe(plus1.r);
  });
});

describe("cap. 7 — índice de transformación", () => {
  it("Loiola es el único «en transformación» social, score 1,02", () => {
    expect(r2(D.transform.socio.loiola)).toBe(1.02);
  });

  it("presión turística: Erdialdea +2,48 (máximo) · Gros +1,39", () => {
    expect(r2(D.transform.tourism.erdialdea)).toBe(2.48);
    expect(r2(D.transform.tourism.gros)).toBe(1.39);
    const max = Math.max(...Object.values(D.transform.tourism));
    expect(D.transform.tourism.erdialdea).toBe(max);
  });

  it("Aiete: presión turística 0,06 — caro pero no turístico", () => {
    expect(r2(D.transform.tourism.aiete)).toBe(0.06);
  });
});

describe("el texto cita los valores vigentes del blob", () => {
  // Los keynums/párrafos del cap. 7 quedaron rancios una vez (blob 2026-06 vs
  // texto): estas comprobaciones de literal impiden que vuelva a pasar.
  let html: string;
  beforeAll(() => { html = readFileSync(htmlPath, "utf-8"); });

  const cita = (esperado: string, ...literales: string[]) =>
    it(`el texto dice ${esperado}`, () => {
      for (const lit of literales) expect(html).toContain(lit);
    });

  cita("Erdialdea +2,48 y Gros +1,39 (presión turística)", "+2,48", "+1,39");
  cita("Aiete 0,06", ">0,06<");
  cita("Altza 21,9 % de esfuerzo", "21,9");
  cita("Gros 370 de índice de vejez", "370");
  cita("r = 0,64 del scatter", "0,64");
});
