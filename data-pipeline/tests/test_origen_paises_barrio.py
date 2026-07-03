"""TDD: REC-21-web — per-barrio top-N countries of origin with 10y evolution.

Unlike ``demografia_origen_region`` (which collapses countries into regional
choropleth metrics), this export keeps the individual countries so the app can
show a "chi vive nel barrio" card. Foreign origins only (Spain excluded), top-N
by latest-year headcount, each with its value a decade earlier.
"""

from conftest import write_csv

from donostia_pipeline.datasets import origen_paises_barrio as mod

FIXTURE = """
Urtea,AuzoKodea,Auzoa,Jatorria,PertsonenKop,PertsonenKopE,PertsonenKopG
2015,9,GROS,ESPAÑA,800,400,400
2015,9,GROS,HONDURAS,50,25,25
2015,9,GROS,MARRUECOS,80,40,40
2015,9,GROS,COLOMBIA,10,5,5
2025,9,GROS,ESPAÑA,700,350,350
2025,9,GROS,HONDURAS,200,100,100
2025,9,GROS,MARRUECOS,100,50,50
2025,9,GROS,COLOMBIA,60,30,30
2025,9,GROS,ALEMANIA,40,20,20
2025,9,GROS,ITALIA,30,15,15
2025,9,GROS,CHINA,20,10,10
2025,8,EGIA,ESPAÑA,900,450,450
2025,8,EGIA,ALEMANIA,100,50,50
2025,,Ezezaguna,ESPAÑA,5,0,0
"""

CODE_TO_ID = {"9": "gros", "8": "egia"}
NAMES = {"gros": "Gros", "egia": "Egia"}


def _payload(tmp_path):
    write_csv(tmp_path, mod.CSV_NAME, FIXTURE)
    return mod.build_payload(tmp_path / mod.CSV_NAME, CODE_TO_ID, NAMES, top_n=5, span=10)


def test_years_detected(tmp_path):
    p = _payload(tmp_path)
    assert p["latestYear"] == "2025"
    assert p["pastYear"] == "2015"


def test_spain_excluded_and_sorted_desc(tmp_path):
    top = _payload(tmp_path)["barrios"]["gros"]["top"]
    assert all(e["country"] != "España" for e in top)
    countries = [e["country"] for e in top]
    assert countries[0] == "Honduras"  # 200, the largest foreign group
    # descending by latest headcount
    people = [e["peopleLatest"] for e in top]
    assert people == sorted(people, reverse=True)


def test_top_n_capped(tmp_path):
    # Gros has 6 foreign countries in 2025; top_n=5 keeps the 5 largest.
    top = _payload(tmp_path)["barrios"]["gros"]["top"]
    assert len(top) == 5
    assert "China" not in [e["country"] for e in top]  # 20 = smallest, dropped


def test_pct_of_barrio_uses_total_population(tmp_path):
    top = _payload(tmp_path)["barrios"]["gros"]["top"]
    honduras = next(e for e in top if e["country"] == "Honduras")
    # 200 / (700+200+100+60+40+30+20) = 200/1150
    assert honduras["pctOfBarrio"] == round(200 / 1150 * 100, 2)


def test_decade_evolution(tmp_path):
    top = _payload(tmp_path)["barrios"]["gros"]["top"]
    honduras = next(e for e in top if e["country"] == "Honduras")
    assert honduras["peopleLatest"] == 200
    assert honduras["peoplePast"] == 50  # 2015 value
    marruecos = next(e for e in top if e["country"] == "Marruecos")
    assert marruecos["peoplePast"] == 80


def test_country_absent_a_decade_ago_is_zero(tmp_path):
    top = _payload(tmp_path)["barrios"]["gros"]["top"]
    alemania = next(e for e in top if e["country"] == "Alemania")
    assert alemania["peoplePast"] == 0  # not present in 2015 fixture rows


def test_region_tag_matches_choropleth_grouping(tmp_path):
    top = _payload(tmp_path)["barrios"]["gros"]["top"]
    honduras = next(e for e in top if e["country"] == "Honduras")
    assert honduras["region"] == "latam"
    marruecos = next(e for e in top if e["country"] == "Marruecos")
    assert marruecos["region"] == "norte_africa"


def test_barrio_name_carried(tmp_path):
    assert _payload(tmp_path)["barrios"]["gros"]["name"] == "Gros"


def test_unknown_barrio_code_skipped(tmp_path):
    # "Ezezaguna" has an empty AuzoKodea → not in code_to_id → dropped.
    barrios = _payload(tmp_path)["barrios"]
    assert set(barrios) == {"gros", "egia"}
