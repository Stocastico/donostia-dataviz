# Backlog — Donostia Dataviz (gap analysis + tareas)

> **Qué es este documento.** Backlog priorizado del proyecto. Compara el plan
> (`PROJECT-BRIEF-v2.md`) con lo implementado y, sobre todo, traduce el
> **feedback externo consolidado** (`FEEDBACK-CONSOLIDADO.md`) en tareas
> concretas de **recolección de datos, análisis, visualización y
> documentación**, orientadas a producir varios *outputs* que cuenten la
> evolución de la ciudad. Se actualiza a medida que las tareas pasan a "hecho".
>
> *Nota: este archivo se reescribió en español (junio 2026) integrando las
> cuatro revisiones externas. La versión previa estaba en italiano.*
>
> **Decisiones adoptadas (junio 2026):**
> 1. **Criminalidad por barrio: descartada formalmente** (fuente eliminada +
>    escala sub-municipal blindada). Fuera del backlog, no del camino crítico.
> 2. **El índice se llama "Índice de Transformación Urbana"** (nunca
>    "gentrificación"), con definición explícita y seleccionable.

**Estado del repo de referencia:** 11 métricas coropléticas por barrio + 5
métricas derivadas de **velocidad de cambio** (`velocity_*`, divergentes) + 1
métrica **categórica** de perfiles de barrio (`barrio_profile`), 5 series
mensuales ciudad, 4 indicadores anuales ciudad, export CSV "long", módulo de join
espacial completo (P0.2), 76 tests pipeline + 29 frontend.

- **Métricas por barrio (11):** `population`, `pct_foreign`, `pct_university`,
  `income_total`, `income_gender_gap`, `rent_eur_m2`, `housing_tension`,
  `vut_count`, `vut_plazas`, `vut_density`, `schools_per_1000`.
- **Series mensuales ciudad (5):** `overnight_stays`, `temp_avg`, `temp_max`,
  `precip`, `hot_days_30`.
- **Indicadores anuales ciudad (4):** `recycling_rate`, `mice_events_total`,
  `mice_attendees`, `mice_icca_congresses`.

---

## 1. Qué ya está hecho y sigue válido

| Área | Estado en el repo | ¿Válido? |
|---|---|---|
| **Geometría de referencia única** (mapa_auzoak, join sobre una sola geometría) | `geometry.py` → 19 barrios, `barrio_id` estable + `kod_auzo`; join por código/nombre + alias | ✅ es el fundamento del proyecto |
| Fase 1 — coropleta + slider + tooltip (Δ) + leyenda | `ChoroplethMap`, `TimeSlider`, `MetricPicker`, `Legend` | ✅ |
| Fase 2 — comparación 2–3 barrios + marca COVID | `BarrioCompareChart` | ✅ |
| Fase 3 — heatmap mes×año + tendencia anual con regresión | `SeasonalityHeatmap` + `AnnualTrendChart` | ✅ |
| Fase 4 — scatter/correlaciones (Pearson en vivo) | `ScatterSection` (VUT↔alquiler r=0,64; renta↔%extranjeros r=−0,58) | ✅ |
| Renta por barrio (total + brecha de género) | `renta.py` | ✅ |
| **Alquiler €/m² por barrio** (Gobierno Vasco EMA, registrado 2016–24) | `rent.py` — mejor que Indomio | ✅ supera el plan |
| Turismo: VUT density/count/plazas | `vut.py`, `vut_density.py` | ✅ |
| Demografía: población, % extranjeros | `demografia.py` | ✅ |
| Educación: % universitarios | `estudios.py` | ✅ (parcial: ver modelos A/B/D) |
| Clima AEMET Igeldo 1024E (temp+precip+extremos+trend) | `aemet_climate.py` | ✅ |
| Estacionalidad INE EOH (tabla 2078) | `ine_eoh.py` | ✅ |
| MICE (eventos/participantes/ICCA) | `mice.py` curado con fuentes citadas | ✅ |
| **Índice tensión alquiler/renta** (`housing_tension`) | derivado, idea #4 | ✅ (revisar fórmula — ver §2) |
| **% recogida selectiva** (`recycling_rate`) + viz genérica de indicadores | `IndicatorsSection` reutilizable | ✅ |
| **Indicator store "largo"** con columna `source` | `export_tables.py` → `*_long.csv` | ✅ esquema `barrio_id, periodo, métrica, valor, unidad, fuente` |

