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
   **seis historias** (la ciudad que se encarece · qué barrios cambian más rápido ·
   quién vive Donostia · el clima cambia · turística vs. vivida · en transformación)
   con texto y **visualizaciones interactivas** (mueve el supuesto de m²/persona,
   recorre los años, cambia de indicador). Ábrelo en cualquier navegador; es
   autocontenido, sin dependencias.
2. **[`output/resumen.md`](output/resumen.md)** — síntesis del proyecto (datos,
   análisis, correlaciones e historias) pensada para revisión externa.
3. **[`docs/GUION-OUTPUTS.md`](docs/GUION-OUTPUTS.md)** — el plan de los relatos:
   para cada historia, la pregunta de partida, las cifras verificadas, dónde vive
   en la app y los avisos de confianza.
4. **[`docs/TESIS-CIUDAD.md`](docs/TESIS-CIUDAD.md)** — la lectura integrada: qué
   dicen en conjunto los datos sobre la transformación de Donostia, y qué **no** se
   puede afirmar todavía.
5. **[`BACKLOG.md`](BACKLOG.md)** — qué está hecho y qué falta, separado en tareas
   de **Cowork** (documentación/relatos) y **Code** (pipeline/web/datos).

---

## 🗺️ Cómo navegar el repositorio

```
.
├── README.md             ← este fichero
├── BACKLOG.md            ← backlog (hecho + pendiente), secciones Cowork / Code
├── output/               ← entregables: historias.html (6 historias) + resumen.md
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
| `NOTA-METODOLOGICA.md` | Decisiones metodológicas (MET-1…5): por qué medimos como medimos. | es |
| `TESIS-CIUDAD.md` | Lectura integrada y *cauta* de la transformación + anexo de hallazgos por eje. | es |
| `GUION-OUTPUTS.md` | **Plan de los relatos finales** (empieza por aquí para narrar). | es |

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

---

## 📊 Los datos

El pipeline escribe JSON limpio en `web/src/data/` (versionado), de modo que **la
web se construye sin Python ni red**: carga JSON/GeoJSON estáticos. Los mismos
números se exportan como **tablas tidy CSV** en `datos/procesado/tablas/` (ver
[`datos/procesado/tablas/README.md`](datos/procesado/tablas/README.md)),
reutilizables en cualquier stack. La carpeta [`datos/`](datos/README.md)
documenta y organiza entrada (`datos/input`, con `FUENTES.md`) y salida
(`datos/procesado`).

Estado actual: métricas coropléticas por barrio (población, origen, estudios,
renta, alquiler, tensión, VUT, **densidad Airbnb**, escuelas) + **velocidad de
cambio** (`velocity_*`) + **perfiles** (categórica) + **estructura por edad** +
**ruido nocturno** (GIS) + el **Índice de Transformación** (`transform_*`); **series
mensuales** de ciudad (clima + pernoctaciones + reseñas Airbnb); **indicadores
anuales** (MICE, reciclaje, fiscalidad). Cada métrica lleva su **ficha de confianza**
(observado / derivado / proxy + supuestos). Geometría única de referencia: 19 barrios
oficiales (`mapa_auzoak`), con `barrio_id` estable como clave de join.

> **Nombre de barrio:** el barrio se escribe **Antiguo** en textos de cara al
> usuario (el `barrio_id` interno sigue siendo `antigua` como clave de join).

Todas las cifras citadas en la documentación y en `output/historias.html` son
**reproducibles** desde `analysis/*.py` o desde las métricas del pipeline.

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
