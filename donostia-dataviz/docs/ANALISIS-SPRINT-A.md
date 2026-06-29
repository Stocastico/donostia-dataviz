# Análisis Sprint A — insights sobre los datos existentes

> **Qué es.** Resultados del primer bloque de análisis del backlog
> (`GAP-ANALYSIS.md` §3.B, tareas AN-1/AN-2/AN-3), **sin datos nuevos**: solo el
> indicator store ya en el repo. Todos los números son **reproducibles**:
>
> ```bash
> python analysis/sprint_a.py --save
> ```
>
> Salidas en `analysis/output/*.csv`. Dependencias: pandas + numpy (las mismas
> del pipeline; Spearman se calcula como Pearson sobre rangos para no requerir
> scipy).
>
> **Cautela transversal (N pequeño).** Hay 19 barrios y varias métricas cubren
> solo 13–17. Los resultados son **descriptivos**, no inferenciales; las
> correlaciones se reportan con Spearman y *leave-one-out*, y los clusters como
> **perfiles**, no como verdad. Correlación ≠ causalidad.

---

## 1. Correlaciones robustas (AN-1)

Corte transversal, último año disponible por métrica. Para cada par clave:
Pearson, Spearman (rangos) y Pearson quitando los dos outliers del centro
turístico (Erdialdea, Gros).

| Par | n | Pearson | Spearman | Pearson sin outliers | ¿Robusto? |
|---|---|---|---|---|---|
| `housing_tension` ~ `income_total` | 13 | **−0,811** | −0,857 | **−0,891** | ✅ muy robusto |
| `pct_university` ~ `income_total` | 17 | **0,752** | 0,846 | 0,755 | ✅ muy robusto |
| `vut_density` ~ `rent_eur_m2` | 13 | **0,635** | 0,747 | 0,624 | ✅ robusto (la tesis central) |
| `rent_eur_m2` ~ `income_total` | 13 | **0,720** | 0,747 | 0,654 | ✅ robusto |
| `income_total` ~ `pct_foreign` | 17 | **−0,578** | −0,522 | **−0,716** | ✅ se refuerza sin el centro |
| `vut_density` ~ `income_total` | 17 | 0,326 | 0,586 | 0,550 | 🟡 débil/moderada, sensible |

**Lectura:**

- **La tensión de vivienda es, ante todo, un problema de renta.** La correlación
  más fuerte y robusta de todo el sistema es `housing_tension ~ income_total`
  (−0,81, y **−0,89 al quitar el centro**): cuanto más pobre el barrio, mayor el
  esfuerzo de alquiler. Confirma cuantitativamente la "inversión" que ya
  señalaba `INSIGHTS.md`: el alquiler absoluto manda en el centro, pero el
  *esfuerzo* manda en el este obrero.
- **La tesis turismo→precio aguanta.** `vut_density ~ rent` se mantiene al quitar
  Erdialdea y Gros (0,62) y es aún más fuerte en rangos (Spearman 0,75): no es un
  artefacto de dos barrios extremos.
- **Renta, educación y alquiler forman un bloque acoplado** (r 0,72–0,84): los
  barrios de renta alta concentran estudios superiores y alquileres altos. Es la
  estructura socioespacial de fondo.
- **`% extranjeros` no es señal de riqueza, al contrario.** `income ~ pct_foreign`
  es negativa y **se refuerza** sin el centro (−0,72). Es decir: salvo en los
  barrios turísticos centrales (donde hay expatriados acomodados), la población
  extranjera se concentra en barrios de **menor** renta. Refuerza la advertencia
  ética ya documentada: no usar `pct_foreign` como proxy de gentrificación.

---

## 2. Velocidad de cambio (AN-2)

Tasas anualizadas 2016→último año por barrio. `level` = %/año (renta, alquiler,
población); `pp` = puntos porcentuales/año (% universitarios, % extranjeros).
`speed_index` = media de |z-score| de las tasas (cuánto se mueve el barrio).

**Dos velocidades distintas, no una:**

- **Periferia en desarrollo (cambio demográfico).** El `speed_index` lo
  encabezan barrios pequeños/periféricos —**Landerbaso, Añorga,
  Miramón-Zorroaga**— por **crecimiento de población** (Landerbaso +4,5 %/año) y
  de renta, no por presión turística. Son barrios con poca o ninguna serie de
  alquiler: su velocidad mide expansión residencial nueva, no transformación
  social. *Tratar aparte.*