### P0 — Fundamentos (COMPLETO ✅)
- **P0.1 ✅** Indicator store alineado: columna `source` añadida a las tablas long.
- **P0.2 ✅** Módulo de join espacial (`spatial.py` + `gis_io.py`):
  point-in-polygon (STRtree), interpolación areal `mean`/`sum`, `rate_per_1000`,
  reproyección **25830→4326** (pyproj, validada) y **lectura SHP** (pyshp).
  Sblocca todas las dimensiones GIS. Primera métrica GIS viva:
  `schools_per_1000`.

**El feedback externo confirma que la arquitectura no debe tocarse.** El cuello
de botella ya no es técnico: es de selección de dimensiones y disciplina causal.

---

## 2. Correcciones metodológicas pendientes (de `FEEDBACK-CONSOLIDADO.md` §6)

Estas no son "datos nuevos": son ajustes a lo que ya existe, acordados por las
cuatro revisiones. Son requisito de credibilidad y van en paralelo a todo.

- **MET-1 — Reformular `housing_tension`.** Hacer el parámetro m²/persona
  **explícito y seleccionable** (20/30/40); mostrar una **familia de medidas**
  (`alquiler/renta`, `z(alquiler)−z(renta)`, `percentil(alquiler)−percentil(renta)`);
  reetiquetar como "presión teórica sobre el residente medio". *(No requiere
  datos nuevos.)*
- **MET-2 — "Índice de Transformación Urbana"** (nombre canónico decidido; nunca
  "gentrificación", porque con los datos actuales no se puede demostrar
  gentrificación — falta rotación de población / sustitución social). Definición
  explícita y **seleccionable** (modo socioeconómico vs. modo presión turística),
  con componentes visibles.
- **MET-3 — Correlaciones robustas como invariante.** Con N=19: añadir Spearman
  junto a Pearson, scatter con/sin outliers, leave-one-out (Erdialdea/Gros),
  correlaciones parciales. Aplica a toda correlación que se publique.
- **MET-4 — Fichas de confianza por indicador** (★ observado / derivado / proxy
  + supuestos). Encaja con la prudencia metodológica ya practicada.
- **MET-5 — Invariantes ya fijadas:** normalizar conteos por población (tasa/1000);
  `% extranjeros` nunca como proxy directo de gentrificación; provenance explícita.

---

## 3. Backlog por tipo de tarea

> Etiquetas: 🟥 P1 (siguiente) · 🟧 P2 · 🟨 P3 · 🟦 P4. Entre corchetes, el sprint
> sugerido (ver §4). Trazabilidad al feedback entre paréntesis.

### A. Recolección de datos

> 📋 **Fuentes verificadas (junio 2026) en `PLAN-RECOLECCION.md`.** REC-1 a REC-4
> confirmadas y accesibles; granularidad de REC-5/6/9 limitada a ciudad/línea
> (ver detalle y caveats allí).

- **REC-1 🟥 [B] Estructura por edad por barrio.** El catálogo `demografia-origen`
  ofrece población por edad y barrio (2000–2025), pero el CSV ya ingerido es solo
  nacionalidad: hay que **descargar el CSV de edad** de la misma fuente y derivar
  **índice de envejecimiento** (pob >64 / pob <15), cuota 25–40 y evolución.
  *Bajo coste* (misma fuente y join), no "ya integrado" (Gemini, Perplexity).
- **REC-2 🟥 [B] Ruido (SHP) por barrio.** Ingerir `ruido-total`/`ruido-noche`
  (EPSG:25830, SHP 2008/2017/2022) vía interpolación areal → dB por barrio. El
  módulo P0.2 ya lo soporta. *Mejor ratio valor/coste* (Perplexity, Gemini,
  DeepSeek).
- **REC-3 🟥 [B] Fiscalidad municipal.** `impuestos_tipo`, `tasas_tipo`,
  `subvenciones` (CSV ciudad, anual). La viz genérica de indicadores ya existe →
  integración casi inmediata.
- **REC-4 🟧 [C] Inside Airbnb (puntos geolocalizados).** Snapshot(s) San
  Sebastián → densidad Airbnb por barrio (join espacial) y, clave, **serie
  temporal por barrio** vía reseñas/mes. Desbloquea presión turística real y el
  lead/lag hoy imposible (DeepSeek "urgente", Gemini).
