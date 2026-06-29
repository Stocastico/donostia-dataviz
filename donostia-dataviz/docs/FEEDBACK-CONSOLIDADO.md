# Feedback consolidado — revisión externa del DATA-HANDOFF

> **Qué es este documento.** Síntesis crítica de las cuatro revisiones externas
> (Gemini, ChatGPT, DeepSeek, Perplexity) sobre `DATA-HANDOFF.md`. No es un
> resumen neutral: marca dónde coinciden, dónde se contradicen, qué está bien
> fundado y qué conviene mirar con escepticismo. Las acciones derivadas se
> trasladan al backlog (`GAP-ANALYSIS.md`).
>
> Fuentes: `uploads/feedback_Gemini.txt`, `feedback_chatGPT.txt`,
> `feedback_deepseek.txt`, `feedback_perplexity.txt` (revisión de junio 2026).

---

## 0. Resumen ejecutivo

Las cuatro revisiones coinciden en un diagnóstico y conviene tomarlo en serio
porque es **independiente y unánime**:

> El proyecto mide muy bien **las presiones y el estado** de los barrios
> (turismo, renta, alquiler, educación) pero todavía mide poco **las fuerzas que
> transforman la ciudad** y **quién la vive**: trabajo, movilidad, edad,
> comercio, ruido. Hay muchas **variables de resultado** y pocas **variables
> explicativas**. La arquitectura (indicator store, geometría única, join
> espacial, procedencia explícita) está más madura que la cobertura temática:
> el cuello de botella ya no es técnico, es **de selección de dimensiones y de
> disciplina causal**.

De ahí salen dos líneas de trabajo, y las dos importan más que "añadir datasets":

1. **Exprimir analíticamente lo que ya hay** (clusters, velocidades de cambio,
   correlaciones robustas, niveles vs. variaciones). Coste casi nulo, no
   requiere datos nuevos, y es lo que convierte la dashboard en un relato.
2. **Cerrar las lagunas de alto valor narrativo** en orden de coste/impacto:
   ruido (módulo GIS ya listo), una dimensión socio-demográfica fuerte
   (edad o trabajo) e Inside Airbnb.

Y un acuerdo unánime sobre lo que **NO** hacer primero: el **scrollytelling**.
Es el envoltorio, no el contenido; va al final.

---

## 1. Consensos fuertes (los cuatro o tres de cuatro)

| Tema | Quién lo dice | Mi valoración |
|---|---|---|
| **No tocar la arquitectura** (indicator store tidy, geometría única, join espacial, provenance) | Los 4 | ✅ Correcto. Es el activo del proyecto. |
| Faltan **variables explicativas**, sobran de resultado | ChatGPT, DeepSeek, Perplexity | ✅ El diagnóstico más importante. |
| **Clustering / tipología de barrios** (4–5 perfiles) | Los 4 | ✅ Alto valor, pero con cautela por N=19 (ver §5). |
| **Correlaciones robustas** (Spearman, sin outliers, N=19 es frágil) | DeepSeek, Perplexity, ChatGPT | ✅ Imprescindible y barato. Hacer ya. |
| **Velocidad / trayectoria de cambio** (pendientes 2016–2023, no solo niveles) | ChatGPT, Perplexity | ✅ Excelente y con datos en casa. |
| **`housing_tension`: el supuesto de 30 m² es débil** | Los 4 | ✅ Cierto; pero ojo con la solución (ver §6). |
| **Renombrar "gentrificación"** y hacer la definición explícita/seleccionable | ChatGPT, DeepSeek, Perplexity | ✅ Muy sólido. Es honestidad metodológica. |
| **Scrollytelling al final**, después de consolidar la base analítica | Los 4 | ✅ Unánime. |
| **Movilidad** es una dimensión ausente clave | ChatGPT (la nº1), Perplexity, Gemini | ✅ Pero ojo a la disponibilidad real del dato por barrio. |
| **Ruido**: mejor ratio valor/coste, fuente ya disponible | Perplexity, Gemini, DeepSeek | ✅ El módulo GIS (P0.2) ya está hecho → es un quick win real. |

