"""TDD: municipal fiscality city indicators (datasets.fiscalidad)."""

from conftest import write_csv

from donostia_pipeline.datasets import fiscalidad

IMP = """
Urtea,Zerga_eu,Zerga_es,Kopurua
2011,IBI,IBI urbana,5.0E7
2011,Veh,Vehículo,1.0E7
2012,IBI,IBI urbana,5.5E7
bad,IBI,IBI urbana,not-a-number
"""

TASAS = """
Urtea,Tasa_eu,Tasa_es,Kopurua
2011,T1,Tasa basura,2.0E7
2012,T1,Tasa basura,2.25E7
"""


def test_yearly_total_in_millions_sums_and_rounds():
    rows = [
        {"Urtea": "2011", "Kopurua": "5.0E7"},
        {"Urtea": "2011", "Kopurua": "1.0E7"},  # → 60.0 M€
        {"Urtea": "2012", "Kopurua": "5.5E7"},  # → 55.0 M€
    ]
    out = fiscalidad._yearly_total_millions(rows, "s")
    assert out["2011"]["value"] == 60.0
    assert out["2012"]["value"] == 55.0
    assert out["2011"]["source"] == "s"


def test_build_indicators_emits_tax_and_fee_series(tmp_path):
    write_csv(tmp_path, "impuestos_ciudad.csv", IMP)
    write_csv(tmp_path, "tasas_ciudad.csv", TASAS)
    inds = {i.id: i for i in fiscalidad.build_indicators(tmp_path)}
    assert set(inds) == {"tax_revenue", "fee_revenue"}
    assert inds["tax_revenue"].unit == "M€"
    assert inds["tax_revenue"].values["2011"]["value"] == 60.0  # 50+10 M€
    assert "bad" not in inds["tax_revenue"].values            # unparseable year/amount skipped
    assert inds["fee_revenue"].values["2012"]["value"] == 22.5


def test_missing_files_yield_nothing(tmp_path):
    assert fiscalidad.build_indicators(tmp_path) == []
