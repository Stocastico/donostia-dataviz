# Perfil migratorio y de empleo en Donostia (AN-21) — exploratorio

> **Estado (jul-2026): implementado en el pipeline.** Las 8 métricas de
> región de origen y los 3 indicadores de empleo/I+D de este análisis ya son
> parte del dashboard en vivo (§4 detalla qué se cableó y qué se quedó
> analysis-only por no encajar en el modelo Metric/Indicator). El resto del
> documento —metodología, hallazgos y límites— sigue siendo la referencia.

> **Qué es.** Respuesta a una pregunta de usuario (jul-2026): ¿la población
> extranjera de Donostia se reparte en los perfiles que la intuición cotidiana
> sugiere (economía de servicios latinoamericana, europeos cualificados/pareja,
> norteafricanos sin empleo estable, nómadas digitales)? Y, más en general,
> ¿en qué trabaja la ciudad, cómo se compara con España en investigación, y qué
> barrios concentran los empleos "humildes" frente a los mejor pagados?
> Reproducible:
>
> ```bash
> python analysis/perfil_extranjeros_empleo.py [--save]   # → analysis/output/*.csv
> ```
>
> **Qué NO es.** No hay ninguna estadística pública en España — ni del INE, ni
> de Eustat, ni de la Seguridad Social — que cruce **nacionalidad × ocupación ×
> salario** a grano municipal, ni siquiera provincial (se comprobó contra el
> catálogo completo de Eustat, 2.321 tablas). Así que **no se puede** decir
> "el X % de los latinoamericanos trabaja en hostelería" con datos — eso sería
> inventar un cruce que no existe. Lo que sí se puede hacer, y es lo que hace
> este documento, es **triangular** tres cosas que sí existen por separado: de
> dónde viene la población (grano barrio), qué tan estable es su situación
> laboral por continente de origen (grano Gipuzkoa), y en qué trabaja/gana la
> población en general (grano Gipuzkoa/C.A. de Euskadi). El resultado es
> consistente con la intuición del usuario, pero es una lectura agregada, no
> una foto individual.

---

## Datos y método

Tres familias de fuentes, cada una con su grano (ver `docs/SOURCES.md` REC-21
y `datos/input/FUENTES.md` para el detalle de cada tabla/query):