---

## 2. Dimensiones faltantes (ordenadas por consenso e impacto)

1. **Movilidad / exposición a flujos** — *la más citada.* ChatGPT la considera
   "la verdadera ausente" (explica valor inmobiliario, presión turística,
   calidad de vida y densidad comercial a la vez). Perplexity la llama la más
   "obvia". Gemini la enmarca como presión antrópica (DBus por parada/línea,
   Dbizi bike-sharing por barrio).
   - ⚠️ **Mi reserva crítica:** el dato de DBus que cita el brief es *anual por
     línea/parada*, no un flujo por barrio limpio. Antes de prometerlo hay que
     verificar que se puede agregar a barrio de forma defendible. Es alto valor
     **si el dato existe a esa granularidad**; si no, degrada a indicador-ciudad.

2. **Trabajo y vulnerabilidad económica** — DeepSeek la pone como **nº1** (el
   "pegamento narrativo": turistificación → precarización estacional →
   desplazamiento). ChatGPT y Perplexity la sitúan entre las top.
   - ⚠️ **Reserva:** paro/empleo por sector raramente está a escala sub-municipal
     abierta. Lo realista es **serie ciudad** (SEPE/Eustat) como contexto, no
     coropleta por barrio. Hay que ser honesto sobre la granularidad.

3. **Estructura por edad / ciclo de vida** — Gemini (índice de vejez, franja
   25–40, saldo migratorio intra-ciudad) y Perplexity (natalidad, cuota
   jóvenes-adultos, "saber quién entra y quién sale") la ven como condición para
   poder hablar de transformación social.
   - ✅ **Mi valoración:** es la de **mejor coste/impacto** de las tres anteriores,
     porque el dataset demográfico que ya usamos (`demografia-origen`,
     2000–2025) muy probablemente trae edad. **Quick win casi gratis.**

4. **Tejido comercial / sustitución de comercio de proximidad** — Gemini,
   ChatGPT y DeepSeek coinciden: el cambio "servicios al residente → servicios
   al turista" (carnicerías/panaderías → souvenirs, hostelería). Proxy posible
   vía licencias por categoría (IAE/CNAE) o catastro de bajos.
   - ⚠️ **Reserva:** no hay dataset abierto limpio de licencias por barrio.
     Requiere proxy (catastro foral, IAE) → coste medio-alto. Narrativamente
     potentísimo, pero no es quick win.

5. **Ruido / calidad ambiental vivida** — Perplexity lo marca como **mejor
   ratio valor/coste** (SHP 2008/2017/2022 ya en el portal, bienal). Gemini
   propone cruzarlo con Inside Airbnb (solapamiento turismo↔ruido nocturno en
   Parte Vieja/Gros). DeepSeek: proxy de conflicto residente-turista.
   - ✅ **Mi valoración:** el módulo de join espacial (P0.2) ya reproyecta
     25830→4326 y lee SHP. **Está técnicamente desbloqueado hoy.** Es el quick
     win más claro de toda la lista de datos nuevos.

6. **Inside Airbnb** — DeepSeek ("urgente", quick win; los VUT legales son solo
   una fracción) y Gemini (prioridad 2). Desbloquea presión turística real,
   densidad por barrio y —clave— **estacionalidad/serie temporal por barrio**
   (reseñas/mes como proxy).
   - ✅ **Mi valoración:** además resuelve un problema que el feedback casi no vio
     (ver §5, lead/lag): hoy **VUT es un *snapshot* sin eje temporal**, así que
     Inside Airbnb es la única vía realista para tener historia de presión
     turística por barrio.

---

## 3. Nuevos análisis sobre los datos que YA tenemos

Esta es la parte de mayor retorno inmediato y la que más alimenta la
"documentación" (insights, correlaciones, causas, evolución temporal).

