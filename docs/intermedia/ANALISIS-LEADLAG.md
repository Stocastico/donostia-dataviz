# Lead/lag turismo → alquiler (AN-6) — exploratorio

> **Qué es.** Un primer test, **exploratorio y cauto**, de la pregunta del relato
> #5: ¿la presión turística *precede* a la subida del alquiler? Reproducible:
>
> ```bash
> python analysis/lead_lag.py [--save]   # → analysis/output/lead_lag.csv
> ```
>
> **Qué NO es.** No es una prueba causal (MET-3). Con alquiler **anual** (pocos
> puntos) y un proxy turístico imperfecto, esto es una *señal direccional*, no una
> estimación de efecto.

---

## Datos y método

Dos paneles barrio×año ya en el pipeline:

- `airbnb_activity` — reseñas/año por 1000 ab. (proxy de presión turística,
  derivado de Inside Airbnb, REC-4),
- `rent_eur_m2` — alquiler medio €/m² (EMA, anual 2016–2024).

**Dos problemas obligan a la cautela**, y dictan el método:

1. El alquiler es **anual** → solo ~9 puntos temporales.
2. Las reseñas crecen con la **adopción de la plataforma**, no solo con la
   ocupación → una tendencia común al alza que inflaría cualquier correlación de
   *niveles*.

Por eso **no** correlacionamos niveles. Trabajamos en **primeras diferencias**
(variación interanual), que descuentan la tendencia común, y montamos un **panel**
de los 13 barrios × años solapados para ganar N (=90). Para cada desfase `k`
correlacionamos Δactividad(t−k) con Δalquiler(t): `k>0` significa *el turismo
precede al alquiler*.

## Resultado

| Desfase (años) | r (panel, Δ) | n | Lectura |
|---|---|---|---|
| −1 | **−0,096** | 90 | el alquiler precede al turismo |
| 0 | 0,189 | 90 | mismo año (contemporáneo) |
| **+1** | **0,274** | 90 | **el turismo precede al alquiler en 1 año** |
| +2 | 0,093 | 90 | el turismo precede al alquiler en 2 años |

**Lectura cauta:**

- La correlación es **máxima a +1 año** (r≈0,27) y **mayor que la contemporánea**
  (0,19) y que la del sentido inverso (−0,10 ≈ cero). El patrón —débil pero
  **asimétrico**— es el que cabría esperar si la presión turística *empujara* el
  alquiler con ~1 año de retardo, y **no** al revés.
- r≈0,27 es una correlación **débil**: explica poca varianza. La señal está en la
  *forma* (lag+1 > lag0 > lag−1), no en su magnitud.
- ⚠️ **Actualización jul-2026: el blindaje AN-16 (abajo) rebaja esta lectura.**
  La señal +1 no sobrevive al control por shocks comunes de año.

## Blindaje AN-16 (jul-2026): la señal no sobrevive al control macro

> Reproducible: `python analysis/lead_lag_robustness.py [--save]`
> (tests en `analysis/tests/test_lead_lag_robustness.py`). Responde a la
> crítica del feedback externo: "sin estacionariedad + control macro,
> r(+1)=0,27 podría ser artefacto". Lo es, al menos en buena parte.

Tres defensas (pandas+numpy, sin scipy):

1. **Estacionariedad del panel en diferencias** — KPSS no rechaza
   estacionariedad en 27/28 series (5 %); Dickey-Fuller rechaza raíz unitaria
   en 15/28, pero con T≈8–14 por serie apenas tiene potencia. Diagnóstico:
   trabajar en diferencias era lo correcto y no hay evidencia de raíz unitaria
   residual, aunque el test dice poco con estas longitudes.

2. **Control macro por efectos fijos de año** (within-year demeaning del panel
   Δ): absorbe *cualquier* shock común de ciudad — IPC, tipos, COVID — sin
   necesitar series externas. Resultado: **r(+1) cae de 0,274 a 0,104**.
   La mayor parte de la señal era covariación común de toda la ciudad, no
   "los barrios con más turismo suben después su alquiler".

3. **Test de permutación** (5.000 permutaciones del orden temporal de
   Δactividad dentro de cada barrio, sobre el panel demediado):
   **p=0,30 a lag +1** (dos colas). Ningún desfase es significativo
   (lag 0: r_fe=0,13, p=0,18).

| Desfase | r naive | r con FE de año | p permutación (FE) |
|---|---|---|---|
| −1 | −0,096 | 0,046 | 0,65 |
| 0 | 0,189 | 0,130 | 0,18 |
| **+1** | **0,274** | **0,104** | **0,30** |
| +2 | 0,093 | −0,027 | 0,80 |

