# Donostia Dataviz — Resumen para revisión

> **Propósito.** Documento de síntesis del proyecto para que otra IA (u otra persona)
> pueda revisar el trabajo hecho y **sugerir ampliaciones y mejoras**. Recoge los
> datos disponibles, el análisis realizado, los insights y correlaciones verificados,
> y las siete historias que salen de todo ello.
>
> **Naturaleza del proyecto.** Análisis y visualización de datos abiertos sobre
> Donostia / San Sebastián (19 barrios oficiales) para *contar la evolución de la
> ciudad* en varios ejes: vivienda, demografía, origen migratorio y empleo, turismo, clima, transformación.
> Todos los números son reproducibles desde el pipeline (`data-pipeline/`) y los
> scripts de `analysis/*.py`. El entregable narrativo es `historias.html`
> (autocontenido, con mapas y gráficos interactivos generados en el navegador).
>
> **Nota de nomenclatura.** El barrio se llama **Antiguo** (no "Antigua").
> Corregido en el entregable narrativo; el `barrio_id` interno sigue siendo
> `antigua` como clave de join (ver §Pendientes).

---

## 1. Datos disponibles

Fuentes oficiales salvo MICE (curado de notas de prensa citadas). Nivel de
confianza por métrica: **observado** (dato directo), **derivado** (calculado),
**proxy** (aproximación).

### Métricas por barrio (choropleths)

| Métrica | Unidad | Cobertura | Confianza | Fuente |
|---|---|---|---|---|
| `housing_tension` | esfuerzo alquiler/renta (%) | 13 barrios, 2023 | derivado | EMA + Eustat |
| `rent_eur_m2` | €/m² | 13 barrios, 2023–2024 | observado | Gob. Vasco EMA |
| `income_total` | renta per cápita € | 17 barrios | observado | Eustat |
| `pct_university` / `pct_foreign` | % | por barrio, serie | observado | Padrón |
| `pct_origin_*` (8 regiones de origen) | % del barrio | por barrio, 2000–2025 | observado | Padrón (país de nacimiento) |
| `ageing_index` | ≥65/<15 ×100 | 18 barrios, 2000–2025 | observado | Padrón |
| `pct_youth_adults` | % 25–39 | 18 barrios, 2000–2025 | observado | Padrón |
| `vut_density` / `vut_count` / `vut_plazas` | VUT /1000 ab. | por barrio | derivado | Donostia Open Data |
| `airbnb_density` | anuncios /1000 ab. | 19 barrios, snapshot 2025-09 | derivado | Inside Airbnb |
| `schools_per_1000` | centros /1000 ab. | por barrio | derivado | Open Data (equipamientos) |
| `health_per_1000` | servicios de salud /1000 ab. | por barrio, snapshot | derivado | Open Data (equipamientos, REC-18) |
| `vpo_dwellings_per_1000` | viviendas Etxebide /1000 ab. | por barrio, snapshot | proxy | Etxebide / Open Data Euskadi (REC-15; ventana parcial: ≤~⅓ del solo alquiler protegido, patronato municipal ausente) |
| `noise_night_pct55` | % área ≥55 dB (Lnight) | por barrio, 2022 | proxy | Mapa estratégico ruido |
| `transform_class` | clase (4 categorías) | 13 barrios | derivado | Índice AN-8 |
| `transform_tourism_score` / `transform_socio_score` | z-score | 13 barrios | derivado | Índice AN-8 |
| `transform_univ_excess` / `transform_rent_excess` | exceso vs mediana | 13 barrios | derivado | Índice AN-8 |

### Series temporales (grano ciudad)

