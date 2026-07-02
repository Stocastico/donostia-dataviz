# BACKLOG — Donostia Dataviz

> Backlog operativo del proyecto, separado por **quién** ejecuta:
>
> - **Cowork** — documentación, análisis narrativo, relatos y *outputs* (no toca código).
> - **Code** — pipeline de datos, frontend, estructura de datos y tests (Claude Code / local).
>
> Reemplaza a `docs/archive/GAP-ANALYSIS.md` (el backlog técnico detallado e
> histórico queda archivado ahí). Convención: ✅ hecho · ⬜ pendiente · 🔷 en curso.

---

## Estado en una línea

Pipeline + web + tests estables. **6 historias + sección de cierre** publicadas
en `output/historias.html`; análisis AN-1…AN-8 y correcciones MET-1…MET-8 hechos.
**Revisión externa por 3 IAs consolidada** (jul-2026,
`docs/intermedia/FEEDBACK-IAS-2026-07.md`) → alimenta AN-9…AN-20 y REC-12…REC-20.
Lo que queda es sobre todo **análisis inferencial y datos nuevos (Code)** e
**iteración narrativa (Cowork)**.

---

## Hecho ✅ (resumen)

- **Datos y pipeline:** 11 métricas coropléticas por barrio + velocidad de cambio
  + perfiles + estructura de edad + ruido nocturno + **Airbnb** (densidad y serie)
  + **Índice de Transformación** (AN-8); 5 series ciudad; 6 indicadores anuales.
  Join espacial, export CSV long, fichas de confianza. Tests pipeline + frontend.
- **Análisis:** correlaciones robustas (Pearson/Spearman/leave-one-out), velocidad,
  perfiles, matriz nivel×variación (AN-4), Gini territorial (AN-5), lead/lag AN-6
  exploratorio, Índice de Transformación AN-8.