**Lectura honesta.** El canal *diferencial entre barrios* (¿sube después el
alquiler donde más crece el turismo, respecto a la media de la ciudad?) no
muestra lead/lag robusto. Matiz importante: el FE de año también absorbe una
eventual señal turismo→alquiler *de toda la ciudad a la vez* — si el efecto
fuera uniforme entre barrios, este diseño no puede separarlo de la inflación o
los tipos. Con estos datos no se puede distinguir "no hay efecto" de "el
efecto es común a toda la ciudad": por eso la conclusión operativa es que el
lead/lag +1 **no puede citarse como indicio direccional** — queda pendiente de
una segunda señal turística independiente (REC-12) y de alquiler
mensual/trimestral.

## Refinamiento AN-6 (jul-2026): la 2ª señal REATE, a grano ciudad

> Reproducible: `python analysis/lead_lag_reate.py [--save]`
> (tests en `analysis/tests/test_lead_lag_reate.py`). Cierra la pista que dejaba
> abierta el blindaje AN-16 y el "Qué lo reforzaría" de abajo.

El punto ciego del AN-16 es explícito: los **efectos fijos de año** absorben
cualquier empujón turismo→alquiler *uniforme en toda la ciudad*. La única forma
de mirar ese canal es un test **a grano ciudad** (una sola serie temporal), y
para no repetir el proxy de reseñas se usa una **segunda señal independiente**:
la curva REATE de **nuevas licencias VUT/HUT** (`vut_licenses_new`, altas
supervivientes por año, 2016–2025; REC-12). Es *oferta legal registrada*, no
*interés de visitante* → ajena al sesgo de adopción de plataforma (MET-7).

Se cruza el flujo anual de licencias con la **variación** del alquiler medio de
ciudad (€/m², primeras diferencias, 2017–2024) para varios desfases:

| Desfase (años) | r crudo (ciudad) | r detrended | n | p permutación |
|---|---|---|---|---|
| −1 | −0,363 | 0,322 | 8 | 0,38 |
| 0 | −0,422 | 0,248 | 8 | 0,29 |
| +1 | −0,125 | 0,564 | 8 | 0,77 |
| +2 | −0,750 | −0,536 | 7 | 0,05 |

**Lectura honesta.** A grano ciudad la asociación cruda es **negativa** en todos
los desfases: el flujo de licencias **cae** a lo largo del periodo (pico 300 en
2017 → 18 en 2025, con la regulación/purga) mientras la variación del alquiler
**se acelera** al final (0,3 €/m² en 2019 → 1,3 en 2024). Eso es un **cruce de
tendencias de signo opuesto**, no una dinámica: cuando se quitan las tendencias
lineales (columna *detrended*), el signo se vuelve **inestable** (−1: +0,32, 0:
+0,25, +1: +0,56, +2: −0,54) y ningún desfase es significativo (p de permutación
0,29–0,77; el único bajo, +2 crudo p=0,05, es negativo, n=7 y desaparece al
detrend). Con **T≈8** nada de esto es concluyente por diseño.

**Conclusión.** La 2ª señal REATE **no reabre H1** — si acaso, refuerza el
veredicto de AN-16: no hay indicio direccional turismo→alquiler citable con estos
datos. La vía que quedaría es la ya anotada: **grano trimestral** del alquiler o
de las licencias, o una serie más larga que dé potencia real. Coherente también
con AN-19 (Airbnb no añade sobre renta/universitarios en la ecuación del
alquiler) y con "dos geografías".

## Contexto-ciudad (descriptivo)

A nivel ciudad (niveles, sin detrending — solo para situar): la actividad Airbnb
pasa de ~354 (2016) a ~1.697 (2024) reseñas/1000 ab. agregadas, con el **hundimiento
de 2020** (COVID, 998→344) bien visible; el alquiler medio sube de 10,5 a 14,4
€/m² en el mismo tramo. Los dos suben, pero esa coincidencia de niveles es
justo la que el método en diferencias evita sobre-interpretar.

## Limitaciones

- **Correlación ≠ causalidad** (MET-3): un tercer factor (atractivo del barrio,
  renovación) puede mover ambas series.
- **Proxy turístico:** reseñas ≠ ocupación; sesgo de crecimiento de plataforma
  (mitigado por las diferencias, no eliminado).
- **Resolución anual** del alquiler → desfases solo en pasos de 1 año; n efectivo
  modesto pese al panel.
- **N=13 barrios.** Los periféricos sin alquiler/actividad quedan fuera.

## En la app

Además del script, el resultado vive en el frontend: sección **"Turismo → affitto
(AN-6)"** (gráfico de barras de r por desfase, con sus avisos), calculada en el
navegador desde las mismas métricas `airbnb_activity` y `rent_eur_m2`
(`web/src/lib/leadLag.ts`, con test).

## Qué lo reforzaría

- Alquiler **mensual/trimestral** (si apareciera) → desfases finos y más potencia.
- ✅ *Una segunda medida de presión turística independiente de reseñas* — **hecho
  (jul-2026): la curva REATE de licencias VUT** (ver "Refinamiento AN-6" arriba).
  No reabre H1; el límite real ya no es el proxy, es la **resolución anual** con
  T≈8. La palanca que queda es el grano trimestral o una serie más larga.