1. **País de origen por barrio** (Donostia Open Data, el mismo CSV que ya
   alimenta `pct_foreign` en el pipeline, pero sin agregar a "extranjero
   sí/no"): 57 países, 19 barrios, 2000–2025. **Es la única pieza de este
   análisis a grano barrio.**
2. **Situación laboral por origen** (Eustat, EPA vasca — EMPA/PRA): ocupados/
   parados/inactivos por **continente** de nacionalidad y tasas de actividad/
   ocupación/paro por nacionalidad española/extranjera. Grano **Gipuzkoa**
   (Eustat no publica la EPA-EUS por debajo de territorio histórico —
   la muestra no da para más finura).
3. **Empleo general** (Eustat): ocupados por ocupación CNO-11, personal en I+D
   por tipo, renta media por profesión (grano Gipuzkoa/C.A. de Euskadi) y
   establecimientos por sector económico **en Donostia** (grano municipio,
   pero cuenta *establecimientos*, no personas empleadas — misma limitación ya
   documentada en REC-7 para el proxy de comercio/hostelería).

**Los 19 barrios** se citan con el nombre oficial de la geometría de
referencia (`barrios.geojson`); "Antiguo" en el texto es el mismo barrio que
el `barrio_id` interno `antigua` (ver nota en `README.md`).

---

## 1. Quién es la población extranjera, y de dónde viene

### 1.1 La cuota crece rápido, y el crecimiento no es homogéneo

En 2025, el 9,4 % de la población de Donostia (169.499 → resto del total)
había nacido fuera de España, frente al 5,2 % de 2015 y menos del 1 % en 2000.
Pero el crecimiento agregado esconde ritmos muy distintos por región de
origen (cuota sobre población total, ciudad):

| Región | 2000 | 2025 | Factor de crecimiento |
|---|---:|---:|---:|
| **América Latina** | 0,25 % | **4,81 %** | ×19 |
| Europa occidental | 0,58 % | 1,50 % | ×2,6 |
| **Norte de África** | 0,04 % | **1,10 %** | ×27 |
| Europa del Este | 0,01 % | 0,86 % | ×140 (base minúscula) |
| Asia oriental/meridional | 0,04 % | 0,76 % | ×17 |
| Norteamérica/Oceanía | 0,02 % | 0,26 % | ×14 |
| África subsahariana | — | 0,08 % | — |
| Oriente Medio | — | 0,02 % | — |

**Lectura**: América Latina no solo es, con diferencia, el grupo más
numeroso (más de la mitad de toda la población extranjera de la ciudad) —
también es el que más ha crecido en términos absolutos. El Magreb parte de
una base casi nula y multiplica su presencia por 27, pero sigue siendo casi
5 veces más pequeño que el bloque latinoamericano. Los europeos occidentales
crecen de forma mucho más pausada: **su cuota sobre población total apenas se
ha triplicado en 25 años**, frente al crecimiento de un orden de magnitud de
los otros grupos. Esto ya matiza la intuición inicial: en volumen, Donostia
no es una ciudad de "muchos perfiles distintos en proporciones parecidas" —
es sobre todo una ciudad con una comunidad latinoamericana creciente y, a
mucha distancia, todo lo demás.

### 1.2 Top-15 países (2025, con comparación a 2015)

| País | 2025 | 2015 | Región |
|---|---:|---:|---|
| Honduras | 2.213 | 1.308 | América Latina |
| Colombia | 2.027 | 427 | América Latina |
| Nicaragua | 1.649 | 1.119 | América Latina |
| Marruecos | 1.521 | 828 | Norte de África |
| Italia | 1.132 | 517 | Europa occidental |
| Ucrania | 744 | 440 | Europa del Este |
| China | 586 | 400 | Asia oriental/meridional |
| Francia | 565 | 314 | Europa occidental |
| Argelia | 534 | 112 | Norte de África |
| Venezuela | 511 | 102 | América Latina |
| Perú | 482 | 123 | América Latina |
| Estados Unidos | 464 | 158 | Norteamérica/Oceanía |
| Argentina | 463 | 188 | América Latina |
| Rumanía | 427 | 547 | Europa del Este (único que **baja**) |
| Ecuador | 386 | 336 | América Latina |

Colombia (×4,7) y Venezuela/Argelia (×5) muestran los crecimientos más
marcados de la última década — migración muy reciente. Honduras y Nicaragua
ya eran las nacionalidades más numerosas en 2015: no es un fenómeno nuevo,
es una comunidad consolidada y todavía en expansión. Rumanía es la única
nacionalidad del top-15 en descenso (contracción de la migración de Europa
del Este post-2015, coherente con la mejora económica rumana y el
envejecimiento de esa oleada migratoria de los 2000).

### 1.3 Dónde vive cada grupo — y su cruce con renta y estudios por barrio

Cruzando la cuota de cada región de origen por barrio (2025) con `income_total`
y `pct_university` — ya en el pipeline — aparece un patrón espacial claro
(correlación de Pearson entre barrios, n=17):

| Región de origen | r con renta per cápita | r con % estudios universitarios |
|---|---:|---:|
| América Latina | **−0,69** | −0,29 |
| Norte de África | **−0,48** | −0,37 |
| Europa occidental | +0,24 | **+0,59** |
| Europa del Este | −0,13 | −0,12 |
| Asia oriental/meridional | −0,28 | +0,16 |

La población de origen latinoamericano y magrebí se concentra sistemáticamente
en los barrios de **menor renta**: Martutene (6,8 %), Mirakruz-Bidebieta
(6,4 %), Altza (6,3 %), Amara Berri (6,0 %) y Egia (5,9 %) encabezan la cuota
latinoamericana; Intxaurrondo (5,8 %) y Loiola (2,3 %) la magrebí. La
población de origen europeo-occidental, en cambio, correlaciona positivamente
con la renta y **fuertemente** con el nivel de estudios (+0,59), y se
concentra en el Erdialdea/Parte Vieja (2,7 %), Ategorrieta-Ulia (2,4 %), Gros
(2,2 %) y Antiguo (1,9 %) — los barrios más caros y turísticos, coherente con
perfiles de expatriados acomodados, jubilados o teletrabajadores, no de
migración económica.

Esto **replica exactamente** el hallazgo ya documentado en el pipeline sobre
`% extranjeros` agregado (`renta ↔ % extranjeros` r=−0,58, ver
`docs/NOTA-METODOLOGICA.md` MET-5) — pero aquí se ve **qué región concreta**
tira de esa correlación negativa (Latinoamérica y Magreb) y cuál la
contrarresta parcialmente en el centro (Europa occidental). Es la prueba
cuantitativa de algo que el proyecto ya intuía cualitativamente: mezclar todo
"extranjero" en una sola cifra esconde dos poblaciones con relación opuesta
con la renta del barrio.

### 1.4 Estabilidad laboral por continente de origen (Gipuzkoa, 2024)

Sin datos de Donostia específicamente, pero con la EPA vasca desagregada por
continente de nacionalidad (Gipuzkoa, 2024):

| Continente | % ocupada | % parada |
|---|---:|---:|
| Europa | 56,1 % | 6,7 % |
| Asia | 51,0 % | 8,4 % |
| Oceanía | 49,4 % | 3,6 % |
| América | 50,3 % | 3,2 % |
| **África** | **43,8 %** | **18,4 %** |

La tasa de paro de la población africana (18,4 %) casi triplica la europea
(6,7 %) y multiplica por seis la americana (3,2 %). Esto es coherente —
aunque no lo demuestra a nivel de Donostia — con la percepción de una
población magrebí/africana con situación laboral más precaria. La comparación
agregada española/extranjera confirma el patrón: en Gipuzkoa (2025),
la población de nacionalidad extranjera tiene una tasa de paro más del doble
que la española (9,4 % vs. 4,3 %), pese a una tasa de actividad más alta
(65,5 % vs. 56,0 % — se buscan empleo con más intensidad, pero se encuentra
menos).

**Lo que este dato no cubre**: la parte de la hipótesis del usuario sobre
"gente sin trabajo estable o que vive en la calle" no es medible con
estadística de empleo — el sinhogarismo y la economía informal no aparecen en
la EPA por diseño (encuesta a hogares con domicilio). No hay proxy honesto
disponible; se documenta como vacío, no se rellena.

### 1.5 Contraste con la hipótesis inicial

| Perfil hipotetizado | Lo que dicen los datos |
|---|---|
| Latinoamericanos en hostelería/cuidados/comercio | **Coherente en volumen y geografía** (grupo mayor y de más rápido crecimiento, concentrado en barrios de renta baja) pero **no verificable en ocupación concreta** — no existe cruce nacionalidad×sector |
| Europeos, pareja o trabajo cualificado | **Coherente**: crecimiento lento en cuota pero fuerte correlación con renta y estudios universitarios altos, concentrado en el centro/Gros |
| Magrebíes sin trabajo estable | **Parcialmente coherente**: tasa de paro africana casi 3× la europea (Gipuzkoa) y concentración en barrios de renta baja (Intxaurrondo); pero "sin techo" no es medible con estos datos |
| Nómadas digitales / rentistas | **No verificable con datos públicos**: no hay estadística de teletrabajo ni de renta por nacionalidad a este grano. Solo se puede señalar que Norteamérica/Oceanía (EE.UU.+Australia) es el grupo de más rápido crecimiento relativo tras Latinoamérica y Magreb (×14 desde 2000, aunque partiendo de una base minúscula: 477 personas en 2025) |

---

## 2. En qué trabaja Donostia, y cómo se compara con España

### 2.1 Investigación: la intuición se confirma, y con margen amplio

Personal dedicado a I+D en Gipuzkoa, 2024: **10.383 personas** en equivalente
a dedicación plena (de ellas, 7.050 investigadores). Sobre los 335.300
ocupados de Gipuzkoa, eso es:

- **31,0 ‰** del empleo total en I+D (España, INE 2024: **13,6 ‰**)
- **21,0 ‰** son investigadores específicamente (España: **8,5 ‰**)

**Gipuzkoa más que duplica la intensidad investigadora española**, tanto en
personal total como en investigadores. No es una impresión: Gipuzkoa es,
además, el territorio con mayor gasto en I+D sobre PIB de los tres vascos
(2,74 %, frente a 1,94 % Bizkaia y 1,59 % Álava — fuente: Eustat, vía
prensa nov-2025). La serie histórica (Gipuzkoa) muestra que esto no es un
pico reciente sino una tendencia sostenida: el personal en I+D casi se ha
triplicado desde 2001 (3.893 → 10.383 EDP, +166 % en 23 años).

*Advertencia de grano*: el dato es de Gipuzkoa, no de Donostia — pero la
capital concentra buena parte de los grandes centros de investigación del
territorio (universidad, centros tecnológicos, institutos de investigación),
así que es razonable leerlo como contexto directo de la ciudad, con la
salvedad explícita de que no es un dato exclusivo de Donostia.

### 2.2 Ocupación general (CNO-11, Gipuzkoa 2024)

| Ocupación | Personas | % del empleo |
|---|---:|---:|
| Ocupaciones elementales | 69.850 | 20,9 % |
| Servicios de restauración, personales, protección y vendedores | 67.790 | 20,3 % |
| **Técnicos y profesionales científicos e intelectuales** | 62.114 | **18,6 %** |
| Técnicos y profesionales de apoyo | 39.036 | 11,7 % |
| Empleados contables/administrativos/oficina | 34.292 | 10,2 % |
| Artesanos y cualificados de industrias manufactureras | 32.754 | 9,8 % |
| Operadores de instalaciones y montadores | 22.218 | 6,6 % |
| Directores y gerentes | 5.074 | 1,5 % |
| Cualificados agrario/ganadero/forestal/pesquero | 1.336 | 0,4 % |

Casi 1 de cada 5 ocupados en Gipuzkoa es "técnico o profesional científico e
intelectual" — el grupo CNO que incluye a investigadores, ingenieros,
sanitarios y docentes universitarios. Pero el grupo *mayor* sigue siendo
"ocupaciones elementales" + "servicios de restauración/personales/vendedores"
(41,2 % conjuntamente): el perfil investigador convive con un mercado laboral
donde los servicios poco cualificados siguen siendo la base numérica más
grande. Sin cruce con nacionalidad (no existe a este grano), no se puede
decir qué parte de cada grupo es población extranjera — pero el §1.3 ya
sugiere, indirectamente, dónde se concentra cada uno por barrio.

### 2.3 El gradiente salarial (C.A. de Euskadi, 2023, renta media del trabajo)

| Profesión | €/año |
|---|---:|
| Directores y gerentes | 65.657 |
| Técnicos y profesionales científicos e intelectuales | 39.359 |
| Técnicos y profesionales de apoyo | 32.512 |
| Empleados contables/administrativos/oficina | 30.054 |
| Operadores de instalaciones y montadores | 28.815 |
| Artesanos y cualificados de manufactura/construcción | 27.333 |
| Cualificados agrario/ganadero/forestal/pesquero | 24.781 |
| Ocupaciones elementales | 21.488 |
| **Servicios de restauración, personales, protección, vendedores y FFAA** | **18.044** |

El sueldo medio de "directores y gerentes" (65.657 €) es **3,6 veces** el de
"servicios de restauración/personales/vendedores" (18.044 €) — la categoría
que agrupa a buena parte de la hostelería. Los "técnicos y profesionales
científicos e intelectuales" (39.359 €, la categoría que incluye
investigación) ganan más del doble que esa misma categoría de servicios. El
dato es de C.A. de Euskadi, sin barrio ni nacionalidad — pero, combinado con
§1.3 (dónde vive cada región de origen) y §2.2 (qué ocupaciones dominan),
permite una lectura indirecta razonable: los barrios con mayor cuota
latinoamericana/magrebí son también los de menor renta media (§1.3), y la
brecha salarial entre "servicios" e "investigación/dirección" es real y
grande a nivel del sistema — la intuición de que "los trabajos que suelen
hacer los extranjeros económicos pagan sensiblemente menos" es consistente
con los números, aunque no se pueda demostrar el cruce exacto por persona.

