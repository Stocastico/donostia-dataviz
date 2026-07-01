# Guion de los outputs narrativos (DOC-5) — **EMPIEZA AQUÍ**

> **Qué es.** El plan de los relatos finales y el **punto de partida para
> escribirlos**. Cada *output* arranca de **una pregunta** (framing "máquina de
> preguntas") y se especifica con: dónde vive ya en la app (métrica/sección
> exacta), el estado de los datos, los números verificados, la conclusión y los
> avisos. Operacionaliza el backlog (`../BACKLOG.md`) y se apoya en
> `TESIS-CIUDAD.md`, `intermedia/ANALISIS-SPRINT-A.md` e `intermedia/INDICE-TRANSFORMACION.md`.
>
> **Todos los números citados son reproducibles** en `analysis/*.py`
> (`sprint_a.py`, `distribucion_barrios.py`, `transformation_index.py`,
> `lead_lag.py`) o salen directamente de las métricas del pipeline. Cada métrica
> lleva su **ficha de confianza** (badge observado/derivado/proxy + supuestos) bajo
> el mapa.

---

## 0. Resumen: qué se puede producir HOY

Tras los Sprints A, B y C, **los seis relatos están listos para escribir ya** —
datos y vistas en el frontend, ambos hechos. REC-4 (Inside Airbnb) y VIZ-6 (el
dashboard de transformación) cerraron los dos que quedaban (#5 y #6).

| # | Relato | Estado | Dónde vive en la app (selector "Metrica" / sección) |
|---|---|---|---|
| **#1** | La ciudad que se encarece | ✅ **LISTO** | métrica `housing_tension` (grupo *Abitazioni*); sección **"Mappa bivariata (3×3)"** (renta × tensión); sección **"Pressione dell'affitto sul residente medio"** (selector m² + familia de medidas) |
| **#2** | Qué barrios cambian más rápido | ✅ **LISTO** | métricas `velocity_*` y `barrio_profile` (grupo *Velocità di cambiamento*); sección scatter |
| **#3** | Quién vive Donostia | ✅ **LISTO** | métricas `ageing_index`, `pct_youth_adults` (grupo *Demografia*) |
| **#4** | El clima cambia | ✅ **LISTO** | secciones de clima (warming stripes, heatmap mes×año, tendencia anual, días ≥30 °C) |
| #5 | Ciudad turística vs. vivida | ✅ **LISTO** *(desbloqueado por REC-4)* | `airbnb_density` (grupo *Turismo*) + serie `airbnb_reviews`; sección **"Due turismi: Airbnb vs hotel"** (índice base 2016); sección **"Turismo → affitto (AN-6)"** (lead/lag); contraste con `noise_night_pct55`/`schools_per_1000` |
| #6 | Donostia en transformación | ✅ **LISTO** *(VIZ-6 en frontend)* | sección **"Donostia in trasformazione (Indice AN-8)"**: dashboard de 3 mapas (`transform_class`, `transform_tourism_score` —ya **consolidado con Airbnb**—, componente seleccionable) |

**Sugerencia de arranque:** escribe en este orden — **#4** (el más cerrado y
autónomo), **#1**, **#2**, **#3**. **#5 y #6 ya tienen datos y vistas** tras REC-4
(Inside Airbnb) y VIZ-6.

> Contexto-ciudad disponible para apoyar cualquier relato (sección "Altri
> indicatori cittadini" + MICE): reciclaje, **impuestos** (`tax_revenue`,
> 73→106 M€) y **tasas** (`fee_revenue`, 35→63 M€) 2011–2025; MICE; pernoctaciones.

---

## 🖋️ Handoff para Cowork — qué escribir ahora

**El trabajo de datos e ingeniería está cerrado para los 6 relatos.** Lo que queda
es **escribir las narrativas**. Para cada una, este documento ya trae la pregunta,
las vistas exactas en la app, los números verificados, la conclusión y los avisos.

**Cómo proceder (Cowork):**

1. **Escribe en este orden:** #4 (clima, el más cerrado) → #1 (encarecimiento) →
   #2 (velocidades) → #3 (quién vive) → #5 (turística vs. vivida) → #6 (síntesis).
   #6 es el cierre: reúne #1–#5.
2. **Para cada relato, usa la plantilla de §"Cómo escribir cada relato"** (al final):
   pregunta → 2–3 números con fuente → conclusión causal *cauta* (MET-3) → aviso de
   confianza (la ficha de la métrica) → enlace a la evidencia (`analysis/*.py`) y a
   la vista de la app.
3. **No inventes números.** Toma cada cifra de la sección del relato (abajo) o de
   `analysis/*.py`; cada métrica de la app lleva su badge observado/derivado/proxy.
