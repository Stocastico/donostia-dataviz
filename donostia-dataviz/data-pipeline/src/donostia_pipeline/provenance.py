"""Confidence provenance for every metric (MET-4).

One canonical place that classifies each metric as **observed** (measured
directly), **derived** (computed from observed metrics) or **proxy** (an
approximation standing in for the thing we actually care about), and lists its
key assumptions. ``build.run`` applies this to every metric before serialization,
so dataset modules don't each repeat it and the UI can show a "confidence card".

Keeping it here (not in each dataset) means the whole provenance picture is
reviewable on one screen — which is the point of MET-4.
"""

from __future__ import annotations

from typing import Iterable

from .model import Metric

# Shared assumption strings.
_PER_1000 = "Normalizzato per popolazione (tasso per 1000 ab.)."
_VELOCITY = "Tasso annualizzato (regressione OLS) sulla finestra 2016→ultimo anno."

# metric_id -> (confidence, [assumptions]). Anything absent defaults to observed.
CONFIDENCE: dict[str, tuple[str, list[str]]] = {
    # --- observed (measured directly) ---
    "population": ("observed", []),
    "pct_foreign": ("observed", [
        "Non è un proxy di gentrificazione: mescola immigrazione economica ed "
        "espatriati benestanti (fuori dal centro si associa a reddito più basso).",
    ]),
    "pct_youth_adults": ("observed", ["Quota 25–39 anni sul totale (Padrón)."]),
    "income_total": ("observed", []),
    "pct_university": ("observed", []),
    "rent_eur_m2": ("observed", [
        "EMA: affitti di nuovi contratti registrati (solo locazioni), non l'intero stock.",
    ]),
    "vut_count": ("observed", ["Snapshot del censo: solo VUT registrate/legali, senza serie storica."]),
    "vut_plazas": ("observed", ["Snapshot del censo: solo VUT registrate/legali."]),
    # --- derived (computed from observed metrics) ---
    "income_gender_gap": ("derived", ["Differenza relativa di reddito uomini–donne (Eustat)."]),
    "ageing_index": ("derived", [
        "Popolazione ≥65 ÷ <15 × 100; bande quinquennali (nessuna età mediana interpolata).",
    ]),
    "vut_density": ("derived", [_PER_1000]),
    "schools_per_1000": ("derived", ["Join spaziale punto→barrio.", _PER_1000]),
    "housing_tension": ("derived", [
        "Assunzione esplicita: 30 m²/persona (regolabile nella sezione dedicata).",
        "Affitto di nuovi contratti vs reddito pro capite di tutti i residenti → "
        "pressione teorica, non spesa reale di una famiglia.",
    ]),
    "barrio_profile": ("derived", [
        "k-means k=4 su 4 variabili standardizzate; N=13 barrios.",
        "Profili descrittivi, non una classificazione dura (sensibile a scala/seme).",
    ]),
    # --- proxy (approximation) ---
    "noise_night_pct55": ("proxy", [
        "I mappe strategiche sono dominate dal rumore di TRASPORTO, non isolano la vita notturna.",
        "% di area (non pesata per popolazione); snapshot 2022.",
    ]),
}

# Velocity metrics share one assumption; fill them programmatically.
for _base in ("income_total", "rent_eur_m2", "population", "pct_university", "pct_foreign"):
    CONFIDENCE[f"velocity_{_base}"] = ("derived", [_VELOCITY])

DEFAULT = ("observed", [])


def apply(metrics: Iterable[Metric]) -> None:
    """Stamp confidence + assumptions onto each metric in place."""
    for m in metrics:
        confidence, assumptions = CONFIDENCE.get(m.id, DEFAULT)
        m.confidence = confidence
        m.assumptions = list(assumptions)
