# Análisis inferencial (AN-11…AN-20) — resultados

> Cuaderno de resultados de la tanda de análisis inferencial derivada del
> feedback externo de jul-2026 (`FEEDBACK-IAS-2026-07.md`). Los que tienen un
> documento natural propio viven allí: **AN-9** (sensibilidad de pesos) en
> `INDICE-TRANSFORMACION.md`, **AN-10** (bootstrap IC) en la tabla de
> `output/resumen.md` y `corr_robustness.csv`, **AN-16** (blindaje lead/lag) en
> `ANALISIS-LEADLAG.md`. Este documento recoge el resto.

---

## AN-11 — Tipologías de barrio: el jerárquico sostiene 3 grupos (no 4)

> Reproducible: `python analysis/barrio_typology.py --save`
> (tests en `analysis/tests/test_barrio_typology.py`).

**Método.** Clustering jerárquico aglomerativo (enlace promedio, euclídea,
Lance-Williams en numpy puro) sobre las mismas 4 variables estandarizadas del
Sprint A (renta, % universitarios, densidad VUT, alquiler; N=13), con
silhouette por k y dendrograma.

**Resultado (jul-2026).**

| k | 2 | **3** | 4 | 5 | 6 |
|---|---|---|---|---|---|
| silhouette | 0,447 | **0,455** | 0,416 | 0,383 | 0,322 |

- La partición mejor sostenida es **k=3**, no el k=4 del k-means: (1) la
  **periferia popular** (Loiola, Mirakruz-Bidebieta, Intxaurrondo, Altza,
  Martutene), (2) el **centro turístico** (Erdialdea + Gros), (3) el
  **residencial acomodado** (Aiete, Antigua, Egia, Amara Berri, Ibaeta,
  Ategorrieta-Ulia). Coincide con la geografía de los relatos (este obrero /
  centro turístico / oeste-alto acomodado).
- Silhouettes ~0,45 = estructura **moderada**, no clusters nítidos: las
  tipologías (k-means k=4 incluido) deben seguir leyéndose como perfiles
  descriptivos, no como clases naturales.
- **Barrio más parecido** (matriz de distancias): Erdialdea↔Gros (el "centro"
  es un par real), Mirakruz↔Intxaurrondo, Altza↔Martutene, y — coherente con
  la historia #6 — el vecino más parecido de **Egia es Loiola** (0,75).
- En el dendrograma, la última fusión (h=3,23) separa exactamente la
  periferia popular del resto de la ciudad: la línea divisoria más profunda
  de Donostia en estas 4 variables es **renta/estudios**, no turismo.

**Ranking multivariable de cambio** (speed_index del Sprint A, ya publicado):
encabezan los periféricos diminutos (Landerbaso, Añorga — poblaciones mínimas,
tasas ruidosas); entre los urbanos, Intxaurrondo (0,91) y Loiola (0,89).

---

## AN-13 — Beta-convergencia: la brecha estable, testeada

> Reproducible: `python analysis/beta_convergence.py --save`
> (tests en `analysis/tests/test_beta_convergence.py`).

**Pregunta.** ¿Los barrios que partían más abajo en 2016 suben más rápido
(convergencia), más despacio (divergencia), o ni una cosa ni otra (brecha
estable)? Es el test riguroso de la H3, que hasta ahora se apoyaba solo en el
Gini territorial plano (AN-5).

**Método.** Regresión clásica `tasa_anualizada(2016→último) ~ α + β·nivel_2016`
por barrio, para renta, alquiler €/m² y % universitarios, con IC95 % bootstrap
percentil para β (2.000 remuestreos — con N=12–17, el intervalo es la parte
informativa, no el punto).

**Resultado (jul-2026):** los tres IC cruzan el cero → **compatible con brecha
estable** en todos los casos.

| Indicador | tasa | β | r² | n | IC95 % β | Lectura |
|---|---|---|---|---|---|---|
| Renta | %/año | +0,00007 | 0,09 | 17 | −0,00011 a +0,00016 | compatible con brecha estable |
| Alquiler €/m² | %/año | −0,129 | 0,17 | 12 | −0,294 a +0,054 | compatible con brecha estable |
| % universitarios | pp/año | +0,002 | 0,01 | 17 | −0,013 a +0,010 | compatible con brecha estable |

