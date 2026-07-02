"""TDD: share of university-educated population per barrio (datasets.estudios)."""

from conftest import write_csv

from donostia_pipeline.datasets import estudios

# Urtea,AuzoKodea,Auzoa,Ikasketak_eu,Ikasketak_es,Ehuneko_Totala,EhunekoE,EhunekoG
FIXTURE = """
Urtea,AuzoKodea,Auzoa,Ikasketak_eu,Ikasketak_es,Ehuneko_Totala,EhunekoE,EhunekoG
2020,9,GROS,UNIBERTSITATE,UNIVERSITARIOS,0.35,0.36,0.34
2020,9,GROS,BIGARREN,SECUNDARIOS,0.20,0.20,0.20
2021,9,GROS,UNIBERTSITATE,UNIVERSITARIOS,0.40,0.41,0.39
2020,8,EGIA,UNIBERTSITATE,UNIVERSITARIOS,0.25,0.26,0.24
2020,99,X,UNIBERTSITATE,UNIVERSITARIOS,0.99,0.99,0.99
"""

CODE_TO_ID = {"9": "gros", "8": "egia"}


def _build(make_ctx):
    write_csv(make_ctx({}).raw_dir, "estudios_barrio.csv", FIXTURE)
    return {m.id: m for m in estudios.build(make_ctx(CODE_TO_ID))}


def test_pct_university_is_proportion_times_100(make_ctx):
    m = _build(make_ctx)["pct_university"]
    assert m.unit == "%"
    assert m.periods == ["2020", "2021"]
    assert m.values["gros"] == {"2020": 35.0, "2021": 40.0}
    assert m.values["egia"] == {"2020": 25.0}


def test_only_university_rows_counted(make_ctx):
    m = _build(make_ctx)["pct_university"]
    # The SECUNDARIOS row must not overwrite the university value.
    assert m.values["gros"]["2020"] == 35.0


def test_unknown_barrio_dropped(make_ctx):
    m = _build(make_ctx)["pct_university"]
    assert all(99 != bid for bid in m.values)
    assert "x" not in m.values