| Serie | Cobertura | Fuente |
|---|---|---|
| `temp_avg` / `temp_max` / `precip` (mensual y anual) | 1981–2025 | AEMET, estación Igeldo |
| `hot_days_30` (días ≥30 °C/año) | 1981–2025 | AEMET, Igeldo |
| `overnight_stays` (pernoctaciones hotel, mensual) | 2005–2026 | INE EOH tabla 2078 |
| `airbnb_reviews` (reseñas/mes, proxy de estancias) | 2011–2025 | Inside Airbnb |
| `airbnb_activity` (reseñas/año/1000 ab., panel barrio×año) | 2011–2025 | Inside Airbnb |

### Indicadores anuales de ciudad

`tax_revenue` (impuestos, 73→106 M€ 2011–2025), `fee_revenue` (tasas, 35→63 M€),
`recycling_rate` (recogida selectiva %), `mice_icca_congresses`,
`mice_events_total` (188 eventos en 2024, récord), `mice_attendees` (259.000).

Nuevos (jul-2026): `unemployment_rate_spanish_gipuzkoa` / `unemployment_rate_foreign_gipuzkoa`
(paro por nacionalidad, Gipuzkoa 2015–2026: 4,3 % vs 9,4 %),
`randd_personnel_per_1000_employed_gipuzkoa` (I+D, 31,0‰ en 2024; España 13,6‰),
`vut_licenses_new` / `vut_licenses_cumulative` / `vut_plazas_cumulative` (registro REATE,
ciudad 2016–2025), `residents_work_in_city_pct` / `residents_study_in_city_pct` / `jobs_located`
+ derivado `job_concentration_ratio` (1,20 en 2024: la ciudad importa trabajadores, cierra H4).

---

## 2. Análisis realizado

Reproducible con `python analysis/<script>.py`. Solo pandas + numpy.

- **`sprint_a.py`** — matriz de correlaciones (Pearson y Spearman) entre métricas
  de barrio, con test de robustez *leave-outliers-out* (`corr_robustness.csv`).
- **`distribucion_barrios.py`** — distribución de renta/alquiler; Gini territorial
  ponderado por población (AN-5), matriz niveles×variaciones del alquiler (AN-4).
- **`transformation_index.py`** — Índice de Transformación Urbana (AN-8):
  dos modos (socioeconómico estilo Freeman 2005 adaptado, y presión turística),
  pesos iguales, componentes a la vista, año base 2016. Bloqueado por test.
- **`lead_lag.py`** — test exploratorio turismo→alquiler (AN-6): panel barrio×año
  en primeras diferencias, correlación por desfase temporal.
- **Velocidad de cambio** (`velocity.csv`) — pendiente anualizada 2016→último de
  cada métrica por barrio, y un `speed_index` compuesto.
- **Índice de vejez / estructura de edad** — series 2000–2025 por barrio.
- **Tanda inferencial AN-9…AN-20 (jul-2026)** — bootstrap, permutaciones, efectos
  fijos, Moran's I, β-convergencia (`analysis/*.py`, uno por análisis) y, en la
  última tanda: descomposición por cohortes (`population_decomposition.py`),
  estacionalidad por barrio (`tourism_seasonality.py`), ruptura COVID
  (`covid_break.py`) y trayectorias (`trajectories.py`). Resultados en
  `docs/intermedia/ANALISIS-INFERENCIAL.md`.

---

## 3. Insights y correlaciones (verificados)

### Correlaciones entre barrios (Pearson; IC95% bootstrap; Spearman; sin outliers)

| Par | Pearson | IC95% (AN-10) | Spearman | Sin outliers | Lectura |
|---|---|---|---|---|---|
| tensión de vivienda ↔ renta | **−0,81** | −0,96 a −0,67 | −0,86 | **−0,89** (n=11) | La más fuerte y robusta del sistema |
| densidad VUT ↔ alquiler €/m² | 0,64 | 0,42 a 0,87 | 0,75 | 0,62 (n=11) | Turismo donde el alquiler es alto; aguanta sin Erdialdea/Gros |
| % universitarios ↔ renta | 0,75 | 0,58 a 0,93 | 0,85 | 0,76 | Capital educativo ligado a renta |
| % universitarios ↔ alquiler | 0,84 | — | 0,83 | — | — |
| alquiler ↔ renta | 0,72 | 0,24 a 0,96 | 0,72 | 0,65 | Intervalo ancho: compatible con asociación débil |
| renta ↔ % extranjeros | −0,58 | −0,86 a −0,18 | −0,52 | −0,72 | Inmigración económica (no gentrificación) |
| tensión ↔ % extranjeros | 0,74 | — | 0,64 | — | La presión recae donde crece la inmigración |
| tensión ↔ escuelas/1000 | −0,63 | — | −0,39 | — | Más equipamiento donde menos presión |

