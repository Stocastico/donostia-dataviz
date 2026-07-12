"""Candado de scripts/build_working_paper.py — el HTML publicado del paper.

El working paper se publica como HTML generado desde docs/WORKING-PAPER.md en
cada deploy (deploy-pages.yml). Este test fija el contrato mínimo de esa
página: conversión completa (sin restos de markdown), la nav del sitio con
sus cuatro hermanas y la tabla de fuentes renderizada como tabla.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

pytest.importorskip("markdown")

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "build_working_paper.py"

spec = importlib.util.spec_from_file_location("build_working_paper", SCRIPT)
bwp = importlib.util.module_from_spec(spec)
sys.modules["build_working_paper"] = bwp
spec.loader.exec_module(bwp)


@pytest.fixture(scope="module")
def html() -> str:
    return bwp.build_html(bwp.SOURCE.read_text(encoding="utf-8"))


def test_es_un_documento_html_completo(html):
    assert html.startswith("<!DOCTYPE html>")
    assert '<html lang="es">' in html
    assert "Donostia en datos · Working paper" in html


def test_titulo_del_md_va_al_hero(html):
    assert "Working paper — Método de un retrato reproducible" in html


def test_nav_enlaza_a_las_paginas_hermanas(html):
    for href in ("historias.html", "metodologia.html", "datos.html", 'href="app/"'):
        assert href in html, f"falta el enlace a {href} en la nav"


def test_sin_restos_de_markdown(html):
    # Si la conversión se rompe, el síntoma típico son marcas crudas.
    assert "\n## " not in html
    assert "**" not in html


def test_tabla_de_fuentes_renderizada(html):
    assert "<table>" in html
    assert "Padrón municipal" in html


def test_exige_h1_inicial():
    with pytest.raises(ValueError):
        bwp.build_html("sin titulo\n\ntexto")