**Lectura.** Ni convergencia ni divergencia detectables: el nivel de partida
de 2016 no predice cuánto sube un barrio después. Refuerza la H3 ("la
desigualdad territorial permanece estable mientras cambia la accesibilidad")
por una vía independiente del Gini. Matiz: el alquiler apunta levemente a
convergencia (los baratos suben algo más rápido, en %) pero el IC no lo
separa del azar con 12 barrios — coherente con que Loiola (barato en 2016)
tenga el mayor crecimiento de alquiler (historia #6).

**Límites.** N pequeño (12–17), ventana corta (2016→2023/24), tasas lineales
anualizadas (no log-growth clásico de la literatura de convergencia); es un
test de asociación transversal, no un modelo dinámico.

---

## AN-19 — Alquiler ~ renta + universitarios + Airbnb: Airbnb no añade

> Reproducible: `python analysis/rent_drivers.py --save`
> (tests en `analysis/tests/test_rent_drivers.py`). **Exploratorio**: con
> N=13 esto es una pregunta disciplinada, nunca un modelo.

**Pregunta.** ¿La densidad Airbnb aporta información sobre el *nivel* de
alquiler controlando por renta y capital educativo?

**Método.** OLS estandarizado (coeficientes en z, comparables), IC95 %
bootstrap por coeficiente (2.000 remuestreos) y ΔR² al añadir Airbnb al
modelo renta+universitarios.

**Resultado (jul-2026, N=13):**

| Predictor | β (z) | IC95 % |
|---|---|---|
| % universitarios | **+1,44** | **+0,35 a +3,20** |
| renta | −0,73 | −2,22 a +0,49 |
| densidad Airbnb | +0,14 | −1,70 a +0,72 |

R² completo 0,77 · sin Airbnb 0,76 · **ΔR² de Airbnb = 0,013**.

**Lectura.** Controlando por el capital socioeconómico, **Airbnb apenas añade
información sobre el nivel de alquiler** — coherente con AN-16 (la relación
turismo↔alquiler es más débil de lo que parece a simple vista) y con el
hallazgo de "dos geografías" (el turismo se concentra en el centro caro, pero
no es lo que ordena los precios en el resto de la ciudad). El único
coeficiente cuyo IC no cruza el 0 es **% universitarios**: en el corte
transversal, el capital educativo absorbe la señal (y nota bene: renta y
universitarios correlacionan 0,75 entre sí → colinealidad, coeficientes
individuales inestables, IC anchísimos — la respuesta honesta con N=13).

---

## AN-20 — Ruptura COVID: 2020 no interrumpió la turistificación, la aceleró

> Reproducible: `python analysis/covid_break.py --save`
> (tests en `analysis/tests/test_covid_break.py`). Descriptivo (idea RDD con
> tramos de 4–9 puntos): pendientes pre (≤2019) vs post (≥2021), 2020 excluido.

**Ciudad:**

| Serie | pendiente pre | pendiente post | ×acel. | recupera nivel 2019 |
|---|---|---|---|---|
| Actividad Airbnb (suma barrios) | +125/año | +231/año | **×1,9** | 2022 |
| Alquiler medio €/m² | +0,35/año | +0,83/año | **×2,4** | 2021 |
| Pernoctaciones hotel | +42k/año | +279k/año | ×6,7 * | 2022 |

\* la ×6,7 del hotel está inflada por el rebote desde la base hundida de
2021; aun así, el nivel 2019 se supera ya en 2022 y sigue subiendo.

**Por barrio (actividad Airbnb):** el ranking de crecimiento pre y post
correlaciona 0,67 (Spearman) — **el mapa de la presión turística no cambió,
solo su ritmo**. Erdialdea y Gros duplican su pendiente (×2,0 / ×2,1), pero
las mayores aceleraciones relativas están en barrios antes poco turísticos:
Ibaeta ×7,5, Mirakruz-Bidebieta ×3,8, Loiola ×2,2 — señal de **difusión**
desde el centro saturado. (Zubieta ×60 es un artefacto per cápita de
población diminuta; Miramón e Igeldo desaceleran.)

**Lectura.** El COVID fue un cráter de un año, no un cambio de régimen: todas
las series recuperan el nivel 2019 en 2021–2022 y salen con **más** pendiente
de la que traían. La hipótesis "la pandemia enfrió la turistificación" queda
descartada con estos datos; la contraria ("la aceleró y la difundió hacia
barrios nuevos") es la lectura compatible.