*IC95% = bootstrap percentil (2.000 remuestreos, `analysis/sprint_a.py`); solo
para los pares del set de robustez. Con N=13–18 los intervalos son anchos a
propósito: esa es la información.*

> ⚠️ **Falacia ecológica (MET-6):** correlaciones a nivel de **barrio** (N=13),
> no individual. P.ej. tensión↔extranjeros no dice nada de hogares concretos:
> los barrios de alquiler proporcionalmente más gravoso son también los de más
> inmigración económica, nada más.

### Otras señales cuantificadas

- **Turismo vs. hotel (índice base 2016=100):** la actividad Airbnb pasa de 100 a
  **599** en 2024 (×6); las pernoctaciones hoteleras, de 100 a **162** (×1,6). El
  turismo reglado crece, el de plataforma se dispara. Bache visible en 2020 (COVID).
  ⚠️ Parte del ×6 es **adopción de plataforma** (migración de canal, mayor tasa de
  reseña), no turistas nuevos (MET-7); orden de magnitud válido, cifra exacta no.
- **Lead/lag turismo→alquiler (AN-6, panel n=90, primeras diferencias):**
  r(−1)=−0,10 · r(0)=0,19 · **r(+1)=0,27** · r(+2)=0,09. Máximo a +1 año.
  ⚠️ **El blindaje AN-16 (jul-2026) rebajó esta señal:** con efectos fijos de
  año (que absorben IPC, tipos, COVID) r(+1) cae a **0,10** y la permutación da
  **p≈0,30** — la mayor parte era covariación macro común. El indicio
  direccional **no se sostiene**; pregunta abierta a la espera de REC-12.
- **La pérdida de población del centro es vegetativa, no de expulsión (AN-12,
  residuo por cohortes):** Erdialdea **atrae** migración neta (+2.162 en
  2000–2025) y aun así pierde población — su déficit nacimientos−defunciones
  (−3.435) se lo come todo. **Gros** es el único barrio con las dos sangrías
  (vegetativa −2.807 y migratoria −562) y el único con éxodo 25–39 en las cinco
  ventanas quinquenales (−4 % a −9 %). El desplazamiento neto, si existe, es
  **selectivo (Gros joven)**, no un vaciado del centro.
- **La dependencia del verano es de la periferia, no del centro (AN-14):**
  ratio verano/invierno ≈4,8 en Intxaurrondo/Igeldo y 4,3 en Antiguo frente a
  **2,1 en Erdialdea, el barrio menos estacional** — su presión turística es
  crónica, no un pico de agosto (validado con pernoctaciones INE de ciudad: 2,0).
- **El COVID no interrumpió la turistificación: la aceleró (AN-20):** todas las
  series recuperan el nivel 2019 en 2021–22 y salen con más pendiente (alquiler
  ×2,4, Airbnb ×1,9); el mapa de la presión no cambia (ρ=0,67 pre/post) pero se
  **difunde** hacia barrios antes poco turísticos (Ibaeta ×7,5).
- **Trayectorias 2000→2025 (AN-18):** la universitarización sube en **17/17
  barrios** (una marea, sin historia diferencial); el relato está en la edad —
  Antiguo +197 puntos, Miramón-Zorroaga −218, Loiola −20 (todo desde 2015) y la
  **V de Egia** (rejuveneció 2000→2010, re-envejeció después; tortuosidad 4,3).
  La dispersión de la nube es plana (1,36→1,28): coherente con H3.
