# Session handoff — 2026-07-03 (perfil migratorio y de empleo, REC-21/AN-21)

> Sigue a `session-handoff-2026-07-02d.md`. Petición directa del usuario, no
> del backlog: recoger datos de extranjeros (cuota, país de origen, empleo)
> y de empleo general (ocupación, comparación con España en investigación)
> por barrio y ciudad, para contrastar su intuición sobre qué tipología de
> extranjero atrae Donostia. Rama `claude/donostia-foreign-employment-data-14000l`,
> **2 commits, pusheada, sin PR abierta todavía** — el usuario va a mergear
> manualmente. El siguiente turno es **Cowork**: integración narrativa, abajo.

## Qué se hizo

Dos commits: primero el análisis exploratorio, después su cableado al
pipeline (a petición del usuario, "puedes implementar el análisis").

### Commit 1 — análisis exploratorio (`analysis/perfil_extranjeros_empleo.py`)

- **País de origen por barrio** (`demografianacionalidadbarrio.csv`, el
  mismo recurso que ya alimentaba `pct_foreign`, sin agregar): 57 países,
  2000–2025, agrupados en 8 regiones de origen (América Latina, Norte de
  África, África subsahariana, Europa occidental, Europa del Este, Oriente
  Medio, Asia oriental/meridional, Norteamérica/Oceanía).
- **Hallazgo central**: dentro de "% extranjeros" conviven dos poblaciones
  que se mueven en sentido **opuesto** con la renta del barrio — América
  Latina r=−0,69, Europa occidental r=+0,24 (y +0,59 con % universitarios).
  Confirma cuantitativamente la advertencia ética que el proyecto ya tenía
  (MET-5, `NOTA-METODOLOGICA.md`), pero ahora con el desglose que faltaba.
- **7 tablas nuevas de Eustat (PxWeb)**, grano Gipuzkoa/C.A. de Euskadi
  (Donostia no tiene EPA propia): actividad laboral por continente,
  tasas de paro por nacionalidad, ocupación CNO-11, personal I+D,
  establecimientos por sector A10 en Donostia, renta por profesión.
  Confirma la intuición de "mucha más investigación que España": Gipuzkoa
  **31 ‰** de ocupados en I+D vs. **13,6 ‰** España (INE 2024).
- **Límite documentado explícitamente**: no existe en ningún sitio de la
  estadística pública española (ni INE ni Eustat, catálogo de 2.321 tablas
  revisado entero) un cruce nacionalidad×ocupación×salario a grano
  municipal ni provincial. No se rellenó con un proxy — se dejó como vacío
  declarado.
- Detalle completo, con todas las tablas y la lectura punto por punto de la
  hipótesis del usuario, en `docs/intermedia/ANALISIS-EXTRANJEROS-EMPLEO.md`.
  9 tests (`analysis/tests/test_perfil_extranjeros_empleo.py`).

### Commit 2 — cableado al pipeline (a petición del usuario)

- **`datasets/demografia_origen_region.py`** → 8 métricas coropléticas
  nuevas `pct_origin_*` (barrio×año, 2000–2025). Reutiliza el `demo_barrio.csv`
  que ya tenía el pipeline — **sin descarga adicional**. Registrado en
  `build.DATASETS`, confianza/supuestos en `provenance.py`.
- **`datasets/empleo_nacionalidad_gipuzkoa.py`** → 3 indicadores de ciudad:
  `unemployment_rate_spanish_gipuzkoa` / `_foreign_gipuzkoa` (paro por
  nacionalidad, Gipuzkoa, 2015–2026) y
  `randd_personnel_per_1000_employed_gipuzkoa` (Gipuzkoa, 2001–2024). Tres
  queries Eustat PxWeb nuevas en `build.py`
  (`ensure_eustat_empleo_nacionalidad`).
- **Ocupación CNO-11, establecimientos por sector A10 y renta por
  profesión se quedaron analysis-only a propósito**: son desgloses
  multi-categoría por año, no encajan en `Metric` (coroplético, un valor)
  ni `Indicator` (un valor por año) sin forzar el modelo.
- 12 tests nuevos (`test_demografia_origen_region.py`,
  `test_empleo_nacionalidad_gipuzkoa.py`).
- **Pipeline ejecutado end-to-end de verdad** (no solo tests): `python -m
  donostia_pipeline.build` completo, con red — 35 métricas + 28 indicadores
  (antes 27 + 25). AEMET incluido (la clave ya estaba en el entorno).
