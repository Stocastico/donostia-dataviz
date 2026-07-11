# BACKLOG — Donostia Dataviz

> Backlog operativo del proyecto, separado por **quién** ejecuta:
>
> - **Cowork** — documentación, análisis narrativo, relatos y *outputs* (no toca código).
> - **Code** — pipeline de datos, frontend, estructura de datos y tests (Claude Code / local).
>
> Reemplaza a `docs/archive/GAP-ANALYSIS.md` (el backlog técnico detallado e
> histórico queda archivado ahí). Convención: ✅ hecho · ⬜ pendiente · 🔷 en curso.
>
> **Regla de parada (jul-2026):** el proyecto cierra tras *una última tanda
> dirigida* de datos (REC-15 VPO + REC-18 accesibilidad) y la publicación. Qué
> falta para dar por «hecho» y qué queda congelado: **`docs/PLAN-CIERRE.md`**.
> Criterio: un dato entra solo si prueba/matiza/refuta H1–H4, no porque exista.

---

## Estado en una línea

Pipeline + web + tests estables. **7 historias + sección de cierre** publicadas
en `output/historias.html`; análisis AN-1…AN-8 y correcciones MET-1…MET-8 hechos.
**Revisión externa por 3 IAs consolidada** (jul-2026,
`docs/intermedia/FEEDBACK-IAS-2026-07.md`) → alimentó AN-9…AN-20 y REC-12…REC-20.
**Tanda inferencial hecha (jul-2026): AN-9, 10, 11, 13, 15, 16, 17, 19, 20**
(`docs/intermedia/ANALISIS-INFERENCIAL.md` + docs propios; hallazgo mayor: el
lead/lag AN-6 **no sobrevive** al blindaje AN-16 y se retiró de los relatos).
**AN-12, AN-14 y AN-18 hechos (jul-2026)** — con esto la tanda AN-9…AN-20
del feedback queda **completa**. Hallazgos: la pérdida del centro es
vegetativa y el éxodo joven es de Gros (AN-12); la periferia turística vive
del verano y el centro todo el año (AN-14); la universitarización es una
marea común y Egia dibuja una V de rejuvenecimiento revertido (AN-18).
**Integración narrativa hecha (jul-2026, Cowork):** AN-12/14/18/20 en
`resumen.md` + `historias.html` (#3, #5, #6, epílogo), connected scatter
estático de AN-18 en la historia #6, y huérfano del lead/lag corregido en el
takeaway de #5. **REC de datos nuevos hechos (jul-2026, Code): REC-12
(licencias REATE, 3 indicadores), REC-17 (movilidad Eustat + empleo
localizado, 4 indicadores — H4 completada), REC-13 (snapshots Airbnb:
oferta +2 % vs reseñas +20 %, MET-7 cuantificado ×1,18) y REC-14 (isla de
calor Landsat: Gros +4,8 °C, el mapa térmico coincide con el este denso).**
Queda su integración narrativa (Cowork).

---

## Hecho ✅ (resumen)

- **Datos y pipeline:** 11 métricas coropléticas por barrio + velocidad de cambio
  + perfiles + estructura de edad + ruido nocturno + **Airbnb** (densidad y serie)
  + **Índice de Transformación** (AN-8); 5 series ciudad; 6 indicadores anuales.
  Join espacial, export CSV long, fichas de confianza. Tests pipeline + frontend.
- **Análisis:** correlaciones robustas (Pearson/Spearman/leave-one-out), velocidad,
  perfiles, matriz nivel×variación (AN-4), Gini territorial (AN-5), lead/lag AN-6
  exploratorio, Índice de Transformación AN-8.
- **Relatos:** las **7 historias** en `output/historias.html` (cap. 4 «Quién
  trabaja Donostia» añadido jul-2026 con REC-21; turística y transformación
  desde jul-2026) + apéndice de contexto y epílogo.
- **Documentos:** `TESIS-CIUDAD`, `GUION-OUTPUTS`, `NOTA-METODOLOGICA`, `SOURCES`,
  `output/resumen.md` (síntesis para revisión externa).
- **Auditoría de parcialidad de fuentes (2026-07-05, petición del usuario):**
  revisadas las ~20 fuentes de las 7 historias con la pregunta «¿registro
  completo o ventana parcial?». Resultado: además del caso VPO/Etxebide (ya
  recalibrado), se declararon 4 parcialidades que faltaban — EPA por
  nacionalidad = encuesta con submuestras pequeñas (cap. 4), Inside Airbnb =
  una sola plataforma, INE EOH = solo hoteles, equipamientos = registro
  municipal — en supuestos de métrica + relato + `datos.html`. Doctrina
  «**Registro ≠ universo**» fijada en MET-5 y en Limitaciones del resumen.
  Detalle por fuente: `session-handoff-2026-07-05.md` (addendum 2).
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

- ✅ **Integración narrativa AN-12/14/18/20** — hecha (jul-2026):
  `resumen.md` (§2 scripts, §3 señales nuevas, H4 descompuesta, §4 historias,
  pregunta abierta #2 respondida) y `historias.html` (#3 AN-12 + takeaway y
  ficha de confianza; #5 AN-20 y AN-14 + takeaway sin el huérfano del
  lead/lag; #6 AN-18 con connected scatter estático + takeaway; epílogo e
  hipótesis 4). De paso: la limitación "sensibilidad AN-9 pendiente" estaba
  rancia en `resumen.md` §6 y `metodologia.html` (AN-9 se hizo) — corregida.
  Revisión en navegador pendiente de validación del usuario (sin Chrome
  conectado en la sesión); estructura HTML y SVG validados por parser.
- ✅ **Revisar el render de los HTML de `output/`** — hecho (jul-2026): el usuario
  validó en navegador `historias.html` (con capítulos y epílogo), `metodologia.html`
  y `datos.html`. La iteración de contenido de #5/#6 quedó cubierta por la ronda
  de feedback de las 3 IAs.
- ✅ **Auditoría de enlaces internos** tras mover docs — hecha (jul-2026): los docs
  activos apuntan a `intermedia/`, `archive/` o `BACKLOG.md`; README y `resumen.md`
  actualizados. Los docs de `intermedia/`/`archive/` se dejan congelados.
- ✅ **Reestructurar las historias como capítulos** — hecho (jul-2026): arco
  estado → cambio → personas → telón de fondo → dos ciudades → síntesis →
  epílogo; eyebrows "Capítulo N · etapa", transiciones `nextcap` entre
  capítulos, hero reescrito. *(Ampliado a 7 capítulos jul-2026 con «Quién trabaja
  Donostia»; renumerados clima→5, turística→6, síntesis→7 en el HTML — los IDs de
  sección `#s4…#s6` se mantienen como anclas.)*
- ✅ **Encuadrar el proyecto como generador de hipótesis** — hecho (jul-2026):
  H1–H4 explícitas con sus tests propuestos en `TESIS-CIUDAD` (§"Las hipótesis
  que estos datos generan"), síntesis en `resumen.md` y en el epílogo del HTML.
- 🔷 **Dar más protagonismo a la línea "tensión residencial"** (resto del punto
  de ChatGPT): las líneas (b) dos-transformaciones y (c) velocidad-vs-estado ya
  quedaron elevadas con los capítulos e hipótesis. *Reforzada narrativamente
  (jul-2026, Cowork):* la síntesis (cap. 7) y su takeaway hacen explícita la
  **convergencia de presiones sobre el este obrero** &mdash;tensión alquiler/renta +
  migración económica (cap. 4) + isla de calor (cap. 5) sobre la misma geografía&mdash;,
  con el caveat de la posible «ilusión de equidad» del Gini. **Alivio ahora a la
  vista, con cobertura acotada (jul-2026, recalibrado el 05):** el contrapeso
  público se cuenta con el dato de ciudad (alquiler protegido = 3.151 viviendas,
  ¼ del alquiler ocupado, memoria de zona tensionada 2024) + la ventana Etxebide
  de REC-15 (≤~⅓ de ese parque, concentrada en el este obrero); su mapa completo
  por barrio no es público. **Cerrado como laguna declarada (jul-2026,
  decisión del usuario):** el indicador «% de hogares que superarían el 30 % de
  esfuerzo» **no se implementa** — exigiría inventar la distribución de renta
  *dentro* del barrio (solo hay media por barrio), justo la inferencia intra-grupo
  que el proyecto rechaza (MET-6, falacia ecológica; mismo criterio que REC-8/11).
  `housing_tension` ya da el esfuerzo teórico medio; el % de hogares necesitaría
  microdatos de hogar que no son públicos a grano barrio.
- 🔷 **Mantener `resumen.md` y `TESIS-CIUDAD`** al día cuando entren datos nuevos.
  *Al día (jul-2026, Code): última tanda (REC-15 VPO, REC-18 salud) y vista calle
  a calle incorporadas a §1/§3/§4 de `resumen.md` y a eslabones/H3/anexo de
  `TESIS-CIUDAD.md`. Con la puerta de datos congelada (PLAN-CIERRE), esta tarea
  queda en mantenimiento pasivo.*
- 🔷 **Mantener `metodologia.html` y `datos.html`** sincronizados con
  `NOTA-METODOLOGICA.md` y `SOURCES.md`/`FUENTES.md` cuando cambien (son
  resúmenes manuales, no generados). *Al día (2026-07-11, Code): recuento de
  confianza refrescado a **17 obs./19 der./5 proxy (41 métricas)** en
  `metodologia.html` y `NOTA-METODOLOGICA.md` (las altas de REC-22 `income_labor`
  y REC-25 `sale_price_eur_m2` habían dejado rancio el 16/18/4); `datos.html` y
  `resumen.md` §1 completados con las filas que faltaban (`population`,
  `income_labor`, `income_gender_gap`, `airbnb_activity`) y el recuento de
  indicadores actualizado a **33**.*
- ✅ **Integración narrativa de REC-15 (VPO) y REC-18 (accesibilidad salud)** —
  hecha (jul-2026, **desde Code**; resultó perfectamente hacible sin Cowork): cap. 7
  gana la figura del contrapeso público (mapa Etxebide **junto al de tensión
  MET-1**) + frase en el takeaway + matiz en la hipótesis 3 del epílogo; cap. 6
  gana la capa «Servicios de salud» en el mapa de la ciudad vivida (13 urbanos:
  Loiola/Egia en cabeza; el artefacto de Miramón-Zorroaga, documentado y fuera
  del mapa de 13). Digest en `resumen.md`/`TESIS-CIUDAD.md` (incl. anexo 🏥 y
  matiz de H3). Verificado en navegador (0 errores JS). *Reescrita el 05 tras
  cuantificar la cobertura del registro Etxebide (ver REC-15): la figura pasa a
  «una ventana parcial» y las lecturas sobre los ceros se retiran.*
- ✅ **Ficha de país en el relato (opcional)** — hecha (jul-2026, Code): la
  historia #4 remite a la vista «Chi vive nel barrio · origini» del panel
  (puente app↔narrativa), mismo patrón que la vista calle a calle.
- ⬜ **Nuevos ejes de relato** cuando haya datos: movilidad, coste de vida, empleo,
  comercio, vivienda pública (dependen de REC-5…REC-10, sección Code).
- ✅ **Integración narrativa de REC-12/13/14/17** — hecha (jul-2026, Cowork):
  la purga VUT de 2025 y el "MET-7 con número" (×1,18) + altas REATE 300→18
  en la historia turística y su ficha de proxy; el ratio de concentración de
  empleo **1,20** (REC-17) cierra la mitad de H4 en el epílogo; la isla de calor
  (REC-14, Gros +4,8 °C, barras divergentes por barrio) da la dimensión espacial
  a la historia del clima. En `historias.html`; digest en `resumen.md`/`TESIS-CIUDAD.md`.
  Verificado con jsdom (0 errores JS) y SVG rasterizados. Commit `3a2d78b`.
- ✅ **Pasada de coherencia de la historia turística** (cap. 6) — hecha (jul-2026,
  Cowork): releída de corrido tras insertar REC-13; el «×6» dejaba de cuadrar con la
  corrección del proxy, así que el keynum de cierre y el takeaway ahora aclaran que es
  actividad/interés, no oferta (parque real +2 %), y el bloque REC-13 se partió en dos
  párrafos más legibles. Encadena densidad → dos turismos → COVID → proxy REC-13 →
  estacionalidad → AN-14 → lead/lag → escuelas; largo pero cada pieza se sostiene.
- ✅ **Accesibilidad** de las visualizaciones (contraste, leyendas, lectura sin
  color) — **completa (jul-2026)**. *Primera pasada (Cowork):* correlación
  origen↔renta a azul/coral con cifras redundantes, `role="img"`+`aria-label` en
  los SVG del cap. 4 y la isla de calor. *Auditoría final (Code, jul-2026):*
  contraste **medido** en todo el sitio narrativo — `--muted` subido de #6b7a90
  (4,25:1, fallaba AA en texto pequeño) a **#5f6e84 (5,19:1)** en los tres HTML y
  en todos los textos SVG inline; las etiquetas del connected scatter pasan a
  variantes oscuras AA (Antiguo estaba en **2,56:1** → #9c5f0e 5,18:1; Egia →
  #c03a4c 5,32:1; Miramón → #1f7a54 5,29:1; las líneas conservan la paleta), con
  `trajectories.py --svg` actualizado (`LABEL_COLORS`) para que el generador siga
  reproduciendo el SVG publicado. Resto de colores de texto verificados ≥4,5:1;
  las trazas grises del scatter quedan como contexto deliberadamente atenuado
  (la lectura vive en las 4 destacadas y en el texto).
- ⬜ **DOC-6 (opcional):** working paper metodológico (pipeline, supuestos, índice).
- ✅ **Granularidad calle/punto (no barrio)** — hecho (jul-2026, Code): primera
  vista **sub-barrio** del proyecto. El censo VUT (`vtur_censo.csv`) trae la
  dirección (`helbidea`) y el **callejero municipal** de Donostia Open Data
  (*Nombres de calle*, SHP de puntos-etiqueta con código estable `KodKalea` +
  nombres ES/EU) da geometría por calle — el "callejero que faltaba" que
  bloqueaba REC-8/REC-12 **ya está cableado**. Un matcher de prefijo más largo
  (que no parte los nombres con número dentro, p. ej. *Abuztuaren 31 Kalea* /
  *31 de Agosto*) empareja dirección→calle al **100 % de las 1.489 filas del
  censo**. Salida: `web/src/data/street_vut.json` + `datos/procesado/tablas/`
  `calles_vut.csv` (301 calles: unidades/plazas VUT-HUT por calle) y una sección
  nueva en la app — *"Viviendas turísticas, calle a calle"* — con **mapa de
  símbolos proporcionales** (un círculo por calle, tamaño+color por unidades o
  plazas), leyenda y **tabla-espejo accesible**. Enseña lo que la media de
  barrio borra: los ejes saturados del centro (Zabaleta, Urbieta, Easo, San
  Marcial) frente a un barrio "medio". Módulo `datasets/calles_vut.py` + tests;
  `lib/streets.ts` + tests. Verificado en navegador (Playwright).
  - *Pendiente / no hecho:* la parte **catastral** de la idea original
    (antigüedad de la edificación `FeFinObr`, densidad de locales/superficie
    media por calle) sigue aparcada — el catastro foral es **inalcanzable desde
    este entorno** (`opendata.gipuzkoa.eus` 502; mirror sin API limpia). Con el
    callejero ya cableado sería abordable el día que el host se desbloquee.
  - REC-6 (movilidad) no aplica hoy: su fuente está dada de baja, sin datos de
    ningún grano disponibles.

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

### Internacionalización del app (idioma)
- ✅ **App React traducido de italiano a español** (jul-2026, decisión del usuario).
  Toda la interfaz del dashboard pasa a español: (1) **capa de datos** — `label`/
  `unit`/`source`/`assumptions`/`categories` de cada `Metric` (en `datasets/*.py`,
  `provenance.py`, `change_velocity.py`, `affordability_index.py`) + los ~40
  `metric_*.json` / `metrics.json` / `indicators.json` / `series*.json` regenerados
  y en sync con el código (verificado provenance↔JSON = 0 mismatches); (2) **UI** —
  los ~25 componentes `web/src/components/*`, `views/Dashboard.tsx`,
  `THEME_LABELS` del `MetricPicker`, meses (`lib/series.ts`), locale de formato y de
  ordenación (`it-IT`/`it`→`es-ES`/`es`), `index.html` `lang="es"`. Tests del
  pipeline (213) y web (70) actualizados y en verde; build y navegador verificados.
  No cambia estructura de datos ni `barrio_id`. Los `docstrings`/comentarios de
  código (dev-facing) se dejan como están.

### Datos crudos (input)
- 🔷 **Poblar `datos/input/raw/`** ejecutando `datos/input/descargar_raw.sh` o
  `python -m donostia_pipeline.build` (necesita red). No se pudo hacer desde
  Cowork (web_fetch agota tiempo; curl prohibido por política). Ver
  `datos/input/FUENTES.md`. **AEMET desbloqueado (jul-2026):** `AEMET_API_KEY`
  configurada como variable de entorno de Code (Claude Code on the web no
  tiene almacén de secretos dedicado; ver aviso en `claude-code-on-the-web`
  docs). ✅ *El typo del nombre (`AEMET_APY_KEY`) ya está corregido en la config
  del entorno: la sesión del 2026-07-05 ve `AEMET_API_KEY` con el nombre bueno,
  sin `export` manual.* El resto de
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
- 🚫 **REC-8 Catastro Foral de Gipuzkoa — NO SE HACE** (jul-2026, decisión del
  usuario: no aparece una fuente con barrio/coordenadas utilizable; el proxy de
  venta de idealista, REC-25, cubre ya el precio de compra por barrio).
  Investigado: los CSV **sí**
  se pueden descargar (el host documentado `opepro08.sare.gipuzkoa.net` no es
  alcanzable; hay espejo funcional en
  `api.gipuzkoairekia.eus/dataset/recurso/<id>/descargar`), pero **ninguno de
  los dos ficheros trae coordenadas ni barrio**: `parcelas` solo trae una
  `Refer` catastral interna de 7 dígitos (haría falta geometría INSPIRE
  WFS/GML de parcelas + cruce de referencia, sin confirmar); `locales` trae
  calle + portal (geocodificable, pero sin callejero→barrio en el proyecto y
  con el mismo problema de calles que cruzan barrios que REC-6). **No es el
  quick-win que asumía `docs/archive/PLAN-RECOLECCION.md`** (lo marcaba ✅);
  aparcado y ahora **descartado**: la geocodificación por calle + WFS INSPIRE no
  compensa cuando REC-25 ya da precio de venta por barrio.
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
- ✅ **AN-6 refinamiento** — hecho (jul-2026): `analysis/lead_lag_reate.py`
  (+ `tests/test_lead_lag_reate.py`, 14 tests). Cruza **a grano ciudad** el flujo
  anual de licencias REATE (`vut_licenses_new`, 2ª señal *independiente* de las
  reseñas — cierra el punto ciego del FE de año de AN-16) con la variación del
  alquiler medio, con detrend lineal + test de permutación. **Resultado: la 2ª
  señal NO reabre H1** — la asociación cruda es negativa (cruce de tendencias:
  licencias que caen vs. alquiler que acelera), el signo se vuelve inestable al
  detrend y ningún desfase es significativo con T≈8. Refuerza el veredicto de
  AN-16. Detalle en `ANALISIS-LEADLAG.md` §"Refinamiento AN-6". **La palanca que
  queda ya no es el proxy sino la resolución anual**: grano trimestral del
  alquiler/licencias o una serie más larga (sin fuente pública hoy).
  ✅ *Veredicto llevado a la narrativa (2026-07-11, Code):* `historias.html`
  (sección lead/lag del cap. 6 + epílogo), `resumen.md` (§2/§3/H1/pregunta
  abierta #1) y `TESIS-CIUDAD.md` (H1) ya no dicen «a la espera de una segunda
  señal» — dicen que la señal REATE se probó y no reabre H1.

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
- ✅ **AN-12 descomponer la pérdida de población del centro** — hecho (jul-2026):
  `analysis/population_decomposition.py` (+ tests). No existe dataset abierto
  de saldo vegetativo/migratorio por barrio (agotados CKAN Donostia, Eustat —
  distrito solo 1991–2003 — y datos.gob.es), así que se estimó por **residuo
  por cohortes** (pirámide del padrón + ₅qx de Gipuzkoa, INE tabla 67235,
  nueva fuente en `FUENTES.md`/`descargar_raw.sh`; requiere crudos).
  Resultado: **la pérdida del centro es vegetativa, no de expulsión** —
  Erdialdea atrae migración neta (+2.162 en 2000–2025) y pierde población por
  déficit nacimientos−defunciones (−3.435); **Gros** es el único barrio con
  ambos saldos negativos y éxodo 25–39 en las cinco ventanas (−4 a −9 % por
  quinquenio). Responde la pregunta abierta #2 y matiza H4 (TESIS-CIUDAD
  actualizada). Detalle en `ANALISIS-INFERENCIAL.md` §AN-12. ✅ *Integrado
  (jul-2026, Cowork) en `resumen.md` (§3, H4, historias, pregunta abierta #2
  respondida) y en `historias.html` (#3 + takeaway, epílogo, hipótesis 4).*
- ✅ **AN-13 beta-convergencia** — hecho (jul-2026):
  `analysis/beta_convergence.py` (+ tests), IC bootstrap para β. Resultado:
  **compatible con brecha estable en los tres indicadores** (renta, alquiler,
  % universitarios: los IC95 de β cruzan el 0) → H3 reforzada por vía
  independiente del Gini. Documentado en `ANALISIS-INFERENCIAL.md` (nuevo
  cuaderno para AN-11…20), H3 en TESIS-CIUDAD, resumen y epílogo de historias.
- ✅ **AN-14 estacionalidad turística por barrio** — hecho (jul-2026):
  `analysis/tourism_seasonality.py` (+ tests) sobre 116k reseñas de Donostia
  (Inside Airbnb 2011–2024, listing→barrio por punto-en-polígono). Resultado
  **al revés de la intuición**: dependen del verano los barrios periféricos
  (Intxaurrondo/Igeldo ratio V/I ≈ 4,8; Antigua 4,3) y el **Erdialdea es el
  menos estacional** (2,1; Gini 0,19) — su turismo es de todo el año y la
  periferia funciona como desbordamiento estival. Validado contra las
  pernoctaciones INE de ciudad (ratio 2,0 vs 2,5 del proxy). Detalle en
  `ANALISIS-INFERENCIAL.md` §AN-14. ✅ *Integrado (jul-2026, Cowork) en la
  historia #5 (párrafo tras el heatmap de estacionalidad + takeaway: presión
  crónica del centro, periferia = desbordamiento) y en `resumen.md`.*
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
- ✅ **AN-18 trayectorias de barrio** — hecho (jul-2026), alcance script+CSV:
  `analysis/trajectories.py` (+ tests) sobre el plano envejecimiento ×
  % universitarios (las 5 métricas 2000–2025 van en `trajectories_long.csv`
  para que la viz elija ejes). Resultado: la **universitarización es una
  marea** (17/17 barrios suben); el relato está en el eje de edad — Antigua
  (+197) envejece más que nadie, **Miramón-Zorroaga (−218) y Loiola (−20,
  todo desde 2015) rejuvenecen**, y **Egia dibuja una V** (rejuveneció
  2000→2010 y re-envejeció; tortuosidad 4,3). La dispersión de la nube es
  plana (brecha estable también en trayectoria, coherente con H3/AN-13).
  Detalle en `ANALISIS-INFERENCIAL.md` §AN-18. ✅ *Decidido con el usuario
  (jul-2026): **gráfico estático** — SVG inline en la historia #6 generado
  desde `trajectories_long.csv` (suavizado 3 años; Egia/Antiguo/Loiola/Miramón
  destacados; Zubieta y Landerbaso fuera por ruido). La sección web
  interactiva queda descartada por ahora.* El generador del SVG, que vivía
  en un script ad hoc efímero, está portado (jul-2026) como
  `trajectories.py --svg` (reproduce el SVG publicado byte a byte).
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
  ✅ *Integrado (jul-2026, Cowork) en la historia #5 (párrafo "cráter, no
  cambio de régimen" tras el gráfico de dos turismos) y en `resumen.md`.*

### Datos nuevos (feedback IAs jul-2026)

- ✅ **REC-12 histórico de licencias VUT** — hecho (jul-2026): 3 indicadores
  ciudad `vut_licenses_new/cumulative` + `vut_plazas_cumulative` (2016–2025)
  desde el registro REATE de Open Data Euskadi (viviendas + habitaciones,
  fecha de alta `FechainscripcionREATE`). ⚠️ Snapshot vivo: las bajas no se
  publican → curvas de licencias *supervivientes* (suelo de la oferta legal);
  solo ciudad (dirección postal sin barrio ni coordenadas, mismo límite que
  REC-8). Señal: las altas caen de 300/año (2017) a 18 (2025). Módulo
  `datasets/reate_licencias.py` + tests. **Sigue pendiente el uso analítico**
  (reabrir H1: lead/lag licencias→alquiler con la curva REATE, ver AN-6).
- ✅ **REC-13 anuncios activos Inside Airbnb** — hecho (jul-2026):
  `analysis/airbnb_snapshots.py` (+ tests) sobre los 8 snapshots trimestrales
  accesibles (2023-12-29 → 2025-09-29; los 8 anteriores hasta 2021-12-30
  dan 403, solo vía data request — fechas listadas en el script). **MET-7 con
  número**: oferta activa +2,0 % vs reseñas-12m +20,2 % (el proxy exagera
  ×1,18 en la ventana); % con licencia declarada 58,5→84,5 % con caída de
  activos −10 % en 2025 (huella de purga); reparto espacial estable
  (confirma AN-20 con oferta). Detalle en `ANALISIS-INFERENCIAL.md` §REC-13.
- ✅ **REC-14 isla de calor superficial** — hecho (jul-2026):
  `analysis/heat_island.py` (+ tests; rasterio/pyproj solo para ese script)
  con 45 escenas de verano Landsat 8/9 C2 L2 (2015–2025, máscara qa_pixel)
  vía el STAC de Planetary Computer (anónimo; USGS/Copernicus piden cuenta).
  Anomalía LST vs media de ciudad: **Gros +4,8 °C, Amara Berri +4,3, Egia
  +4,1** — el mapa térmico coincide con el este denso de "la presión recae
  en el este"; anillo verde −3…−5 °C. La historia #4 gana dimensión espacial;
  `lst_anomaly` es candidata a coropleta. Detalle en
  `ANALISIS-INFERENCIAL.md` §REC-14.
- ✅ **REC-15 vivienda protegida / VPO** — hecho (jul-2026), **recalibrado
  (2026-07-05, petición del usuario)**: métrica coroplética
  `vpo_dwellings_per_1000` (proxy, snapshot) desde las **promociones de Etxebide**
  (Open Data Euskadi): coords UTM + nº de viviendas, geocodificadas punto→barrio
  y normalizadas por 1000 hab. Módulo `datasets/vpo_etxebide.py` + 4 tests.
  Hallazgo (lo afirmable): las promociones del registro (1.120 viviendas, 13
  promociones) se concentran en el este obrero/periferia interior (Loiola 22,3‰,
  Amara Berri 18,7, Intxaurrondo 16,3, Ibaeta 15,5).
  ⚠️ **Cobertura cuantificada (2026-07-05):** el registro es una **ventana
  parcial** — la memoria de la **zona tensionada (2024)** cifra el alquiler
  protegido + dotacionales de la ciudad en **3.151 viviendas (¼ del alquiler
  ocupado)**: Etxegintza 2.087 («repartidas por la mayor parte de los barrios»),
  GV/Alokabide 554, Benta Berri 510. Las promociones Etxebide son ≤~⅓ de solo
  ese parque de alquiler → **los «0» por barrio no son interpretables como
  ausencia de VPO** y la lectura «cero en el centro / no toca a Altza-Egia» se
  **retiró** de relato, resumen y TESIS. Ni el parque de Etxegintza ni el
  Registro de Vivienda Protegida completo se publican georreferenciados
  (buscado en Donostia OD, Open Data Euskadi, Eustat PxWeb, Udalmap) → la foto
  completa queda como **laguna declarada**; el contrapeso se cuenta con el dato
  de ciudad (3.151 = ¼) + la ventana Etxebide etiquetada como tal.
  ✅ *Integración narrativa (jul-2026, Code, reescrita el 05):* figura «El
  contrapeso público: una ventana parcial» en el cap. 7 + resumen/TESIS.*
- ⬜ **REC-16 tipología comercial vía OSM** (histórico): ¿comercio de barrio →
  servicios turísticos? Complementa REC-7 (que solo llega a ciudad).
- ✅ **REC-17 matrices origen-destino Eustat** — hecho (jul-2026) con matiz:
  **la matriz municipio×municipio no existe en el banco PxWeb** (catálogo
  completo revisado, 2.321 tablas); se cablea lo que hay: EMPA mt02 (lugar
  de trabajo categórico, 2021–2024 → `residents_work_in_city_pct`, 66 %
  trabaja en el propio municipio), EME me02 (estudios →
  `residents_study_in_city_pct`), DIRAE est07 (empleo localizado 1995–2025 →
  `jobs_located`, 65.962→103.446) y el derivado `job_concentration_ratio`
  (**1,20 en 2024**: la ciudad importa trabajadores). **Con esto la mitad
  coja de H4 ("sin dejar de concentrar actividad") tiene dato.** Módulo
  `datasets/movilidad_laboral.py` + tests.
- ✅ **REC-18 equipamientos ampliados** — hecho (jul-2026, primer corte):
  `health_per_1000` (equipamientos de salud, 29 puntos, join punto→barrio,
  normalizado por 1000 hab.) — el lado «ciudad vivida» de la accesibilidad,
  junto a `schools_per_1000`. Nuevo tema «Sanità» en el picker. Se deja como
  **densidad de servicios**, no isócrona/tiempo de trayecto (fuera de
  presupuesto, ver `PLAN-CIERRE.md`); Miramón-Zorroaga sale alto por el hospital
  con poca población (artefacto per cápita conocido, documentado). Bibliotecas /
  zonas verdes / socio-asistencial no añadidos en este corte (un recurso dio 500;
  se pueden sumar con el mismo patrón si se retoma). Módulo `datasets/salud_gis.py`
  + 2 tests. ✅ *Integración narrativa hecha (jul-2026, Code): capa «Servicios de
  salud» en el mapa de la ciudad vivida del cap. 6 + resumen/TESIS (anexo 🏥).*
- ⬜ **REC-19 percepción ciudadana** (encuestas municipales de satisfacción):
  la capa subjetiva que falta.
- ⬜ **REC-20 cajón de ideas** (menor prioridad): licencias de obra y
  rehabilitación, matrícula escolar por centro, vegetación/arbolado satelital.
- ✅ **REC-21 perfil migratorio y de empleo** — hecho y **cableado al pipeline**
  (jul-2026), petición de usuario: país de origen por barrio (57 países,
  2000–2025, único dato a grano barrio) cruzado con renta/estudios (r=−0,69
  renta↔% América Latina, +0,59 % univ.↔% Europa occidental); actividad
  laboral por continente y ocupación/renta/I+D generales (grano Gipuzkoa/C.A.
  de Euskadi — Eustat no cruza nacionalidad×ocupación×salario a ningún grano
  español, catálogo completo revisado). Confirma la intensidad investigadora
  de Gipuzkoa (31 ‰ ocupados vs. 13,6 ‰ España, INE 2024). Análisis
  exploratorio en `analysis/perfil_extranjeros_empleo.py` + tests; detalle en
  `docs/intermedia/ANALISIS-EXTRANJEROS-EMPLEO.md`. **Implementación en el
  pipeline**: `datasets/demografia_origen_region.py` → 8 métricas coropléticas
  nuevas `pct_origin_*` (barrio×año, mismo `demo_barrio.csv` que `pct_foreign`)
  + `datasets/empleo_nacionalidad_gipuzkoa.py` → 3 indicadores de ciudad
  (`unemployment_rate_spanish/foreign_gipuzkoa`, `randd_personnel_per_1000_employed_gipuzkoa`);
  35 métricas y 28 indicadores en total tras el build, verificado en el
  dashboard (mapa + panel de indicadores). Quedan **analysis-only** por no
  encajar en el modelo Metric/Indicator (desglose multi-categoría, no un
  valor por año): ocupación CNO-11, establecimientos por sector A10 en
  Donostia, renta por profesión. ✅ **Integración narrativa hecha (jul-2026, Cowork):**
  capítulo 4 «Quién trabaja Donostia» en `historias.html` (coropleta interactiva de
  origen + gráficos de correlación/salario/I+D, caveats MET-5/MET-6) + digest en
  `resumen.md`/`TESIS-CIUDAD.md`. **Pendiente (Code):** ver REC-21-web abajo.

#### Hipótesis desde encuestas de percepción (H5–H8, `docs/HIPOTESIS-FUTURAS.md` §3)

> ✅ **Integración narrativa hecha (jul-2026, Code):** coda **«Lo que preocupa a
> la ciudad — y lo que dicen los datos»** en `historias.html` (tras el apéndice,
> antes del epílogo): contrasta las preocupaciones de la encuesta 2026 con los
> datos — inseguridad (HU-1, con gráfico percepción Eustat + criminalidad
> Gipuzkoa), turismo (H8 + HU-5/6), ruido (H6), vivienda (H7). Etiquetado
> Gipuzkoa≠Donostia. `datos.html` con las fuentes nuevas. Verificado en Chromium
> (0 errores JS). De paso, arreglado un bug de layout de `.conf` (fichas de
> confianza) en todo el relato. **H5 sigue bloqueada** (el usuario buscó el
> desglose por barrio de la encuesta de seguridad 2026, no existe público).

- ✅ **H6 (ruido percibido × isla de calor × VUT)** — hecho (jul-2026,
  analysis-only): `analysis/perceived_noise_geography.py` (9 tests) + 2 inputs
  curados (`percepcion_ruido_donostia.csv` encuesta 2026 parcial;
  `isla_calor_barrio.csv` reproducción de REC-14). **Hallazgo:** el ruido
  percibido va con el calor (r≈0,73) y el ruido medido (r≈0,75), **no** con la
  VUT (r≈0,47, confundida por el centro) → ruido = densidad/tráfico, no turismo
  (MET-5/VIZ-5). ⬜ *Pendiente (opcional, Cowork):* llevarlo a la narrativa.
- ✅ **H7 (heterogeneidad del alquiler / «Zubieta barato»)** — hecho (jul-2026,
  analysis-only): `analysis/rent_heterogeneity.py` (7 tests). (1) El «Zubieta
  barato» **no es verificable**: 6/19 barrios sin dato EMA (Zubieta, Igeldo,
  Añorga, Miramón-Zorroaga, Landerbaso, Oarain) + 2 parciales → registro parcial
  (MET-5). (2) Entre los 11 con serie, subida heterogénea pero al revés: el este
  obrero barato sube más (Loiola +48 %) que el centro caro (Egia +28 %),
  corr(nivel, crec.)≈−0,5 → convergencia en % (brecha en €/m² persiste, AN-13).
  ⬜ *Opcional (Cowork):* narrativa (une con HU-7).
- ✅ **H8 (turismo↑ / altas VUT↓)** — hecho (jul-2026, analysis-only):
  `analysis/tourism_concern_flow_stock.py` (7 tests). Flujo de altas −94 % desde
  2017 (300→18) y crecimiento del parque 171 %→1,4 %, pero stock (1.329 lic.,
  5.706 plazas) y volumen (pernoctaciones récord 2,2 M) en máximos → la
  preocupación de 2026 va con el stock/masificación, no con el flujo. Descriptivo
  (encuesta de un solo año). ⬜ *Opcional (Cowork):* narrativa.
- 🚫 **H5** (inseguridad percibida por barrio) — **NO SE HACE** (jul-2026,
  decisión del usuario): no aparece el desglose por barrio de la encuesta de
  seguridad 2026. Sin ese dato la hipótesis no es evaluable; se retira del plan.

- ✅ **HU-5/HU-6 (desestacionalización + MICE)** — hecho (jul-2026,
  analysis-only): `analysis/tourism_deseasonalization.py` (8 tests) sobre
  pernoctaciones mensuales INE 2005–2026. **HU-5 confirmada:** estacionalidad ↓
  sostenida (%verano 35,9→32,9 %, CV 0,32→0,26; 2023–25 los años menos
  estacionales); la temporada baja crece +44 % más rápido que agosto.
  **HU-6:** cruce MICE×mes **imposible** (MICE solo anual) → contribuyente
  plausible pero no aislable; limitación declarada. ⬜ *Opcional (Cowork):*
  narrativa (encaja con la historia turística, cap. 6).

#### Batería de hipótesis del usuario (HU-1…HU-7, jul-2026)

> Propuestas por el usuario; evaluadas con semáforo y fuentes en
> `docs/HIPOTESIS-FUTURAS.md` §5. Trabajadas HU-7, HU-1 y HU-3 (las tres
> priorizadas). HU-2/HU-4/HU-5/HU-6: ver §5 (congeladas o bloqueadas por datos).

- ✅ **REC-22 (HU-7) asequibilidad: alquiler vs. salario vs. IPC** — hecho y
  **cableado al pipeline+web** (jul-2026). Nueva métrica coroplética de barrio
  `income_labor` (renta del trabajo, Eustat `PX_173402_crpf_rpf_rp22_2p`, tipo
  110, 2016–2023) → `datasets/renta_trabajo.py` + `ensure_eustat_renta_trabajo`
  + tests; aparece en el selector *Economia*. IPC curado
  (`datos/input/ipc_espana.csv`, INE tabla 50902). Análisis
  `analysis/housing_affordability.py` (13 tests). **Hallazgo:** alquiler
  **+24,8 %** > salario **+21,8 %** > IPC **+20,4 %** (2016–2023; a 2024 alquiler
  +34,8 %). El «más que el sueldo» se sostiene con el **salario real**, no con la
  renta disponible pc (+28 %, inflada por capital/pensiones). ✅ **Casilla del
  precio de venta €/m² cerrada** por REC-25 (jul-2026): la venta subió **+29 %**
  (2016–2023), por delante del alquiler, el salario y el IPC → refuerza «comprar se
  encareció más que todo lo demás». ✅ **Sección web dedicada hecha** (jul-2026):
  `AffordabilitySection` en el app — gráfico indexado (base 2016=100) de **venta ·
  alquiler · salario · IPC** de ciudad (media ponderada por población) desde
  `web/src/data/affordability_index.json` (`datasets/affordability_index.py`, 6
  tests + 1 web). Tarjetas con la ventana común 2016–2023 (venta +30 % > alquiler
  +25 % > salario +22 % > IPC +20 %) y el acumulado por serie. Verificado en navegador.
- ✅ **REC-25 (Usuario) — precio de venta €/m² por barrio vía idealista** — hecho
  y **cableado a pipeline+web+relato** (jul-2026, dato aportado por el usuario).
  idealista publica en su **sala de prensa** informes de precio de vivienda por
  barrio, pero el sitio devuelve **403 (anti-bot)** a cualquier cliente automatizado
  (verificado; no se evade el anti-bot por ToS) → el usuario pasó la **serie mensual
  larga ~2010–2026** como Excel, transcrita a snapshot curado
  `datos/input/precios_venta_idealista.csv` (10 zonas idealista). Nueva métrica
  coroplética **`sale_price_eur_m2`** (tema *Abitazioni*, €/m², **media anual
  2011–2026**, proxy) vía `datasets/precio_venta.py` (+ `velocity_sale_price_eur_m2`)
  con **crosswalk documentado** idealista→19 barrios (agregadas comparten valor;
  `erdialdea` = Centro-Miraconcha, decisión del usuario; Parte Vieja aparte;
  Miramón/Loiola-Martutene excluidas: serie duplicada byte a byte hasta 2019).
  7 tests pipeline. **Al relato:** nueva sección en la Historia 1 de
  `historias.html` (gráfico de líneas 2011–2026 con 4 barrios resaltados) — **cierra
  la casilla 🔴 de HU-7**: entre 2016–2023 la venta subió **+29 %** (por delante de
  alquiler +24,8 %, salario +21,8 %, IPC +20,4 %) y **+60 %** acumulado 2016→2026;
  la brecha de nivel centro/este (2,2×) persiste. metrics.json / metric_*.json /
  metrics_long.csv regenerados; recuento de confianza sube a 40 métricas.
  ⚠️ Precios de **oferta**, no de transacción; verificado en navegador (mapa + app).
- ✅ **REC-23 (HU-1) percepción de seguridad vs. criminalidad real** — hecho y
  **cableado al pipeline+web** (jul-2026). Indicadores de ciudad
  `perception_insecurity_donostia/_euskadi` (Eustat ECV `PX_010901_cecv_ma04_3`,
  % familias con problema de seguridad, 1989–2024) + `crime_infractions`/
  `crime_rate_1000` (parcial) → `datasets/seguridad.py` + tests; tema
  *Sicurezza* nuevo en el frontend; render en «Altri indicatori cittadini».
  Datos curados `percepcion_seguridad_eustat.csv` + `criminalidad_donostia.csv`.
  Análisis `analysis/perception_vs_crime.py` (8 tests). **Hallazgo:** «la
  seguridad ha bajado mucho» es **falso a largo plazo** (35,4 % de familias con
  problema en 1989 → 14–18 % en 2004–2019) con **repunte 2019→2024 (→21,5 %)**.
  ✅ **Serie oficial de criminalidad integrada (jul-2026, dato del usuario):**
  Portal Estadístico de Criminalidad (Min. Interior), **Gipuzkoa 2010–2024**
  (`datos/input/criminalidad_gipuzkoa_mir.csv`, 44 tipologías + total) → indicador
  `crime_infractions_gipuzkoa` (`datasets/seguridad.py`, +2 tests) y análisis
  ampliado (`perception_vs_crime.py`, 11 tests, quita el proxy). Hallazgo: el
  delito real estuvo **plano en la década de 2010** y **sube +34 % 2019→2024** →
  percepción y realidad **coinciden**, la «tijera» no se sostiene, pero el
  repunte de preocupación **tiene base real**; a largo plazo la seguridad
  percibida es mucho mejor que en 1989. ⚠️ **Es provincia, no municipio**
  (Donostia ≈ ⅓ de Gipuzkoa) — etiquetado así en el indicador y a declarar en
  cualquier relato; el grano municipal sigue parcial (prensa). Pendiente
  (opcional, Cowork): llevar la «tijera» y el matiz Gipuzkoa≠Donostia al HTML.
- ✅ **REC-24 (HU-3) tipología comercial de la Parte Vieja (OSM)** — hecho como
  **analysis-only** (jul-2026): `analysis/commercial_typology.py` (24 tests)
  clasifica locales OSM (`shop=*` + hostelería `amenity=*`) en hosteleria/
  turistico/cotidiano/otro/vacant por barrio (Overpass, cache gitignored),
  cruza con densidad VUT y triangula con la serie CNAE de ciudad (REC-7).
  **Hallazgo:** la Parte Vieja (bbox) es **~82 % hostelería** (85/103 locales),
  3 comercios cotidianos → distrito casi monofuncional de consumo de visitante;
  `corr(turistico_share ↔ VUT)=+0,39`. ⚠️ OSM = foto actual (no cambio) y
  completitud variable por barrio → proporciones > recuentos. ✅ **Llevado a la
  web (jul-2026, decisión del usuario):** métrica de barrio `hosteleria_share`
  (tema *Turismo*) desde un **snapshot curado** `datos/input/tipologia_comercial_osm.csv`
  (sin fetch OSM en build, reproducible offline) vía `datasets/tipologia_comercial.py`
  (4 tests, proxy). Barrios con <15 locales mapeados = sin dato (mata artefactos
  de tejido fino: Miramón 5 locales → 100 %). 13 barrios con dato; aparece en el
  selector y pinta el mapa (verificado en navegador). metrics.json/metric_*.json/
  metrics_long.csv regenerados; recuento de confianza a 38 métricas (4 proxy).

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
- ✅ **REC-21-web — ficha de país en el detalle de barrio** (Code, `web/`) —
  hecho (jul-2026): sección **«Chi vive nel barrio · origini»** en el app con
  selector de barrio → top-5 nacionalidades extranjeras del barrio, cada una con
  barra (cuota del barrio), nº de personas y variación a 10 años (▲/▼/nuovo).
  Decidido: **vive en el app** (no solo en el relato). No es un `Metric` (lista
  de países por barrio); export propio `web/src/data/origen_paises_barrio.json`
  vía nuevo `datasets/origen_paises_barrio.py` desde el mismo `demo_barrio.csv`
  que `pct_origin_*`, cableado en `build.run()`. Color por región reutiliza la
  agrupación del choropleth pero **legible sin color** (dot + nombre + flechas +
  cifras, a11y). Aviso MET-5 explícito en la copy. 9 tests pipeline + 7 web
  (TDD); verificado en navegador. Contrato en `docs/DATA-CONTRACT.md`. ✅ *Enlace
  desde la historia #4 hecho (jul-2026, Code).*
- ✅ **A11y del app React** (Code, `web/`) — hecho (jul-2026): los mapas del app
  son canvas WebGL (opacos a AT, tooltip solo-ratón); cada uno gana una
  **tabla-espejo accesible** (`MapDataTable`: `<details>` en el orden de
  tabulación, teclado, `<table>` de todos los barrios con valor+Δ) y su
  `map-area` un `role=img`+`aria-label` descriptivo — el dato deja de ser
  solo-color. Cobertura **completa**: mapa principal, los 2 de «città turistica
  vs. vissuta», los **3 de Transformación**, el de **tensión residencial**
  (MET-1) y el **bivariado** (X×Y con clases, en texto plano). `MapDataTable` es
  presentacional: `barrioRows` (mapas de `MetricData`), `rowsFromDecorated`
  (shape computado) y filas a medida (bivariado); lógica en `lib/mapTable.ts` +
  5 tests; utilidad `.sr-only`. Contraste verificado: `--muted` 4,60:1,
  `--accent` 4,82:1, `--fg` 16:1 → **todos pasan AA**. ✅ *Auditoría de foco
  cerrada (jul-2026): anillo `:focus-visible` global y consistente en
  button/select/input/a (los selects/sliders nativos ya eran accesibles), chips
  m²/persona con `role=group`+`aria-pressed`, heatmap de estacionalidad con
  `role=img`+`aria-label` (antes era solo-hover). 67 tests web en verde.*
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
- **Scraping de anuncios de venta (Indomio/Idealista)** — descartado (ToS). La vía
  de los **informes publicados** de la sala de prensa de idealista sí se usó: el
  usuario los pasó como snapshot curado → **REC-25 hecho** (métrica `sale_price_eur_m2`).
  La del catastro foral (REC-8) sigue abierta.
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
