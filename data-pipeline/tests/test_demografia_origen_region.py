"""TDD: REC-21 — population share by broad region of origin, per barrio."""

from conftest import write_csv

from donostia_pipeline.datasets import demografia_origen_region

FIXTURE = """
Urtea,AuzoKodea,Auzoa,Jatorria,PertsonenKop,PertsonenKopE,PertsonenKopG
2025,9,GROS,ESPAÑA,700,350,350
2025,9,GROS,HONDURAS,200,100,100
2025,9,GROS,MARRUECOS,100,50,50
2025,8,EGIA,ESPAÑA,900,450,450
2025,8,EGIA,ALEMANIA,100,50,50
2025,,Ezezaguna,ESPAÑA,5,0,0
"""

CODE_TO_ID = {"9": "gros", "8": "egia"}


def _values(metrics, region_id):
    by_id = {m.id: m for m in metrics}
    return by_id[f"pct_origin_{region_id}"].values


def test_pct_latam_share_of_barrio_population(make_ctx, tmp_path):
    write_csv(tmp_path, "demo_barrio.csv", FIXTURE)
    ctx = make_ctx(CODE_TO_ID)
    metrics = demografia_origen_region.build(ctx)
    latam = _values(metrics, "latam")
    assert latam["gros"]["2025"] == 20.0  # 200/1000
    assert "egia" not in latam or latam["egia"].get("2025") in (0.0, None)


def test_pct_norte_africa_and_europa_occidental(make_ctx, tmp_path):
    write_csv(tmp_path, "demo_barrio.csv", FIXTURE)
    ctx = make_ctx(CODE_TO_ID)
    metrics = demografia_origen_region.build(ctx)
    assert _values(metrics, "norte_africa")["gros"]["2025"] == 10.0  # 100/1000
    assert _values(metrics, "europa_occidental")["egia"]["2025"] == 10.0  # 100/1000


def test_eight_region_metrics_emitted(make_ctx, tmp_path):
    write_csv(tmp_path, "demo_barrio.csv", FIXTURE)
    ctx = make_ctx(CODE_TO_ID)
    metrics = demografia_origen_region.build(ctx)
    assert {m.id for m in metrics} == {
        "pct_origin_latam", "pct_origin_norte_africa", "pct_origin_africa_subsahariana",
        "pct_origin_europa_occidental", "pct_origin_europa_este", "pct_origin_oriente_medio",
        "pct_origin_asia", "pct_origin_norteamerica_oceania",
    }
    for m in metrics:
        assert m.kind == "sequential"
        assert m.theme == "demography"
        assert m.geo_grain == "barrio"


def test_unassigned_barrio_code_is_skipped(make_ctx, tmp_path):
    write_csv(tmp_path, "demo_barrio.csv", FIXTURE)
    ctx = make_ctx(CODE_TO_ID)
    metrics = demografia_origen_region.build(ctx)
    for m in metrics:
        assert "" not in m.values


def test_unclassified_country_does_not_crash(make_ctx, tmp_path):
    fixture = FIXTURE + "2025,9,GROS,NARNIA,50,25,25\n"
    write_csv(tmp_path, "demo_barrio.csv", fixture)
    ctx = make_ctx(CODE_TO_ID)
    metrics = demografia_origen_region.build(ctx)
    # Narnia isn't in any region -> doesn't inflate any bucket, doesn't error;
    # it still counts toward the population denominator (1050, not 1000).
    assert round(_values(metrics, "latam")["gros"]["2025"], 3) == round(200 / 1050 * 100, 3)