- **El contrapeso público tiene número de ciudad, pero no mapa completo (REC-15):**
  el alquiler protegido + alojamientos dotacionales suma **3.151 viviendas — la
  cuarta parte del alquiler ocupado** del municipio (memoria de la zona
  tensionada, 2024: Etxegintza 2.087, Gob. Vasco/Alokabide 554, Benta Berri 510).
  La única ventana georreferenciada abierta son las **promociones de Etxebide**
  (1.120 viviendas, ≤~⅓ del solo parque de alquiler): se concentran en el este
  obrero/periferia interior —Loiola **22,3‰**, Amara Berri 18,7, Intxaurrondo
  16,3, Ibaeta 15,5—. ⚠️ **Los ceros de ese mapa no son ceros de vivienda
  protegida**: el patronato municipal (2/3 del parque de alquiler, «repartido por
  la mayor parte de los barrios») no se publica georreferenciado — dónde *falta*
  el contrapeso queda como **laguna declarada**.
- **La concentración turística se agudiza al bajar al callejero (sub-barrio):**
  cruzando el censo VUT con el callejero municipal (301 calles con ≥1 vivienda
  turística, emparejamiento del 100 % de 1.489 fichas), las **diez calles** más
  cargadas reúnen el **19 %** de todo el censo VUT/HUT: Zabaleta (35 unidades),
  Urbieta (34), Easo (33), San Marcial (31). La media de barrio borra estos ejes.
- **Dos transformaciones, dos geografías:** correlación entre el score
  socioeconómico y el turístico ≈ **0,25** (débil, N=13) → **no coinciden**.
  Turismo en el centro acomodado (Erdialdea +2,40, Gros +1,37); cambio social en la
  periferia interior (Loiola +1,02, único "en transformación"; Egia incipiente).
- **Brecha de renta entre barrios estable:** Gini territorial ponderado ~0,10 en
  2016 y ~0,10 en 2023 (el pico de 2022 sin ponderar es un outlier de
  Miramón-Zorroaga). No es "los ricos se separan de los pobres".
- **Velocidad de cambio 2016→:** alquiler +3–4 %/año en casi todos (Loiola +4,3,
  Aiete +3,9, Intxaurrondo +3,9); % extranjeros crece más en el este (Intxaurrondo
  +0,92 pp/año); el centro pierde población (Gros −0,60 %/año, Antiguo −0,45,
  Egia −0,33).
- **Clima (Igeldo 1981–2025):** +0,31 °C/década (R²=0,39; 13,1→14,7 °C); días
  ≥30 °C +0,81/década (R²=0,10; picos 2003/2022/2023); precipitación sin tendencia
  (R²=0,06). Máxima absoluta 39,7 °C (2022).

### Tesis integradora (cauta)

La touristificación se concentra en el centro acomodado y se asocia a alquileres
altos, pero la **presión de vivienda más dura recae en el este obrero**, donde la
renta no acompaña. La brecha de renta *entre* barrios no se ensancha: lo que cambia
no es tanto cuánto gana cada zona como **quién puede permitirse vivir dónde** — con
el clima calentándose de fondo. *(Lectura sugerida por señales convergentes, no
hecho demostrado: sin microdatos de movilidad no se puede afirmar desplazamiento.)*

### El proyecto como generador de hipótesis

Más que respuestas cerradas, el análisis deja **cuatro hipótesis empíricas**
contrastables con datos mejores (detalle y tests propuestos en
`docs/TESIS-CIUDAD.md`): **H1** la presión turística anticipa el alquiler ~1 año
(⚠️ *debilitada por AN-16: no sobrevive al control por shocks comunes de año*);
**H2** transformación turística y social siguen geografías distintas (✅
*reforzada por AN-9: el patrón no depende de los pesos del índice*); **H3** la
desigualdad territorial permanece estable mientras cambia la accesibilidad (✅
*reforzada por AN-13: ni convergencia ni divergencia — β≈0 en renta, alquiler y
% universitarios*); **H4** el centro pierde población sin dejar de concentrar actividad (✅ *cerrada
jul-2026: la pérdida es vegetativa (AN-12, el centro atrae migración neta y el éxodo joven es
de Gros) y la concentración de actividad es real — Donostia cuenta 1,20 empleos localizados por
residente ocupado en 2024, REC-17: importa trabajadores*).

