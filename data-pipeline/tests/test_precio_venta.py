"""TDD: REC-25 — sale price €/m² per barrio from the curated idealista CSV."""

from donostia_pipeline.datasets import precio_venta as pv

BARRIOS = {
    "amaraberri", "gros", "antigua", "egia", "intxaurrondo", "ategorrieta-ulia",
    "aiete", "anorga", "ibaeta", "altza", "mirakruz-bidebieta", "erdialdea",
}


def _rows(*triples):
    return [
        {"zona_idealista": z, "mes": m, "precio_eur_m2": str(p)}
        for z, m, p in triples
    ]


def test_metric_basic_shape():
    rows = _rows(
        ("Amara", "2011-01", 4000), ("Amara", "2011-02", 4100), ("Amara", "2011-03", 4300),
    )
    (m,) = pv.build_from_rows(rows, BARRIOS)
    assert m.id == "sale_price_eur_m2"
    assert m.unit == "€/m²"
    assert m.theme == "housing"
    assert m.geo_grain == "barrio" and m.time_grain == "year"
    assert m.periods == ["2011"]
    # calendar-year mean of the three months
    assert m.values["amaraberri"]["2011"] == round((4000 + 4100 + 4300) / 3)


def test_year_needs_min_months():
    rows = _rows(("Amara", "2011-01", 4000), ("Amara", "2011-02", 4200))  # only 2
    (m,) = pv.build_from_rows(rows, BARRIOS)
    assert "amaraberri" not in m.values  # < MIN_MONTHS → year dropped, no data


def test_years_before_first_year_dropped():
    rows = _rows(
        ("Amara", "2010-10", 3000), ("Amara", "2010-11", 3000), ("Amara", "2010-12", 3000),
        ("Amara", "2011-01", 4000), ("Amara", "2011-02", 4000), ("Amara", "2011-03", 4000),
    )
    (m,) = pv.build_from_rows(rows, BARRIOS)
    assert m.periods == ["2011"]  # 2010 partial tail excluded


def test_zone_spanning_many_barrios_shares_value():
    rows = _rows(
        ("Aiete-Anorga-Ibaeta", "2011-01", 4200),
        ("Aiete-Anorga-Ibaeta", "2011-02", 4200),
        ("Aiete-Anorga-Ibaeta", "2011-03", 4200),
    )
    (m,) = pv.build_from_rows(rows, BARRIOS)
    for bid in ("aiete", "anorga", "ibaeta"):
        assert m.values[bid]["2011"] == 4200


def test_erdialdea_uses_centro_not_parte_vieja():
    rows = _rows(
        ("Centro-Miraconcha", "2011-01", 8000), ("Centro-Miraconcha", "2011-02", 8000),
        ("Centro-Miraconcha", "2011-03", 8000),
        ("Parte Vieja", "2011-01", 6000), ("Parte Vieja", "2011-02", 6000),
        ("Parte Vieja", "2011-03", 6000),
    )
    (m,) = pv.build_from_rows(rows, BARRIOS)
    assert m.values["erdialdea"]["2011"] == 8000  # Centro-Miraconcha, not Parte Vieja


def test_build_reads_real_curated_snapshot():
    """Integración: lee el CSV real del repo y cruza a barrios oficiales."""
    from donostia_pipeline import config

    path = config.CURATED_DIR / pv.CSV_NAME
    with path.open(encoding="utf-8", newline="") as fh:
        import csv

        rows = list(csv.DictReader(fh))
    (m,) = pv.build_from_rows(rows, BARRIOS)
    # centro is the priciest; the east is cheaper; rural/broken zones absent.
    assert m.values["erdialdea"]["2025"] > m.values["intxaurrondo"]["2025"]
    assert "loiola" not in m.values and "martutene" not in m.values
    assert "miramon-zorroaga" not in m.values
    assert m.confidence == "observed"  # provenance applied in build.run, not here
