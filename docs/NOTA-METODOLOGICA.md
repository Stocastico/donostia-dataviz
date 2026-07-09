# Nota metodológica (MET-1…MET-8)

> **Qué es.** Las decisiones metodológicas que rigen el proyecto, acordadas con
> las cuatro revisiones externas (`FEEDBACK-CONSOLIDADO.md`) y la ronda de
> jul-2026 (`intermedia/FEEDBACK-IAS-2026-07.md`, que añadió MET-6…MET-8).
> Documenta *por qué* medimos como medimos. Es la base de credibilidad:
> cualquier output debe ser coherente con esto.

## MET-1 — `housing_tension` se reformula como índice relativo

El índice actual (`alquiler €/m² × 12 × 30 m²/persona ÷ renta per cápita × 100`)
es útil pero descansa en un supuesto fijo (30 m²/persona) y mezcla un alquiler de
contratos nuevos con la renta de toda la población residente. Por eso **no** se
presenta como "porcentaje de renta que gasta una familia", sino como **presión
teórica sobre el residente medio**, comparable entre barrios y en el tiempo.

Cambios acordados (no requieren datos nuevos):

- Hacer el parámetro **m²/persona seleccionable** (20 / 30 / 40) → muestra la
  sensibilidad del índice en vez de esconder el supuesto.
- Acompañarlo de una **familia de medidas** que apunten en la misma dirección:
  `alquiler/renta`, `z(alquiler) − z(renta)`, `percentil(alquiler) −
  percentil(renta)`. Cuando todas coinciden, el mensaje gana solidez.
- Cuando llegue el catastro foral (REC-8), sustituir el 30 fijo por la
  **superficie construida real por barrio**.
- **Caveat adicional (jul-2026, Gemini):** el tamaño medio del hogar varía con
  la demografía del barrio — hogares de 1–2 personas en el centro envejecido
  (Gros, Erdialdea) frente a posible mayor ocupación en el este obrero — así que
  un m²/persona uniforme puede exagerar o atenuar la tensión *relativa* entre
  barrios. El selector 20/30/40 mitiga (el ranking apenas se mueve), pero la
  corrección de fondo sigue siendo REC-8.

**Implementado (junio 2026).** El metric de mapa se reetiqueta a *"Pressione
dell'affitto sul residente medio (30 m²)"* y hay una sección dedicada
(`HousingPressureSection`, VIZ-4) con selector m²/persona (20/30/40) y las tres
medidas. **Hallazgo honesto:** la familia de medidas **no converge del todo**, y
eso es informativo, no un fallo:
- La *quota di reddito* (alquiler×m²/renta) mide **carga de accesibilidad** y está
  dominada por la renta baja → señala el **este obrero** (Loiola, Altza,
  Intxaurrondo, Mirakruz).
- Los *scarti standardizzati* (`z(alquiler)−z(renta)`, `percentil−percentil`) miden
  cuánto el alquiler **corre por delante** de la renta → iluminan también el
  **centro caro** (Gros, Erdialdea).
- **Egia** es el único barrio en el top-5 de las tres medidas: bajo presión se mida
  como se mida — y coincide con su perfil "transicional / en movimiento" de AN-3.
No se fuerza un relato de "todas coinciden": carga de renta y desajuste
alquiler-renta no son lo mismo, y la UI lo dice.

## MET-2 — "Índice de Transformación Urbana", nunca "gentrificación"

Con los datos disponibles **no se puede demostrar gentrificación**: faltan
rotación de población y sustitución social (quién entra y quién sale). Lo que sí
podemos medir es **transformación observable**. Por eso:

- El índice se llama **Índice de Transformación Urbana** (ver
  `intermedia/INDICE-TRANSFORMACION.md`).
- Definición **explícita y seleccionable**, con al menos dos modos
  (socioeconómico estilo Freeman; presión turística) y los **componentes a la
  vista** — nunca una caja negra de muchas variables.
- `% extranjeros` **no** se usa como proxy de transformación (ver MET-5).

## MET-3 — Correlaciones robustas como invariante

Con N = 13–19 barrios, una sola r de Pearson es frágil. Toda correlación que se
publique debe reportarse con:

- **Pearson + Spearman** (rangos), para no depender de la forma de la relación.
- **Leave-one-out** de los outliers del centro (Erdialdea, Gros): si el
  coeficiente se desploma al quitarlos, el mensaje cambia y hay que decirlo.
- Cuando proceda, **correlación parcial** controlando por población/densidad.

Y siempre: **correlación ≠ causalidad**. Ejemplo aplicado en
`intermedia/ANALISIS-SPRINT-A.md` (la tesis VUT↔alquiler sobrevive al leave-one-out; otras
relaciones no).

## MET-4 — Fichas de confianza por indicador

Cada métrica lleva (o llevará, en la UI) una **ficha de confianza** que distingue:

- **Observado** (dato medido directamente: p.ej. alquiler EMA, padrón).
- **Derivado** (calculado: housing_tension, densidades, índice).
- **Proxy** (aproximación: reseñas Airbnb como ocupación, ruido por punto medio
  de rango).