---

## 4. Las siete historias (entregable `historias.html`)

Cada relato: pregunta → 2–3 números con fuente → conclusión causal *cauta* → aviso
de confianza → vista interactiva.
Desde jul-2026 se presentan como **capítulos de un solo relato** (estado → cambio
→ personas → trabajo/origen → telón de fondo → dos ciudades → síntesis → epílogo), con
transiciones entre capítulos y enlaces a `metodologia.html` y `datos.html`.

1. **La ciudad que se encarece.** ¿Dónde es insostenible vivir? El esfuerzo
   alquiler/renta **se invierte** respecto al precio: máximo en el este obrero
   (Altza ~21,9 %, Egia ~21,3 %, Intxaurrondo ~20,9 %), no en el centro caro.
   Correlación tensión↔renta −0,89. *Derivado; supuesto 30 m²/persona regulable.*
2. **Qué barrios cambian más rápido.** Alquiler +3–4 %/año en todas partes;
   extranjeros crecen en el este; el centro pierde población. Egia es el "barrio en
   movimiento" (universitarios al alza). *Perfiles descriptivos, N=13.*
3. **Quién vive Donostia.** El centro turístico es el más envejecido (Gros índice
   370, Erdialdea 350) y el este el más joven (Intxaurrondo 21 % de 25–39). Antiguo
   envejece rápido (+203 puntos 2000→2025); Miramón rejuvenece. La
   descomposición por cohortes (AN-12) precisa el porqué de la pérdida del
   centro: **vegetativa, no de expulsión** — Erdialdea atrae migración; Gros es
   el único con éxodo joven sostenido. *Sin rotación no
   hay prueba de desplazamiento; el envejecimiento del centro es anterior al boom
   turístico.*
4. **Quién trabaja Donostia.** *(nueva, REC-21)* «% extranjeros» esconde dos poblaciones
   opuestas: la de origen latinoamericano (×19 desde 2000, >½ del total) y magrebí se concentra
   en el este de renta baja (r=−0,69 y −0,48 con la renta del barrio); la europeo-occidental, en
   el centro caro (+0,24 con renta, +0,59 con % universitarios). El paro extranjero en Gipuzkoa
   dobla al español (9,4 % vs 4,3 %; africano 18,4 % — EPA: encuesta con
   submuestras pequeñas por continente, orden robusto pero cifra con error). La ciudad tiene intensidad investigadora
   doble que España (31,0‰ vs 13,6‰) y a la vez una base ancha de servicios mal pagados
   (dirección 65.657 € vs servicios 18.044 €, ×3,6). *No existe cruce nacionalidad×ocupación×salario
   a este grano (MET-5): todo es triangulación entre barrios, nunca lectura individual (MET-6).*
5. **El clima cambia.** +0,31 °C/década, más días de calor, picos de 39,7 °C; la
   lluvia sin señal. Con satélite (Landsat, REC-14) el calentamiento gana mapa: Gros +4,8 °C,
   Amara Berri +4,3, Egia +4,1 de temperatura de superficie sobre la media de ciudad — el este denso.
   *Serie temporal de una sola estación; la isla de calor es LST de superficie, rasgo estructural.*
