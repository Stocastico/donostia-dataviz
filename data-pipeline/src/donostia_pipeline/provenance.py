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
    "airbnb_density": ("derived", [
        "Join spaziale punto→barrio.", _PER_1000,
        "Annunci Inside Airbnb (snapshot 2025-09, inclusi non registrati): "
        "universo più ampio dei VUT legali, non lo stesso dato.",
    ]),
    "airbnb_activity": ("proxy", [
        "Recensioni/anno ≈ soggiorni recensiti («modello San Francisco»): sottostima "
        "le presenze reali e cresce con l'adozione della piattaforma, non solo con l'occupazione.",
        "Denominatore: popolazione dell'ultimo anno (semplificazione a denominatore fisso).",
    ]),
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
    # --- Urban Transformation Index (AN-8 / VIZ-6) ---
    "transform_class": ("derived", [
        "Modo Freeman: suscettibilità (reddito base 2016 < mediana città) + crescita "
        "laureati e affitto sopra la mediana; pesi uguali, componenti a vista.",
        "Mai «gentrificazione»: nessun dato di sostituzione/rotazione dei residenti (MET-2).",
    ]),
    "transform_socio_score": ("derived", [
        "Media degli z-score dei due componenti locali (eccesso laureati / affitto).",
        "Mai «gentrificazione»: nessun dato di sostituzione/rotazione dei residenti (MET-2).",
    ]),
    "transform_tourism_score": ("derived", [
        "Media degli z-score di densità VUT, livello d'affitto e densità Airbnb "
        "(livelli, non crescita).",
        "Airbnb (REC-4) aiuta a separare «caro» da «turistico» (es. Aiete). Il rumore "
        "notturno NON è incluso: è dominato dal traffico, non è un proxy di turismo.",
    ]),
    "transform_univ_excess": ("derived", [
        "Crescita annua di % laureati meno la mediana della città (shift-share).",
    ]),
    "transform_rent_excess": ("derived", [
        "Crescita annua dell'affitto meno la mediana della città (shift-share).",
    ]),
    # --- origine per regione (REC-21) ---
    "pct_origin_latam": ("observed", [
        "Sottoinsieme di pct_foreign per regione di origine (18 paesi). "
        "Correla negativamente col reddito di barrio (r=-0.69): migrazione economica, "
        "non un proxy di gentrificazione.",
    ]),
    "pct_origin_norte_africa": ("observed", [
        "Sottoinsieme di pct_foreign per regione di origine (Marocco, Algeria). "
        "Tasso di disoccupazione quasi 3x quello europeo a livello Gipuzkoa (EPA vasca).",
    ]),
    "pct_origin_africa_subsahariana": ("observed", [
        "Sottoinsieme di pct_foreign per regione di origine (7 paesi); popolazione minima "
        "in valore assoluto — letture per barrio poco robuste sotto pochi individui.",
    ]),
    "pct_origin_europa_occidental": ("observed", [
        "Sottoinsieme di pct_foreign per regione di origine (9 paesi UE-15/nordici). "
        "Correla positivamente con reddito e % universitari — profilo opposto a America "
        "Latina e Nordafrica nello stesso aggregato pct_foreign.",
    ]),
    "pct_origin_europa_este": ("observed", [
        "Sottoinsieme di pct_foreign per regione di origine (8 paesi, ex blocco sovietico).",
    ]),
    "pct_origin_oriente_medio": ("observed", [
        "Sottoinsieme di pct_foreign per regione di origine (Iran, Siria); popolazione "
        "minima — componente di asilo non distinguibile con questi dati.",
    ]),
    "pct_origin_asia": ("observed", [
        "Sottoinsieme di pct_foreign per regione di origine (9 paesi, Asia orientale/meridionale).",
    ]),
    "pct_origin_norteamerica_oceania": ("observed", [
        "Sottoinsieme di pct_foreign per regione di origine (Stati Uniti, Australia); "
        "popolazione minima in valore assoluto.",
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
