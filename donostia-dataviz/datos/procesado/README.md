# datos/procesado/

Aquí vivirán los **datos procesados** por el pipeline. Hoy están vacíos a
propósito: el código (pipeline, web y tests) los lee de sus rutas originales, así
que **mover los ficheros aquí es una tarea de Code**, no de documentación.

Cuándo esté hecho (ver BACKLOG → Code), esta carpeta agrupará:

| Origen actual | Contenido | Lo lee |
|---|---|---|
| `../../data/*.csv` | tablas tidy (metrics/series/indicators en formato long) + `barrios.csv` | `analysis/*.py` |
| `../../web/src/data/*.json` | métricas y series para la web (una por fichero) + `barrios.geojson` | `web/src/lib/data.ts` |
| `../../analysis/output/*.csv` | salidas de análisis (correlaciones, clusters, índice de transformación, velocity) | reproducibles con `analysis/*.py` (gitignored) |

Mover esto exige actualizar rutas en `data-pipeline/.../config.py` y `build.py`,
`analysis/*.py`, `web/src/lib/data.ts` y los tests, y dejar el CI en verde.
Mientras tanto, la fuente de verdad son las rutas originales.
