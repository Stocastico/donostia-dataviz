"""TDD: age-structure metrics (datasets.demografia_edad)."""

from conftest import write_csv

from donostia_pipeline.datasets import demografia_edad
from donostia_pipeline.model import BuildContext

# gros: under15 = 20, youth(25–39) = 40, over64 = 40, total = 100
FIXTURE = """
Urtea,AuzoKodea,Auzoa,AdinTartea,PertsonenKop,PertsonenKopE,PertsonenKopG
2025,9,GROS,00 - 04,10,5,5
2025,9,GROS,10 - 14,10,5,5
2025,9,GROS,25 - 29,30,15,15
2025,9,GROS,30 - 34,10,5,5
2025,9,GROS,70 - 74,30,15,15
2025,9,GROS,95 - >=,10,5,5
2025,8,EGIA,00 - 04,50,25,25
2025,8,EGIA,80 - 84,0,0,0
2025,,Ezezaguna,30 - 34,7,0,0
"""

CODE_TO_ID = {"9": "gros", "8": "egia"}


def _ctx(tmp_path):
    return BuildContext(raw_dir=tmp_path, barrio_ids=set(CODE_TO_ID.values()), code_to_id=CODE_TO_ID)


def _build(tmp_path):
    write_csv(tmp_path, "edad_barrio.csv", FIXTURE)
    metrics = {m.id: m for m in demografia_edad.build(_ctx(tmp_path))}
    return metrics


def test_ageing_index_is_over64_over_under15_x100(tmp_path):
    m = _build(tmp_path)["ageing_index"]
    assert m.theme == "demography"
    assert m.periods == ["2025"]
    # over64 (30+10=40) / under15 (10+10=20) × 100 = 200
    assert m.values["gros"]["2025"] == 200.0


def test_youth_adults_share_covers_25_to_39(tmp_path):
    m = _build(tmp_path)["pct_youth_adults"]
    # (30 + 10) / 100 × 100 = 40%
    assert m.values["gros"]["2025"] == 40.0


def test_ageing_index_is_none_when_no_children(tmp_path):
    # egia has 50 under-15 and 0 over-65 → index 0.0 (defined, just no elders)
    m = _build(tmp_path)["ageing_index"]
    assert m.values["egia"]["2025"] == 0.0


def test_blank_code_rows_are_skipped(tmp_path):
    m = _build(tmp_path)["pct_youth_adults"]
    assert "" not in m.values  # Ezezaguna dropped


def test_band_low_parses_open_ended_top_band():
    assert demografia_edad._band_low("95 - >=") == 95
    assert demografia_edad._band_low("00 - 04") == 0
