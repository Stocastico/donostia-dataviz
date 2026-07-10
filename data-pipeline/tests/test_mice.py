"""TDD: curated MICE annual indicators (datasets.mice)."""

from donostia_pipeline.datasets import mice

ROWS = [
    {"indicator_id": "mice_icca_congresses", "year": "2018", "value": "16", "source": "ICCA 2018"},
    {"indicator_id": "mice_icca_congresses", "year": "2019", "value": "12", "source": "ICCA 2019"},
    {"indicator_id": "mice_attendees", "year": "2024", "value": "259000", "source": "Donostitik 2024"},
]


def test_groups_rows_into_indicators_by_id():
    inds = {i.id: i for i in mice.indicators_from_rows(ROWS)}
    assert set(inds) == {"mice_icca_congresses", "mice_attendees"}
    icca = inds["mice_icca_congresses"]
    assert sorted(icca.values) == ["2018", "2019"]
    assert icca.values["2018"] == {"value": 16.0, "source": "ICCA 2018"}


def test_metadata_comes_from_the_registry():
    icca = next(i for i in mice.indicators_from_rows(ROWS) if i.id == "mice_icca_congresses")
    assert icca.unit == "congresos"
    assert icca.theme == "tourism"
    assert "ICCA" in icca.label


def test_unknown_indicator_id_is_skipped():
    rows = ROWS + [{"indicator_id": "bogus", "year": "2020", "value": "1", "source": "x"}]
    ids = {i.id for i in mice.indicators_from_rows(rows)}
    assert "bogus" not in ids