- **REC-5 🟨 [F] Trabajo / paro / sectores.** SEPE/Eustat. ⚠️ Probablemente solo
  **escala ciudad** (no barrio): integrar como contexto y declararlo (DeepSeek
  nº1, ChatGPT, Perplexity).
- **REC-6 🟨 [F] Movilidad.** DBus por línea/parada, Dbizi. ⚠️ Verificar
  agregabilidad real a barrio antes de prometer coropleta (ChatGPT la nº1,
  Perplexity).
- **REC-7 🟨 [F] Tejido comercial.** Licencias por categoría (IAE/CNAE) o bajos
  vía catastro foral → sustitución comercio residente→turista. Sin dataset
  abierto limpio: requiere proxy (Gemini, ChatGPT, DeepSeek).
- **REC-8 🟦 [F] Catastro Foral de Gipuzkoa** (`gipuzkoairekia.eus`, CSV bulk,
  CC-BY — **NO** el catastro estatal). Parcela → agregación espacial a barrio:
  superficie construida (para m²/persona real de MET-1), valor catastral,
  proxy de venta €/m².
- **REC-9 🟦 [F] Modelos lingüísticos A/B/D (euskera).** Eustat — Censo,
  Características Sociolingüísticas (sección censal → barrio) o Mapa
  Sociolingüístico GV (municipal). Ser pragmático con la granularidad.
- **REC-10 🟦 [F] Ibiltur (Eustat).** Gasto/segmentos, motivo de visita,
  nacionalidad. Tablas Eustat, municipal.
- **REC-X ⛔ DESCARTADA (decisión junio 2026):** **criminalidad por barrio**
  (fuente eliminada + escala sub-municipal blindada). Ver §5.
- **REC-Y ⛔ No hacer:** scraping de Indomio (ToS). Venta €/m² solo vía catastro
  foral agregado (REC-8) o renuncia explícita.

### B. Análisis (sobre datos que YA tenemos — mayor retorno inmediato)

> ✅ **AN-1…AN-5 HECHOS.** Sprint A en `analysis/sprint_a.py`; AN-4/AN-5 en
> `analysis/distribucion_barrios.py`. Resultados en `ANALISIS-SPRINT-A.md`.

- **AN-1 ✅ Correlaciones robustas.** Hechas con Pearson + Spearman (rangos) +
  leave-one-out. Hallazgo más fuerte y robusto: `housing_tension ~ income`
  −0,89 (sin outliers). La tesis `vut_density ~ rent` aguanta (0,62 sin centro).
- **AN-2 ✅ Velocidad / trayectoria de cambio.** Tasas anualizadas 2016→último
  por barrio. Patrón: alquiler sube ~3–4 %/año en todas partes; % extranjeros
  crece más rápido en el este obrero; el centro pierde población.
- **AN-3 ✅ Tipología de barrios.** k-means k=4 (semilla fija) → 4 perfiles
  (central turístico / acomodado / transicional / popular en tensión). Egia es
  el caso "en movimiento". Presentado como perfiles descriptivos (N=13).
- **AN-4 ✅ [A] Matriz niveles vs. variaciones — HECHA.** Cruce nivel × pendiente (p.ej.
  alquiler alto vs. crecimiento de alquiler; renta baja vs. tensión alta).
  Insumo de la coropleta bivariada VIZ-3 (Perplexity, Gemini, ChatGPT).
- **AN-5 ✅ [A] Índices de polarización — HECHA** (Gini territorial estable ~0,10 2016–23; brecha no se ensancha). Gini inter-barrio y ratio P90/P10 de
  renta por año → ¿se ensancha la brecha Aiete↔Altza? (Gemini).
- **AN-6 🟧 [C] Lead/lag y shift-share.** Tras REC-4: ¿la presión turística
  *precede* a la subida de alquileres? Descomposición shift-share del alza
  (componente ciudad vs. local). ⚠️ Hoy bloqueado por falta de VUT histórico
  (DeepSeek, Gemini, ChatGPT).
- **AN-7 🟨 [A] PCA exploratorio.** Diagnóstico interno de qué dimensiones
  explican Donostia. Uso interno, no output público (ChatGPT; cautela propia).
