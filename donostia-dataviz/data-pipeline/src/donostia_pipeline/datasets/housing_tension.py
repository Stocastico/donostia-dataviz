"""Derived metric: rent-to-income housing stress per barrio.

The brief's "tensione affitti vs salari" (idea #4): how heavy the rent is
relative to residents' income — where living is becoming unaffordable. Combines
two metrics already in the store, so it reads no raw files:

    tension(%) = rent_eur_m2 × 12 months × M2_PER_PERSON ÷ income_per_capita × 100

i.e. the share of one person's annual disposable income needed to rent their
typical living space. ``M2_PER_PERSON`` (≈ the Spanish average living area per
person) is the one transparent assumption; change it here to rescale.

Caveats (documented, not hidden): rent comes from the EMA (renters only) while
income covers all residents, so this is a *relative* pressure index, comparable
across barrios and years, not a precise household budget share.
"""

from __future__ import annotations

from ..model import Metric

M2_PER_PERSON = 30
SOURCE = "Derivata — (affitto €/m² × 12 × 30 m²/persona) / reddito pro capite (EMA + Eustat)"


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
            label="Sforzo per l'affitto (% del reddito)",
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
