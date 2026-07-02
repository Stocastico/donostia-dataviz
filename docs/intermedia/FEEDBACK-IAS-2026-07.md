# Feedback de revisión externa (jul-2026) — consolidación y decisiones

> **Qué es.** Tres IAs (ChatGPT, DeepSeek, Gemini) revisaron `output/resumen.md`
> en julio de 2026. Este documento consolida sus observaciones, registra **qué se
> acepta, qué se descarta y por qué**, y mapea cada punto aceptado a una tarea del
> `BACKLOG.md`. Sustituye a las notas sueltas; los textos originales no se
> versionan (ficheros de chat).
>
> Valoración global de las tres: proyecto sólido (~8,5–9/10), rigor y cautela por
> encima de lo habitual. Lo que falta no son más gráficos sino **inferencia
> (incertidumbre, sensibilidad, tipologías)** y **cohesión narrativa**.

---

## 1. Consenso entre las tres revisiones

| Tema | Quién | Decisión |
|---|---|---|
| El índice AN-8 con pesos iguales es arbitrario; hace falta análisis de sensibilidad (permutación de pesos, 60/40, PCA como contraste) | las tres | ✅ Aceptado → **AN-9** (Code) |
| El proxy de reseñas Airbnb arrastra **sesgo de adopción de plataforma**: parte del ×6 vs ×1,6 hotelero es migración de canal, no más turistas | las tres | ✅ Aceptado → caveat aplicado ya (MET-7, historias #5, resumen) + triangulación → **REC-12/REC-13** (Code) |
| Clustering / tipologías de barrio como visualización de alto impacto | ChatGPT, DeepSeek | ✅ Aceptado con matiz: ya existe `barrio_profile` (k-means k=4, historia #2). Lo nuevo es refinarlo (jerárquico, silhouette, dendrograma) y darle protagonismo → **AN-11** (Code) |

## 2. Correcciones de encuadre (aplicadas en jul-2026, Cowork)

Estas no requerían datos nuevos, solo honestidad adicional. **Hechas**:

- **Falacia ecológica** (DeepSeek): las correlaciones son entre barrios (N=13),
  no entre personas. En particular tensión↔extranjeros (0,74) no dice nada de
  hogares individuales. → Nuevo **MET-6**; aviso en historias #1 y en `resumen.md`.
- **El centro ya estaba envejecido antes del boom turístico** (DeepSeek): la
  historia #3 podía leerse como "el turismo envejece el centro". El envejecimiento
  del centro es anterior (2000→) y común a muchas ciudades europeas; el turismo se
  implanta sobre una estructura demográfica preexistente, no la crea. → Caveat en
  historia #3 y `TESIS-CIUDAD`.
- **El Gini territorial solo mide desigualdad *entre* barrios** (Gemini): si las
  rentas bajas salen de la ciudad, el Gini interno puede mantenerse estable
  creando una ilusión de equidad. → Caveat en historia #1, `TESIS-CIUDAD` y
  `resumen.md`.
- **"Quién puede permitirse vivir dónde" es sugerencia, no hecho** (DeepSeek):
  sin microdatos de movilidad residencial no se puede afirmar desplazamiento. La
  tesis ya lo decía en "qué no se puede afirmar"; ahora la propia frase-tesis
  lleva el matiz.
- **Estado ≠ cambio ≠ trayectoria** (ChatGPT): distinguir explícitamente cuándo
  un relato habla de la foto actual, de la velocidad o del recorrido. → **MET-8**.
- **Supuesto 30 m²/persona y tamaño del hogar** (Gemini): el tamaño medio del
  hogar varía por demografía del barrio (hogares de 1–2 personas en el centro
  envejecido, posible hacinamiento en el este), lo que puede sesgar la tensión
  calculada por barrio. → Ampliación del caveat en MET-1; sustituir el supuesto
  por superficie/hogar real sigue dependiendo de REC-8 (catastro).
- **Sección de cierre "Lo que los datos aún no pueden responder"** (ChatGPT):
  añadida a `historias.html` — desplazamiento, causalidad, intra-barrio, adopción
  de plataforma, nivel individual.

## 3. Ampliaciones analíticas aceptadas → backlog Code

| ID | Qué | Origen |
|---|---|---|
| AN-9 | Sensibilidad del índice AN-8: ~1000 permutaciones de pesos + 60/40 y 40/60 + PCA de contraste (frágil con N=13, solo contraste). ¿Loiola y Egia siguen arriba? | las tres |
| AN-10 | Bootstrap IC95 % para las correlaciones clave (r=0,72 → IC 0,48–0,86 cambia la lectura) | ChatGPT |
| AN-11 | Clustering jerárquico + silhouette + dendrograma sobre las métricas de barrio; tipologías narrativas; extra: "barrio más parecido" (matriz de distancias) y ranking de cambio multivariable desde 2016 | ChatGPT, DeepSeek |
| AN-12 | Descomponer la pérdida de población del centro: saldo vegetativo vs migratorio, cruce con Δ% 25–39 (¿éxodo joven?). **El mejor proxy de desplazamiento alcanzable sin microdatos** — responde la pregunta abierta #2 del resumen | Gemini |
| AN-13 | Beta-convergencia entre barrios: `Δindicador ~ α + β·nivel_inicial`; β<0 = convergencia. Refuerza o matiza la tesis de "brecha estable" mejor que el Gini | DeepSeek |
| AN-14 | Estacionalidad turística por barrio (reseñas mensuales 2011–2025): ratio verano/invierno o Gini mensual; rosa de estacionalidad | DeepSeek |
| AN-15 | Estadística espacial: Moran's I global y local (¿los barrios similares se agrupan?) | ChatGPT |
| AN-16 | Blindar AN-6: test de estacionariedad del panel en diferencias (ADF/KPSS) + control macro (IPC, tipos) — sin esto, r(+1)=0,27 podría ser artefacto | DeepSeek, Gemini |
| AN-17 | Red de correlaciones (nodo=variable, arista=correlación robusta): ¿qué variable es "central"? | ChatGPT |
| AN-18 | Trayectorias por barrio 2000→2025 (connected scatter, p.ej. envejecimiento × universitarios) | ChatGPT |
| AN-19 | Regresión múltiple exploratoria alquiler ~ renta + universitarios + Airbnb (¿Airbnb aporta información controlando por renta?; N=13, solo exploratorio) | ChatGPT |
| AN-20 | ¿Cambió el COVID las trayectorias? Comparar tendencia pre/post-2020 (idea RDD, con cautela por N) | DeepSeek |

## 4. Datos nuevos aceptados → backlog Code (REC)

| ID | Qué | Origen |
|---|---|---|
| REC-12 | Histórico del registro VUT (fecha de alta de licencia, Gob. Vasco): curva de oferta legal, independiente del sesgo de adopción — 2ª señal para el lead/lag (cierra el AN-6 refinamiento ya listado) | Gemini |
| REC-13 | Serie de *snapshots* de anuncios activos de Inside Airbnb (vs reseñas): si divergen, cuantificar el sesgo de adopción | DeepSeek |
| REC-14 | Isla de calor superficial por satélite (Landsat/Copernicus, datos abiertos): cruza con la tesis "la presión recae en el este" | Gemini |
| REC-15 | Vivienda protegida / VPO (Observatorio Vasco de Vivienda): ¿la VPO amortigua la tensión? | DeepSeek, ChatGPT |
| REC-16 | Tipología comercial vía OpenStreetMap (histórico): ¿comercio de barrio → servicios turísticos? Complementa REC-7 (que es ciudad, no barrio) | Gemini, ChatGPT |
| REC-17 | Matrices origen-destino de Eustat (commuting): reactiva el eje movilidad tras la baja de la fuente DBus (REC-6) | DeepSeek, Gemini |
| REC-18 | Equipamientos ampliados (salud, bibliotecas, zonas verdes) → índice de accesibilidad por barrio, cruzado con renta/tensión | DeepSeek, ChatGPT |
| REC-19 | Encuestas municipales de percepción/satisfacción vecinal (capa subjetiva) | DeepSeek |
| REC-20 | Cajón de ideas de menor prioridad: licencias de obra/rehabilitación, matrícula escolar por centro, vegetación/arbolado satelital | ChatGPT |

## 5. Descartado o matizado

- **Transacciones inmobiliarias (compraventa €/m²)** (ChatGPT): ya descartado en
  el backlog — solo sería viable vía catastro foral (REC-8, aparcado); nunca
  scraping de portales (ToS).
- **PCA como método principal de pesos del AN-8** (Gemini): con N=13 un PCA es
  frágil (lo admite DeepSeek). Se usa solo como **contraste** dentro de AN-9; la
  credibilidad se gana con permutaciones de pesos.
- **"Indicador sintético de presión compuesta"** (DeepSeek §3.4): choca con la
  decisión firme de no crear índices caja-negra; los componentes del AN-8 ya
  están a la vista. No se hace.
- **Movilidad vía DBus** (Gemini): fuente dada de baja (verificado en REC-6);
  la vía viable es Eustat OD (REC-17).
- **Reorganización completa de las 6 historias en capítulos** (ChatGPT): aceptada
  como dirección, pero es una reescritura mayor → tarea Cowork pendiente, no un
  parche. Mientras tanto, la sección de cierre nueva ya da un arco común.
