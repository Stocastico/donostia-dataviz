#!/usr/bin/env python3
"""Convierte docs/WORKING-PAPER.md en una página HTML autocontenida.

La página se genera en el deploy (deploy-pages.yml), no se versiona: así el
HTML publicado nunca puede divergir del markdown, que es la fuente de verdad
y está atado por los candados de fact-check. El estilo replica la paleta y el
chrome (hero + nav) de output/metodologia.html para que el paper se lea como
una página hermana del resto del sitio.

Uso:  python scripts/build_working_paper.py --out _site/working-paper.html

Requiere el paquete `markdown` (pip install markdown).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "WORKING-PAPER.md"

# La nav enlaza a las páginas hermanas del sitio publicado: el paper vive en
# la raíz junto a historias/metodologia/datos, y la app React cuelga de app/.
TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Donostia en datos · Working paper</title>
<style>
  :root{{
    --ink:#14233a; --ink2:#3a4a63; --muted:#5f6e84; --line:#e2e7ef;
    --bg:#fbfcfe; --card:#ffffff; --sea:#1f6f8b; --sea-d:#0f4c5c;
    --coral:#d1495b; --amber:#e0902f; --green:#2a9d6f;
    --shadow:0 1px 2px rgba(20,35,58,.06),0 8px 28px rgba(20,35,58,.07);
    --maxw:900px;
  }}
  *{{box-sizing:border-box}}
  html{{scroll-behavior:smooth}}
  body{{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    line-height:1.65;-webkit-font-smoothing:antialiased;font-size:17px}}
  h1,h2,h3,h4{{line-height:1.18;letter-spacing:-.01em;color:var(--ink)}}
  a{{color:var(--sea)}}
  .wrap{{max-width:var(--maxw);margin:0 auto;padding:0 24px}}
  header.hero{{background:linear-gradient(160deg,#0f4c5c 0%,#1f6f8b 55%,#2a8aa8 100%);color:#eaf6fb;padding:56px 0 44px}}
  .hero .eyebrow{{text-transform:uppercase;letter-spacing:.18em;font-size:.74rem;font-weight:700;color:#bfe3ef;margin:0 0 12px}}
  .hero h1{{font-size:clamp(1.5rem,3.2vw,2.2rem);margin:0;color:#fff}}
  nav.toc{{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.92);backdrop-filter:saturate(140%) blur(8px);border-bottom:1px solid var(--line)}}
  nav.toc .wrap{{display:flex;gap:6px;flex-wrap:wrap;align-items:center;padding-top:10px;padding-bottom:10px}}
  nav.toc .brand{{font-weight:800;color:var(--sea-d);margin-right:auto;font-size:.95rem}}
  nav.toc a{{color:var(--ink2);text-decoration:none;font-size:.85rem;font-weight:600;padding:7px 12px;border-radius:999px}}
  nav.toc a:hover{{background:#eef4f8;color:var(--sea-d)}}
  main{{padding:40px 0 60px}}
  main h2{{font-size:1.45rem;margin:2.2em 0 .6em}}
  main h3{{font-size:1.12rem;margin:1.8em 0 .5em}}
  p{{color:var(--ink2)}}
  p strong,li strong{{color:var(--ink)}}
  ul,ol{{padding-left:1.2em}}
  li{{margin:.4em 0;color:var(--ink2)}}
  code{{background:#f0f4f9;border-radius:6px;padding:1px 6px;font-size:.85em}}
  blockquote{{margin:1.2em 0;padding:14px 22px;background:var(--card);border-left:4px solid var(--sea);
    border-radius:0 12px 12px 0;box-shadow:var(--shadow)}}
  blockquote p{{margin:.5em 0}}
  hr{{border:none;border-top:1px solid var(--line);margin:2.4em 0}}
  table{{border-collapse:collapse;width:100%;font-size:.9rem;display:block;overflow-x:auto;margin:1.2em 0}}
  th,td{{border:1px solid var(--line);padding:8px 12px;text-align:left;vertical-align:top;color:var(--ink2)}}
  th{{background:#eef4f8;color:var(--sea-d);font-size:.82rem;letter-spacing:.04em;text-transform:uppercase}}
  .fine{{font-size:.8rem;color:#7d93a8;margin-top:36px;border-top:1px solid var(--line);padding-top:16px}}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <p class="eyebrow">Donostia / San Sebastián · datos abiertos</p>
    <h1>{title}</h1>
  </div>
</header>

<nav class="toc">
  <div class="wrap">
    <span class="brand">Donostia en datos</span>
    <a href="historias.html">← Historias</a>
    <a href="metodologia.html">Metodología</a>
    <a href="datos.html">Datos y fuentes</a>
    <a href="app/">Panel interactivo</a>
  </div>
</nav>

<main>
<div class="wrap">
{body}
  <p class="fine">Generado automáticamente a partir de <code>docs/WORKING-PAPER.md</code> en cada
    despliegue del sitio · Proyecto Donostia Dataviz ·
    <a href="https://github.com/Stocastico/donostia-dataviz">código y pipeline en GitHub</a>.</p>
</div>
</main>

</body>
</html>
"""


def build_html(md_text: str) -> str:
    """Renderiza el markdown del paper dentro del chrome del sitio.

    El H1 del documento pasa al hero (como en las páginas hermanas); el resto
    del cuerpo se convierte tal cual, con tablas y anclas por sección.
    """
    lines = md_text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"{SOURCE} debe empezar con un título H1 ('# ...')")
    title = lines[0][2:].strip()
    body = markdown.markdown(
        "\n".join(lines[1:]),
        extensions=["tables", "toc"],
        output_format="html5",
    )
    return TEMPLATE.format(title=title, body=body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "_site" / "working-paper.html",
        help="ruta del HTML generado (por defecto _site/working-paper.html)",
    )
    args = parser.parse_args()
    html = build_html(SOURCE.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(f"OK: {args.out} ({len(html):,} bytes) desde {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
