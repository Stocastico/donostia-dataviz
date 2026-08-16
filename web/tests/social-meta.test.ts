// Contract for social-sharing metadata and share buttons across the three
// published pages. A page shared on X/Bluesky/LinkedIn/Slack must render a card
// (Open Graph + Twitter tags, absolute image URL) and offer a discreet way to
// share it. These are static tags, so we assert on the raw HTML.
//
// El dominio importa tanto como las etiquetas: el sitio se publica bajo
// stefanomasneri.com y stocastico.github.io solo redirige (301) hacia allí. Si
// el canonical, og:url o los botones de compartir apuntan a github.io, Google
// puede indexar la copia equivocada y cada vez que alguien comparte la página
// promociona un dominio que no es el del autor.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const out = (f: string) => readFileSync(resolve(here, "../../output", f), "utf-8");

const SITE = "https://stefanomasneri.com/donostia-dataviz";
const OG_IMAGE = `${SITE}/og-cover.png`;

const PAGES: { file: string; url: string }[] = [
  { file: "historias.html", url: `${SITE}/` },
  { file: "metodologia.html", url: `${SITE}/metodologia.html` },
  { file: "datos.html", url: `${SITE}/datos.html` },
];

const meta = (html: string, prop: string, attr: "property" | "name") => {
  const re = new RegExp(`<meta[^>]+${attr}=["']${prop}["'][^>]*content=["']([^"']*)["']`, "i");
  const alt = new RegExp(`<meta[^>]+content=["']([^"']*)["'][^>]*${attr}=["']${prop}["']`, "i");
  return (html.match(re) ?? html.match(alt))?.[1] ?? null;
};

describe.each(PAGES)("metadatos sociales — $file", ({ file, url }) => {
  const html = out(file);

  it("tiene meta description no vacía", () => {
    const d = meta(html, "description", "name");
    expect(d, "falta <meta name=description>").toBeTruthy();
    expect(d!.length).toBeGreaterThan(30);
  });

  it("tiene Open Graph completo (title, description, type, url, image)", () => {
    expect(meta(html, "og:title", "property")).toBeTruthy();
    expect(meta(html, "og:description", "property")!.length).toBeGreaterThan(30);
    expect(meta(html, "og:type", "property")).toBe("website");
    expect(meta(html, "og:url", "property")).toBe(url);
    expect(meta(html, "og:image", "property")).toBe(OG_IMAGE);
    // Dimensiones declaradas: ayudan a los scrapers a no re-descargar.
    expect(meta(html, "og:image:width", "property")).toBe("1200");
    expect(meta(html, "og:image:height", "property")).toBe("630");
  });

  it("tiene Twitter card grande con imagen", () => {
    expect(meta(html, "twitter:card", "name")).toBe("summary_large_image");
    expect(meta(html, "twitter:image", "name")).toBe(OG_IMAGE);
  });

  it("declara la URL canónica", () => {
    expect(html).toMatch(new RegExp(`<link[^>]+rel=["']canonical["'][^>]+href=["']${url.replace(/[.]/g, "\\.")}["']`, "i"));
  });
});

describe.each(PAGES)("botones de compartir — $file", ({ file, url }) => {
  const html = out(file);
  const enc = encodeURIComponent(url);

  it("enlaza a X, Bluesky y LinkedIn con la URL de la propia página", () => {
    // X/Twitter intent
    expect(html).toMatch(/(twitter|x)\.com\/intent\/tweet\?[^"']*/i);
    // Bluesky compose intent
    expect(html).toContain("bsky.app/intent/compose");
    // LinkedIn share
    expect(html).toContain("linkedin.com/sharing/share-offsite");
    // Cada enlace lleva la URL de esta página (codificada)
    expect(html).toContain(enc);
  });

  it("los enlaces de compartir abren en pestaña nueva de forma segura", () => {
    // Al menos un rel con noopener en la zona de compartir.
    expect(html).toMatch(/rel=["'][^"']*noopener[^"']*["']/i);
  });
});

describe.each(PAGES)("dominio publicado — $file", ({ file }) => {
  const html = out(file);

  it("no menciona stocastico.github.io en ninguna URL", () => {
    // github.io solo redirige al dominio propio: dejar esas URLs en el HTML
    // reparte señal de SEO y enlaces sociales al sitio equivocado. (github.com,
    // el enlace al repositorio, sí es legítimo y no lo toca esta comprobación.)
    // Cubre también los intents de compartir: al percent-encodificar la URL
    // (…?url=https%3A%2F%2F…) el host viaja literal, sin escapar.
    expect(html).not.toContain("github.io");
  });
});