- **Relatos:** las **6 historias** en `output/historias.html` (#5 turística vs.
  vivida y #6 en transformación añadidas jul-2026) + apéndice de contexto.
- **Documentos:** `TESIS-CIUDAD`, `GUION-OUTPUTS`, `NOTA-METODOLOGICA`, `SOURCES`,
  `output/resumen.md` (síntesis para revisión externa).
- **Reestructuración (jul-2026, Cowork):** `output/` (html + resumen),
  `datos/input` (MICE curado + `FUENTES.md` + `descargar_raw.sh`),
  `datos/procesado` (placeholder), `docs/intermedia/` y `docs/archive/`, este BACKLOG.
- **Revisión externa (jul-2026, Cowork):** feedback de ChatGPT/DeepSeek/Gemini
  consolidado con decisiones en `docs/intermedia/FEEDBACK-IAS-2026-07.md`.
  Aplicado ya: **MET-6** (falacia ecológica), **MET-7** (sesgo de adopción del
  proxy Airbnb), **MET-8** (estado ≠ cambio ≠ trayectoria) en
  `NOTA-METODOLOGICA`; matices en `TESIS-CIUDAD` (tesis como lectura sugerida,
  Gini inter-barrio, envejecimiento preexistente) y `resumen.md`; caveats en
  `historias.html` (#1, #3, #5) + **sección de cierre** "Lo que los datos aún
  no pueden responder".
- **Capítulos + páginas de apoyo (jul-2026, Cowork):** `historias.html`
  reestructurado como relato por capítulos con transiciones e hipótesis H1–H4
  en el epílogo; nuevos `output/metodologia.html` (MET-1…8, fichas de
  confianza, límites) y `output/datos.html` (catálogo métrica→fuente→confianza
  + fuentes caídas/descartadas), enlazados desde nav y footer de historias.

---

## Pendiente — Cowork ⬜

- ✅ **Revisar el render de los HTML de `output/`** — hecho (jul-2026): el usuario
  validó en navegador `historias.html` (con capítulos y epílogo), `metodologia.html`
  y `datos.html`. La iteración de contenido de #5/#6 quedó cubierta por la ronda
  de feedback de las 3 IAs.
- ✅ **Auditoría de enlaces internos** tras mover docs — hecha (jul-2026): los docs
  activos apuntan a `intermedia/`, `archive/` o `BACKLOG.md`; README y `resumen.md`
  actualizados. Los docs de `intermedia/`/`archive/` se dejan congelados.
- ✅ **Reestructurar las 6 historias como capítulos** — hecho (jul-2026): arco
  estado → cambio → personas → telón de fondo → dos ciudades → síntesis →
  epílogo; eyebrows "Capítulo N · etapa", transiciones `nextcap` entre
  capítulos, hero reescrito. Sin reordenar secciones ni renumerar (los IDs
  #1…#6 de los docs siguen valiendo).
- ✅ **Encuadrar el proyecto como generador de hipótesis** — hecho (jul-2026):
  H1–H4 explícitas con sus tests propuestos en `TESIS-CIUDAD` (§"Las hipótesis
  que estos datos generan"), síntesis en `resumen.md` y en el epílogo del HTML.
- ⬜ **Dar más protagonismo a la línea "tensión residencial"** (resto del punto
  de ChatGPT): las líneas (b) dos-transformaciones y (c) velocidad-vs-estado ya
  quedaron elevadas con los capítulos e hipótesis; queda (a) — un indicador de
  accesibilidad residencial más completo, que es trabajo de Code (familia de
  medidas ya existe en MET-1; ampliarla p.ej. con % de hogares que superarían
  el 30 % de esfuerzo).
- ⬜ **Mantener `resumen.md` y `TESIS-CIUDAD`** al día cuando entren datos nuevos.
- ⬜ **Mantener `metodologia.html` y `datos.html`** sincronizados con
  `NOTA-METODOLOGICA.md` y `SOURCES.md`/`FUENTES.md` cuando cambien (son
  resúmenes manuales, no generados).
- ⬜ **Nuevos ejes de relato** cuando haya datos: movilidad, coste de vida, empleo,
  comercio, vivienda pública (dependen de REC-5…REC-10, sección Code).
- ⬜ **Accesibilidad** de las visualizaciones (contraste, leyendas, lectura sin color).
- ⬜ **DOC-6 (opcional):** working paper metodológico (pipeline, supuestos, índice).
- ⬜ **Explorar granularidad calle/punto (no barrio) para REC-8**: el fichero
  `locales` del catastro foral (REC-8, ver sección Code) trae calle + portal
  por local — no agregable a barrio sin un callejero (bloqueado en Code), pero
  sí explotable *sin* agregar a barrio: densidad de locales, superficie media,
  antigüedad de la edificación (`FeFinObr`) por calle o por punto. Investigar
  si tiene sentido narrativo una visualización a esa escala (mapa de puntos o
  por eje viario en vez de coropleta) y qué insight aportaría (p. ej. ejes
  comerciales, antigüedad del parque construido) que la vista por barrio no
  muestre. REC-6 (movilidad) no aplica hoy: su fuente está dada de baja, sin
  datos de ningún grano disponibles.

---

## Pendiente — Code ⬜

### Nomenclatura y estructura
- ✅ **Renombrar el barrio a "Antiguo"** (nombre visible) en
  `datos/procesado/tablas/barrios.csv` (columna `name`),
  `web/src/data/barrios.geojson`, `datos/procesado/tablas/metrics_long.csv`,
  `output/historias.html` y docs activos (`GUION-OUTPUTS.md`, `TESIS-CIUDAD.md`).
  El `barrio_id`/clave de join sigue siendo `antigua` (no cambiado). `geometry.py`
  lleva la entrada en `DISPLAY_NAME_OVERRIDES` como fuente de verdad.
- ✅ **Mover los datos procesados a `datos/procesado/`** (parcial, decisión
  deliberada): `data/*.csv` → `datos/procesado/tablas/`, con `config.TABLES_DIR`
  y `analysis/*.py` actualizados. `web/src/data/*.json` **se queda donde está**:
  Vite los carga con `import.meta.glob` desde dentro de `web/src/`, así que
  sacarlos de ahí exige tocar `server.fs.allow` por una ganancia puramente
  organizativa; `config.WEB_DATA_DIR` no cambia. `analysis/output/` (gitignored,
  regenerable) tampoco se ha movido por bajo valor. CI en verde.
- ✅ **Consolidar `data-pipeline/curated/` en `datos/input/`** — `config.CURATED_DIR`
  apunta ahora a `datos/input/`; se elimina el duplicado en `data-pipeline/curated/`.

### Datos crudos (input)
- 🔷 **Poblar `datos/input/raw/`** ejecutando `datos/input/descargar_raw.sh` o
  `python -m donostia_pipeline.build` (necesita red). No se pudo hacer desde
  Cowork (web_fetch agota tiempo; curl prohibido por política). Ver
  `datos/input/FUENTES.md`. **AEMET desbloqueado (jul-2026):** `AEMET_API_KEY`
  configurada como variable de entorno de Code (Claude Code on the web no
  tiene almacén de secretos dedicado; ver aviso en `claude-code-on-the-web`
  docs). ⚠️ Ojo: se guardó con el nombre `AEMET_APY_KEY` (typo) en vez de
  `AEMET_API_KEY` — corregir el nombre de la variable en la config del
  entorno para no depender de un `export` manual en cada sesión. El resto de
  fuentes (Donostia Open Data, INE, EMA, Airbnb) sigue sin probar en esta
  sesión — solo se ha corrido `ensure_aemet`, no el pipeline completo.

### Datos nuevos / análisis (del backlog histórico)
- ✅ **REC-5 tasa de paro** — hecho (jul-2026): 3 indicadores ciudad
  `unemployment_rate(_men/_women)` desde Eustat PxWeb (tabla
  `PX_050403_cpra_tab19`, capital Donostia — no agregada con otros
  municipios —, auto-fetch por POST en `build.ensure_eustat_paro`), anual
  **2015–2025** (promedio anual): 12,0%→5,0% (hombres 12,9%→5,1%, mujeres
  11,0%→5,0%), con el repunte de 2020 (COVID) visible. Módulo
  `datasets/paro.py` + tests. Ciudad, no barrio ni por sectores — la
  "ventana barrio 2016-19" que el plan archivado marcaba como pista a
  verificar no aparece en el banco PxWeb de Eustat; sectores/LANBIDE no
  investigados.
- ⬜ **REC-6 movilidad** — investigado (jul-2026): el dataset `dbus_utilizacion`
  (viajeros DBus por línea/mes/hora) que enlaza Open Data Euskadi ya **no existe**
  en el catálogo CKAN de Donostia (403 + 0 resultados en su buscador de
  paquetes/recursos) — parece otra fuente dada de baja, como la de criminalidad.
  Sin URL viva confirmada, aparcado.
- ✅ **REC-7 tejido comercial (proxy CNAE)** — hecho (jul-2026): 3 indicadores
  ciudad `total_establishments`, `retail_establishments_share`,
  `hospitality_establishments_share` desde el Directorio de Actividades
  Económicas de Eustat (tabla `PX_200163_cdirae_est04b`, municipio Donostia,
  ~630 códigos CNAE-2009 sumados a comercio 47xx / hostelería 55xx+56xx en
  el pipeline, sin rollup de sección en la fuente), anual **2008–2025**:
  comercio al por menor 14,9%→12,6%, hostelería 6,0%→8,1%, locales totales
  22.862→18.037. **Proxy, no causal**: consistente con la sustitución
  residente→turista de la hipótesis, pero no la demuestra (erosión del
  comercio por e-commerce no descartada). No hay licencias por barrio (lo
  que pedía originalmente REC-7); ciudad únicamente. Módulo
  `datasets/tejido_comercial.py` + tests.
- ⬜ **REC-8 Catastro Foral de Gipuzkoa** — investigado (jul-2026): los CSV **sí**
  se pueden descargar (el host documentado `opepro08.sare.gipuzkoa.net` no es
  alcanzable; hay espejo funcional en
  `api.gipuzkoairekia.eus/dataset/recurso/<id>/descargar`), pero **ninguno de
  los dos ficheros trae coordenadas ni barrio**: `parcelas` solo trae una
  `Refer` catastral interna de 7 dígitos (haría falta geometría INSPIRE
  WFS/GML de parcelas + cruce de referencia, sin confirmar); `locales` trae
  calle + portal (geocodificable, pero sin callejero→barrio en el proyecto y
  con el mismo problema de calles que cruzan barrios que REC-6). **No es el
  quick-win que asumía `docs/archive/PLAN-RECOLECCION.md`** (lo marcaba ✅);
  aparcado hasta decidir si vale la pena la geocodificación por calle o el WFS.
- ✅ **REC-9 modelos lingüísticos (euskera)** — hecho (jul-2026): 3 indicadores
  ciudad `pct_language_model_a/b/d` (% alumnado por modelo) desde Eustat PxWeb
  (tabla `PX_040601_ceens_mun01`, municipio Donostia, auto-fetch por POST en
  `build.ensure_eustat_modelos`), serie completa **1983/1984–2024/2025**.
  Municipio, no barrio (mismo límite que anticipaba el plan archivado).
  Módulo `datasets/modelos_linguisticos.py` + tests; se renderiza solo con la
  `IndicatorsSection` genérica, sin cambios de frontend.
- ✅ **REC-10 Ibiltur Ocio (Basquetour)** — hecho (jul-2026): 3 indicadores
  ciudad `ibiltur_ocio_*` (gasto/persona, gasto/persona/día, impacto
  económico) desde la ficha de destino Donostia 2023 de Basquetour (PDF,
  curado como MICE — `datos/input/ibiltur_donostia.csv`). Solo turista de
  ocio que pernocta; **no** están los segmentos excursionista/MICE-negocios
  (solo existen a nivel Euskadi, no Donostia) ni una serie temporal (la ficha
  2022 es "Verano", ventana distinta a "Ocio" 2023 → no se mezclan para no
  fabricar una tendencia falsa). Módulo `datasets/ibiltur.py` + tests.
- ⬜ **REC-11 locales comerciales vacíos** (idea jul-2026): ¿cuántos/qué % de
  locales están vacíos (cierre de negocio, jubilación, alquiler
  inasequible…) y tendría sentido reconvertir parte a vivienda para aliviar
  la presión del mercado inmobiliario? Investigado sin éxito por ahora:
  - El fichero `locales` del catastro foral (REC-8) trae un campo `Om` con
    solo 5 valores (`EU` 65%, `MI` 16%, `EC` 15%, `MP` 6%, `ES` <1%) que
    *podría* clasificar el tipo/ocupación de la unidad, pero **no hay manual
    público que lo confirme** (el formato CAT nacional no aplica al catastro
    foral de Gipuzkoa) — no se construye una métrica sobre una suposición sin
    verificar. Contacto técnico: `hirilurra@gipuzkoa.eus`.
  - Las tablas "altas/bajas" de establecimientos de Eustat (CDIRAE, ver
    REC-7) solo bajan a nivel **comarca** (Donostialdea = Donostia + pueblos
    vecinos), no aíslan la ciudad — tampoco sirven como proxy de vacío.
  - Sin fuente pública verificable hoy. Pendiente: confirmar el campo `Om` o
    localizar un censo municipal de locales vacíos (algunos ayuntamientos lo
    publican vía su observatorio de comercio; no verificado para Donostia).
  - **Cowork**: si aparecen datos, el ángulo narrativo (reconversión
    comercial→vivienda como alivio a la tensión habitacional) encaja con la
    tesis de transformación urbana ya desarrollada.
- ⬜ **AN-6 refinamiento** — alquiler mensual/trimestral y 2ª señal turística
  independiente para triangular el lead/lag. Ver AN-16 (estacionariedad +
  control macro) y REC-12 (histórico VUT como 2ª señal).

### Análisis inferencial (feedback IAs jul-2026 — detalle y origen en `docs/intermedia/FEEDBACK-IAS-2026-07.md`)

Prioridad sugerida: **AN-9, AN-10 y AN-16 blindan lo ya publicado** (índice,
correlaciones, lead/lag) y van antes que las ampliaciones.

- ✅ **AN-9 sensibilidad del índice AN-8** — hecho (jul-2026):
  `analysis/index_sensitivity.py` (+ tests en `analysis/tests/`, ahora con CI).
  1000 permutaciones Dirichlet + variantes 60/40 y 40/60 + PCA contraste.
  **El ranking aguanta**: Loiola 1º en el 83 % y nunca peor que 3º (Egia
  mediana 2º, top-3 70 %); Erdialdea 1º en el 100 % en el modo turístico.
  PCA confirma la decisión de no usarlo: en el modo A los dos componentes
  están anticorrelacionados y la PC1 sale como contraste, no como índice.
  Documentado en `INDICE-TRANSFORMACION.md` §"Sensibilidad de pesos" y una
  línea en la ficha de historia #6.
- ✅ **AN-10 incertidumbre en correlaciones** — hecho (jul-2026):
  `bootstrap_ci_pearson` en `sprint_a.py` (percentil, 2.000 remuestreos,
  semilla fija) + tests; columnas `pearson_ci95_lo/hi` en
  `corr_robustness.csv`. El caso estrella confirma la intuición del feedback:
  alquiler↔renta r=0,72 con IC 0,24–0,96. Fichas actualizadas: tabla de
  `resumen.md`, MET-3 en `metodologia.html`, ficha VUT↔alquiler en
  `historias.html`.
- ✅ **AN-11 tipologías de barrio** — hecho (jul-2026):
  `analysis/barrio_typology.py` (+ tests; jerárquico average-linkage y
  silhouette en numpy puro). Resultado: la partición mejor sostenida es
  **k=3** (silhouette 0,455 vs 0,416 de k=4): periferia popular /
  Erdialdea+Gros / residencial acomodado — la división más profunda es
  renta/estudios, no turismo. Estructura moderada (~0,45): las tipologías
  siguen siendo perfiles descriptivos. Vecino más parecido: Egia↔Loiola
  (coherente con historia #6). Detalle en `ANALISIS-INFERENCIAL.md`.
- ⬜ **AN-12 descomponer la pérdida de población del centro** *(prioridad alta)*:
  saldo vegetativo vs migratorio + cruce con Δ% 25–39 (¿éxodo joven?). El mejor
  proxy de desplazamiento sin microdatos; responde la pregunta abierta #2.
- ✅ **AN-13 beta-convergencia** — hecho (jul-2026):
  `analysis/beta_convergence.py` (+ tests), IC bootstrap para β. Resultado:
  **compatible con brecha estable en los tres indicadores** (renta, alquiler,
  % universitarios: los IC95 de β cruzan el 0) → H3 reforzada por vía
  independiente del Gini. Documentado en `ANALISIS-INFERENCIAL.md` (nuevo
  cuaderno para AN-11…20), H3 en TESIS-CIUDAD, resumen y epílogo de historias.
- ⬜ **AN-14 estacionalidad turística por barrio**: ratio verano/invierno o Gini
  mensual sobre reseñas 2011–2025; ¿qué barrios dependen del turismo estival?
- ✅ **AN-15 estadística espacial** — hecho (jul-2026):
  `analysis/spatial_autocorrelation.py` (+ tests; contigüidad queen desde
  `barrios.geojson` con shapely, p por permutación). Moran I significativo en
  alquiler (0,58, p=0,003), % universitarios (0,52), % extranjeros, renta,
  VUT y Airbnb; **tensión no** (encaja: el ratio mezcla las dos geografías).
  LISA: este obrero = cluster bajo-bajo, centro = alto-alto. H2 reforzada
  (2º test). Exclaves (Zubieta/Landerbaso/Oarain) sin vecinos, fuera.
  Detalle en `ANALISIS-INFERENCIAL.md`.
- ✅ **AN-16 blindar el lead/lag AN-6** — hecho (jul-2026), **y la señal no
  sobrevive**: `analysis/lead_lag_robustness.py` (+ tests). (1) DF/KPSS en
  numpy puro sobre el panel en diferencias: KPSS no rechaza estacionariedad en
  27/28 series, DF sin potencia con T≈8 (diagnóstico honesto). (2) Control
  macro por **efectos fijos de año** (absorbe IPC/tipos/COVID sin series
  externas): r(+1) cae de 0,274 a **0,104**. (3) Test de permutación (5.000):
  **p=0,30**. Conclusión: el 0,27 era en su mayor parte shock común de ciudad;
  el indicio direccional se retira de los relatos (historias #5 y epílogo,
  resumen, metodologia.html MET-3, `LeadLagSection` de la app, H1 en
  TESIS-CIUDAD debilitada). Matiz documentado en ANALISIS-LEADLAG.md: el FE de
  año no puede ver un efecto uniforme en toda la ciudad → REC-12 sigue siendo
  la vía para reabrir la pregunta.
- ✅ **AN-17 red de correlaciones** — hecho (jul-2026):
  `analysis/correlation_network.py` (+ tests; doble umbral Pearson+Spearman
  ≥0,5, n≥10). 12 aristas robustas. Respuesta: no es "la renta" — es el
  **triángulo renta–universitarios–alquiler** como núcleo denso; el turismo
  (VUT↔Airbnb) es un módulo aparte conectado vía alquiler; el ruido,
  periférico (refuerza MET-5). Detalle en `ANALISIS-INFERENCIAL.md`.
- ⬜ **AN-18 trayectorias de barrio**: connected scatter 2000→2025 (p.ej.
  envejecimiento × % universitarios); la lectura "trayectoria" de MET-8.
- ✅ **AN-19 regresión múltiple exploratoria** — hecho (jul-2026):
  `analysis/rent_drivers.py` (+ tests). Respuesta: **Airbnb no añade**
  (ΔR²=0,013, IC del coeficiente cruza 0); solo % universitarios sostiene IC
  fuera de 0 (+0,35 a +3,20 en z). Colinealidad renta↔universitarios (0,75)
  → coeficientes individuales inestables, y se dice. Coherente con AN-16 y
  con "dos geografías". Detalle en `ANALISIS-INFERENCIAL.md`.
- ✅ **AN-20 efecto COVID en trayectorias** — hecho (jul-2026):
  `analysis/covid_break.py` (+ tests). Resultado: **aceleró, no interrumpió**
  — pendiente post (≥2021) vs pre (≤2019): Airbnb ciudad ×1,9, alquiler ×2,4,
  hotel rebota y supera 2019 en 2022. El mapa por barrio se mantiene
  (Spearman pre/post 0,67) con difusión hacia barrios antes poco turísticos
  (Ibaeta ×7,5, Mirakruz ×3,8). Detalle en `ANALISIS-INFERENCIAL.md`.

### Datos nuevos (feedback IAs jul-2026)

- ⬜ **REC-12 histórico de licencias VUT** (Gob. Vasco, fecha de alta): curva de
  oferta legal independiente del sesgo de adopción; 2ª señal para el lead/lag.
- ⬜ **REC-13 anuncios activos Inside Airbnb** (serie de snapshots): contrastar
  con reseñas; si divergen, cuantificar el sesgo de adopción (MET-7).
- ⬜ **REC-14 isla de calor superficial** (Landsat/Copernicus): temperatura por
  barrio; cruza con "la presión recae en el este" y da dimensión espacial al clima.
- ⬜ **REC-15 vivienda protegida / VPO** (Observatorio Vasco de Vivienda): ¿la
  VPO amortigua la tensión de alquiler?
- ⬜ **REC-16 tipología comercial vía OSM** (histórico): ¿comercio de barrio →
  servicios turísticos? Complementa REC-7 (que solo llega a ciudad).
- ⬜ **REC-17 matrices origen-destino Eustat** (commuting trabajo/estudios):
  reactiva el eje movilidad tras la baja de DBus (REC-6).
- ⬜ **REC-18 equipamientos ampliados** (salud, bibliotecas, zonas verdes; Open
  Data): índice de accesibilidad por barrio × renta/tensión.
- ⬜ **REC-19 percepción ciudadana** (encuestas municipales de satisfacción):
  la capa subjetiva que falta.
- ⬜ **REC-20 cajón de ideas** (menor prioridad): licencias de obra y
  rehabilitación, matrícula escolar por centro, vegetación/arbolado satelital.

### Visualización (si se llevan a la web)
- ✅ **VIZ-8** small multiples por año + "play" animado — hecho (jul-2026):
  botón ▶/⏸ junto al `TimeSlider` que recorre automáticamente los periodos
  (900 ms/paso, para al cambiar de métrica); nueva sección `SmallMultiples`
  con un mini-mapa SVG por año (misma escala de color que el mapa principal),
  clicable para saltar directamente a ese periodo. Renderizado en SVG plano
  (`lib/miniMap.ts`, proyección equirectangular con corrección coseno-latitud,
  testeada), no maplibre — métricas con 20+ años agotarían el límite de
  contextos WebGL concurrentes del navegador si cada mini-mapa fuera una
  instancia maplibre real.
- ⬜ **VIZ-9** scrollytelling (solo tras cerrar contenido).
- ✅ **VIZ-10** "ciudad turística vs. vivida" en la app — hecho (jul-2026):
  nueva sección `TwoCitiesSection` con **dos mapas independientes** lado a
  lado (cada uno con su propio selector de métrica y escala de color, no
  fusionados como la mappa bivariata VIZ-3). Izquierda: turismo (`airbnb_density`
  por defecto, + `vut_density`/`vut_count`). Derecha: ciudad vivida
  (`schools_per_1000` por defecto, + `population`/`ageing_index`/
  `pct_youth_adults`/`noise_night_pct55`). Reutiliza `ChoroplethMap`/`Legend`/
  `MetricPicker` sin lib nueva; nota de advertencia sobre ruido↔tráfico
  (VIZ-5) enlazada. Colocada antes de "Due turismi"/lead-lag, siguiendo el
  orden narrativo de la historia #5 (`GUION-OUTPUTS.md`).
- ✅ **VIZ-5 (resto)** overlay ruido × densidad turística — hecho (jul-2026,
  análisis): `sprint_a.py` añade `noise_night_pct55 ~ vut_density` (r=0,29,
  **0,05 sin outliers**) y `~ airbnb_density` (r=−0,05, **−0,44 sin
  outliers**) — ambas colapsan/se invierten al quitar el centro turístico,
  confirmando cuantitativamente que el ruido es de tráfico, no de turismo
  (ver `NOTA-METODOLOGICA.md` MET-5 y `intermedia/ANALISIS-SPRINT-A.md`). El
  overlay en sí **ya existe** en la app (`BivariateSection`, ejes X/Y
  seleccionables libremente); no se promueve como historia/mapa dedicado
  porque los datos no sostienen esa narrativa.

---

## Descartado / no hacer (decisiones firmes)

- **Criminalidad por barrio** — fuente eliminada + escala sub-municipal protegida.
- **Precios de venta €/m² por barrio** — solo vía catastro foral (REC-8); nunca
  scraping de Indomio/Idealista (ToS).
- **"Índice de gentrificación" como caja negra** — se usa "Transformación Urbana",
  multi-definición y con componentes a la vista.
- **PCA como método principal de pesos del AN-8** — frágil con N=13; solo como
  contraste dentro de AN-9 (feedback jul-2026).
- **"Índice de presión compuesta" adicional** (DeepSeek) — sería otra caja negra;
  los componentes del AN-8 ya están a la vista.

---

## Convenciones vigentes

- **"Transformación", nunca "gentrificación"** (falta rotación de población).
- **Correlación ≠ causalidad**; incluso el lead/lag es exploratorio.
- **% de extranjeros no es proxy** de transformación; el **ruido es de tráfico**,
  no de turismo.
- **Falacia ecológica** (MET-6): correlaciones entre barrios, nunca entre personas.
- **Proxy Airbnb con sesgo de adopción** (MET-7); el **envejecimiento del centro
  es anterior al turismo** — no se sugiere causalidad.
- **Estado ≠ cambio ≠ trayectoria** (MET-8): cada afirmación dice de cuál habla.
- Toda métrica lleva su **ficha de confianza** (observado / derivado / proxy).
- **No versionar crudos grandes**; sí el input curado + `FUENTES.md` + script de descarga.
