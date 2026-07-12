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
_PER_1000 = "Normalizado por población (tasa por 1000 hab.)."
_VELOCITY = "Tasa anualizada (regresión OLS) sobre la ventana 2016→último año."

# metric_id -> (confidence, [assumptions]). Anything absent defaults to observed.
CONFIDENCE: dict[str, tuple[str, list[str]]] = {
    # --- observed (measured directly) ---
    "population": ("observed", []),
    "pct_foreign": ("observed", [
        "No es un proxy de gentrificación: mezcla inmigración económica y expatriados acomodados (fuera del centro se asocia a renta más baja).",
    ]),
    "pct_youth_adults": ("observed", [
        "Cuota de 25–39 años sobre el total (Padrón).",
    ]),
    "income_total": ("observed", []),
    "income_labor": ("observed", [
        "Renta del trabajo (salarios) per cápita: la parte laboral de la renta, sin pensiones/capital/transferencias — la medida relevante para «vivir de un sueldo» (HU-7). En 2016–2023 creció menos que el alquiler.",
    ]),
    "pct_university": ("observed", []),
    "rent_eur_m2": ("observed", [
        "EMA: alquileres de nuevos contratos registrados (solo arrendamientos), no el stock completo.",
    ]),
    "vut_count": ("observed", [
        "Snapshot del censo: solo VUT registradas/legales, sin serie histórica.",
    ]),
    "vut_plazas": ("observed", [
        "Snapshot del censo: solo VUT registradas/legales.",
    ]),
    # --- derived (computed from observed metrics) ---
    "income_gender_gap": ("derived", [
        "Diferencia relativa de renta hombres–mujeres (Eustat).",
    ]),
    "ageing_index": ("derived", [
        "Población ≥65 ÷ <15 × 100; bandas quinquenales (sin edad mediana interpolada).",
    ]),
    "vut_density": ("derived", [
        _PER_1000,
    ]),
    "airbnb_density": ("derived", [
        "Join espacial punto→barrio.",
        _PER_1000,
        "Anuncios de Inside Airbnb (snapshot 2026-06, incluidos no registrados): universo más amplio que las VUT legales, no el mismo dato.",
        "Solo plataforma Airbnb: un suelo del alquiler turístico online (Booking/Vrbo y otras plataformas excluidas).",
    ]),
    # --- proxy (approximation) ---
    "airbnb_activity": ("proxy", [
        "Reseñas/año ≈ estancias reseñadas («modelo San Francisco»): infraestima las presencias reales y crece con la adopción de la plataforma, no solo con la ocupación.",
        "Solo plataforma Airbnb (otras plataformas excluidas).",
        "Denominador: población del último año (simplificación a denominador fijo).",
    ]),
    "hosteleria_share": ("proxy", [
        "Cuota de restauración (bares/restaurantes/cafés) sobre el total de locales a pie de calle por barrio, desde OpenStreetMap (shop=* + hostelería amenity=*).",
        "OSM es un snapshot (foto actual, no evolución) y su completitud varía por barrio: es una proporción, no un recuento.",
        "Los barrios con menos de 15 locales mapeados quedan sin dato (la cuota sería un artefacto, p.ej. Miramón 5 locales → 100 %).",
        "La prueba temporal («cierran los comercios, abren los bares») es la serie CNAE de ciudad (REC-7), triangulada en el análisis.",
    ]),
    # --- derived (computed from observed metrics) ---
    "schools_per_1000": ("derived", [
        "Registro municipal de educación formal (157 centros: escolares, universitarios, haurreskolak; públicos y privados) — academias y formación no reglada excluidas.",
        "Join espacial punto→barrio.",
        _PER_1000,
    ]),
    "health_per_1000": ("derived", [
        "Registro municipal de equipamientos (hospitales, ambulatorios, centros de salud; públicos y clínicas privadas) — consultas médicas privadas y farmacias excluidas.",
        "Join espacial punto→barrio (hospitales, ambulatorios, centros de salud).",
        _PER_1000,
        "Accesibilidad como densidad de servicios, no tiempo de trayecto real.",
    ]),
    # --- proxy (approximation) ---
    "vpo_dwellings_per_1000": ("proxy", [
        "Solo promociones gestionadas por Etxebide (VISESA/Alokabide/Gobierno Vasco), 1.120 viviendas: cubre como máximo ~un tercio del solo parque protegido en alquiler de la ciudad (3.151 unidades, memoria de la zona tensionada 2024) y no incluye el patronato municipal (Donostiako Etxegintza, 2.087 unidades repartidas por la mayoría de los barrios).",
        "Un «0» significa cero en este registro, no ausencia de vivienda protegida en el barrio.",
        "Snapshot acumulativo (en su mayoría «Terminada»), no una serie histórica.",
        "Join espacial punto→barrio.",
        _PER_1000,
    ]),
    # --- derived (computed from observed metrics) ---
    "housing_tension": ("derived", [
        "Supuesto explícito: 30 m²/persona (regulable en la sección dedicada).",
        "Alquiler de nuevos contratos frente a renta per cápita de todos los residentes → presión teórica, no gasto real de un hogar.",
    ]),
    "barrio_profile": ("derived", [
        "k-means k=4 sobre 4 variables estandarizadas; N=13 barrios.",
        "Perfiles descriptivos, no una clasificación dura (sensible a escala/semilla).",
    ]),
    "transform_class": ("derived", [
        "Modo Freeman: susceptibilidad (renta base 2016 < mediana de ciudad) + crecimiento de universitarios y alquiler por encima de la mediana; pesos iguales, componentes a la vista.",
        "Nunca «gentrificación»: no hay dato de sustitución/rotación de residentes (MET-2).",
    ]),
    "transform_socio_score": ("derived", [
        "Media de los z-score de los dos componentes locales (exceso de universitarios / alquiler).",
        "Nunca «gentrificación»: no hay dato de sustitución/rotación de residentes (MET-2).",
    ]),
    "transform_tourism_score": ("derived", [
        "Media de los z-score de densidad VUT, nivel de alquiler y densidad Airbnb (niveles, no crecimiento).",
        "Airbnb (REC-4) ayuda a separar «caro» de «turístico» (p.ej. Aiete). El ruido nocturno NO está incluido: está dominado por el tráfico, no es un proxy de turismo.",
    ]),
    "transform_univ_excess": ("derived", [
        "Crecimiento anual del % de universitarios menos la mediana de la ciudad (shift-share).",
    ]),
    "transform_rent_excess": ("derived", [
        "Crecimiento anual del alquiler menos la mediana de la ciudad (shift-share).",
    ]),
    # --- observed (measured directly) ---
    "pct_origin_latam": ("observed", [
        "Subconjunto de pct_foreign por región de origen (18 países). Correla negativamente con la renta del barrio (r=-0.69): migración económica, no un proxy de gentrificación.",
    ]),
    "pct_origin_norte_africa": ("observed", [
        "Subconjunto de pct_foreign por región de origen (Marruecos, Argelia). Tasa de paro casi 3x la europea a nivel Gipuzkoa (EPA vasca).",
    ]),
    "pct_origin_africa_subsahariana": ("observed", [
        "Subconjunto de pct_foreign por región de origen (7 países); población mínima en valor absoluto — lecturas por barrio poco robustas con pocos individuos.",
    ]),
    "pct_origin_europa_occidental": ("observed", [
        "Subconjunto de pct_foreign por región de origen (9 países UE-15/nórdicos). Correla positivamente con renta y % de universitarios — perfil opuesto a América Latina y Norte de África en el mismo agregado pct_foreign.",
    ]),
    "pct_origin_europa_este": ("observed", [
        "Subconjunto de pct_foreign por región de origen (8 países, ex bloque soviético).",
    ]),
    "pct_origin_oriente_medio": ("observed", [
        "Subconjunto de pct_foreign por región de origen (Irán, Siria); población mínima — componente de asilo no distinguible con estos datos.",
    ]),
    "pct_origin_asia": ("observed", [
        "Subconjunto de pct_foreign por región de origen (9 países, Asia oriental/meridional).",
    ]),
    "pct_origin_norteamerica_oceania": ("observed", [
        "Subconjunto de pct_foreign por región de origen (Estados Unidos, Australia); población mínima en valor absoluto.",
    ]),
    # --- proxy (approximation) ---
    "sale_price_eur_m2": ("proxy", [
        "Precios de **oferta** (anuncios idealista), no de transacción: estimación por exceso de lo que realmente se compraventa.",
        "Las zonas de idealista no son los 19 barrios oficiales: algunas están agregadas (Aiete-Añorga-Ibaeta, Altza-Bidebieta) y toman el mismo valor; erdialdea usa la zona Centro-Miraconcha (Parte Vieja se muestra aparte).",
        "Media anual de los meses disponibles; sin dato: distritos rurales (Igeldo, Zubieta, Landerbaso, Oarain) y Loiola/Martutene/Miramón (serie idealista ausente o poco fiable).",
    ]),
    "noise_night_pct55": ("proxy", [
        "Los mapas estratégicos están dominados por el ruido del TRANSPORTE, no aíslan la vida nocturna.",
        "% de área (no ponderada por población); snapshot 2022.",
    ]),
}

# Velocity metrics share one assumption; fill them programmatically.
for _base in ("income_total", "rent_eur_m2", "sale_price_eur_m2", "population",
              "pct_university", "pct_foreign"):
    CONFIDENCE[f"velocity_{_base}"] = ("derived", [_VELOCITY])

DEFAULT = ("observed", [])


def apply(metrics: Iterable[Metric]) -> None:
    """Stamp confidence + assumptions onto each metric in place."""
    for m in metrics:
        confidence, assumptions = CONFIDENCE.get(m.id, DEFAULT)
        m.confidence = confidence
        m.assumptions = list(assumptions)