4. **Reglas de encuadre no negociables:** "transformación", **no** "gentrificación"
   (MET-2, falta rotación de población); correlación ≠ causalidad (MET-3); el ruido
   nocturno es de **tráfico**, no proxy de turismo (corrección de #5).
5. **Idioma/tono:** la app está en italiano; los relatos siguen la voz de
   `TESIS-CIUDAD.md`. Tono editorial pero cauto; los avisos van *dentro* del texto,
   no como nota al pie.

**Insumos por relato** (detalle completo en cada §abajo): #1 corr. tensión↔renta
−0,89; #2 alquiler +3–4 %/año, centro pierde población; #3 Gros/Erdialdea los más
envejecidos vs. este joven; #4 +0,31 °C/década; #5 Airbnb se dispara (Erdialdea
~34/1000) y crece mucho más rápido que los hoteles, lead/lag turismo→alquiler
r≈0,27 a +1 año; #6 las dos transformaciones **no coinciden** (turismo en el centro
acomodado, cambio social en la periferia interior).

---

## #1 — "La ciudad que se encarece"  ·  ✅ LISTO

- **Pregunta:** ¿Dónde se está volviendo insostenible vivir, y coincide con donde
  el alquiler es más caro?
- **Vistas (todas en frontend):** choropleth `housing_tension`; **coropleta
  bivariada renta × tensión** (resalta el ángulo anómalo); **sección de presión
  de alquiler** con selector m²/persona (20/30/40) y familia de medidas.
- **Números:** tensión↔renta **−0,89** (la correlación más fuerte y robusta del
  sistema, leave-one-out incluido); esfuerzo máximo en el este obrero (Altza
  ~21,9 %, Egia ~21,3 %, Intxaurrondo ~20,9 %). La **familia de medidas** no
  converge del todo: la cuota-de-renta apunta al este pobre, los gaps
  estandarizados también iluminan el centro caro; **Egia** es el único barrio en
  el top-5 de las tres.
- **Conclusión:** el esfuerzo de vivienda **se invierte** respecto al precio
  absoluto — pesa más la renta baja que el alquiler bajo.
- **Aviso (ficha):** índice relativo *derivado*, no % real de gasto familiar;
  supuesto 30 m²/persona explícito y regulable (MET-1).

## #2 — "Qué barrios cambian más rápido"  ·  ✅ LISTO

- **Pregunta:** ¿Qué barrios se están moviendo, y hacia qué perfil?
- **Vistas:** mapas de **velocidad de cambio** (`velocity_income_total`,
  `velocity_rent_eur_m2`, `velocity_population`, `velocity_pct_university`,
  `velocity_pct_foreign`, escala divergente azul=baja/rojo=sube); mapa de
  **perfiles** (`barrio_profile`, 4 categorías); scatter.
- **Números:** alquiler **+3–4 %/año en todas partes** (Loiola +4,3, Aiete +3,9,
  Intxaurrondo +3,9, Altza +3,6); **% extranjeros crece más rápido en el este**
  (Intxaurrondo +0,92 pp/año); **el centro pierde población** (Gros −0,60 %/año,
  Antiguo −0,45, Egia −0,33). Cuatro perfiles (central turístico / acomodado /
  transicional / popular en tensión).
- **Conclusión:** dos velocidades: periferia que crece en población vs. ciudad
  consolidada que se transforma en lo social; **Egia** es el caso "en movimiento"
  (universitarios al alza) hacia el perfil del centro.
- **Aviso:** clusters con N=13 → **perfiles descriptivos**, no clasificación dura.

## #3 — "Quién vive Donostia"  ·  ✅ LISTO  *(desbloqueado por REC-1)*

- **Pregunta:** ¿Está cambiando *quién* vive en cada barrio (edad, recambio)?
- **Vistas:** choropleth `ageing_index` (índice de vejez ≥65/<15) y
  `pct_youth_adults` (cuota 25–39), ambos con slider 2000–2025.
- **Números:** los barrios **centrales y turísticos son los más envejecidos** de
  los urbanos (Gros índice **370**, Erdialdea **350**), mientras el **este obrero
  tiene la población adulta más joven** (Intxaurrondo **21 %** de 25–39, Loiola).
  Antiguo **envejece rápido** (+203 puntos de índice 2000→2025);
  Miramón-Zorroaga **rejuvenece** por desarrollo residencial nuevo.