- **AN-8 🟢 [D] Índice de Transformación Urbana — versión exploratoria HECHA.**
  Código `analysis/transformation_index.py`; resultados en
  `INDICE-TRANSFORMACION.md`. Multi-definición (modo socioeconómico estilo
  Freeman + modo presión turística), componentes visibles, clasificación
  categórica. Hallazgo: las dos geografías **no coinciden** (turismo en el centro
  acomodado; transformación social en Loiola/Egia). *Pendiente consolidar* con
  edad (REC-1), ruido (REC-2) y Airbnb/temporal (REC-4); y exponer en frontend
  (VIZ-6).

### C. Visualización

- **VIZ-1 ✅ [A] Vista de "velocidad de cambio" — HECHA.** Coropleta de tasas
  anualizadas (escala divergente, azul=baja / rojo=sube) por barrio para renta,
  alquiler, población, % universitarios y % extranjeros. Implementada como
  **métricas derivadas** (`datasets/change_velocity.py`, `velocity_*`), así que
  reutiliza el choropleth/leyenda existentes sin vista nueva; aparecen en el
  selector bajo "Velocità di cambiamento". Valores reproducen AN-2 (p.ej. alquiler
  Loiola +4,3 %/año; % extranjeros Intxaurrondo +0,92 p.p./año; población
  Gros −0,60 %/año).
- **VIZ-2 ✅ [A] Vista de perfiles/clusters — HECHA.** Métrica categórica
  `barrio_profile` (`datasets/barrio_profiles.py`): coropleta por perfil con
  paleta cualitativa + leyenda de swatches. Introduce el **tipo de métrica
  `categorical`** en el contrato (model + frontend: colorScale, Legend, tooltip),
  reutilizable por VIZ-6. Reproduce la asignación documentada de AN-3
  (Erdialdea/Gros = central turístico; Aiete/Antigua/Ibaeta = acomodado;
  Egia/Amara/Ategorrieta = transicional; Altza/Intxaurrondo/Loiola/Martutene/
  Mirakruz = popular en tensión), fijada por test. *Pendiente opcional:* ver el
  cambio de cluster en el tiempo.
- **VIZ-3 🟧 [A] Coropleta bivariada 3×3.** Cruza dos métricas (renta × tensión)
  para resaltar barrios anómalos (AN-4).
- **VIZ-4 🟧 [B] Selector de parámetro en `housing_tension`** (20/30/40 m²) +
  panel de "familia de medidas" (MET-1).
- **VIZ-5 🟧 [B] Coropleta de ruido nocturno por barrio** + overlay sobre
  densidad VUT/Airbnb (REC-2 + REC-4) — relato turismo↔ruido en Parte Vieja/Gros.
- **VIZ-6 🟨 [D] Dashboard del Índice de Transformación** (3 mapas en paralelo:
  presión inmobiliaria / cambio demográfico / presión turística + índice
  sintético opcional, definición seleccionable) (AN-8; DeepSeek).
