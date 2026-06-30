# Guion de los outputs narrativos (DOC-5) — **EMPIEZA AQUÍ**

> **Qué es.** El plan de los relatos finales y el **punto de partida para
> escribirlos**. Cada *output* arranca de **una pregunta** (framing "máquina de
> preguntas") y se especifica con: dónde vive ya en la app (métrica/sección
> exacta), el estado de los datos, los números verificados, la conclusión y los
> avisos. Operacionaliza la §6 de `GAP-ANALYSIS.md` y se apoya en
> `TESIS-CIUDAD.md`, `ANALISIS-SPRINT-A.md` e `INDICE-TRANSFORMACION.md`.
>
> **Todos los números citados son reproducibles** en `analysis/*.py`
> (`sprint_a.py`, `distribucion_barrios.py`, `transformation_index.py`) o salen
> directamente de las métricas del pipeline. Cada métrica lleva su **ficha de
> confianza** (badge observado/derivado/proxy + supuestos) bajo el mapa.

---

## 0. Resumen: qué se puede producir HOY

Tras los Sprints A y B, **cuatro de los seis relatos están listos para escribir
ya** — datos y vistas en el frontend, ambos hechos. Empieza por estos.

| # | Relato | Estado | Dónde vive en la app (selector "Metrica" / sección) |
|---|---|---|---|
| **#1** | La ciudad que se encarece | ✅ **LISTO** | métrica `housing_tension` (grupo *Abitazioni*); sección **"Mappa bivariata (3×3)"** (renta × tensión); sección **"Pressione dell'affitto sul residente medio"** (selector m² + familia de medidas) |
| **#2** | Qué barrios cambian más rápido | ✅ **LISTO** | métricas `velocity_*` y `barrio_profile` (grupo *Velocità di cambiamento*); sección scatter |
| **#3** | Quién vive Donostia | ✅ **LISTO** | métricas `ageing_index`, `pct_youth_adults` (grupo *Demografia*) |
| **#4** | El clima cambia | ✅ **LISTO** | secciones de clima (warming stripes, heatmap mes×año, tendencia anual, días ≥30 °C) |
| #5 | Ciudad turística vs. vivida | 🟡 **PARCIAL** | `noise_night_pct55` (grupo *Ambiente*) listo, pero es ruido de transporte; falta Airbnb (REC-4) |
| #6 | Donostia en transformación | 🟡 **EXPLORATORIO** | `INDICE-TRANSFORMACION.md` + fichas de confianza; consolidación pendiente de REC-4 |

**Sugerencia de arranque:** escribe en este orden — **#4** (el más cerrado y
autónomo), **#1**, **#2**, **#3**. Luego #5/#6 cuando llegue Airbnb (REC-4).

> Contexto-ciudad disponible para apoyar cualquier relato (sección "Altri
> indicatori cittadini" + MICE): reciclaje, **impuestos** (`tax_revenue`,
> 73→106 M€) y **tasas** (`fee_revenue`, 35→63 M€) 2011–2025; MICE; pernoctaciones.

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
  Antigua −0,45, Egia −0,33). Cuatro perfiles (central turístico / acomodado /
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
  Antigua **envejece rápido** (+203 puntos de índice 2000→2025);
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

## #5 — "La ciudad turística vs. la ciudad vivida"  ·  🟡 PARCIAL

- **Pregunta:** ¿Conviven dos ciudades superpuestas — la del visitante y la del
  residente?
- **Vistas hoy:** lado "residente/ambiente" disponible (`noise_night_pct55`,
  `schools_per_1000`); lado "turismo" disponible (`vut_density`, `vut_count`).
- **Números:** el ruido nocturno está **dominado por el transporte** (Amara 60 %
  por estación/arterias, corredor este Intxaurrondo/Martutene, Gros), **no por el
  ocio**.
- **⚠️ Corrección de encuadre:** el relato original "ruido↔turismo en Parte
  Vieja/Gros" **no se sostiene** con este dato — el mapa estratégico de ruido es
  de tráfico, no de vida nocturna. Para la presión turística real por barrio
  hace falta **Inside Airbnb (REC-4)**; el ruido entra como capa ambiental, no
  como proxy de turismo.
- **Pendiente:** REC-4 (Airbnb) para el lado turístico con serie temporal.

## #6 — "Donostia en transformación"  ·  🟡 EXPLORATORIO LISTO

- **Pregunta:** Reuniéndolo todo, ¿qué barrios se transforman y cómo?
- **Estado:** versión exploratoria en `analysis/transformation_index.py` +
  `INDICE-TRANSFORMACION.md` (modo socioeconómico estilo Freeman + modo presión
  turística, componentes visibles). Falta el **dashboard de 3 mapas** en frontend
  (VIZ-6) y consolidar con edad (✅ ya disponible, REC-1), ruido (✅ REC-2) y
  Airbnb (⏳ REC-4).
- **Número clave:** las dos transformaciones **no coinciden** geográficamente —
  turismo en el centro acomodado (Erdialdea, Gros); cambio social en la periferia
  interior (Loiola, Egia).
- **Aviso:** "transformación", no "gentrificación" (MET-2); definición visible y
  seleccionable; fichas de confianza ya en la UI (VIZ-7).

---

## Cómo escribir cada relato (plantilla)

Para cada output, cierra con: **(1)** la pregunta; **(2)** 2–3 números verificados
con su fuente; **(3)** la conclusión causal *cauta* (correlación ≠ causalidad,
MET-3); **(4)** el aviso de confianza (la ficha de la métrica); **(5)** enlace a
la evidencia reproducible (`analysis/*.py`) y a la vista de la app.

## Qué falta para cerrar los pendientes

- **#5 completo y #6 consolidado:** dependen de **REC-4 (Inside Airbnb)** —
  presión turística real por barrio + serie temporal (reseñas/mes) → habilita el
  lead/lag turismo→alquiler (AN-6) hoy imposible (VUT es snapshot).
- **#6 en frontend:** VIZ-6 (3 mapas en paralelo + selector de definición), que
  ya puede integrar edad y ruido además de la base socioeconómica.
