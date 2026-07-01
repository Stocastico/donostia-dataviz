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

Pipeline + web + tests estables. **6 historias** publicadas en
`output/historias.html`; análisis AN-1…AN-8 y correcciones MET-1…MET-5 hechos.
Documentación reorganizada (`output/`, `datos/`, `docs/intermedia/`,
`docs/archive/`). Lo que queda es sobre todo **datos nuevos y refinamientos (Code)**
e **iteración narrativa (Cowork)**.

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

---

## Pendiente — Cowork ⬜

- ⬜ **Revisar el render de `output/historias.html`** e iterar #5 y #6 según feedback.
  Pendiente de abrirlo en navegador (la extensión de Chrome estuvo desconectada en
  las sesiones anteriores); la validación hasta ahora es estática (JSON, sintaxis JS, IDs).
- ✅ **Auditoría de enlaces internos** tras mover docs — hecha (jul-2026): los docs
  activos apuntan a `intermedia/`, `archive/` o `BACKLOG.md`; README y `resumen.md`
  actualizados. Los docs de `intermedia/`/`archive/` se dejan congelados.
- ⬜ **Mantener `resumen.md` y `TESIS-CIUDAD`** al día cuando entren datos nuevos.
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
- ⬜ **Poblar `datos/input/raw/`** ejecutando `datos/input/descargar_raw.sh` o
  `python -m donostia_pipeline.build` (necesita red; **AEMET requiere
  `AEMET_API_KEY`**). No se pudo hacer desde Cowork (web_fetch agota tiempo; curl
  prohibido por política). Ver `datos/input/FUENTES.md`.

### Datos nuevos / análisis (del backlog histórico)
- ⬜ **REC-5 empleo/paro/sectores** (SEPE/Eustat, prob. solo ciudad).
- ⬜ **REC-6 movilidad** — investigado (jul-2026): el dataset `dbus_utilizacion`
  (viajeros DBus por línea/mes/hora) que enlaza Open Data Euskadi ya **no existe**
  en el catálogo CKAN de Donostia (403 + 0 resultados en su buscador de
  paquetes/recursos) — parece otra fuente dada de baja, como la de criminalidad.
  Sin URL viva confirmada, aparcado.
- ⬜ **REC-7 tejido comercial** (licencias IAE/CNAE o bajos vía catastro foral).
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
- ⬜ **AN-6 refinamiento** — alquiler mensual/trimestral y 2ª señal turística
  independiente para triangular el lead/lag.

### Visualización (si se llevan a la web)
- ⬜ **VIZ-8** small multiples por año + "play" animado.
- ⬜ **VIZ-9** scrollytelling (solo tras cerrar contenido).
- ⬜ **VIZ-10** "ciudad turística vs. vivida" en la app (ya existe como historia #5 en el HTML).
- ⬜ **VIZ-5 (resto)** overlay ruido × densidad turística.

---

## Descartado / no hacer (decisiones firmes)

- **Criminalidad por barrio** — fuente eliminada + escala sub-municipal protegida.
- **Precios de venta €/m² por barrio** — solo vía catastro foral (REC-8); nunca
  scraping de Indomio/Idealista (ToS).
- **"Índice de gentrificación" como caja negra** — se usa "Transformación Urbana",
  multi-definición y con componentes a la vista.

---

## Convenciones vigentes

- **"Transformación", nunca "gentrificación"** (falta rotación de población).
- **Correlación ≠ causalidad**; incluso el lead/lag es exploratorio.
- **% de extranjeros no es proxy** de transformación; el **ruido es de tráfico**,
  no de turismo.
- Toda métrica lleva su **ficha de confianza** (observado / derivado / proxy).
- **No versionar crudos grandes**; sí el input curado + `FUENTES.md` + script de descarga.
