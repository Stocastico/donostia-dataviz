"""TDD: derived touristic-housing density per 1000 inhabitants.

Combines the VUT census (units per barrio) with the latest-year population from
the demographics file -> units / population * 1000.
"""

from conftest import write_csv

from donostia_pipeline.datasets import vut_density

VUT_FIXTURE = """
Auzoa,helbidea,Mota,plazak
GROS,addr1,VUT,4
GROS,addr2,HUT,2
EGIA,addr3,VUT,3
"""

# Two years present; density must use the LATEST (2025), not 2020.
DEMO_FIXTURE = """
Urtea,AuzoKodea,Auzoa,Jatorria,PertsonenKop,PertsonenKopE,PertsonenKopG
2020,9,GROS,ESPAÑA,99999,0,0
2025,9,GROS,ESPAÑA,800,400,400
2025,9,GROS,FRANCIA,200,100,100
2025,8,EGIA,ESPAÑA,250,125,125
2025,1,AIETE,ESPAÑA,500,250,250
"""

CODE_TO_ID = {"9": "gros", "8": "egia", "1": "aiete"}


def _build(make_ctx):
    ctx = make_ctx(CODE_TO_ID)
    write_csv(ctx.raw_dir, "vtur_censo.csv", VUT_FIXTURE)
    write_csv(ctx.raw_dir, "demo_barrio.csv", DEMO_FIXTURE)
    return {m.id: m for m in vut_density.build(ctx)}


def test_density_uses_latest_year_population(make_ctx):
    m = _build(make_ctx)["vut_density"]
    assert m.periods == ["actual"]
    assert m.time_grain == "snapshot"
    # gros: 2 units / 1000 people * 1000 = 2.0  (1000 = 800 + 200, year 2025)
    assert m.values["gros"]["actual"] == 2.0
    # egia: 1 unit / 250 * 1000 = 4.0
    assert m.values["egia"]["actual"] == 4.0


def test_populated_barrio_without_vut_is_zero(make_ctx):
    m = _build(make_ctx)["vut_density"]
    assert m.values["aiete"]["actual"] == 0.0


def test_metric_metadata(make_ctx):
    m = _build(make_ctx)["vut_density"]
    assert m.unit == "per 1000 ab."
    assert m.kind == "sequential"
    assert m.theme == "tourism"