- **Ciudad consolidada (transformación social).** Entre los barrios urbanos, el
  patrón relevante:
  - **El alquiler sube de forma parecida en todas partes** (~3–4 %/año):
    Loiola +4,3, Aiete +3,9, Intxaurrondo +3,9, Altza +3,6. Es una marea
    general, no localizada.
  - **La población extranjera crece más rápido en el este obrero**: Intxaurrondo
    **+0,92 pp/año**, Mirakruz-Bidebieta +0,68, Martutene +0,65, Altza +0,62 —
    frente a Aiete +0,27 o Erdialdea +0,50. Coherente con inmigración económica
    (no expatriados), y con la correlación renta↔extranjeros del §1.
  - **El centro pierde población** (Gros −0,60 %/año, Antigua −0,45, Egia −0,33)
    mientras gana renta y estudios — compatible con sustitución residencial,
    aunque **no demostrable** sin datos de rotación (ver §4).

> Idea para visualización (VIZ-1): mapa de **velocidad** (Δ/año) por métrica, con
> escala divergente, separando población (periferia) de las socioeconómicas
> (ciudad consolidada).

---

## 3. Tipología de barrios (AN-3)

k-means (k=4, semilla fija) sobre `income_total`, `pct_university`,
`vut_density`, `rent_eur_m2` estandarizadas. Cubre los **13 barrios** con las
cuatro variables (los 6 restantes son rurales/periféricos sin renta o alquiler).

| Perfil | Barrios | Rasgo |
|---|---|---|
| **Central turístico de renta alta** | Erdialdea, Gros | Densidad VUT extrema (29,9 y 20,7/1000), renta y alquiler altos |
| **Residencial acomodado, poco turístico** | Aiete, Antigua, Ibaeta | Renta y % universitarios altos, VUT moderada/baja |
| **Transicional / mixto** | Egia, Ategorrieta-Ulia, Amara Berri | Valores intermedios; candidatos a vigilar |
| **Popular / en tensión** | Altza, Intxaurrondo, Loiola, Martutene, Mirakruz-Bidebieta | Renta y estudios bajos, alquiler bajo, VUT baja — pero esfuerzo de vivienda alto (§1) |

**Lectura:** los perfiles reproducen la geografía social de la ciudad: un centro
turístico, una corona acomodada, el este popular y un cinturón transicional. El
caso interesante para la narrativa es **Egia**, transicional con el % de
universitarios subiendo rápido (+0,58 pp/año, de los más altos): el candidato más
claro a "moverse" hacia el perfil de Gros — exactamente el tipo de trayectoria
que el Índice de Transformación Urbana (AN-8) debe capturar.

> Cautela: con N=13 los límites entre clusters son sensibles al escalado y la
> semilla. Presentar como **perfiles descriptivos**, no como clasificación dura.

---

## 4. Lectura conjunta (hacia la tesis de la ciudad)

Los tres análisis convergen en una misma historia, ahora **cuantificada y
contrastada**:

1. La **touristificación** está concentrada (Erdialdea/Gros) y **sí** va de la
   mano de alquileres altos (robusto, §1).
2. Pero la **presión de vivienda** más dura no está donde el alquiler es más
   caro, sino donde la **renta es más baja** (correlación −0,89, la más fuerte
   del sistema): el este obrero (Altza, Intxaurrondo, Martutene, Mirakruz).
3. Ese mismo este es donde **crece más rápido la población extranjera** (de renta
   baja), mientras el **centro pierde residentes** y gana renta/estudios.

Lo que **no** podemos afirmar todavía: que haya **desplazamiento/sustitución**
(gentrificación en sentido estricto). Para eso falta rotación de población y, en
el lado turístico, una **serie temporal** de presión por barrio — hoy imposible
porque VUT es un *snapshot*. Es la justificación directa de **Inside Airbnb**
(REC-4 → AN-6) y de la estructura por **edad** (REC-1).

---

## 5. Limitaciones

- **N pequeño** (13–17 barrios según métrica); resultados descriptivos.
- **Años no homogéneos** entre métricas (renta 2023, alquiler 2024, demografía
  2025, VUT snapshot): el corte transversal usa el último valor de cada una.
- **VUT sin historia** → no hay lead/lag turismo↔alquiler todavía (AN-6 espera a
  REC-4).
- **Barrios periféricos** (Landerbaso, Añorga, Zubieta, Igeldo, Oarain,
  Miramón) con datos dispersos distorsionan el `speed_index`; se interpretan
  aparte.
- Sin `scipy`, no se reportan p-valores; con N=13–17 tendrían poco valor de todos
  modos. El énfasis está en magnitud, signo y robustez (Spearman + leave-one-out).

---

## 6. Qué alimenta cada output narrativo

| Hallazgo | Output (`GAP-ANALYSIS.md` §6) |
|---|---|
| Tensión ↔ renta (−0,89); el este obrero | #1 "La ciudad que se encarece" |
| Velocidades + perfiles; Egia como caso | #2 "Qué barrios cambian más rápido" |
| Centro pierde población / extranjeros al este | #3 "Quién vive Donostia" (necesita REC-1 edad) |
| Perfiles + trayectorias como insumo del índice | #6 "Donostia en transformación" (AN-8) |
