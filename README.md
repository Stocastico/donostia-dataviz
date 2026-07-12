# Donostia Dataviz

Análisis y narrativa de datos sobre la evolución de **Donostia / San Sebastián**,
barrio a barrio: turismo, vivienda, renta, demografía, educación, medio ambiente y
clima. El proyecto combina un **pipeline de datos** reproducible, un **dashboard
interactivo** y, sobre todo, un cuerpo de **documentación y relatos** que convierte
los datos en historias sobre cómo cambia la ciudad.

> **Naturaleza del proyecto.** Hoy es un proyecto **de documentación y análisis**:
> el pipeline y el frontend ya existen y funcionan; el trabajo actual es *definir,
> analizar y narrar* — no modificar el código. La documentación define qué se
> analiza, qué se concluye y qué quedaría por desarrollar.

---

## 🚀 Empieza aquí

1. **[`output/historias.html`](output/historias.html)** — el documento narrativo:
   **siete historias** (la ciudad que se encarece · qué barrios cambian más rápido ·
   quién vive Donostia · quién trabaja Donostia · el clima cambia · turística vs.
   vivida · en transformación)
   en formato **scrollytelling**: los mapas principales quedan fijos y van
   cambiando al hilo del texto, y todos los controles se pueden mover también a
   mano (el supuesto de m²/persona, el año, el indicador). Las métricas complejas
   llevan cajas «La métrica, en claro». Ábrelo en cualquier navegador; es
   autocontenido, sin dependencias.
2. **[`output/resumen.md`](output/resumen.md)** — síntesis del proyecto (datos,
   análisis, correlaciones e historias) pensada para revisión externa.
3. **[`docs/TESIS-CIUDAD.md`](docs/TESIS-CIUDAD.md)** — la lectura integrada: qué
   dicen en conjunto los datos sobre la transformación de Donostia, y qué **no** se
   puede afirmar todavía.
4. **[`BACKLOG.md`](BACKLOG.md)** — qué está hecho y qué falta, separado en tareas
   de **Cowork** (documentación/relatos) y **Code** (pipeline/web/datos).

---

## 🗺️ Cómo navegar el repositorio

```
.
├── README.md             ← este fichero
├── BACKLOG.md            ← backlog (hecho + pendiente), secciones Cowork / Code
├── output/               ← entregables: historias.html (7 historias) + resumen.md
├── datos/                ← input/ (crudos + curados + FUENTES.md) · procesado/tablas/ (tablas tidy CSV)
├── docs/                 ← documentación activa (fuentes, metodología, relatos)
│   ├── intermedia/       ← análisis ya volcados en los outputs (congelados)
│   └── archive/          ← documentos históricos / superados (no borrados)
├── data-pipeline/        ← Python: fuentes públicas → JSON/CSV limpios
├── analysis/             ← scripts de análisis (correlaciones, velocidades, clusters, índice)
└── web/                  ← app React + Vite (dashboard coroplético); web/src/data/ * es su JSON estático

* Vite carga estos JSON con `import.meta.glob` desde dentro de `web/src/`, así
  que se quedan en su sitio (a diferencia de `data/`, ya movido a
  `datos/procesado/tablas/`; ver BACKLOG).
```

### Mapa de documentos (`docs/`)

Agrupados por para qué sirven. Toda la documentación activa está en español.

**Visión y plan**

| Documento | Qué es | Idioma |
|---|---|---|
| `../BACKLOG.md` | **El backlog** (canónico): hecho + pendiente, secciones Cowork / Code. | es |
| `PROJECT-BRIEF-v2.md` | Brief del proyecto: objetivo, dimensiones de datos, ideas. La visión. | es |

**Fuentes y datos (técnico)**

| Documento | Qué es | Idioma |
|---|---|---|
| `SOURCES.md` | Registro de fuentes verificadas + estado de acceso de cada dataset. | en |
| `../datos/input/FUENTES.md` | Manifiesto de los datos de entrada: origen, URL y qué alimenta cada uno. | es |
| `DATA-CONTRACT.md` | Contrato pipeline ↔ frontend (forma estable de cada métrica). | en |
| `../datos/procesado/tablas/README.md` | Diccionario de las tablas CSV (`metrics_long`, `series_long`, …). | en |

**Metodología y relatos (activos)**

| Documento | Qué es | Idioma |
|---|---|---|
| `NOTA-METODOLOGICA.md` | Decisiones metodológicas (MET-1…8): por qué medimos como medimos. | es |
| `TESIS-CIUDAD.md` | Lectura integrada y *cauta* de la transformación + anexo de hallazgos por eje. | es |
| `WORKING-PAPER.md` | El *working paper* (DOC-6): método completo — datos, supuestos, inferencia con N pequeño, límites y patrón reutilizable. | es |

