# Session handoff — 2026-07-02 (d) (Code, datos nuevos REC)

> Cuarta sesión del día (sigue a `session-handoff-2026-07-02c.md`). Cierra
> las 5 tareas que la sesión (c) dejaba a Code. El siguiente turno es
> **Cowork**: integración narrativa, abajo.

## Qué se hizo (PR #9, mergeada a main, CI en verde)

Las cuatro adquisiciones de datos priorizadas + la opcional, todas con TDD
(pipeline 145 ✓ · analysis 107 ✓ · web 47 ✓):

- **REC-12 → pipeline.** Registro REATE (Open Data Euskadi, viviendas +
  habitaciones de uso turístico con fecha de alta) → `vut_licenses_new`,
  `vut_licenses_cumulative`, `vut_plazas_cumulative` (ciudad, 2016–2025).
  ⚠️ Snapshot vivo: **las bajas no se publican** → curvas de licencias
  *supervivientes* (el caveat viaja en el `source` de cada punto). Las altas
  caen de 300/año (2017) a 18 (2025).
- **REC-17 → pipeline, H4 completada.** La matriz O-D municipio×municipio
  **no existe** en el banco PxWeb de Eustat (catálogo completo revisado,
  2.321 tablas). Cableado lo que hay: EMPA mt02 + EME me02 (lugar de
  trabajo/estudio categórico, 2021–2024) y DIRAE est07 (empleo localizado,
  1995–2025) → 4 indicadores; el derivado `job_concentration_ratio` da
  **1,20 (2024)**: la ciudad importa trabajadores. La mitad coja de H4
  ("sin dejar de concentrar actividad") ya tiene dato.
- **REC-13 → análisis, MET-7 con número.** 8 snapshots trimestrales de
  Inside Airbnb (2023-12-29 → 2025-09-29; los 8 anteriores hasta 2021-12-30
  dan 403, solo data request): oferta activa **+2,0 %** vs reseñas-12m
  **+20,2 %** — el proxy de reseñas exagera el crecimiento de oferta
  **×1,18**. Y una huella de purga: % con licencia declarada 58,5→84,5 %
  con −10 % de activos en 2025. `ANALISIS-INFERENCIAL.md` §REC-13.
- **REC-14 → análisis.** Isla de calor con 45 escenas de verano Landsat 8/9
  (2015–2025, Planetary Computer, acceso anónimo): **Gros +4,8 °C, Amara
  Berri +4,3, Egia +4,1** sobre la media de ciudad; anillo verde −3…−5 °C.
  El mapa térmico coincide con el este denso de "la presión recae en el
  este". `ANALISIS-INFERENCIAL.md` §REC-14.
- **Port del SVG de AN-18**: `trajectories.py --svg` regenera el connected
  scatter de la historia #6, **byte-idéntico** al inline publicado.

Catálogos sincronizados en la misma PR: `FUENTES.md`, `descargar_raw.sh`,
`SOURCES.md`, `datos.html`, BACKLOG.

## Tareas que esta sesión deja a Cowork (priorizadas)

1. **Integración narrativa de REC-12/13/14/17** (ya en BACKLOG):
   - Historia #5 + ficha del proxy Airbnb: el MET-7 cuantificado (×1,18) y
     la purga de 2025 (licencias 58→85 %, activos −10 %); las altas REATE
     desplomándose (300→18/año) rima con "cráter, no cambio de régimen".
   - Epílogo / hipótesis 4: el ratio de concentración de empleo 1,20 cierra
     la mitad que faltaba de H4 (la pérdida es vegetativa *y* la actividad
     sigue concentrada).
   - Historia #4: la dimensión espacial del clima (Gros +4,8 °C); candidata
     a coropleta `lst_anomaly` si se quiere en la app.
2. **Pasada de coherencia de la historia #5** (pendiente de la sesión c,
   ahora con más motivo: entrará material nuevo).
3. **Accesibilidad de las visualizaciones** (pendiente heredado).

## Pendiente que queda a Code (próxima sesión)

- **Reabrir H1 con la curva REATE** (el porqué de REC-12): lead/lag
  licencias→alquiler. Ojo: T≈9 anual a nivel ciudad — valorar esperar más
  serie o buscar grano trimestral antes de repetir AN-16.
- Los REC-15/16/18/19/20 siguen ⬜ en el BACKLOG.

## Gotchas de la sesión

- **AEMET**: la variable de entorno ya se llama `AEMET_API_KEY` (el typo
  `AEMET_APY_KEY` que anotaba la sesión b está corregido en la config del
  entorno; el pipeline la encontró sin export manual).
- `heat_island.py` necesita `pip install rasterio pyproj` (solo ese script;
  lazy imports para no romper el CI). Cachea recortes en
  `datos/input/raw/heat_island/` (gitignored).
- Los snapshots de Inside Airbnb usan el CSV resumen
  (`visualisations/listings.csv`), no los `data/*.gz` completos; el campo
  `license` es autodeclarado (señal, no censo).
- Las fechas de los 8 snapshots antiguos (2021–2023, hoy 403) quedan
  listadas en `airbnb_snapshots.py` por si algún día se piden a Inside
  Airbnb vía data request.

## Estado git

`main` al día tras la PR #9 (6 commits de trabajo + este handoff en PR
aparte). Sin tocar: `web/` (los indicadores nuevos se renderizan solos vía
`IndicatorsSection`), relatos (`historias.html` solo esperó a Cowork).
