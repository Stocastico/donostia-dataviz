"""TDD: REC-17 — labor/study mobility and localized employment, city indicators.

Eustat's PxWeb bank has no municipio×municipio origin-destination matrix; what
exists is (a) EMPA/EME categorical "lugar de trabajo/estudios" for residents
(2021–), and (b) DIRAE persons employed in establishments located in the city
(1995–). Together they answer H4's missing half (job concentration).

Source shapes: PxWeb query responses.
- EMPA mt02 / EME me02: key = [ámbito, lugar (_T/10/20/30/40), periodo]
- DIRAE est07: key = [ámbito, periodo]
"""

import json
from pathlib import Path

from donostia_pipeline.datasets import movilidad_laboral


def _mob(lugar: str, periodo: str, value: str) -> dict:
    return {"key": ["20069", lugar, periodo], "values": [value]}


def _emp(periodo: str, value: str) -> dict:
    return {"key": ["20069", periodo], "values": [value]}


def test_jobs_located_series_from_dirae():
    payload = {"data": [_emp("1995", "65962"), _emp("2024", "101409")]}
    by_id = {i.id: i for i in movilidad_laboral.indicators_from_pxweb(
        empa=None, eme=None, dirae=payload)}
    jobs = by_id["jobs_located"].values
    assert jobs["1995"]["value"] == 65962.0
    assert jobs["2024"]["value"] == 101409.0


def test_pct_working_in_own_municipality():
    payload = {"data": [
        _mob("_T", "2024", "84173"), _mob("10", "2024", "55279"),
        _mob("20", "2024", "22593"),
    ]}
    by_id = {i.id: i for i in movilidad_laboral.indicators_from_pxweb(
        empa=payload, eme=None, dirae=None)}
    pct = by_id["residents_work_in_city_pct"].values
    assert round(pct["2024"]["value"], 1) == 65.7


def test_pct_studying_in_own_municipality():
    payload = {"data": [_mob("_T", "2023", "20000"), _mob("10", "2023", "15000")]}
    by_id = {i.id: i for i in movilidad_laboral.indicators_from_pxweb(
        empa=None, eme=payload, dirae=None)}
    assert by_id["residents_study_in_city_pct"].values["2023"]["value"] == 75.0


def test_job_concentration_ratio_only_on_overlapping_years():
    empa = {"data": [_mob("_T", "2024", "84173"), _mob("10", "2024", "55279")]}
    dirae = {"data": [_emp("1995", "65962"), _emp("2024", "101409")]}
    by_id = {i.id: i for i in movilidad_laboral.indicators_from_pxweb(
        empa=empa, eme=None, dirae=dirae)}
    ratio = by_id["job_concentration_ratio"].values
    assert round(ratio["2024"]["value"], 2) == 1.2
    assert "1995" not in ratio  # no resident denominator that year


def test_pxweb_missing_marker_is_skipped():
    payload = {"data": [_emp("2025", ":"), _emp("2024", "101409")]}
    by_id = {i.id: i for i in movilidad_laboral.indicators_from_pxweb(
        empa=None, eme=None, dirae=payload)}
    assert "2025" not in by_id["jobs_located"].values


def test_indicators_have_expected_metadata():
    empa = {"data": [_mob("_T", "2024", "100"), _mob("10", "2024", "50")]}
    eme = {"data": [_mob("_T", "2024", "100"), _mob("10", "2024", "50")]}
    dirae = {"data": [_emp("2024", "120")]}
    inds = movilidad_laboral.indicators_from_pxweb(empa=empa, eme=eme, dirae=dirae)
    by_id = {i.id: i for i in inds}
    assert set(by_id) == {"jobs_located", "residents_work_in_city_pct",
                          "residents_study_in_city_pct", "job_concentration_ratio"}
    for ind in inds:
        assert ind.theme == "economy"
        assert "Eustat" in ind.source
    assert by_id["residents_work_in_city_pct"].unit == "%"
    assert by_id["job_concentration_ratio"].unit == "ratio"


def test_empty_indicators_are_dropped():
    dirae = {"data": [_emp("2024", "120")]}
    ids = {i.id for i in movilidad_laboral.indicators_from_pxweb(
        empa=None, eme=None, dirae=dirae)}
    assert ids == {"jobs_located"}  # no pct/ratio without the EMPA/EME payloads


def test_build_indicators_reads_cached_files_and_tolerates_missing(tmp_path: Path):
    assert movilidad_laboral.build_indicators(tmp_path) == []
    (tmp_path / movilidad_laboral.RAW_DIRAE).write_text(
        json.dumps({"data": [_emp("2024", "101409")]}), encoding="utf-8")
    by_id = {i.id: i for i in movilidad_laboral.build_indicators(tmp_path)}
    assert by_id["jobs_located"].values["2024"]["value"] == 101409.0