6. **La ciudad turística vs. la vivida.** *(nueva)* Airbnb se concentra en el
   centro (Erdialdea ~34/1000, Gros ~19) y crece ×6 desde 2016 (vs ×1,6 el hotel;
   parte es adopción de plataforma, MET-7 — cuantificado en REC-13: la oferta activa real solo sube
   +2,0 % en 2023–2025 frente a +20,2 % de reseñas, ×1,18 de exageración; altas VUT del REATE 300/año→18). El indicio de que precedía al
   alquiler ~1 año (r≈0,27) **no superó el blindaje AN-16** (con FE de año,
   r≈0,10, p≈0,30). El ruido nocturno es de **tráfico**, no de turismo (capa
   ambiental). La estacionalidad por barrio (AN-14) invierte la intuición: la
   periferia depende del verano (ratio ~4,8) y **Erdialdea es el menos
   estacional (2,1)** — presión crónica; y el COVID no interrumpió la
   turistificación, la aceleró y difundió (AN-20). Bajo la media de barrio, la
   vista calle a calle enseña los ejes saturados (top-10 calles = 19 % del censo
   VUT). La cara vivida suma la capa de **salud** (REC-18): sanidad de proximidad
   con Loiola/Egia en cabeza de los 13 urbanos; Miramón-Zorroaga (3,4/1000) es
   artefacto per cápita del hospital. *Densidad derivada;
   reseñas = proxy.*
7. **Donostia en transformación.** *(nueva)* Índice AN-8 con 3 mapas + scatter: la
   presión turística (centro) y la transformación social (Loiola/Egia, periferia)
   **no coinciden** (r≈0,25). Con Airbnb integrado, Aiete baja de 0,37 a 0,07: caro
   pero no turístico. Las trayectorias 2000→2025 (AN-18, connected scatter
   estático nuevo) añaden la lectura MET-8: universitarización como marea
   (17/17), tres formas de envejecer y la **V de Egia** (su momento joven ya
   revirtió). Cierra con el **contrapeso público** (REC-15): a escala ciudad el
   alquiler protegido es ¼ del alquiler ocupado (3.151 viviendas); la única
   ventana por barrio (promociones Etxebide, ≤~⅓ de ese parque) apunta al este
   obrero (Loiola 22,3‰) — sus ceros **no** son ceros de vivienda protegida.
   *"Transformación", no "gentrificación"; N=13, pesos iguales.*

> **Apéndice del HTML — "La ciudad de fondo":** estacionalidad hotelera,
> reciclaje, fiscalidad municipal y MICE, como contexto de ciudad.
> **Cierre del HTML — "Lo que los datos aún no pueden responder":** los límites
> del proyecto, en primera plana (jul-2026).

---

## 5. Reglas de encuadre (no negociables)

- **"Transformación", no "gentrificación"** — falta rotación/sustitución de
  población (MET-2).