**Análisis intermedio (`docs/intermedia/`)**

Análisis ya volcados en los outputs (`historias.html`, `resumen.md`, `TESIS-CIUDAD`);
se conservan como referencia reproducible y, en principio, no se vuelven a tocar.

| Documento | Qué es |
|---|---|
| `intermedia/ANALISIS-SPRINT-A.md` | Correlaciones robustas, velocidades, perfiles. |
| `intermedia/ANALISIS-LEADLAG.md` | Lead/lag turismo→alquiler (AN-6, exploratorio). |
| `intermedia/INDICE-TRANSFORMACION.md` | Índice de Transformación Urbana (multi-definición). |

**Histórico / superado (`docs/archive/`)**

Conservados como referencia, no borrados. No forman parte del camino activo.

| Documento | Qué es |
|---|---|
| `archive/GAP-ANALYSIS.md` | Backlog técnico detallado previo; sustituido por `BACKLOG.md`. |
| `archive/PLAN-RECOLECCION.md` | Especificación de adquisición de fuentes (trabajo ya ejecutado). |
| `archive/IMPLEMENTACION-INGESTA.md` | Guía de ingesta (pipeline ya construido). |
| `archive/FEEDBACK-CONSOLIDADO.md` | Síntesis de revisiones externas; sus acciones ya están aplicadas. |
| `archive/INSIGHTS.md` | Digest por eje; su contenido vive en el anexo de `TESIS-CIUDAD.md`. |
| `archive/DATA-HANDOFF.md` | Resumen para revisión externa. En italiano. |
| `archive/PROJECT-BRIEF.md` | Brief original (v1). Superado por v2. En italiano. |
| `archive/GUION-OUTPUTS.md` | Plan de los relatos. Función cumplida: las 7 historias ya están escritas (cifras vigentes en `output/` y `TESIS-CIUDAD.md`). |
| `archive/session-handoff-*.md` | Bitácoras de sesión (jul-2026): qué se hizo y por qué, sesión a sesión. |

---

## 📊 Los datos

El pipeline escribe JSON limpio en `web/src/data/` (versionado), de modo que **la
web se construye sin Python ni red**: carga JSON/GeoJSON estáticos. Los mismos
números se exportan como **tablas tidy CSV** en `datos/procesado/tablas/` (ver
[`datos/procesado/tablas/README.md`](datos/procesado/tablas/README.md)),
reutilizables en cualquier stack. La carpeta [`datos/`](datos/README.md)
documenta y organiza entrada (`datos/input`, con `FUENTES.md`) y salida
(`datos/procesado`).

Estado actual (**41 métricas coropléticas** por barrio, jul-2026): población,
origen (incl. **8 regiones de origen** `pct_origin_*` + **ficha de países** por
barrio), estudios, renta (total y **del trabajo**, REC-22), alquiler, **precio de
venta €/m²** (idealista, REC-25), tensión, VUT, **densidad Airbnb**, escuelas y
**servicios de salud** (accesibilidad, REC-18), **vivienda protegida** (Etxebide,
REC-15), **hostelería sobre locales** (OSM, HU-3) + **velocidad de cambio**
(`velocity_*`) + **perfiles** (categórica) +
**estructura por edad** + **ruido nocturno** (GIS) + el **Índice de
Transformación** (`transform_*`); **series mensuales** de ciudad (clima +
pernoctaciones + reseñas Airbnb); **33 indicadores anuales** (MICE, reciclaje,
fiscalidad, paro, comercio, movilidad laboral, modelos lingüísticos, seguridad
—percepción y delito—…). Cada
métrica lleva su **ficha de confianza** (observado / derivado / proxy +
supuestos) y el mapa tiene **tabla-espejo accesible** (teclado / lector de
pantalla). Geometría única de referencia: 19 barrios oficiales (`mapa_auzoak`),
con `barrio_id` estable como clave de join.

> **Vigencia de los datos:** última descarga completa de las fuentes el
> **2026-07-10**; build online re-validado contra las fuentes vivas el
> **2026-07-11** (todas responden; diffs aguas arriba mínimos, no aplicados —
> ver BACKLOG §Datos crudos). El **2026-07-12** se refrescó **solo Inside
> Airbnb** al snapshot **2026-06-30** (métricas `airbnb_*`, serie de reseñas y
> componente turístico del Índice de Transformación); el resto sigue en el
> estado del 07-10. Detalle por fuente en `datos/input/FUENTES.md`
> y en la sección «Vigencia» de `output/datos.html`.

