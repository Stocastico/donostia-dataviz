"""Language-model schooling share — annual city indicator (REC-9).

Source: Eustat PxWeb table ``PX_040601_ceens_mun01`` ("Alumnado matriculado...
por municipio... y modelo lingüístico", 1983/1984–), filtered server-side to
municipio Donostia/San Sebastián (``20069``), titularidad "Total", nivel de
enseñanza "Enseñanzas de régimen general" (``100``) and características
"Total alumnos" (``10``) — see ``build.ensure_eustat_modelos`` for the fetch.

Model X ("no aplica" / other) exists in the source but is not reported here:
it is near-zero since the 1990s and not one of the three Basque-schooling
models (A/B/D) the brief tracks.

Only Territorio Histórico / municipio granularity — **no per-barrio figure
exists** for this dataset (REC-9's caveat in BACKLOG.md).
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from ..model import Indicator

RAW_FILE = "eustat_modelos_linguisticos.json"
SOURCE = (
    "Eustat — Alumnado matriculado en Enseñanzas de Régimen General no "
    "universitarias por municipio y modelo lingüístico (tabla PX_040601_ceens_mun01), "
    "Donostia-San Sebastián"
)

# key = [municipio, titularidad, nivel, modelo lingüístico, características, periodo]
_MODEL_CODE_IDX = 3
_PERIOD_IDX = 5
_TOTAL_CODE = "10"
_MODEL_CODES = {"20": "a", "30": "b", "40": "d"}
_LABELS = {
    "a": "Alumnado en modelo lingüístico A (%)",
    "b": "Alumnado en modelo lingüístico B (%)",
    "d": "Alumnado en modelo lingüístico D (%)",
}


def _format_period(raw: str) -> str:
    """``"19831984"`` -> ``"1983/1984"``."""
    return f"{raw[:4]}/{raw[4:]}"


def pct_by_model_from_pxweb(payload: dict) -> list[Indicator]:
    """Pure transform: a PxWeb query response -> one Indicator per model (unit-tested)."""
    by_period: dict[str, dict[str, float]] = defaultdict(dict)
    for row in payload.get("data", []):
        key = row["key"]
        code = key[_MODEL_CODE_IDX]
        model = "total" if code == _TOTAL_CODE else _MODEL_CODES.get(code)
        if model is None:
            continue
        try:
            value = float(row["values"][0])
        except (TypeError, ValueError):
            continue  # PxWeb's ":" (confidential/suppressed) or other marker
        by_period[_format_period(key[_PERIOD_IDX])][model] = value

    indicators = {
        model: Indicator(
            id=f"pct_language_model_{model}",
            label=label,
            unit="%",
            theme="demography",
            source=SOURCE,
        )
        for model, label in _LABELS.items()
    }
    for period, counts in by_period.items():
        total = counts.get("total")
        if not total:
            continue
        for model in _LABELS:
            count = counts.get(model)
            if count is None:
                continue
            indicators[model].values[period] = {
                "value": round(count / total * 100, 2),
                "source": SOURCE,
            }
    return list(indicators.values())


def build_indicators(raw_dir: Path) -> list[Indicator]:
    path = raw_dir / RAW_FILE
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return pct_by_model_from_pxweb(payload)
