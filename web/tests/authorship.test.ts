// Contrato de autoría: el sitio no puede ser una isla. Quien llega desde una
// red social a cualquiera de las páginas publicadas tiene que poder volver a
// stefanomasneri.com —el sitio del que este proyecto es una pieza— sin buscar:
// un enlace en la barra de navegación (visible con cualquier scroll) y una
// línea de autoría firmada en el pie. Son enlaces estáticos, así que se
// comprueban sobre el HTML crudo.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const out = (f: string) => readFileSync(resolve(here, "../../output", f), "utf-8");

const HOME = "https://stefanomasneri.com/";
const PAGES = ["historias.html", "metodologia.html", "datos.html"];

/** Recorta el HTML de la nav para poder afirmar «el enlace está en la barra»
 *  y no solo «está en algún sitio de la página». */
const navOf = (html: string) => {
  const start = html.search(/<nav[^>]*class=["']toc["']/i);
  if (start < 0) return "";
  const end = html.indexOf("</nav>", start);
  return end < 0 ? html.slice(start) : html.slice(start, end);
};

/** La línea de autoría del pie, marcada con class="author" en las tres páginas. */
const authorLineOf = (html: string) => {
  const start = html.search(/<p[^>]*class=["']author["']/i);
  if (start < 0) return "";
  const end = html.indexOf("</p>", start);
  return end < 0 ? html.slice(start) : html.slice(start, end);
};

describe.each(PAGES)("enlace a la web del autor — %s", (file) => {
  const html = out(file);

  it("enlaza a stefanomasneri.com desde la barra de navegación", () => {
    const nav = navOf(html);
    expect(nav, "no se encontró <nav class=toc>").not.toBe("");
    expect(nav).toContain(`href="${HOME}"`);
  });

  it("el enlace de la nav muestra el dominio como texto visible", () => {
    // Un «← inicio» no dice de quién es el sitio; el dominio sí.
    const nav = navOf(html);
    const link = nav.match(new RegExp(`<a[^>]*href="${HOME}"[^>]*>([^<]*)</a>`, "i"));
    expect(link, "el enlace de la nav no tiene texto visible").toBeTruthy();
    expect(link![1]).toContain("stefanomasneri.com");
  });

  it("firma la página en el pie con el nombre del autor enlazado", () => {
    const line = authorLineOf(html);
    expect(line, "no se encontró <p class=author> en el pie").not.toBe("");
    expect(line).toContain("Stefano Masneri");
    expect(line).toContain(`href="${HOME}"`);
  });
});