### 2.4 Composición sectorial de Donostia (establecimientos, 2008 vs. 2025)

| Sector | 2008 | 2025 |
|---|---:|---:|
| Comercio, transporte y hostelería | 33,3 % | 30,9 % |
| Actividades profesionales, científicas y administrativas | 21,9 % | 24,9 % |
| Administración pública, educación, sanidad y otros servicios | 8,9 % | **15,1 %** |
| Construcción | **14,0 %** | **7,3 %** |
| Información y comunicaciones | 2,5 % | 3,4 % |
| Actividades financieras y seguros | 3,0 % | 3,1 % |
| Industria, energía y saneamiento | 3,4 % | 2,8 % |
| Actividades inmobiliarias | 3,9 % | 2,7 % |

El total de establecimientos cae un 21 % en el período (22.862 → 18.037) —
la huella de la crisis de 2008-2013, muy visible en el desplome de la
construcción (14,0 %→7,3 %, se reduce a la mitad). Comercio/hostelería sigue
siendo, con diferencia, el sector con más establecimientos (31 % del tejido),
pero pierde peso relativo frente al crecimiento de "profesionales,
científicas y administrativas" y sobre todo de "administración pública,
educación, sanidad" (+6,2 p.p., el mayor movimiento del período). Es
*establecimientos*, no empleo — un solo hospital o universidad cuenta como un
establecimiento igual que una tienda de una persona, así que esta tabla dice
más sobre la diversificación del tejido económico que sobre dónde trabaja
más gente (para eso, ver §2.2).