- **Correlación ≠ causalidad** (MET-3): incluso el lead/lag es exploratorio.
- **El ruido nocturno es de tráfico**, no proxy de turismo (corrección de #5).
- **% de extranjeros no es proxy de transformación** (inmigración económica).
- **Falacia ecológica** (MET-6): correlaciones entre barrios, nunca leídas a
  nivel individual.
- **El turismo no crea el envejecimiento del centro**: la estructura demográfica
  es anterior al boom de 2016; se implanta sobre ella.
- **El proxy Airbnb arrastra sesgo de adopción** (MET-7): el ×6 mezcla
  crecimiento real y migración de canal.
- **Estado ≠ cambio ≠ trayectoria** (MET-8): cada afirmación dice de cuál habla.
- Cada métrica lleva su ficha de confianza (observado/derivado/proxy).

---

## 6. Limitaciones conocidas

- **Registro ≠ universo** (auditoría de parcialidad, jul-2026): Airbnb = una
  sola plataforma (suelo del alquiler turístico online); EOH = solo
  establecimientos hoteleros; REATE = solo altas supervivientes; promociones
  Etxebide = ≤~⅓ del solo alquiler protegido; EPA por nacionalidad = encuesta
  con submuestras pequeñas; equipamientos = registro municipal (sin consultas
  privadas ni academias). **Un cero en un registro parcial no es un cero del
  fenómeno**; la cobertura se declara en la ficha de cada métrica.
- **N=13 barrios** clasificables en los análisis de renta/alquiler/transformación
  (los 6 periféricos rurales no tienen renta/alquiler; se excluyen de densidades
  per cápita para evitar artefactos).
- **Alquiler anual** → lead/lag solo en pasos de 1 año, potencia modesta.
- **Reseñas Airbnb** infraestiman estancias y crecen con la adopción de la
  plataforma (mitigado con primeras diferencias, no eliminado).
- **Renta en bandas / sin edad mediana interpolada**; sin microdatos de rotación.
- **Índice AN-8:** combina *niveles* (foto actual), pesos iguales; no mide la
  velocidad de la presión turística (eso vive en el lead/lag). La sensibilidad
  a los pesos ya está testeada (AN-9: en 1.000 combinaciones aleatorias el
  podio no cambia); renta y % universitarios están
  correlacionados (0,75) → posible doble conteo del capital socioeconómico.
- **Gini territorial:** mide desigualdad *entre* los 13 barrios; ciego a la
  desigualdad intra-barrio y a quien se marcha del municipio (posible "ilusión
  de equidad").
- **Supuesto 30 m²/persona:** uniforme entre barrios pese a que el tamaño del
  hogar varía con la demografía (hogares pequeños en el centro envejecido);
  regulable en la UI, corrección de fondo pendiente de REC-8.

---

## 7. Preguntas abiertas para la revisión (dónde ampliar)

> **Nota (jul-2026):** este documento ya pasó una ronda de revisión externa por
> tres IAs. La consolidación y las decisiones están en
> `docs/intermedia/FEEDBACK-IAS-2026-07.md`; las tareas resultantes, en
> `BACKLOG.md` (AN-9…AN-20, REC-12…REC-20).

Pensado para que otra IA proponga mejoras. Candidatos:

1. **Serie temporal de presión turística por barrio** (plazas VUT históricas, o
   Airbnb longitudinal) para triangular el proxy de reseñas y reforzar el AN-6.
2. ~~Estructura de edad como señal de sustitución residencial~~ ✅
   **Respondida (jul-2026, AN-12)**: la pérdida del centro es vegetativa
   (Erdialdea atrae migración neta); el éxodo 25–39 es de Gros. Queda el salto
   de barrio a hogar: microdatos de movilidad residencial.
3. **Alquiler mensual/trimestral** (si apareciera) → desfases finos en el lead/lag.
4. **Consolidar el modo turístico** del índice con más señales independientes.
5. **Revisar el encuadre y las cautelas**: ¿alguna afirmación excede lo que
   permiten los datos? ¿Falta algún aviso de confianza?
6. **Nuevos ejes de historia**: movilidad, coste de vida, servicios públicos,
   vivienda pública — ¿qué datos abiertos faltan por incorporar?
7. **Accesibilidad y claridad** de las visualizaciones (contraste, leyendas,
   lectura sin color).

---

## 8. Reproducibilidad

- Datos tidy: `data/*.csv` (metrics/series/indicators en formato long).
- Regenerar pipeline: `python -m donostia_pipeline.build`.
- Análisis: `python analysis/{sprint_a,distribucion_barrios,transformation_index,lead_lag}.py`.
- Documentación de referencia: `docs/GUION-OUTPUTS.md` (empieza aquí),
  `docs/TESIS-CIUDAD.md`, `docs/NOTA-METODOLOGICA.md`, `docs/SOURCES.md`;
  análisis en `docs/intermedia/` (`ANALISIS-SPRINT-A.md`, `ANALISIS-LEADLAG.md`,
  `INDICE-TRANSFORMACION.md`); backlog en `BACKLOG.md` (raíz).
- Entregable narrativo: `output/historias.html` (autocontenido).
- Datos de entrada: `datos/input/FUENTES.md` (manifiesto de fuentes).
