# Índice de Transformación Urbana (AN-8)

> **Qué es.** Un índice **multi-definición y transparente** que clasifica los
> barrios según cuánto y cómo se están transformando, con los datos ya en el
> repo. Reproducible:
>
> ```bash
> python analysis/transformation_index.py --save   # → analysis/output/transformation_index.csv
> ```
>
> **Qué NO es.** No es un "índice de gentrificación" (decisión de proyecto). Con
> los datos disponibles **no se puede demostrar gentrificación**: falta rotación
> de población y sustitución de residentes. Medimos **transformación observable**,
> con la definición explícita y dos modos seleccionables. Solo pandas + numpy.

---

## Metodología

Dos modos, pesos iguales, **componentes a la vista** (no caja negra). Año base
**2016**. El "crecimiento" de cada variable es la pendiente anualizada
2016→último año.

### Modo A — socioeconómico (estilo Freeman 2005, adaptado)

Sigue la lógica clásica de Freeman: un barrio se transforma si **partía por
debajo** y **sube en cultura y precio** más que la media de la ciudad.

- **Susceptibilidad (puerta de entrada):** renta del barrio < **mediana de la
  ciudad en 2016** (umbral verificado: **19.041 €**).
- **Señales de transformación** (cada una vs. la **mediana** de la ciudad):
  - crecimiento de `% universitarios` (puntos pct/año),
  - crecimiento de `alquiler €/m²` (%/año).
- **Componente local:** se reporta el *exceso* sobre la mediana de la ciudad
  (`*_excess`), que ya descuenta el efecto macro/inflación común a todos los
  barrios (idea shift-share) — más limpio que un deflactor externo que no
  tenemos.
- **Clasificación:** `consolidado / no susceptible` (renta base ≥ mediana) ·
  `en transformación` (susceptible + ambas señales > mediana) ·
  `transformación incipiente` (susceptible + una señal) ·
  `estable` (susceptible + ninguna).
- **Score continuo:** media de z-scores de los dos componentes locales.

### Modo B — presión turística (PROVISIONAL)