- **Tipología de barrios por clustering** (k-means / jerárquico) — los 4. Pasar
  de rankings de una variable a **perfiles** ("hub turístico de alta renta",
  "popular en tensión", "residencial acomodado", "transicional"). Ver cómo un
  barrio **cambia de cluster** en el tiempo (p.ej. Egia acercándose a Gros).
- **Correlaciones robustas** — DeepSeek, Perplexity, ChatGPT. Con N=19:
  Spearman junto a Pearson; scatter con y sin outliers; **leave-one-out** (si
  al quitar Erdialdea/Gros el coeficiente se desploma, el mensaje cambia);
  **correlaciones parciales** controlando población/densidad (ChatGPT).
- **Velocidad / trayectoria de cambio** — ChatGPT, Perplexity. Pendientes
  2016–2023 de renta, alquiler, % universitarios, % extranjeros, población.
  Mapear **qué barrio cambia más rápido**, no su valor absoluto.
- **Matriz niveles vs. variaciones** — Perplexity, Gemini, ChatGPT. Un barrio
  puede ser rico sin estar transformándose, o transformarse sin ser aún rico.
  Visualmente: **coropleta bivariada 3×3** (p.ej. renta × esfuerzo de alquiler)
  para resaltar los "anómalos".
- **Lead/lag temporal** — Gemini, ChatGPT, DeepSeek. ¿La densidad VUT *precede*
  a la subida de alquileres?
  - ⚠️ **Reserva crítica fuerte:** esto **hoy no se puede hacer bien**, porque
    VUT es un *snapshot* sin serie histórica. El lead/lag exige VUT histórico,
    que no tenemos. → Refuerza la prioridad de **Inside Airbnb** (reseñas como
    serie temporal). DeepSeek y Perplexity lo intuyen; conviene decirlo claro.
- **Índices de polarización / desigualdad** — Gemini (P90/P10, Gini
  inter-barrio), DeepSeek (descomposición **shift-share** del alza de
  alquileres: componente ciudad vs. componente local; Herfindahl de diversidad
  económica si hay datos de empleo).
- **PCA** — ChatGPT. No para el usuario, sino para entender **qué dimensiones
  explican Donostia** (¿el 80% de la varianza son 2 componentes?).
  - ⚠️ **Reserva:** con 11 métricas y 19 barrios el PCA es exploratorio, no
    concluyente. Útil como diagnóstico interno, no como output público.

---

## 4. Fuentes alternativas para los datos no disponibles (§6a del handoff)

- **Precios de venta €/m²:** unanimidad en **evitar el scraping de Indomio**
  (ToS). Vías, en orden de preferencia:
  1. Agregado municipal oficial — Colegio de Registradores (*Estadística
     Registral Inmobiliaria*, informe trimestral) o **Eustat EOI** (Encuesta de
     Oferta Inmobiliaria). Solo nivel ciudad.
  2. **Catastro Foral de Gipuzkoa** (`gipuzkoairekia.eus`, CC-BY) agregado a
     barrio: valor catastral ≠ precio de mercado, pero da **tendencia relativa
     defendible** por barrio.
  3. **Renuncia explícita** a la métrica de venta hasta tener fuente limpia
     (Perplexity): "un dato más pobre pero defendible vale más que una serie rica
     pero discutible". ✅ Suscribo esta jerarquía.
- **Criminalidad por barrio:** los 4 coinciden en que está **bloqueado**
  (el CSV de la Guardia Municipal ya no está; la escala sub-municipal está
  blindada por protección de datos). Alternativas mencionadas: Portal
  Estadístico de Criminalidad del MIR (solo municipal), Observatorio de
  Convivencia de Euskadi (encuestas de victimización por comarca), o **proxies**
  (quejas y sugerencias ciudadanas — Gemini; locales vacíos/de apuestas vía
  catastro — DeepSeek).
  - ✅ **Mi recomendación (Perplexity):** no malgastar esfuerzo buscando un
    sustituto "equivalente" por barrio. Elegir conscientemente entre renunciar a
    la granularidad o construir un proxy distinto y honesto. **Quitar
    criminalidad del camino crítico.**