…y enumera los **supuestos**. Es poco habitual en dashboards públicas y refuerza
la honestidad del proyecto.

**Implementado (junio 2026).** Cada métrica lleva un campo `confidence`
(`observed`/`derived`/`proxy`) + `assumptions`, definidos en un único lugar
(`data-pipeline/.../provenance.py`) y aplicados centralmente en `build.run`. La UI
muestra una **ficha de confianza** (badge de color + supuestos) bajo el mapa.
Reparto actual (jul-2026): **38 métricas live — 16 observadas, 18 derivadas, 4
proxy** (`noise_night_pct55` ruido de transporte, `airbnb_activity` sesgo de
adopción, `vpo_dwellings_per_1000` solo promociones Etxebide — ventana parcial:
≤~⅓ del solo alquiler protegido de la ciudad, patronato municipal ausente, sus
«0» no implican ausencia de VPO —, y `hosteleria_share` HU-3 vía OSM —foto
actual, completitud variable, barrios con <15 locales sin dato—). Ejemplos de
supuestos expuestos: el 30 m²/persona de `housing_tension`, el k-means N=13 de
`barrio_profile`, "% extranjeros no es proxy de gentrificación", el join
punto→barrio de `schools/health_per_1000` y `vpo_dwellings_per_1000`.

## MET-5 — Invariantes ya fijadas

- **Normalizar por población** (tasa/1000) antes de mapear cualquier conteo;
  nunca valores absolutos en mapa.
- **`% extranjeros` no es proxy de gentrificación**: en Donostia mezcla
  inmigración económica y expatriados acomodados. Empíricamente, fuera del centro
  turístico se asocia a **menor** renta (renta ↔ % extranjeros r = −0,58, que se
  refuerza a −0,72 sin el centro), así que usarla acríticamente sería engañoso.
- **`noise_night_pct55` no es proxy de turismo** (VIZ-5, verificado jul-2026):
  ruido↔VUT r = 0,29 (cae a **0,05** sin Erdialdea/Gros); ruido↔densidad Airbnb
  r = −0,05 (se vuelve **−0,44** sin esos dos barrios) — ambas correlaciones se
  desmoronan o invierten al quitar el centro turístico, confirmando que el mapa
  estratégico de ruido mide **tráfico** (carreteras/infraestructura), no ocio
  nocturno; ver `intermedia/ANALISIS-SPRINT-A.md`.
- **Provenance explícita**: cada valor arrastra su fuente (`source`).
- **Una sola geometría de referencia** (19 barrios `mapa_auzoak`); todo join se
  hace una vez, en ingestión.

## MET-6 — Falacia ecológica: las correlaciones son entre barrios, no entre personas

*(jul-2026, feedback DeepSeek.)* Toda correlación del proyecto usa el **barrio
como unidad** (N=13–19). Describe patrones espaciales; **no** permite inferir
relaciones a nivel individual. El caso más delicado es
`tensión ↔ % extranjeros` (r = 0,74): significa que los barrios con más
inmigración económica son también los de alquiler proporcionalmente más gravoso
— **no** que los hogares extranjeros soporten esa tensión ni, menos aún, que la
causen. Regla: cualquier output que publique una correlación de barrio debe
poder leerse sin saltar al nivel individual; cuando el riesgo de mala lectura
sea alto (extranjeros, edad), el aviso va **en el texto**, no solo en la ficha.

## MET-7 — El proxy de reseñas Airbnb arrastra sesgo de adopción

*(jul-2026, consenso de las tres revisiones.)* Las reseñas/mes son un proxy de
estancias con dos sesgos: la **tasa de reseña cambió en el tiempo** (creció con
la adopción de la plataforma) y varía por tipo de viajero. Consecuencia
directa: en la comparación "Airbnb ×6 vs hotel ×1,6 desde 2016", **parte del ×6
es migración de canal y captura de cuota de la plataforma, no turistas nuevos**.
El contraste sigue siendo válido como orden de magnitud (y el bache de 2020 lo
ancla a la realidad), pero no se publica sin este aviso. Mitigación pendiente:
triangular con el histórico de licencias VUT (REC-12) y con la serie de
anuncios activos de Inside Airbnb (REC-13); si divergen de las reseñas,
cuantificar el sesgo.

## MET-8 — Estado, cambio y trayectoria son tres lecturas distintas

*(jul-2026, feedback ChatGPT.)* Cada afirmación del proyecto habla de una de
estas tres cosas, y debe decir cuál:

- **Estado** — la foto actual (p.ej. densidad Airbnb 2025, tensión 2023, índice
  AN-8, que combina *niveles*).
- **Cambio** — la velocidad (`velocity_*`, pp/año, %/año desde 2016).
- **Trayectoria** — el recorrido completo (series 2000–2025; pendiente AN-18).

Un barrio "muy transformado" (estado) no es lo mismo que un barrio
"transformándose" (cambio): Erdialdea encabeza el estado turístico mientras
Loiola/Egia encabezan el cambio social. Mezclarlos en una misma frase sin
marcar la diferencia es el error de encuadre más fácil de cometer.
