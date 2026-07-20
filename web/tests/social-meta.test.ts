// Contract for social-sharing metadata and share buttons across the three
// published pages. A page shared on X/Bluesky/LinkedIn/Slack must render a card
// (Open Graph + Twitter tags, absolute image URL) and offer a discreet way to
// share it. These are static tags, so we assert on the raw HTML.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const out = (f: string) => readFileSync(resolve(here, "../../output", f), "utf-8");

const SITE = "https://stocastico.github.io/donostia-dataviz";
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