---

## 3. Qué no se puede afirmar (límites)

1. **No existe nacionalidad × ocupación × salario en ningún grano español**
   (municipal, provincial, ni C.A.). Todo lo dicho sobre "qué trabajo hace
   cada grupo de origen" en §1.5 es una triangulación de geografía + renta +
   estabilidad laboral por continente — nunca una medición directa.
2. **La mayoría de los datos de empleo son de Gipuzkoa, no de Donostia**
   (Eustat no baja de territorio histórico en la EPA vasca por diseño
   muestral). Donostia concentra ~35 % de la población de Gipuzkoa y buena
   parte de sus centros de investigación/servicios, así que es razonable
   como contexto — pero no es una cifra propia de la ciudad.
3. **El sinhogarismo y la economía informal no aparecen en ninguna encuesta
   de actividad** (por diseño, encuestan hogares con domicilio). No hay proxy
   honesto; se documenta como vacío.
4. **"% extranjeros" nunca debe leerse como proxy único de nada** — este
   mismo análisis es la prueba: dentro de "extranjero" conviven una
   correlación de −0,69 con la renta (América Latina) y de +0,24 (Europa
   occidental) en el mismo grano barrio. Coherente con MET-5
   (`docs/NOTA-METODOLOGICA.md`) y con el principio de "transformación, nunca
   gentrificación" del proyecto.
