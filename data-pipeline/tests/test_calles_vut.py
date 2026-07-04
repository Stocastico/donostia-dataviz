"""TDD: per-street touristic-housing (VUT/HUT) count — datasets.calles_vut.

Street granularity, *not* barrio: the VUT census carries a full street address
(``helbidea``) and the Donostia callejero gives a stable street code + a
representative label point per street. We match address → street and count
touristic units per street, so the map can show which concrete streets are
saturated — something the barrio choropleth averages away.
"""

from donostia_pipeline.datasets import calles_vut


def _pt(code, izen, izen_l, nom_la, lon, lat):
    """A callejero label-point feature (as gis_io yields it, already WGS84)."""
    return {
        "type": "Feature",
        "properties": {
            "KodKalea": code,
            "IzenKalea": izen,     # EU name (uppercase, as in source)
            "IzenKaleaL": izen_l,  # EU long name (title-ish)
            "NomCalleLa": nom_la,  # ES long name
            "IzenKaleaM": "",
            "NomCalleCo": "",
        },
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
    }


# Two of the streets have several label points (long streets are labelled more
# than once); "ABUZTUAREN 31 KALEA" has a number *inside* the name on purpose.
CALLEJERO = {
    "features": [
        _pt("100", "MELODI KALEA", "Melodi Kalea", "Melodi, Calle", -2.00, 43.30),
        _pt("200", "LA FE PASEALEKUA", "La Fe Pasealekua", "Fe, Paseo de la", -2.02, 43.31),
        _pt("200", "LA FE PASEALEKUA", "La Fe Pasealekua", "Fe, Paseo de la", -2.04, 43.33),
        _pt("300", "ABUZTUAREN 31 KALEA", "Abuztuaren 31 Kalea", "31 de Agosto, Calle", -1.98, 43.32),
        _pt("400", "AISPUA KALEA", "Aispua Kalea", "Aispua, Calle", -1.99, 43.29),
    ],
}


def _vut(helbidea, mota, plazak):
    return {"helbidea": helbidea, "Mota": mota, "plazak": plazak}


VUT_ROWS = [
    _vut("MELODI KALEA 5; 00-A", "VUT", "4"),
    _vut("Melodi Kalea 9 B", "HUT", "2"),
    _vut("La Fe Pasealekua 50 A", "VUT", "6"),
    _vut("ABUZTUAREN 31 KALEA 12; 01-DR", "VUT", "8"),  # number inside the name
    _vut("KALE EZEZAGUNA 1", "VUT", "5"),               # no such street → unmatched
]


def test_normalize_strips_accents_case_and_punctuation():
    assert calles_vut.normalize("La Fé, Pasealékua") == "LA FE PASEALEKUA"


def test_match_code_longest_prefix_ignores_portal_number():
    index = calles_vut.build_index(CALLEJERO)
    assert calles_vut.match_code("MELODI KALEA 5; 00-A", index) == "100"


def test_match_code_handles_number_inside_street_name():
    """The famous '31 de Agosto' street must not be cut at its own number."""
    index = calles_vut.build_index(CALLEJERO)
    assert calles_vut.match_code("ABUZTUAREN 31 KALEA 12; 01-DR", index) == "300"


def test_match_code_returns_none_for_unknown_street():
    index = calles_vut.build_index(CALLEJERO)
    assert calles_vut.match_code("KALE EZEZAGUNA 1", index) is None


def test_representative_point_is_centroid_of_label_points():
    index = calles_vut.build_index(CALLEJERO)
    lon, lat = index["by_code"]["200"]["lon"], index["by_code"]["200"]["lat"]
    assert lon == -2.03  # mean of -2.02 and -2.04
    assert lat == 43.32  # mean of 43.31 and 43.33


def test_build_payload_counts_units_and_beds_per_street():
    payload = calles_vut.build_payload(CALLEJERO, VUT_ROWS)
    streets = {s["code"]: s for s in payload["streets"]}
    # Melodi: 1 VUT + 1 HUT = 2 units, 6 beds
    assert streets["100"]["units"] == 2
    assert streets["100"]["vut"] == 1
    assert streets["100"]["hut"] == 1
    assert streets["100"]["beds"] == 6
    # La Fe: 1 unit, 6 beds
    assert streets["200"]["units"] == 1
    # 31 de Agosto matched despite the in-name number
    assert streets["300"]["units"] == 1
    # Aispua has no VUT → not present
    assert "400" not in streets


def test_build_payload_reports_match_diagnostics():
    payload = calles_vut.build_payload(CALLEJERO, VUT_ROWS)
    assert payload["matchedRows"] == 4
    assert payload["totalRows"] == 5
    assert payload["matchRate"] == 80.0


def test_streets_carry_display_names_and_point():
    payload = calles_vut.build_payload(CALLEJERO, VUT_ROWS)
    melodi = next(s for s in payload["streets"] if s["code"] == "100")
    assert melodi["nameEu"] == "Melodi Kalea"
    assert melodi["nameEs"] == "Melodi, Calle"
    assert melodi["lon"] == -2.00 and melodi["lat"] == 43.30


def test_payload_contract_invariants():
    """Invariants the DATA-CONTRACT promises for street_vut.json."""
    payload = calles_vut.build_payload(CALLEJERO, VUT_ROWS)
    assert payload["matchedRows"] <= payload["totalRows"]
    assert payload["streetCount"] == len(payload["streets"])
    for s in payload["streets"]:
        assert s["units"] == s["vut"] + s["hut"]  # split sums to the total
        assert s["units"] >= 1                      # only streets with VUT are kept
        assert s["beds"] >= 0
        assert s["lon"] is not None and s["lat"] is not None  # always placeable
    # sorted by units descending
    unit_seq = [s["units"] for s in payload["streets"]]
    assert unit_seq == sorted(unit_seq, reverse=True)