- **Modelos lingüísticos (euskera) A/B/D:** unanimidad en que **no está en el
  portal municipal**. Fuente correcta: **Eustat — Censo, Características
  Sociolingüísticas** (hasta sección censal → agregar a barrio con el módulo
  espacial) o el **Mapa Sociolingüístico** del Gobierno Vasco (municipal). Ser
  pragmático: nivel ciudad/centro puede bastar; no forzar una narrativa por
  barrio que la fuente no soporta.

---

## 5. Lectura crítica: dónde matizo al feedback

No todo lo que sugieren las cuatro IAs es igual de sólido. Cuatro matices:

1. **El clustering también es frágil con N=19.** Los cuatro lo recomiendan con
   entusiasmo, pero ninguno avisa de que k-means sobre 19 puntos da clusters
   inestables (dependientes de la semilla y del escalado). Hacerlo, sí, pero:
   presentarlo como **perfiles descriptivos** (no "verdad"), preferir
   jerárquico/visual, fijar semilla, y validar la estabilidad. El mismo N=19 que
   hace frágil a Pearson hace frágil al clustering.

2. **El lead/lag VUT→alquiler no es viable hoy.** (Ver §3.) El feedback lo pide
   sin notar que **no tenemos serie histórica de VUT**. Es la principal razón
   técnica para priorizar Inside Airbnb, no un análisis que se pueda lanzar ya.

3. **La mejora de `housing_tension` que propone Gemini puede no ser ejecutable.**
   Usar renta familiar y tamaño medio de hogar **por barrio** (Ley de Vivienda
   12/2023, umbral 30% renta del hogar) es conceptualmente mejor, pero **exige
   datos de hogar por barrio que probablemente no están abiertos** (la fuente
   actual da renta *per cápita*). La propuesta de ChatGPT (z-score o percentiles)
   y la de Perplexity (parámetro m²/persona **seleccionable** 20/30/40 +
   "familia de medidas") **no requieren datos nuevos** y son ejecutables ya.
   → Empezar por ahí; la versión hogar queda para cuando/si llega el dato.

4. **"Trabajo" y "movilidad" por barrio pueden ser un espejismo de granularidad.**
   DeepSeek y ChatGPT los piden a escala barrio; la realidad española es que
   suelen estar a escala municipal. No prometer coropletas que la fuente no
   sostiene: integrarlos como **contexto-ciudad** y decirlo.

Una observación de producto que sí elevo (la dijo solo ChatGPT pero es muy
buena): **fichas de confianza por indicador** (★ observado / derivado / proxy +
supuestos). Es rarísimo en dashboards públicas y encaja con la prudencia
metodológica que ya practica el proyecto. Y su reencuadre general —pasar de
"Wikipedia cuantitativa de Donostia" a **"una máquina de hacer preguntas"**
(cada vista parte de una pregunta)— es la mejor idea de framing de las cuatro.

---

## 6. Metodología: las dos correcciones acordadas

**`housing_tension`** — debilidad real (supuesto fijo de 30 m²/persona,
*mismatch* entre alquiler de nuevos contratos y renta per cápita de toda la
población). Plan acordado:
- Hacer el parámetro m²/persona **explícito y seleccionable** (20/30/40) →
  muestra la sensibilidad en vez de esconder un supuesto (Perplexity).
- Mostrar una **familia de medidas** convergentes: `alquiler/renta per cápita`,
  `z-score(alquiler) − z-score(renta)`, `percentil(alquiler) − percentil(renta)`
  (ChatGPT). Cuando todas apuntan igual, el mensaje gana credibilidad.
- Reetiquetar como **"presión teórica sobre el residente medio"**, no "% de
  renta que gasta una familia tipo" (Perplexity).
- Métrica complementaria comunicativa: **horas de SMI para un alquiler medio**
  (DeepSeek).