5. Los "nómadas digitales" y los "extranjeros ricos que aprecian la ciudad"
   de la hipótesis inicial **no tienen ninguna fuente pública que los mida**
   — ni volumen, ni concentración geográfica específica más allá de lo que ya
   captura "Norteamérica/Oceanía" (grupo demasiado pequeño y heterogéneo para
   aislarlos).

---

## 4. Del análisis al dashboard — qué se implementó

Implementado en el pipeline (jul-2026):

- **8 choropletas nuevas barrio-año** (`pct_origin_latam`,
  `pct_origin_norte_africa`, `pct_origin_africa_subsahariana`,
  `pct_origin_europa_occidental`, `pct_origin_europa_este`,
  `pct_origin_oriente_medio`, `pct_origin_asia`,
  `pct_origin_norteamerica_oceania`) — mismo `demo_barrio.csv` que ya
  alimentaba `pct_foreign`, agregado por región en vez de extranjero sí/no.
  Módulo `data-pipeline/src/donostia_pipeline/datasets/demografia_origen_region.py`,
  registrado en `build.DATASETS`, sin descarga adicional (reutiliza la fuente
  de `pct_foreign`). Seleccionables ya en el picker de métricas del dashboard.
- **3 indicadores de ciudad** — `unemployment_rate_spanish_gipuzkoa` /
  `unemployment_rate_foreign_gipuzkoa` (tasa de paro por nacionalidad,
  Gipuzkoa, 2015–2026) y `randd_personnel_per_1000_employed_gipuzkoa`
  (intensidad investigadora, Gipuzkoa, 2001–2024). Módulo
  `datasets/empleo_nacionalidad_gipuzkoa.py`, tres nuevas queries Eustat
  PxWeb en `build.py` (`ensure_eustat_empleo_nacionalidad`). Visibles en el
  panel "Altri indicatori cittadini" del dashboard.
