"""TDD: HU-3 — hosteleria_share como métrica de barrio (OSM, snapshot curado)."""

import csv

from donostia_pipeline.datasets import tipologia_comercial as tc


def _write(tmp_path, rows):
    p = tmp_path / "tipologia_comercial_osm.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "barrio_id", "hosteleria", "n_comercios", "vacant", "n_locales_total",
            "hosteleria_share", "turistico_share_shops", "vacancy_rate", "source"])
        w.writeheader()
        w.writerows(rows)
    return p


def _row(bid, total, share):
    return {"barrio_id": bid, "hosteleria": int(total * share),
            "n_comercios": total - int(total * share), "vacant": 0,
            "n_locales_total": total, "hosteleria_share": share,
            "turistico_share_shops": 0.1, "vacancy_rate": 0.0, "source": "OSM"}


def test_metric_shape_and_theme(tmp_path):
    path = _write(tmp_path, [_row("gros", 498, 0.3635)])
    (m,) = tc.build_from_csv(path, {"gros"})
    assert m.id == "hosteleria_share"
    assert m.theme == "tourism"
    assert m.geo_grain == "barrio" and m.time_grain == "snapshot"
    # se guarda como porcentaje 0–100
    assert m.values["gros"]["actual"] == 36.4


def test_thin_barrios_nulled(tmp_path):
    path = _write(tmp_path, [
        _row("erdialdea", 952, 0.40),
        _row("miramon-zorroaga", 5, 1.0),   # tejido fino → artefacto
        _row("zubieta", 7, 0.86),
    ])
    (m,) = tc.build_from_csv(path, {"erdialdea", "miramon-zorroaga", "zubieta"})
    assert m.values["erdialdea"]["actual"] == 40.0
    assert m.values["miramon-zorroaga"]["actual"] is None   # < MIN_LOCALES
    assert m.values["zubieta"]["actual"] is None


def test_unknown_barrio_ignored(tmp_path):
    path = _write(tmp_path, [_row("gros", 498, 0.36), _row("noexiste", 50, 0.5)])
    (m,) = tc.build_from_csv(path, {"gros"})
    assert "noexiste" not in m.values


def test_build_reads_real_curated_snapshot():
    """Integración: lee el snapshot real del repo."""
    from donostia_pipeline import config
    (m,) = tc.build_from_csv(config.CURATED_DIR / tc.CSV, {
        "erdialdea", "gros", "amaraberri", "miramon-zorroaga"})
    # Parte Vieja/centro con dato; Miramón (tejido fino) nulo
    assert m.values["erdialdea"]["actual"] is not None
    assert m.values["miramon-zorroaga"]["actual"] is None
    assert m.confidence == "observed"  # provenance se aplica en build.run, no aquí
