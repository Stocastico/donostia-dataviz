"""TDD: curated Ibiltur Ocio annual indicators (datasets.ibiltur)."""

from donostia_pipeline.datasets import ibiltur

ROWS = [
    {"indicator_id": "ibiltur_ocio_spend_per_person", "year": "2023", "value": "606.1",
     "source": "IBILTUR Ocio 2023 — ficha Donostia"},
    {"indicator_id": "ibiltur_ocio_economic_impact", "year": "2023", "value": "500.1",
     "source": "IBILTUR Ocio 2023 — ficha Donostia"},
]


def test_groups_rows_into_indicators_by_id():
    inds = {i.id: i for i in ibiltur.indicators_from_rows(ROWS)}
    assert set(inds) == {"ibiltur_ocio_spend_per_person", "ibiltur_ocio_economic_impact"}
    spend = inds["ibiltur_ocio_spend_per_person"]
    assert spend.values["2023"] == {"value": 606.1, "source": "IBILTUR Ocio 2023 — ficha Donostia"}


def test_metadata_comes_from_the_registry():
    spend = next(i for i in ibiltur.indicators_from_rows(ROWS)
                 if i.id == "ibiltur_ocio_spend_per_person")
    assert spend.unit == "€"
    assert spend.theme == "tourism"


def test_unknown_indicator_id_is_skipped():
    rows = ROWS + [{"indicator_id": "bogus", "year": "2020", "value": "1", "source": "x"}]
    ids = {i.id for i in ibiltur.indicators_from_rows(rows)}
    assert "bogus" not in ids