- Confianza y supuestos registrados en `provenance.py` para las 8 métricas
  (incluida la advertencia de que `pct_origin_latam`/`_norte_africa`
  correlacionan con renta en sentido opuesto a `_europa_occidental` — la
  razón por la que se desglosó el agregado).
- 21 tests nuevos (`data-pipeline/tests/test_demografia_origen_region.py`,
  `test_empleo_nacionalidad_gipuzkoa.py`); pipeline completo verificado
  end-to-end (`python -m donostia_pipeline.build`, 35 métricas + 28
  indicadores) y dashboard comprobado en navegador (choropleta + panel de
  indicadores renderizando con los valores esperados).

**Se quedan analysis-only**, porque no encajan en el modelo `Metric`
(coroplético barrio×año, un valor numérico) ni `Indicator` (un valor por
año, ciudad): la ocupación por CNO-11 (§2.2, 10 categorías por año), los
establecimientos por sector A10 en Donostia (§2.4, 9 categorías por año) y la
renta por profesión (§2.3, 9 categorías, sin serie anual larga). Encajarían
mejor como un gráfico de barras/tabla dedicado que como una entrada más del
picker de choropletas — candidato a componente propio si se narra una
séptima historia (ver más abajo), no a una nueva métrica del contrato de
datos.

**Pendiente (Cowork, no código)**:

- **Ficha de país** en el detalle de barrio: top-5 países de origen con su
  evolución a 10 años, usando `extranjeros_top_paises.csv`.
- **Séptima historia** para `output/historias.html`: "quién trabaja Donostia"
  — combinaría el mapa de origen por región (ya wireado) con el ya existente
  de renta/estudios, más el gradiente ocupación→salario (§2.2–2.3, vía
  gráfico propio), con el aviso metodológico de §3 en el texto, no solo en la
  ficha (mismo criterio que ya aplica el proyecto al `% extranjeros`
  agregado).

---

## Reproducibilidad

```bash
# Análisis exploratorio (este documento)
python analysis/perfil_extranjeros_empleo.py --save
pytest analysis/tests/test_perfil_extranjeros_empleo.py

# Pipeline (métricas/indicadores en vivo del dashboard)
cd data-pipeline && python -m donostia_pipeline.build
pytest data-pipeline/tests/test_demografia_origen_region.py \
       data-pipeline/tests/test_empleo_nacionalidad_gipuzkoa.py
```

Fuentes crudas en `datos/input/raw/` (no versionadas; se descargan con las
queries documentadas en `datos/input/FUENTES.md` y en las docstrings de cada
`load_*` del script). Salidas tidy en `analysis/output/`:
`extranjeros_origen_ciudad.csv`, `extranjeros_origen_barrio.csv`,
`extranjeros_top_paises.csv`, `extranjeros_actividad_continente_gipuzkoa.csv`,
`tasas_actividad_nacionalidad_gipuzkoa.csv`, `ocupacion_cno_gipuzkoa.csv`,
`id_personal_gipuzkoa.csv`, `establecimientos_sector_donostia.csv`,
`renta_por_profesion_caev.csv`.
