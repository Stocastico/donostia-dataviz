# datos/procesado/

Los **datos procesados** por el pipeline. Estado actual:

| Carpeta / origen | Contenido | Lo lee |
|---|---|---|
| `tablas/` (antes `../../data/`) | tablas tidy (metrics/series/indicators en formato long) + `barrios.csv` | `analysis/*.py` |
| `../../web/src/data/*.json` | métricas y series para la web (una por fichero) + `barrios.geojson` | `web/src/lib/data.ts` |
| `../../analysis/output/*.csv` | salidas de análisis (correlaciones, clusters, índice de transformación, velocity) | reproducibles con `analysis/*.py` (gitignored) |

`tablas/` ya vive aquí: `config.TABLES_DIR` (pipeline) y `analysis/*.py` apuntan
a `datos/procesado/tablas/`. `web/src/data/` **se queda donde está**
deliberadamente — Vite carga esos JSON con `import.meta.glob` desde dentro de
`web/src/`, así que sacarlos de ahí complica el dev server sin aportar nada
funcional. `analysis/output/` es gitignored y se regenera con `--save`; no se
ha movido por ser de bajo valor y uso puramente local.
