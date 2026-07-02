# Donostia Dataviz — Resumen para revisión

> **Propósito.** Documento de síntesis del proyecto para que otra IA (u otra persona)
> pueda revisar el trabajo hecho y **sugerir ampliaciones y mejoras**. Recoge los
> datos disponibles, el análisis realizado, los insights y correlaciones verificados,
> y las seis historias que salen de todo ello.
>
> **Naturaleza del proyecto.** Análisis y visualización de datos abiertos sobre
> Donostia / San Sebastián (19 barrios oficiales) para *contar la evolución de la
> ciudad* en varios ejes: vivienda, demografía, turismo, clima, transformación.
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
| `ageing_index` | ≥65/<15 ×100 | 18 barrios, 2000–2025 | observado | Padrón |
| `pct_youth_adults` | % 25–39 | 18 barrios, 2000–2025 | observado | Padrón |
| `vut_density` / `vut_count` / `vut_plazas` | VUT /1000 ab. | por barrio | derivado | Donostia Open Data |
| `airbnb_density` | anuncios /1000 ab. | 19 barrios, snapshot 2025-09 | derivado | Inside Airbnb |
| `schools_per_1000` | centros /1000 ab. | por barrio | derivado | Open Data (equipamientos) |
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

---

## 3. Insights y correlaciones (verificados)

### Correlaciones entre barrios (Pearson; Spearman; sin outliers)

| Par | Pearson | Spearman | Sin outliers | Lectura |
|---|---|---|---|---|
| tensión de vivienda ↔ renta | **−0,81** | −0,86 | **−0,89** (n=11) | La más fuerte y robusta del sistema |
| densidad VUT ↔ alquiler €/m² | 0,64 | 0,75 | 0,62 (n=11) | Turismo donde el alquiler es alto; aguanta sin Erdialdea/Gros |
| % universitarios ↔ renta | 0,75 | 0,85 | 0,76 | Capital educativo ligado a renta |
| % universitarios ↔ alquiler | 0,84 | 0,83 | — | — |
| alquiler ↔ renta | 0,72 | 0,72 | 0,65 | — |
| renta ↔ % extranjeros | −0,58 | −0,52 | −0,72 | Inmigración económica (no gentrificación) |
| tensión ↔ % extranjeros | 0,74 | 0,64 | — | La presión recae donde crece la inmigración |
| tensión ↔ escuelas/1000 | −0,63 | −0,39 | — | Más equipamiento donde menos presión |

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
  r(−1)=−0,10 · r(0)=0,19 · **r(+1)=0,27** · r(+2)=0,09. Máximo a +1 año: el
  turismo *precede* al alquiler. Débil pero asimétrico y direccional. **No** causal.
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

---

## 4. Las seis historias (entregable `historias.html`)

Cada relato: pregunta → 2–3 números con fuente → conclusión causal *cauta* → aviso
de confianza → vista interactiva.

1. **La ciudad que se encarece.** ¿Dónde es insostenible vivir? El esfuerzo
   alquiler/renta **se invierte** respecto al precio: máximo en el este obrero
   (Altza ~21,9 %, Egia ~21,3 %, Intxaurrondo ~20,9 %), no en el centro caro.
   Correlación tensión↔renta −0,89. *Derivado; supuesto 30 m²/persona regulable.*
2. **Qué barrios cambian más rápido.** Alquiler +3–4 %/año en todas partes;
   extranjeros crecen en el este; el centro pierde población. Egia es el "barrio en
   movimiento" (universitarios al alza). *Perfiles descriptivos, N=13.*
3. **Quién vive Donostia.** El centro turístico es el más envejecido (Gros índice
   370, Erdialdea 350) y el este el más joven (Intxaurrondo 21 % de 25–39). Antiguo
   envejece rápido (+203 puntos 2000→2025); Miramón rejuvenece. *Sin rotación no
   hay prueba de desplazamiento; el envejecimiento del centro es anterior al boom
   turístico.*
4. **El clima cambia.** +0,31 °C/década, más días de calor, picos de 39,7 °C; la
   lluvia sin señal. *Observado; una sola estación (relato temporal, no espacial).*
5. **La ciudad turística vs. la vivida.** *(nueva)* Airbnb se concentra en el
   centro (Erdialdea ~34/1000, Gros ~19) y crece ×6 desde 2016 (vs ×1,6 el hotel;
   parte es adopción de plataforma, MET-7); indicio de que precede al alquiler
   ~1 año (r≈0,27). El ruido nocturno es de **tráfico**, no de turismo (capa
   ambiental). *Densidad derivada; reseñas = proxy.*
6. **Donostia en transformación.** *(nueva)* Índice AN-8 con 3 mapas + scatter: la
   presión turística (centro) y la transformación social (Loiola/Egia, periferia)
   **no coinciden** (r≈0,25). Con Airbnb integrado, Aiete baja de 0,37 a 0,07: caro
   pero no turístico. *"Transformación", no "gentrificación"; N=13, pesos iguales.*

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

- **N=13 barrios** clasificables en los análisis de renta/alquiler/transformación
  (los 6 periféricos rurales no tienen renta/alquiler; se excluyen de densidades
  per cápita para evitar artefactos).
- **Alquiler anual** → lead/lag solo en pasos de 1 año, potencia modesta.
- **Reseñas Airbnb** infraestiman estancias y crecen con la adopción de la
  plataforma (mitigado con primeras diferencias, no eliminado).
- **Renta en bandas / sin edad mediana interpolada**; sin microdatos de rotación.
- **Índice AN-8:** combina *niveles* (foto actual), pesos iguales; no mide la
  velocidad de la presión turística (eso vive en el lead/lag). Sensibilidad a
  los pesos sin testear aún (AN-9 pendiente); renta y % universitarios están
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
2. **Estructura de edad como señal de sustitución residencial**: cruzar la pérdida
   de población del centro (#2) con su cambio de perfil de edad (#3).
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
