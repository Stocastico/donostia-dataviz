# datos/

Organización de los datos del proyecto, separando **entrada** de **salida**.

```
datos/
├── input/          ← datos de entrada (crudos + curados)
│   ├── mice_donostia.csv     input curado versionado
│   ├── FUENTES.md            manifiesto: origen, URL y qué alimenta cada dataset
│   ├── descargar_raw.sh      script para poblar raw/ (ejecutar en local)
│   └── raw/                  crudos descargados (grandes/binarios; ver FUENTES.md)
└── procesado/      ← datos ya procesados por el pipeline (ver README interno)
```

- **`input/`** — todo lo que entra al pipeline. Solo el MICE curado está
  versionado; el resto son descargas públicas documentadas en `FUENTES.md` y
  reproducibles con `descargar_raw.sh` o el pipeline.
- **`procesado/`** — los datos que produce el pipeline (tablas tidy CSV y JSON de
  la web). **Hoy siguen viviendo en sus rutas originales** (`../data/`,
  `../web/src/data/`, `../analysis/output/`) porque el código las lee de ahí;
  moverlas físicamente aquí es una **tarea de Code** (actualizar rutas + tests).
  Ver `procesado/README.md` y el BACKLOG.