**Gentrificación → "Índice de Transformación Urbana"** — con los datos
disponibles **no se puede demostrar gentrificación** (falta rotación de
población, sustitución social, residencialidad). Plan acordado:
- **Renombrar** a *Urban Change Index* / Índice de Transformación Urbana
  (ChatGPT). Más defendible.
- **Definición explícita y seleccionable**, al menos dos modos (DeepSeek,
  Perplexity): (a) **socioeconómico** (renta, educación, estructura social) y
  (b) **presión turística** (VUT/Airbnb, alquiler, ruido/movilidad).
- Mostrar la **contribución de cada componente** (3 mapas en paralelo + índice
  sintético opcional), no una caja negra de 12 variables (DeepSeek).
- Criterios tipo Freeman como una de las definiciones (Gemini): condición de
  entrada (renta < mediana ciudad en año base) + alza de % universitarios > media
  + alza de alquiler real > media.
- **% extranjeros con cautela ética** (ya documentado): no usarla acríticamente
  como proxy de transformación.

---

## 7. Prioridades reconciliadas

Hay una tensión real entre las cuatro: **Gemini** dice "construye el índice
primero" (insumos ya están, bajo esfuerzo); **ChatGPT, DeepSeek y Perplexity**
dicen "enriquece dimensiones (edad/trabajo/ruido) antes, o el índice saldrá
incompleto". Reconciliación:

- **Los análisis puros (clusters, velocidades, correlaciones robustas, matriz
  niveles/variaciones) van YA**: no necesitan datos nuevos, producen insights y
  no dependen de la discusión anterior. Esto satisface a Gemini sin el riesgo
  que señalan los otros tres.
- **Un índice de transformación EXPLORATORIO** (prueba de concepto con lo que
  hay) puede salir pronto, etiquetado como tal (Gemini + DeepSeek).
- **El índice "consolidado" espera** a integrar al menos edad y ruido
  (Perplexity, DeepSeek).
- **Scrollytelling y narrativa avanzada al final** (unánime).

Roadmap de sprints resultante (detalle accionable en `GAP-ANALYSIS.md`):

| Sprint | Foco | Por qué |
|---|---|---|
| **A** | Análisis sobre datos existentes: correlaciones robustas, velocidades de cambio, perfiles/clusters, matriz niveles-vs-variaciones | Coste casi nulo, no necesita datos nuevos, genera relato inmediato |
| **B** | Datos de bajo coste y alto valor: **ruido** (GIS listo), **edad** (mismo dataset demográfico), **fiscalidad** (viz lista) | Quick wins reales; cierran las lagunas más baratas |
| **C** | **Inside Airbnb** + estacionalidad por barrio + lead/lag con la nueva serie | Desbloquea presión turística real y el análisis temporal imposible hoy |
| **D** | **Índice de Transformación Urbana** (multi-definición, componentes visibles) + fichas de confianza | Llega cuando el perímetro es más completo y defendible |
| **E** | Narrativa: scrollytelling, dimensión temporal (small multiples/play), "ciudad turística vs. vivida" | El envoltorio, una vez sólido el contenido |
| **F** | Dimensiones difíciles: trabajo, comercio, Ibiltur, catastro foral, venta €/m², modelos lingüísticos | Coste alto / granularidad limitada; cuando aporten más que cuesten |

---

## 8. Qué descartar o despriorizar (decisiones explícitas)

> **Adoptado (junio 2026):** criminalidad por barrio **descartada formalmente**;
> el índice se llama **"Índice de Transformación Urbana"** (nunca "gentrificación").

- **Criminalidad por barrio:** descartada formalmente (bloqueada; ver §4).
- **Precios de venta por barrio:** solo vía catastro foral agregado, o renuncia
  explícita. No scraping.
- **Scrollytelling temprano:** no, hasta cerrar Sprints A–D.
- **Índice "de gentrificación" como tal:** no con este nombre ni como caja
  negra; reencuadrar (§6).
- **Lead/lag con VUT histórico:** no es posible hoy; esperar a Inside Airbnb.
