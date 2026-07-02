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