- **Verificado en navegador** (Playwright contra el Chromium preinstalado,
  `npm run dev` + capturas): el picker de métricas lista las 8
  "Popolazione di origine…", la coropleta pinta con la fuente/confianza
  correctas, y el panel "Altri indicatori cittadini" muestra los 3
  indicadores nuevos con los valores esperados (paro español 4,3 %,
  extranjero 9,4 %, I+D 31 ‰ — coinciden exactamente con el análisis).
- Efecto colateral benigno: `npm install` sincronizó `web/package-lock.json`
  quitando una entrada huérfana de `playwright` (estaba en el lockfile sin
  estar en `package.json`, de alguna sesión anterior).
- `FUENTES.md`, `SOURCES.md`, `descargar_raw.sh`, `BACKLOG.md` y el propio
  `ANALISIS-EXTRANJEROS-EMPLEO.md` (§4 reescrita) actualizados para reflejar
  qué quedó wireado y qué sigue siendo analysis-only.

## Tareas que esta sesión deja a Cowork (próxima sesión)

1. **Ficha de país** en el detalle de barrio: top-5 países de origen con su
   evolución a 10 años (`analysis/output/extranjeros_top_paises.csv` ya
   calculado; falta decidir si entra en `web/` o solo en el relato).
2. **Séptima historia** para `output/historias.html`: "quién trabaja
   Donostia" — el mapa de origen por región (ya wireado) + renta/estudios
   (ya en la app) + el gradiente ocupación→salario (§2.2–2.3 del análisis,
   necesitaría un gráfico propio, esos datos no son coropléticos). El aviso
   de MET-5 (no leer origen como proxy de nada) va en el texto, no solo en
   la ficha — mismo criterio que ya aplica el proyecto a `% extranjeros`.
3. **`resumen.md` / `TESIS-CIUDAD.md`**: aún no mencionan REC-21; si se
   narra, es la primera vez que el proyecto separa el origen migratorio en
   perfiles económicos vs. cualificados en vez de un agregado.

## Pendiente que queda a Code (si se retoma)

- Nada bloqueante. Si se quiere ir más allá: **REC-15/16/18/19/20** del
  backlog general siguen ⬜ (no tocados esta sesión).
- Posible mejora menor: los 3 indicadores de I+D/paro por nacionalidad son
  Gipuzkoa, no Donostia — si algún día Eustat publica la EPA vasca a grano
  municipal (poco probable, tamaño muestral), sustituir sin cambiar el
  contrato (mismos ids).

## Gotchas de la sesión

- **La descarga sí funciona desde este entorno** (`curl` a Donostia Open
  Data / Eustat / INE, sin proxy issues) — contradice la nota de
  `descargar_raw.sh` sobre que Cowork no puede descargar. Puede ser una
  diferencia entre el sandbox de Cowork "clásico" y este entorno de
  ejecución remota; dejar la nota como está por si aplica a otros modos.
- **PxWeb (Eustat) es un catálogo plano de 2.321 tablas** vía
  `GET .../bankupx/api/v1/es/DB/`, sin jerarquía de carpetas — buscar por
  palabra clave en el JSON completo es más rápido que navegar. Los códigos
  de columna (`territorio histórico`, `nacionalidad`, etc.) hay que
  mandarlos tal cual, con tildes, en el POST.
- Dos tablas de Eustat tienen unidades distintas y no lo dicen en el título:
  `cpra_tab04` (población ocupada) viene en **miles**, `empa_po38`
  (ocupados por CNO-11) viene en **personas** — se verificó por orden de
  magnitud (la suma de categorías cuadra con el total). Documentado en el
  docstring de cada loader.
- Bug propio detectado y corregido en la propia sesión: un `.replace(",",
  ".")` aplicado a un f-string concatenado corrompía nombres de sector con
  comas de verdad ("Comercio, transporte y hostelería" → "Comercio.
  transporte…"). Solucionado con un helper `miles()` aplicado solo al
  número, nunca a la cadena completa.
- Las etiquetas de `Metric`/`Indicator` siguen en **italiano** en todo el
  pipeline (convención heredada, no touched — ver `provenance.py`,
  `demografia.py`, etc.); las 8 métricas y 3 indicadores nuevos siguen esa
  convención para no romper la coherencia del picker.

## Estado git

Rama `claude/donostia-foreign-employment-data-14000l`, 2 commits por encima
de `main` (`7a70751` análisis, `7ec1619` cableado al pipeline), pusheada a
`origin`. **Sin PR abierta** — pendiente de que el usuario la abra/mergee.
Tests en verde: pipeline 170 (158 previos + 12 nuevos), web 47, analysis 9
nuevos. `web/`, pipeline y datos generados (`web/src/data/`,
`datos/procesado/tablas/`) todos tocados y regenerados de verdad, no a mano.