- **VIZ-7 🟨 [D] Fichas de confianza** por indicador en la UI (MET-4).
- **VIZ-8 🟦 [E] Dimensión temporal protagonista.** Small multiples por año +
  botón "play" animado; opcional 3D extrusion (idea #2).
- **VIZ-9 🟦 [E] Scrollytelling** (Scrollama) — **solo tras Sprints A–D**.
- **VIZ-10 🟦 [E] "Ciudad turística vs. ciudad vivida"** — dos mapas en paralelo;
  requiere servicios GIS (idea #5).

### D. Documentación (insights, correlaciones, causas, conclusiones, evolución)

> El objetivo del proyecto: convertir los datos en **relatos** sobre la evolución
> de la ciudad. Cada tarea aquí produce texto reproducible para `INSIGHTS.md` y,
> al final, los *outputs* narrativos.

- **DOC-1 ✅ [A] HECHO** — hallazgos de AN-1/AN-2/AN-3 documentados en
  `ANALISIS-SPRINT-A.md` (correlaciones robustas, velocidades, perfiles, con
  distinción explícita correlación/causa). *Pendiente menor:* fundir un resumen
  en `INSIGHTS.md` (está en italiano; decidir si se migra a español).
- **DOC-2 ✅ [A] Nota metodológica — HECHA** (`NOTA-METODOLOGICA.md`): de las correcciones MET-1…MET-4 (por qué se
  reformula la tensión, por qué "transformación" y no "gentrificación").
- **DOC-3 🟧 [B/C] Fichas de fuente y supuestos** por dimensión nueva (edad,
  ruido, fiscalidad, Airbnb) en `SOURCES.md`, con nivel de confianza.
- **DOC-4 ✅ [D] Documento de "tesis de la ciudad" — HECHO** (`TESIS-CIUDAD.md`). Integrar señales en una
  lectura causal cauta: touristificación concentrada → presión inmobiliaria →
  tensión máxima en barrios obreros del este; clima que se calienta; etc.
  (amplía la tesis ya esbozada en `INSIGHTS.md`).
- **DOC-5 ✅ [D/E] Guion de los outputs narrativos — HECHO** (`GUION-OUTPUTS.md`) (ver §6): para cada relato,
  la pregunta que responde, las métricas/vistas que usa y la conclusión.
- **DOC-6 🟦 [F] Working paper metodológico** (opcional, DeepSeek): pipeline,
  supuestos e índice compuesto, publicable en sitio personal/arXiv.

---

## 4. Roadmap de sprints

| Sprint | Foco | Tareas | Por qué |
|---|---|---|---|
| **A** | Análisis y relato sobre datos existentes | AN-1, AN-2, AN-3, AN-4, AN-5, AN-7, VIZ-1, VIZ-2, VIZ-3, DOC-1, DOC-2 | Coste casi nulo, sin datos nuevos, relato inmediato |
| **B** | Datos de bajo coste / alto valor | REC-1 (edad), REC-2 (ruido), REC-3 (fiscalidad), MET-1, VIZ-4, VIZ-5, DOC-3 | Quick wins reales; cierran las lagunas más baratas |
| **C** | Presión turística real + tiempo | REC-4 (Inside Airbnb), AN-6 (lead/lag, shift-share) | Desbloquea el análisis temporal hoy imposible |
| **D** | Índice de Transformación Urbana | AN-8, MET-2, VIZ-6, VIZ-7, DOC-4, DOC-5 | Llega cuando el perímetro es completo y defendible |
| **E** | Narrativa | VIZ-8, VIZ-9, VIZ-10 | El envoltorio, una vez sólido el contenido |
| **F** | Dimensiones difíciles | REC-5…REC-10, DOC-6 | Coste alto / granularidad limitada; cuando aporten más que cuesten |

---

## 5. Descartado / despriorizado (decisiones explícitas)

- **Criminalidad por barrio — DESCARTADA formalmente (decisión junio 2026):**
  fuente eliminada del catálogo + escala sub-municipal blindada por protección de
  datos. Alternativas solo municipales (MIR) o proxies (quejas ciudadanas,
  locales vacíos). No se invierte esfuerzo en buscar un equivalente por barrio.
- **Precios de venta €/m² por barrio** — solo vía catastro foral agregado
  (REC-8) o **renuncia explícita**. Nunca scraping de Indomio/Idealista (ToS).
- **Scrollytelling temprano** — no, hasta cerrar Sprints A–D.
- **"Índice de gentrificación" como caja negra** — reencuadrar a Transformación
  Urbana, multi-definición, componentes visibles (MET-2).
- **Lead/lag con VUT histórico** — imposible hoy (VUT es snapshot); esperar a
  Inside Airbnb (REC-4 → AN-6).

---

## 6. Outputs narrativos objetivo (la meta final)

Los relatos que el proyecto debe poder contar al final, cada uno como una vista o
pieza con una pregunta de partida (framing "máquina de preguntas", ChatGPT):

1. **"La ciudad que se encarece"** — touristificación concentrada (Erdialdea/Gros)
   → presión inmobiliaria → tensión máxima en barrios obreros del este (Altza,
   Egia, Intxaurrondo). *Datos ya disponibles.* (MET-1, VIZ-3, DOC-4)
2. **"Qué barrios cambian más rápido"** — mapa de velocidades + perfiles/clusters.
   *Datos ya disponibles.* (AN-2, AN-3, VIZ-1, VIZ-2)
3. **"Quién vive Donostia"** — estructura por edad y su evolución; ¿sustitución
   residencial? (REC-1)
4. **"El clima cambia"** — calentamiento +0,31 °C/década, más días ≥30 °C.
   *Ya sólido* — empaquetar como relato. (DOC-5)
5. **"La ciudad turística vs. la ciudad vivida"** — contraste espacial de usos.
   (REC-4, VIZ-5, VIZ-10)
6. **"Donostia en transformación"** — el Índice de Transformación Urbana como
   síntesis, con definición seleccionable y componentes a la vista. (AN-8, VIZ-6)
