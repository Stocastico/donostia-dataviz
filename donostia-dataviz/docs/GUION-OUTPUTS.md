# Guion de los outputs narrativos (DOC-5)

> **Qué es.** El plan de los relatos finales. Cada *output* arranca de **una
> pregunta** (framing "máquina de preguntas") y se especifica con: las
> métricas/vistas que usa, el estado de los datos (listo / pendiente), la
> conclusión que sostiene y los avisos. Operacionaliza la §6 de `GAP-ANALYSIS.md`
> y se apoya en `TESIS-CIUDAD.md` y `ANALISIS-SPRINT-A.md`.

Estado global: **2 relatos listos para producir hoy** (#1, #2 y, ya sólido, #4);
los demás esperan datos (REC-1/2/4). Los números citados están verificados en
`analysis/*.py`.

---

## #1 — "La ciudad que se encarece"  ·  LISTO

- **Pregunta:** ¿Dónde se está volviendo insostenible vivir, y coincide con donde
  el alquiler es más caro?
- **Vistas:** choropleth de `housing_tension` con selector de m²/persona (VIZ-4);
  coropleta bivariada renta × tensión (VIZ-3); scatter VUT↔alquiler con
  leave-one-out.
- **Datos:** listos (`rent_eur_m2`, `income_total`, `housing_tension`,
  `vut_density`).
- **Conclusión:** el esfuerzo de vivienda **se invierte** respecto al precio —
  máximo en el este obrero (Altza 21,9 %, Egia 21,3 %, Intxaurrondo 20,9 %),
  porque pesa más la renta baja que el alquiler bajo (tensión↔renta −0,89).
- **Aviso:** índice relativo, no % real de gasto familiar (MET-1).

## #2 — "Qué barrios cambian más rápido"  ·  LISTO

- **Pregunta:** ¿Qué barrios se están moviendo, y hacia qué perfil?
- **Vistas:** mapa de velocidad de cambio (VIZ-1, pendientes Δ/año); mapa de
  perfiles/clusters (VIZ-2); matriz niveles×variaciones (AN-4).
- **Datos:** listos (Sprint A: velocidades, clusters; AN-4).
- **Conclusión:** el alquiler sube ~3–4 %/año en todas partes, pero el este es
  "barato y calentándose"; **Loiola** y **Egia** son los que más se mueven en lo
  social (Egia, con el mayor crecimiento de universitarios, es el caso "en
  movimiento" hacia el perfil del centro).
- **Aviso:** clusters con N=13 → perfiles descriptivos, no clasificación dura.

## #3 — "Quién vive Donostia"  ·  PENDIENTE (REC-1)

- **Pregunta:** ¿Está cambiando *quién* vive en cada barrio (edad, recambio)?
- **Vistas:** choropleth de índice de envejecimiento y de cuota 25–40; evolución.
- **Datos:** **pendiente REC-1** (CSV de edad por barrio, fuente confirmada).
- **Conclusión esperada:** contrastar el centro que pierde población (Gros −0,60
  %/año, Antigua −0,45) con su perfil de edad → señal indirecta de sustitución.
- **Aviso:** sin rotación de población no se demuestra desplazamiento (MET-2).

## #4 — "El clima cambia"  ·  LISTO (empaquetar)

- **Pregunta:** ¿Cómo ha cambiado el clima de Donostia en 45 años?
- **Vistas:** warming stripes, ciclos mensuales por año, tendencia anual con
  regresión, días ≥30 °C (todas ya implementadas en el frontend).
- **Datos:** listos (AEMET Igeldo 1981–2025).
- **Conclusión:** +0,31 °C/década (13,1 → 14,7 °C); días ≥30 °C al alza
  (+0,81/década); picos hasta 39,7 °C (2022). Precipitación sin tendencia.
- **Aviso:** una sola estación → relato temporal de ciudad, no espacial.

## #5 — "La ciudad turística vs. la ciudad vivida"  ·  PENDIENTE (REC-2/REC-4)

- **Pregunta:** ¿Conviven dos ciudades superpuestas — la del visitante y la del
  residente?
- **Vistas:** dos mapas en paralelo (VIZ-10): VUT/Airbnb/ruido vs.
  escuelas/servicios; overlay ruido nocturno × densidad turística (VIZ-5).
- **Datos:** **pendiente** ruido (REC-2, GIS listo) y Airbnb (REC-4).
- **Conclusión esperada:** solapamiento turismo↔ruido nocturno en Parte
  Vieja/Gros frente a la trama de servicios del residente.

## #6 — "Donostia en transformación"  ·  EXPLORATORIO LISTO, consolidación pendiente

- **Pregunta:** Reuniéndolo todo, ¿qué barrios se transforman y cómo?
- **Vistas:** dashboard del Índice de Transformación (VIZ-6): 3 mapas en paralelo
  (presión inmobiliaria / cambio social / presión turística) + selector de
  definición + fichas de confianza (VIZ-7).
- **Datos:** versión **exploratoria lista** (`INDICE-TRANSFORMACION.md`);
  consolidación pendiente de REC-1/REC-2/REC-4.
- **Conclusión:** las dos transformaciones **no coinciden** geográficamente —
  turismo en el centro acomodado (Erdialdea, Gros); cambio social en la periferia
  interior susceptible (Loiola, Egia).
- **Aviso:** "transformación", no "gentrificación" (MET-2); definición visible y
  seleccionable.

---

## Orden de producción sugerido

1. **Hoy:** #1, #2 y #4 — datos listos; solo falta el frontend (VIZ-1/2/3/4) y
   empaquetar el clima ya implementado.
2. **Tras Sprint B (REC-1/REC-2):** #3 y avance de #5.
3. **Tras Sprint C (REC-4) y D:** #6 consolidado y #5 completo.

Cada relato debería cerrar enlazando a su evidencia reproducible (`analysis/*.py`)
y a su ficha de confianza, para que el lector pueda auditar el número.
