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

1. **[`historias.html`](historias.html)** — el documento narrativo: cuatro
   historias (la ciudad que se encarece · qué barrios cambian más rápido · quién
   vive Donostia · el clima cambia) con texto y **visualizaciones interactivas**
   (mueve el supuesto de m²/persona, recorre los años, cambia de indicador). Ábrelo
   en cualquier navegador; es autocontenido, sin dependencias.
2. **[`docs/GUION-OUTPUTS.md`](docs/GUION-OUTPUTS.md)** — el plan de los relatos:
   para cada historia, la pregunta de partida, las cifras verificadas, dónde vive
   en la app y los avisos de confianza.
3. **[`docs/TESIS-CIUDAD.md`](docs/TESIS-CIUDAD.md)** — la lectura integrada: qué
   dicen en conjunto los datos sobre la transformación de Donostia, y qué **no** se
   puede afirmar todavía.

---

## 🗺️ Cómo navegar el repositorio

```
donostia-dataviz/
├── historias.html        ← documento narrativo interactivo (output principal)
├── README.md             ← este fichero
├── docs/                 ← documentación activa (brief, fuentes, metodología, análisis, relatos)
│   └── archive/          ← documentos históricos / superados (no borrados)
├── data/                 ← tablas tidy CSV (datos en formato abierto, ver data/README.md)
├── data-pipeline/        ← Python: fuentes públicas → JSON/CSV limpios
├── analysis/             ← scripts de análisis (correlaciones, velocidades, clusters, índice)
└── web/                  ← app React + Vite (dashboard coroplético)
```

### Mapa de documentos (`docs/`)

Agrupados por para qué sirven. Toda la documentación activa está en español.

**Visión y plan**

| Documento | Qué es | Idioma |
|---|---|---|
| `PROJECT-BRIEF-v2.md` | Brief del proyecto: objetivo, dimensiones de datos, ideas. La visión. | es |
| `GAP-ANALYSIS.md` | **El backlog** (canónico): qué está hecho, qué falta, prioridades y sprints. | es |

**Fuentes y datos (técnico)**

| Documento | Qué es | Idioma |
|---|---|---|
| `SOURCES.md` | Registro de fuentes verificadas + estado de acceso de cada dataset. | en |
| `PLAN-RECOLECCION.md` | Especificación de adquisición de las fuentes **pendientes** (REC-*). | es |
| `IMPLEMENTACION-INGESTA.md` | Guía para implementar la ingesta de nuevas fuentes en el pipeline. | es |
| `DATA-CONTRACT.md` | Contrato pipeline ↔ frontend (forma estable de cada métrica). | en |
| `../data/README.md` | Diccionario de las tablas CSV (`metrics_long`, `series_long`, …). | en |

**Metodología, análisis y relatos**

| Documento | Qué es | Idioma |
|---|---|---|
| `NOTA-METODOLOGICA.md` | Decisiones metodológicas (MET-1…5): por qué medimos como medimos. | es |
| `ANALISIS-SPRINT-A.md` | Resultados del análisis: correlaciones robustas, velocidades, perfiles. | es |
| `INDICE-TRANSFORMACION.md` | Índice de Transformación Urbana (multi-definición, componentes a la vista). | es |
| `TESIS-CIUDAD.md` | Lectura integrada y *cauta* de la transformación + **anexo con el digest de hallazgos por eje**. | es |
| `GUION-OUTPUTS.md` | **Plan de los relatos finales** (empieza por aquí para narrar). | es |

**Histórico / revisión (`docs/archive/`)**

Conservados como referencia, no borrados. No forman parte del camino activo.

| Documento | Qué es |
|---|---|
| `archive/FEEDBACK-CONSOLIDADO.md` | Síntesis de cuatro revisiones externas; sus acciones ya están en GAP-ANALYSIS y NOTA-METODOLOGICA. |
| `archive/INSIGHTS.md` | Digest por eje; su contenido vive ahora en el anexo de `TESIS-CIUDAD.md`. |
| `archive/DATA-HANDOFF.md` | Resumen que se pasó a revisión externa (su origen). En italiano. |
| `archive/PROJECT-BRIEF.md` | Brief original (v1), verbatim. Superado por v2. En italiano. |

> **Consolidación aplicada (junio 2026):** se archivaron los cuatro documentos
> anteriores y se tradujo el brief v2 al español. Los técnicos `SOURCES.md`,
> `DATA-CONTRACT.md` y `data/README.md` se mantienen en inglés a propósito (campos
> y términos del código en inglés); traducirlos es opcional.

---

## 📊 Los datos

El pipeline escribe JSON limpio en `web/src/data/` (versionado), de modo que **la
web se construye sin Python ni red**: carga JSON/GeoJSON estáticos. Los mismos
números se exportan como **tablas tidy CSV** en `data/` (ver
[`data/README.md`](data/README.md)), reutilizables en cualquier stack.

Estado actual: **11 métricas coropléticas por barrio** + **5 de velocidad de
cambio** (`velocity_*`) + **1 categórica** de perfiles + **2 de estructura por
edad** + **1 GIS** de ruido nocturno; **5 series mensuales** de ciudad (clima +
pernoctaciones); **6 indicadores anuales** (MICE, reciclaje, fiscalidad). Cada
métrica lleva su **ficha de confianza** (observado / derivado / proxy + supuestos).
Geometría única de referencia: 19 barrios oficiales (`mapa_auzoak`), con `barrio_id`
estable como clave de join.

Todas las cifras citadas en la documentación y en `historias.html` son
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
```

### Regenerar `historias.html`

El documento narrativo embebe sus datos. Para regenerarlo tras refrescar el
pipeline, vuelve a extraer los datos de `data/*_long.csv`, `analysis/output/*.csv`
y `web/src/data/barrios.geojson` (ver el script de extracción del proyecto) y
reinyéctalos en la plantilla.

---

## 🧭 Principios

- **Una sola geometría de referencia** y join único en ingestión.
- **Provenance explícita**: cada valor arrastra su fuente.
- **Honestidad metodológica**: correlación ≠ causalidad; fichas de confianza;
  "transformación", nunca "gentrificación" (no se puede demostrar con estos datos).
- **Reproducibilidad**: todo número tiene un script o una métrica detrás.