> **Nombre de barrio:** el barrio se escribe **Antiguo** en textos de cara al
> usuario (el `barrio_id` interno sigue siendo `antigua` como clave de join).

Además de las 41 métricas por barrio, hay una vista **sub-barrio** (grano
**calle**): *"Viviendas turísticas, calle a calle"* — un mapa de símbolos
proporcionales de las **viviendas turísticas por calle** (301 calles), cruzando
el censo VUT con el callejero municipal. Datos en `web/src/data/street_vut.json`
y `datos/procesado/tablas/calles_vut.csv`.

Todas las cifras citadas en la documentación y en `output/historias.html` son
**reproducibles** desde `analysis/*.py` o desde las métricas del pipeline.

---

## 🌐 Sitio publicado (GitHub Pages)

El proyecto se publica como un único sitio estático:

- **El relato** (las siete historias) es la **portada**:
  `https://stocastico.github.io/donostia-dataviz/` (también `…/historias.html`)
- **Metodología**: `…/metodologia.html` · **datos y fuentes**: `…/datos.html`
- **Working paper** (DOC-6): `…/working-paper.html`, generado en cada deploy
  desde `docs/WORKING-PAPER.md` por `scripts/build_working_paper.py`
- **Panel interactivo** (la app React): `…/app/`

El despliegue lo hace `.github/workflows/deploy-pages.yml` y es **solo manual**:
pestaña *Actions → Deploy site (GitHub Pages) → Run workflow* (sobre `main`).
Construye `web/` con `VITE_BASE=/donostia-dataviz/app/`, copia los HTML
autocontenidos de `output/` a la raíz (historias también como `index.html`) y
convierte el working paper de markdown a HTML. **Ningún merge ni push
publica nada por sí solo**: se revisan los textos y se lanza cuando se decide.

> **Activación (una sola vez):** en *Settings → Pages*, poner **Source =
> "GitHub Actions"**. El workflow intenta activarlo solo (`enablement: true`);
> si el primer despliegue falla por permisos, basta ese ajuste manual.

---

## ⚙️ Ejecutar

### Frontend (dashboard)

```bash
cd web
npm install
npm run dev        # http://localhost:5173
npm test           # vitest
npm run build      # type-check + build de producción
```

### Pipeline de datos (solo para refrescar datos)

```bash
cd data-pipeline
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m donostia_pipeline.build            # descarga + reconstruye web/src/data
python -m donostia_pipeline.build --offline  # reconstruye desde raw/ cacheado
pytest                                        # tests de contrato e integridad de joins
```

Añadir una métrica = añadir un módulo en
`data-pipeline/src/donostia_pipeline/datasets/` que exponga `build(ctx) -> list[Metric]`,
registrarlo en `build.DATASETS` y reejecutar. El frontend la recoge vía
`metrics.json` sin cambios. El dataset AEMET necesita una API key gratuita en
`AEMET_API_KEY` (se solicita en <https://opendata.aemet.es>).

### Análisis

```bash
python analysis/sprint_a.py --save             # correlaciones, velocidades, clusters
python analysis/distribucion_barrios.py --save # niveles×variaciones, polarización
python analysis/transformation_index.py --save # índice de transformación urbana
python analysis/lead_lag.py --save             # lead/lag turismo→alquiler (AN-6)
```

### Regenerar `output/historias.html`

El documento narrativo embebe sus datos en una única línea `<script>window.DONO =
{…}` y dibuja los mapas/gráficos en SVG en el navegador. Para actualizar los datos
tras refrescar el pipeline: parsea esa línea, funde las métricas desde
`web/src/data/metric_*.json` / `series_*.json` (y `barrios.geojson` para la
geometría) y reescríbela. Es autocontenido: no depende de ficheros externos en runtime.

El DOM renderizado (scrollytelling, etiquetas del scatter, sincronía de los
controles, explicadores) está cubierto por `web/tests/historias.test.ts`, que
ejecuta el HTML completo bajo jsdom: tras regenerar el documento, correr
`npm test` en `web/` verifica que nada se rompió.

---

## 🧭 Principios

- **Una sola geometría de referencia** y join único en ingestión.
- **Provenance explícita**: cada valor arrastra su fuente.
- **Honestidad metodológica**: correlación ≠ causalidad; fichas de confianza;
  "transformación", nunca "gentrificación" (no se puede demostrar con estos datos).
- **Reproducibilidad**: todo número tiene un script o una métrica detrás.

---

## License

See LICENSE file for details.
