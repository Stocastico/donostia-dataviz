"""TDD: latest-year population helper (datasets.demografia)."""

from conftest import write_csv

from donostia_pipeline.datasets import demografia

FIXTURE = """
Urtea,AuzoKodea,Auzoa,Jatorria,PertsonenKop,PertsonenKopE,PertsonenKopG
2020,9,GROS,ESPAÑA,99999,0,0
2025,9,GROS,ESPAÑA,800,400,400
2025,9,GROS,FRANCIA,200,100,100
2025,8,EGIA,ESPAÑA,250,125,125
2025,,Ezezaguna,ESPAÑA,5,0,0
"""

CODE_TO_ID = {"9": "gros", "8": "egia"}


def test_population_latest_sums_latest_year_across_nationalities(make_ctx, tmp_path):
    write_csv(tmp_path, "demo_barrio.csv", FIXTURE)
    pop = demografia.population_latest_by_barrio(tmp_path, CODE_TO_ID)
    assert pop == {"gros": 1000, "egia": 250}  # 2025 only; 800+200 for gros


def test_population_latest_ignores_unknown_codes(make_ctx, tmp_path):
    write_csv(tmp_path, "demo_barrio.csv", FIXTURE)
    pop = demografia.population_latest_by_barrio(tmp_path, CODE_TO_ID)
    assert "" not in pop  # blank AuzoKodea ("Ezezaguna") dropped
