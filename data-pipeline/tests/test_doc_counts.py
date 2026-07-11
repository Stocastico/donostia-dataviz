"""Counts quoted in prose docs must match ``web/src/data``, not memory.

README, ``NOTA-METODOLOGICA.md``, ``metodologia.html`` and ``resumen.md`` all
quote hand-written totals ("41 métricas", "33 indicadores", the
observed/derived/proxy split). Those numbers drifted three times in jul-2026
(37→38→40→41) because nothing tied them to the data. These tests do: adding or
removing a metric/indicator now fails CI until every quoted count is updated.

Each assertion anchors on the exact sentence that carries the number. If that
sentence is reworded the test fails with the missing pattern — update the doc
and the pattern together.
"""

import json
import re
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "web" / "src" / "data"


@pytest.fixture(scope="module")
def real():
    metrics = json.loads((DATA_DIR / "metrics.json").read_text(encoding="utf-8"))
    indicators = json.loads(
        (DATA_DIR / "indicators.json").read_text(encoding="utf-8")
    )
    conf = Counter(m["confidence"] for m in metrics)
    return {
        "metrics": len(metrics),
        "indicators": len(indicators),
        "observed": conf["observed"],
        "derived": conf["derived"],
        "proxy": conf["proxy"],
    }


def quoted(relpath: str, pattern: str) -> tuple[int, ...]:
    """Return the ints captured by ``pattern`` in the doc at ``relpath``."""
    text = (ROOT / relpath).read_text(encoding="utf-8")
    m = re.search(pattern, text)
    assert m, (
        f"{relpath}: anchor pattern not found: {pattern!r} "
        "(if the sentence was reworded, update doc and test together)"
    )
    return tuple(int(g) for g in m.groups())


def test_confidence_split_adds_up(real):
    assert real["observed"] + real["derived"] + real["proxy"] == real["metrics"]


def test_readme_counts(real):
    (n,) = quoted("README.md", r"\*\*(\d+) métricas coropléticas\*\*")
    assert n == real["metrics"]
    (n,) = quoted("README.md", r"de las (\d+) métricas por barrio")
    assert n == real["metrics"]
    (n,) = quoted("README.md", r"\*\*(\d+) indicadores anuales\*\*")
    assert n == real["indicators"]


def test_metodologia_html_counts(real):
    obs, der, pro, total = quoted(
        "output/metodologia.html",
        r"(\d+) observadas, (\d+) derivadas y (\d+) proxy\s*"
        r"\((\d+) métricas por barrio",
    )
    assert (obs, der, pro, total) == (
        real["observed"],
        real["derived"],
        real["proxy"],
        real["metrics"],
    )


def test_nota_metodologica_counts(real):
    total, obs, der, pro = quoted(
        "docs/NOTA-METODOLOGICA.md",
        r"\*\*(\d+) métricas live — (\d+) observadas, (\d+) derivadas, "
        r"(\d+)\s*proxy\*\*",
    )
    assert (total, obs, der, pro) == (
        real["metrics"],
        real["observed"],
        real["derived"],
        real["proxy"],
    )


def test_resumen_counts(real):
    total, obs, der, pro = quoted(
        "output/resumen.md",
        r"\((\d+) métricas en total; recuento de confianza: "
        r"(\d+) observadas · (\d+) derivadas · (\d+) proxy",
    )
    assert (total, obs, der, pro) == (
        real["metrics"],
        real["observed"],
        real["derived"],
        real["proxy"],
    )
    (n,) = quoted("output/resumen.md", r"\*\*(\d+) indicadores en total\.\*\*")
    assert n == real["indicators"]
