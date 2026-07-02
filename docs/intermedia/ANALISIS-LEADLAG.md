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
- Una segunda medida de presión turística independiente de reseñas (p. ej. plazas
  VUT con serie temporal) para triangular el proxy.