- **Conclusión:** el centro que pierde población (#2) es además el que más
  envejece → señal **indirecta** de recambio; el este se mantiene joven vía
  inmigración (coherente con #2).
- **Aviso:** sin **rotación** de población no se demuestra desplazamiento (MET-2);
  no se interpola edad mediana sobre datos en bandas.

## #4 — "El clima cambia"  ·  ✅ LISTO  *(el más cerrado)*

- **Pregunta:** ¿Cómo ha cambiado el clima de Donostia en 45 años?
- **Vistas:** warming stripes, ciclos mensuales por año, tendencia anual con
  regresión, días ≥30 °C — todas en el frontend.
- **Números:** **+0,31 °C/década** (13,1 → 14,7 °C); días ≥30 °C al alza
  (**+0,81/década**); picos hasta **39,7 °C (2022)**. Precipitación **sin
  tendencia** clara.
- **Conclusión:** calentamiento sostenido y más extremos de calor; la lluvia no
  muestra señal.
- **Aviso:** una sola estación (Igeldo) → relato **temporal de ciudad**, no
  espacial por barrio.

## #5 — "La ciudad turística vs. la ciudad vivida"  ·  ✅ LISTO  *(desbloqueado por REC-4)*

- **Pregunta:** ¿Conviven dos ciudades superpuestas — la del visitante y la del
  residente?
- **Vistas hoy:** lado "turismo" con **Inside Airbnb** (`airbnb_density`, annunci
  per 1000 ab.) además de los VUT legales (`vut_density`, `vut_count`); **serie
  temporal de presión turística** `airbnb_reviews` (reseñas/mes, proxy de
  presencia, 2011→2025) en estacionalidad; sección **"Due turismi: Airbnb vs
  hotel"** (índice base 2016, Airbnb vs pernoctaciones INE); sección **"Turismo →
  affitto (AN-6)"** (lead/lag); lado "residente/ambiente" con `noise_night_pct55` y
  `schools_per_1000`.
- **Números:** la densidad Airbnb se dispara en el centro turístico (**Erdialdea
  ~34/1000**, **Gros ~19/1000**) — un universo **más amplio que los VUT legales**
  (Airbnb incluye no registrados). El alojamiento turístico **crece mucho más rápido
  que la hotelería** (índice base 2016; ≈25.000 reseñas en 2024). El **lead/lag
  AN-6** sugiere que el turismo **precede al alquiler ~1 año** (r≈0,27, débil pero
  direccional). El ruido nocturno, en cambio, está **dominado por el transporte**.
- **⚠️ Corrección de encuadre (mantenida):** el ruido estratégico es de tráfico,
  no de vida nocturna → entra como **capa ambiental**, no como proxy de turismo.
  La presión turística real por barrio la da ahora **Airbnb**.
- **Conclusión:** dos ciudades superpuestas y **geográficamente separadas** — el
  alojamiento turístico se concentra en Parte Vieja/Centro y Gros, mientras la
  ciudad vivida (escuelas, residentes) se reparte por la periferia.
- **Aviso (ficha):** `airbnb_density` es *derivado* (join espacial + per cápita);
  `airbnb_reviews` es **proxy** de ocupación ("modelo San Francisco": una reseña ≈
  un alojamiento recensito), infraestima las estancias reales.

## #6 — "Donostia en transformación"  ·  ✅ LISTO  *(VIZ-6 en frontend)*

- **Pregunta:** Reuniéndolo todo, ¿qué barrios se transforman y cómo?
- **Vistas:** sección **"Donostia in trasformazione (Indice AN-8)"** — dashboard de
  **3 mapas en paralelo**: (1) `transform_class` (clase socioeconómica categórica),
  (2) `transform_tourism_score` (presión turística, **consolidado con Airbnb**),
  (3) un mapa de **componente seleccionable** (`transform_univ_excess` /
  `transform_rent_excess` / `vut_density` / `airbnb_density`). Reproduce los números
  de `analysis/transformation_index.py` (test que los bloquea en el pipeline) y
  lleva fichas de confianza por mapa.
- **Número clave:** las dos transformaciones **no coinciden** geográficamente —
  turismo en el centro acomodado (Erdialdea +2,40, Gros +1,37); cambio social en la
  periferia interior (Loiola +1,02 en transformación; Egia/Altza/Intxaurrondo
  incipientes). Con Airbnb integrado, **Aiete baja de 0,37 a 0,07**: caro pero no
  turístico — el modo turístico ya separa "caro" de "turístico".
- **Aviso:** "transformación", no "gentrificación" (MET-2); definición visible y
  seleccionable; fichas de confianza en la UI (VIZ-7). El modo turístico combina
  niveles (VUT + Airbnb + alquiler); el ruido **no** entra (es tráfico, no turismo).

---

## Cómo escribir cada relato (plantilla)

Para cada output, cierra con: **(1)** la pregunta; **(2)** 2–3 números verificados
con su fuente; **(3)** la conclusión causal *cauta* (correlación ≠ causalidad,
MET-3); **(4)** el aviso de confianza (la ficha de la métrica); **(5)** enlace a
la evidencia reproducible (`analysis/*.py`) y a la vista de la app.

## Qué falta para cerrar los pendientes

- **#5 y #6: ✅ cerrados.** REC-4 (Inside Airbnb) aportó `airbnb_density` por barrio
  + la serie `airbnb_reviews` (reseñas/mes), y VIZ-6 llevó el Índice de
  Transformación al frontend como dashboard de 3 mapas.
- **Lead/lag turismo→alquiler (AN-6): ✅ primer cut exploratorio** en
  `analysis/lead_lag.py` + `intermedia/ANALISIS-LEADLAG.md`. Sobre el panel barrio×año
  `airbnb_activity` (reseñas/año/1000 ab.) vs `rent_eur_m2`, en primeras
  diferencias: la correlación es máxima a **+1 año (r≈0,27)** —el turismo precede
  al alquiler— y mayor que la contemporánea (0,19) y que el sentido inverso
  (≈0). Débil pero **direccionalmente consistente**; exploratorio (MET-3).
- **Siguiente refinamiento (opcional):** **consolidar el modo turístico** del
  índice integrando `airbnb_density` junto a VUT y ruido.
