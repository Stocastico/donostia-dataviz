// Contract tests for output/historias.html (self-contained narrative document).
//
// The document runs its inline scripts under jsdom here, so these tests assert
// the *rendered* DOM, not just the markup: every scatter point must be
// identifiable, the scrollytelling steps must drive the map state, and the
// metric explainers must exist. IntersectionObserver does not exist in jsdom;
// the document must degrade gracefully and expose window.__scrollyActivate so
// steps can be driven programmatically (tests and keyboard users alike).
import { beforeAll, describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { JSDOM } from "jsdom";

const here = dirname(fileURLToPath(import.meta.url));
const htmlPath = resolve(here, "../../output/historias.html");

type ScrollyWindow = Window & {
  __scrollyActivate?: (step: Element) => void;
};

let doc: Document;
let win: ScrollyWindow;

beforeAll(() => {
  const html = readFileSync(htmlPath, "utf-8");
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true });
  doc = dom.window.document;
  win = dom.window as unknown as ScrollyWindow;
});

describe("scatter «Donde hay turismo, hay alquileres altos»", () => {
  it("labels every barrio circle so points are identifiable", () => {
    const svg = doc.getElementById("scatter")!;
    const circles = svg.querySelectorAll("circle");
    expect(circles.length).toBeGreaterThanOrEqual(10);
    // Every circle must have a text label with a barrio name (non-numeric text).
    const labels = [...svg.querySelectorAll("text")]
      .map((t) => t.textContent ?? "")
      .filter((t) => t.length > 1 && !/^[\d\s.,%€rR=−+-]+$/.test(t) && !t.startsWith("Densidad") && !t.startsWith("Alquiler") && !t.startsWith("Perfil"));
    expect(labels.length).toBeGreaterThanOrEqual(circles.length);
    // The low-density cluster (east) was previously unlabelled — spot-check it.
    for (const name of ["Altza", "Intxaurrondo", "Martutene"]) {
      expect(labels.some((l) => l.includes(name)), `missing label ${name}`).toBe(true);
    }
  });

  it("colours the circles by the profile palette of the previous figure (colour carries meaning)", () => {
    const svg = doc.getElementById("scatter")!;
    const fills = new Set(
      [...svg.querySelectorAll("circle")].map((c) => c.getAttribute("fill")),
    );
    // More than one fill: colour encodes the barrio profile, not decoration.
    expect(fills.size).toBeGreaterThan(1);
  });
});

describe("scrollytelling", () => {
  it("has at least five scrolly groups, each with steps and a sticky figure", () => {
    const groups = [...doc.querySelectorAll("[data-scrolly]")];
    expect(groups.length).toBeGreaterThanOrEqual(5);
    for (const g of groups) {
      expect(g.querySelectorAll(".step").length, `steps in ${g.getAttribute("data-scrolly")}`).toBeGreaterThanOrEqual(2);
      expect(g.querySelector(".scrolly-fig"), `figure in ${g.getAttribute("data-scrolly")}`).toBeTruthy();
    }
  });

  it("exposes __scrollyActivate and a press step switches the measure", () => {
    expect(typeof win.__scrollyActivate).toBe("function");
    const step = doc.querySelector('[data-scrolly="press"] .step[data-measure="zgap"]')!;
    expect(step).toBeTruthy();
    win.__scrollyActivate!(step);
    const active = doc.querySelector<HTMLElement>("#measure button.active")!;
    expect(active.dataset.m).toBe("zgap");
    expect(step.classList.contains("active")).toBe(true);
  });

  it("an age step scrubs the year slider", () => {
    const step = doc.querySelector('[data-scrolly="age"] .step[data-year="2000"]')!;
    expect(step).toBeTruthy();
    win.__scrollyActivate!(step);
    expect(doc.getElementById("yearval")!.textContent).toBe("2000");
    expect((doc.getElementById("year") as HTMLInputElement).value).toBe("2000");
  });

  it("a velocity step switches the indicator", () => {
    const step = doc.querySelector('[data-scrolly="vel"] .step[data-velk="population"]')!;
    expect(step).toBeTruthy();
    win.__scrollyActivate!(step);
    expect(doc.querySelector<HTMLElement>("#velsel button.active")!.dataset.k).toBe("population");
    expect(step.classList.contains("active")).toBe(true);
  });

  it("an origins step switches the region and a tourism step switches the source", () => {
    const org = doc.querySelector('[data-scrolly="org"] .step[data-orgk="europa_occidental"]')!;
    expect(org).toBeTruthy();
    win.__scrollyActivate!(org);
    expect(doc.querySelector<HTMLElement>("#orgsel button.active")!.dataset.k).toBe("europa_occidental");

    const tour = doc.querySelector('[data-scrolly="tour"] .step[data-tourk="vut"]')!;
    expect(tour).toBeTruthy();
    win.__scrollyActivate!(tour);
    expect(doc.querySelector<HTMLElement>("#toursel button.active")!.dataset.k).toBe("vut");
  });

  it("manual controls still work after a scrolly step (bidirectional state)", () => {
    const btn = [...doc.querySelectorAll<HTMLElement>("#measure button")].find((b) => b.dataset.m === "cuota")!;
    btn.click();
    expect(doc.querySelector<HTMLElement>("#measure button.active")!.dataset.m).toBe("cuota");
  });
});

describe("accesibilidad", () => {
  // Cada gráfico es un <svg> dibujado por JS; para un lector de pantalla debe
  // anunciar QUÉ es (role="img" + aria-label). Un gráfico añadido más tarde que
  // olvide su etiqueta falla aquí.
  it("gives every svg.map role=\"img\" and a non-empty aria-label", () => {
    const maps = [...doc.querySelectorAll("svg.map")];
    expect(maps.length).toBeGreaterThanOrEqual(40);
    const missing = maps
      .filter((s) => s.getAttribute("role") !== "img" || !(s.getAttribute("aria-label") ?? "").trim())
      .map((s) => s.id || "(sin id)");
    expect(missing, `SVGs sin role/aria-label: ${missing.join(", ")}`).toEqual([]);
  });

  it("offers a skip link that targets the main landmark", () => {
    const skip = doc.querySelector('a[href="#main"]');
    expect(skip, "falta el enlace «saltar al contenido»").toBeTruthy();
    expect((skip!.textContent ?? "").trim().length).toBeGreaterThan(0);
    expect(doc.getElementById("main"), 'el <main> necesita id="main"').toBeTruthy();
  });

  it("labels the sticky section nav", () => {
    const nav = doc.querySelector("nav.toc");
    expect(nav).toBeTruthy();
    expect((nav!.getAttribute("aria-label") ?? "").trim().length).toBeGreaterThan(0);
  });
});

describe("metric explainers and text", () => {
  it("explains the complex metrics in plain language boxes", () => {
    const expl = doc.querySelectorAll(".metric-expl");
    expect(expl.length).toBeGreaterThanOrEqual(4);
    const all = [...expl].map((e) => e.textContent ?? "").join(" ");
    // The four metrics readers stumble on: z-scores, Gini, k-means, Pearson r.
    expect(all).toMatch(/desviaci/i); // z-score explained via desviaciones típicas
    expect(all).toMatch(/Gini/);
    expect(all).toMatch(/k-means|grupos|perfiles/i);
    expect(all).toMatch(/correlaci/i);
  });

  it("keeps the story count consistent (no stale «Seis relatos»)", () => {
    expect(doc.body.textContent).not.toContain("Seis relatos");
  });
});
