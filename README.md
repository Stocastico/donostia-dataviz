# Donostia Dataviz

Análisis y narrativa de datos sobre la evolución de **Donostia / San Sebastián**,
barrio a barrio: turismo, vivienda, renta, demografía, educación, medio ambiente y
clima. El proyecto combina un **pipeline de datos** reproducible, un **dashboard
interactivo** y, sobre todo, un cuerpo de **documentación y relatos** que convierte
los datos en historias sobre cómo cambia la ciudad.

Este repositorio nació como una rama de
[`Claude-code-experiments`](https://github.com/Stocastico/Claude-code-experiments)
y ahora vive de forma independiente. Todo el proyecto está en el subdirectorio
[`donostia-dataviz/`](donostia-dataviz/) — empieza por su README.

## 🚀 Empieza aquí

1. **[`donostia-dataviz/output/historias.html`](donostia-dataviz/output/historias.html)**
   — el documento narrativo: seis historias con texto y visualizaciones
   interactivas. Autocontenido, ábrelo en cualquier navegador.
2. **[`donostia-dataviz/output/resumen.md`](donostia-dataviz/output/resumen.md)**
   — síntesis del proyecto (datos, análisis, correlaciones e historias) pensada
   para revisión externa, por ejemplo para pegarla a otra IA.
3. **[`donostia-dataviz/README.md`](donostia-dataviz/README.md)** — documentación
   completa del proyecto: cómo navegar el repo, ejecutar el pipeline y el
   dashboard, y mapa de toda la documentación (`docs/`).
4. **[`donostia-dataviz/BACKLOG.md`](donostia-dataviz/BACKLOG.md)** — qué está
   hecho y qué falta, separado en tareas de Cowork (documentación/relatos) y
   Code (pipeline/web/datos).

## Estructura

```
.
├── README.md              ← este fichero
├── LICENSE
├── .github/workflows/      ← CI (tests pipeline Python + build/test frontend)
└── donostia-dataviz/       ← el proyecto completo (código, datos, docs, outputs)
```

## License

See LICENSE file for details.