Componentes de **nivel**: densidad VUT y nivel de alquiler ("la ciudad
turística-cara"). **No** se usa el *crecimiento* de alquiler: penalizaría a los
centros ya caros en 2016 (menos margen de subida). Score = media de z-scores.
Se consolidará con **ruido (REC-2)** y **Airbnb + serie temporal (REC-4)**.

---

## Resultados — Modo A (socioeconómico)

13 barrios clasificables (los 6 periféricos sin renta/alquiler quedan fuera).
Ordenados por score.

| Barrio | Renta base 2016 | Δ univ (pp/año) | Δ alquiler (%/año) | Score | Clase |
|---|---|---|---|---|---|
| **Loiola** | 16.239 | 0,54 | **4,25** | **1,02** | **en transformación** |
| **Egia** | 16.959 | **0,58** | 2,97 | 0,23 | transformación incipiente |
| Aiete | 24.908 | 0,32 | 3,93 | 0,22 | consolidado / no susceptible |
| Antigua | 24.068 | 0,48 | 3,23 | 0,16 | consolidado / no susceptible |
| Erdialdea | 23.428 | 0,55 | 2,93 | 0,12 | consolidado / no susceptible |
| Gros | 19.932 | 0,51 | 3,02 | 0,09 | consolidado / no susceptible |
| Intxaurrondo | 16.053 | 0,26 | 3,88 | 0,04 | transformación incipiente |
| Mirakruz-Bidebieta | 15.961 | 0,38 | 3,33 | −0,04 | estable |
| Amara Berri | 19.857 | 0,29 | 3,52 | −0,14 | consolidado / no susceptible |
| Altza | 14.316 | 0,26 | 3,63 | −0,15 | transformación incipiente |
| Ibaeta | 21.964 | 0,29 | 3,38 | −0,24 | consolidado / no susceptible |
| Martutene | 15.924 | 0,30 | 2,80 | −0,63 | estable |
| Ategorrieta-Ulia | 21.886 | 0,44 | 1,36 | −1,27 | consolidado / no susceptible |

**Lectura:**

- **Loiola es el caso más claro de transformación social**: partía pobre
  (16.239 €, bajo la mediana) y subió por encima de la media tanto en estudios
  como en alquiler. Score 1,02, muy por delante del resto.
- **Egia = transformación incipiente "de manual"**: el **mayor crecimiento de
  universitarios** de la ciudad (+0,58 pp/año) pero con el alquiler aún rezagado
  — el patrón típico de fase temprana (primero llega el capital cultural, luego
  el shock de precios). Coincide con que el Sprint A ya lo señalaba como "el
  barrio en movimiento".
- **Intxaurrondo y Altza**: incipientes por **presión de precio** (alquiler > 
  mediana) pero sin recambio educativo — "presión sin mejora", distinto de Egia.
- Los barrios ricos (Aiete, Antigua, Erdialdea, Gros, Ibaeta, Ategorrieta) salen
  `consolidado / no susceptible`: ya estaban sobre la mediana de renta, así que
  **no son casos de gentrificación "desde abajo"**. Es correcto y revelador
  (ver §"hallazgo clave").

## Resultados — Modo B (presión turística, provisional)

| Barrio | Densidad VUT | Alquiler €/m² | Score |
|---|---|---|---|
| **Erdialdea** | 29,9 | 16,6 | **2,22** |
| **Gros** | 20,7 | 15,9 | **1,46** |
| Antigua | 8,5 | 15,3 | 0,54 |
| Aiete | 2,3 | 16,2 | 0,37 |
| Ibaeta | 3,1 | 15,4 | 0,23 |
| Egia | 4,9 | 14,5 | 0,10 |
| Amara Berri | 3,9 | 14,4 | 0,03 |
| Loiola | 2,6 | 13,6 | −0,25 |
| Intxaurrondo | 1,5 | 12,9 | −0,51 |
| Mirakruz-Bidebieta | 1,7 | 12,1 | −0,70 |
| Ategorrieta-Ulia | 2,3 | 11,7 | −0,77 |
| Altza | 0,4 | 11,7 | −0,89 |
| Martutene | 0,8 | 10,6 | −1,14 |

**Lectura:** Erdialdea y Gros dominan con claridad (densidad VUT extrema).
⚠️ **Caveat transparente:** Aiete (0,37) puntúa por **alquiler alto, no por
turismo** (VUT muy baja). Los componentes a la vista lo dejan ver — es el límite
del modo hasta integrar ruido y Airbnb, que separarán "caro" de "turístico".

---

## El hallazgo clave: son dos geografías distintas

Lo más interesante es que **los dos modos NO coinciden**:

- Los centros turísticos (**Erdialdea, Gros**) lideran el Modo B pero son
  `consolidado` en el Modo A: **no se están transformando socialmente desde
  abajo** — ya eran caros y de renta media-alta.
- Los barrios en transformación social (**Loiola, Egia**) lideran el Modo A pero
  puntúan bajo en presión turística.

Es decir: en Donostia, **la presión turística y la transformación socioeconómica
ocurren en barrios diferentes**. El turismo se concentra en el centro ya
acomodado; la transformación social ocurre en la periferia interior susceptible
(Loiola, Egia). Un único "índice de gentrificación" habría fundido ambos
fenómenos y ocultado justo este contraste — que es la razón de ser del diseño
multi-definición.

---

## Limitaciones

- **N=13** barrios clasificables; los periféricos (Igeldo, Zubieta, Landerbaso,
  Añorga, Oarain, Miramón) no tienen renta/alquiler.
- **"Real" aproximado**: el crecimiento se mide como exceso sobre la mediana de
  la ciudad (descuenta lo macro común), no con un deflactor IPC.
- **Modo B provisional**: VUT es un *snapshot*; el nivel de alquiler se comparte
  con la riqueza (Aiete). Se firma con ruido (REC-2) y Airbnb (REC-4).
- **Sin desplazamiento/rotación** → "transformación", no "gentrificación".
- **Pesos iguales** (documentado); umbrales = medianas de la ciudad.

## Qué lo consolidaría (próximos insumos)

- **REC-1 (edad):** añadir cambio en estructura de edad → señal de sustitución
  residencial (¿el centro que pierde población gana qué perfil?).
- **REC-4 (Inside Airbnb):** presión turística real + **serie temporal** →
  permitiría una versión *dinámica* del Modo B y el lead/lag (AN-6).
- **REC-2 (ruido):** componente de calidad de vida para el Modo B.

## Para el frontend (VIZ-6) — ✅ implementado

Expuesto en la sección **"Donostia in trasformazione (Indice AN-8)"** del
dashboard: **3 mapas en paralelo** — (1) `transform_class` (clase socioeconómica
categórica), (2) `transform_tourism_score` (presión turística), (3) un mapa de
**componente seleccionable** (`transform_univ_excess` / `transform_rent_excess` /
`vut_density` / `airbnb_density`). Cada mapa lleva su ficha de confianza; nunca
se etiqueta como "gentrificación".

Los datos los produce el módulo del pipeline
`data-pipeline/.../datasets/transformation.py` (`build_from_metrics`), que
**reproduce exactamente** la lógica de `analysis/transformation_index.py` (mismo
año base, mismas medianas, mismos z-scores) y queda bloqueado contra los números
documentados por `tests/test_transformation.py`. Los componentes salen como
métricas `diverging` (centradas en 0) y la clase como `categorical`, así que
encajan en el choropleth/leyenda existentes sin código de mapa nuevo.

> **Airbnb (REC-4) ya disponible.** `airbnb_density` entra como capa-componente
> del tercer mapa. La consolidación del **modo turístico** del score (sumar Airbnb
> y ruido a VUT+alquiler) queda como refinamiento; el score publicado sigue siendo
> el documentado (VUT + nivel de alquiler) para no divergir de estas tablas.
