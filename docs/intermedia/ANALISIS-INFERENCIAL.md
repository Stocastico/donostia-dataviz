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

---

## AN-17 — Red de correlaciones: un núcleo socioeconómico y un módulo turístico

> Reproducible: `python analysis/correlation_network.py --save`
> (tests en `analysis/tests/test_correlation_network.py`). Arista solo si
> |Pearson| **y** |Spearman| ≥ 0,5 con n ≥ 10 — el doble umbral impide que un
> outlier fabrique una conexión.

**Resultado (jul-2026): 12 aristas robustas.** Centralidad (fuerza = Σ|r|):
renta 2,86 · % universitarios 2,82 · alquiler 2,76 · tensión 2,21 · VUT 1,98
· % extranjeros 1,94 · Airbnb 1,35 · ruido 0,62.

**Lectura.**

- El corazón de la red es el **triángulo renta–universitarios–alquiler**
  (aristas 0,72–0,84 entre sí): a la pregunta del feedback ("¿la renta conecta
  todo?") la respuesta es que no es la renta sola — es un **núcleo
  socioeconómico denso** de tres variables casi intercambiables (la
  colinealidad que AN-19 señala).
- La **tensión de vivienda** cuelga de ese núcleo con signo negativo (−0,81
  con renta) y positivo con % extranjeros (0,74): la geografía del esfuerzo.
- El **turismo forma un módulo aparte** (VUT↔Airbnb 0,78) que se conecta al
  núcleo casi solo a través del alquiler (0,64/0,57) — otra vez las "dos
  geografías".
- El **ruido nocturno es periférico** (una única arista, con % extranjeros
  0,62 — ambos siguen los grandes ejes viarios/vivienda más barata), y no
  conecta con el turismo: refuerza MET-5.

---

## AN-15 — Moran's I: las geografías son reales, no ruido

> Reproducible: `python analysis/spatial_autocorrelation.py --save`
> (tests en `analysis/tests/test_spatial_autocorrelation.py`). Contigüidad
> queen desde `barrios.geojson` (los exclaves Zubieta/Landerbaso/Oarain
> quedan fuera por no tener vecinos — geografía real); p por permutación
> (999), sin supuestos distribucionales.

**Global (jul-2026):**

| Métrica | Moran I | p perm | n |
|---|---|---|---|
| alquiler €/m² | **0,58** | **0,003** | 13 |
| % universitarios | **0,52** | **0,002** | 17 |
| % extranjeros | 0,33 | 0,007 | 18 |
| renta | 0,24 | 0,031 | 17 |
| densidad VUT | 0,24 | 0,019 | 18 |
| densidad Airbnb | 0,18 | 0,043 | 18 |
| tensión de vivienda | 0,13 | 0,19 | 13 |

**Lectura.** Todas las variables clave menos la tensión muestran
autocorrelación espacial positiva significativa: **los barrios parecidos se
tocan** — las "geografías" de los relatos son estructura espacial real, no
una forma de hablar. El Moran local dibuja los dos clusters esperables: el
**este obrero** (Altza–Martutene–Mirakruz–Intxaurrondo) como cluster
bajo-bajo en renta/universitarios/alquiler, y el **centro** (Erdialdea–Gros,
con Aiete) como alto-alto en precio y turismo. Que la **tensión** no sea
espacialmente significativa encaja con su definición (ratio alquiler/renta):
mezcla las dos geografías y el patrón se difumina.

---

## AN-12 — La pérdida del centro es vegetativa, no de expulsión (y el éxodo joven es de Gros)

> Reproducible: `python analysis/population_decomposition.py --save`
> (tests en `analysis/tests/test_population_decomposition.py`). Requiere los
> crudos (`bash datos/input/descargar_raw.sh`): pirámide quinquenal del padrón
> (`edad_barrio.csv`) + tablas de mortalidad de Gipuzkoa del INE
> (`ine_mortalidad_gipuzkoa.json`, nueva fuente registrada en FUENTES.md).

**Método.** No existe dataset abierto de saldo vegetativo/migratorio por
barrio (se agotaron CKAN Donostia, Eustat y datos.gob.es), así que se estima
con el **residuo por cohortes**: en ventanas de 5 años cada grupo quinquenal
envejece exactamente un grupo; las defunciones esperadas salen de las ₅qx
provinciales (INE, promedio de la ventana) aplicadas a la pirámide inicial, y
la migración neta es el residuo. La identidad ΔP = nacimientos_proxy −
defunciones_esperadas + migración_neta es exacta por construcción.

**Resultado (jul-2026), acumulado 2000→2025 (personas):**

| Barrio | ΔP | Saldo vegetativo (est.) | Migración neta (est.) |
|---|---|---|---|
| **Gros** | **−3.369** | −2.807 | **−562** |
| **Erdialdea** | **−1.273** | −3.435 | **+2.162** |
| Antigua | −512 | −444 | −68 |
| Amara Berri | +4.139 | −996 | +5.135 |
| Aiete | +3.178 | +1.607 | +1.571 |
| Ibaeta | +2.301 | +646 | +1.655 |
| Loiola | +2.122 | +356 | +1.766 |

(Barrios restantes en `analysis/output/population_decomposition.csv`; el
padrón por edad no incluye Oarain.)

- **La pérdida de población del centro es ante todo vegetativa.** Erdialdea
  pierde 1.273 personas pese a **atraer** +2.162 por migración neta: su
  déficit nacimientos−defunciones (−3.435) se lo come todo. La imagen de un
  centro que "expulsa" residentes en términos netos **no se sostiene** en
  2000–2025; lo que hay es un centro envejecido que no se repone y que
  recambia población.
- **Gros es el único barrio con las dos sangrías a la vez**: déficit
  vegetativo (−2.807) **y** migración neta negativa (−562). Y en las
  cohortes 25–39 es el único con tasa neta negativa en **las cinco
  ventanas** (entre −4 % y −9 % por quinquenio, la peor 2020–2025). El
  "éxodo joven" del relato del centro tiene nombre propio: Gros.
- En Erdialdea el éxodo 25–39 existió en 2000–2015 (−4,5/−4,8/−6,5 %) pero
  se frenó después (+0,6/−0,5 %); su migración neta positiva reciente entra
  por otras cohortes (y muy probablemente por la inmigración extranjera que
  ya recoge `pct_foreign`).
- Los que más crecen lo hacen por migración (Amara Berri +5.135, Loiola,
  Ibaeta, Miramón-Zorroaga) — desarrollos nuevos y recepción del recambio.

**Lecturas honestas.** (1) `nacimientos_proxy` = población 00-04 al cierre:
mezcla nacimientos con migración de menores de 5; el ΔP no se ve afectado,
el reparto vegetativo/migratorio es aproximado. (2) ₅qx provinciales para
todos los barrios: si el centro envejecido muere algo más/menos que la media
provincial, parte del residuo se movería entre columnas — no hay mortalidad
por barrio publicada. (3) El grupo abierto 95+ usa ₅q=1 (tabla INE):
sobreestima defunciones e infla la migración estimada en esa cola; efecto
de decenas de personas, no cambia ninguna lectura. (4) Exclaves con
población mínima (Landerbaso, Zubieta) dan tasas jóvenes absurdas por
denominador pequeño: no leerlas. (5) Chequeo de escala: los totales de
ciudad implícitos (~1.400 nacimientos/año, ~1.600 defunciones/año) cuadran
con las cifras municipales publicadas.

**Consecuencia editorial.** Responde la pregunta abierta #2 del resumen
(descomposición de la pérdida del centro) y matiza H4: la presión turística
convive con un centro que **atrae** migración neta; el desplazamiento neto,
si existe, es selectivo por edad (Gros 25–39) y no un vaciado. Pendiente de
que Cowork lo integre en resumen/historias (#5/#6).

---

## AN-14 — Estacionalidad por barrio: la periferia turística vive del verano; el centro, todo el año

> Reproducible: `python analysis/tourism_seasonality.py --save`
> (tests en `analysis/tests/test_tourism_seasonality.py`). Requiere los crudos
> (`bash datos/input/descargar_raw.sh`): 116.101 reseñas de Donostia
> (Inside Airbnb, 2011–2024 — el 2025 parcial del snapshot se descarta),
> asignadas a barrio por punto-en-polígono como en el pipeline (REC-4).

**Método.** Perfil mensual de reseñas por barrio (reseña ≈ estancia
reseñada, "modelo San Francisco") y tres índices: **ratio verano/invierno**
(media mensual jun–sep / nov–feb), **Gini mensual** (0 = uniforme) y **%
verano** (cuota jun–sep; uniforme = 33 %). Barrios con <300 reseñas fuera.

**Resultado (jul-2026), 2011–2024:**

| Barrio | n reseñas | ratio V/I | Gini | % verano |
|---|---|---|---|---|
| Intxaurrondo | 1.684 | **4,8** | 0,41 | 63 % |
| Igeldo | 391 | 4,8 | 0,37 | 62 % |
| Antigua | 7.331 | **4,3** | 0,35 | 59 % |
| Ibaeta | 2.862 | 3,5 | 0,33 | 56 % |
| Aiete | 4.844 | 3,3 | 0,29 | 53 % |
| … | | | | |
| Gros | 23.741 | 2,7 | 0,25 | 49 % |
| Egia | 6.061 | 2,2 | 0,22 | 48 % |
| **Erdialdea** | **54.109** | **2,1** | **0,19** | **45 %** |
| *(ciudad)* | *116.101* | *2,5* | *0,23* | *48 %* |

(Tabla completa y rosa mensual en `analysis/output/tourism_seasonality*.csv`
y `seasonality_monthly.csv`.)

- **El gradiente va al revés de la intuición**: los barrios que dependen del
  verano no son los turísticos, sino la periferia con poca oferta —
  Intxaurrondo, Igeldo y Antigua-Ibaeta casi quintuplican en verano su nivel
  de invierno. El **Erdialdea es el barrio MENOS estacional** de la ciudad
  (ratio 2,1, Gini 0,19): su turismo es de todo el año.
- Lectura económica: el centro tiene demanda continua (city-break,
  gastronomía, congresos — el récord MICE de `mice_donostia.csv` encaja
  aquí) y la periferia funciona como **desbordamiento estival**: solo se
  llena cuando el centro no da más de sí. La "dependencia del turismo
  estival" es un rasgo de la periferia turística, no del núcleo.
- La ventana **2022–2024** mantiene el orden (estabilidad del patrón):
  Intxaurrondo 5,3 · Antigua 4,3 · … · Erdialdea 2,1; Egia es el que más se
  aplana (2,2 → 1,8), coherente con su deriva "urbana" (historia #6).
- **Validación externa**: las pernoctaciones hoteleras del INE (ciudad,
  2011–2024) dan ratio 2,04 y 45 % de verano — el proxy de reseñas a nivel
  ciudad (2,5 y 48 %) reproduce la magnitud, con Airbnb algo más estacional
  que el hotel, como cabía esperar.

**Lecturas honestas.** (1) Reseña ≈ estancia reseñada: proxy sesgado por la
propensión a reseñar y el crecimiento de la plataforma; sirve para comparar
**formas** de perfil entre barrios, no volúmenes absolutos. (2) El agregado
2011–2024 pondera más los años recientes (hay más reseñas); la ventana
2022–2024 hace de contraste y no cambia el orden. (3) Altza y Miramón rozan
el umbral de 300–1.300 reseñas: leer con cautela. (4) Landerbaso, Martutene,
Zubieta (y Oarain) quedan fuera por muestra insuficiente.

**Consecuencia editorial.** Matiza la historia #5: la presión del centro es
*crónica* (todo el año), no un pico de agosto; y da un dato nuevo para el
relato de la periferia. Pendiente de que Cowork valore dónde encaja.
