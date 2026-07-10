"""Derived metric: theoretical rent pressure on the average resident, per barrio.

The brief's "tensione affitti vs salari" (idea #4): how heavy the rent is
relative to residents' income — where living is becoming unaffordable. Combines
two metrics already in the store, so it reads no raw files:

    pressure(%) = rent_eur_m2 × 12 months × M2_PER_PERSON ÷ income_per_capita × 100

i.e. the share of one person's annual disposable income needed to rent their
typical living space. ``M2_PER_PERSON`` (≈ the Spanish average living area per
person) is the one transparent assumption.

MET-1: this assumption is **not** hidden. The label says "(30 m²)" and the
frontend's housing-pressure section makes m²/person selectable (20/30/40) and
shows two assumption-free companions (z-score and percentile gaps) — see
``docs/NOTA-METODOLOGICA.md``. So this is deliberately framed as a *theoretical
pressure on the average resident*, comparable across barrios and years, **not**
"the share of income a household spends": rent comes from the EMA (new contracts)
while income covers all residents.
"""

from __future__ import annotations

from ..model import Metric

M2_PER_PERSON = 30
SOURCE = (
    "Derivada — presión teórica del alquiler sobre el residente medio: "
    "(alquiler €/m² × 12 × 30 m²/persona) / renta per cápita (EMA + Eustat)"
)


def build_from_metrics(metrics: dict[str, Metric]) -> list[Metric]:
    rent = metrics.get("rent_eur_m2")
    income = metrics.get("income_total")
    if rent is None or income is None:
        return []

    values: dict[str, dict[str, float | None]] = {}
    periods: set[str] = set()
    for barrio_id, rent_by_year in rent.values.items():
        income_by_year = income.values.get(barrio_id, {})
        for year, rent_v in rent_by_year.items():
            income_v = income_by_year.get(year)
            if rent_v is None or not income_v:
                continue
            tension = rent_v * 12 * M2_PER_PERSON / income_v * 100
            values.setdefault(barrio_id, {})[year] = round(tension, 2)
            periods.add(year)

    return [
        Metric(
            id="housing_tension",
            label="Presión del alquiler sobre el residente medio (30 m²)",
            unit="%",
            kind="sequential",
            theme="housing",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="year",
            periods=sorted(periods),
            values=values,
        )
    ]
