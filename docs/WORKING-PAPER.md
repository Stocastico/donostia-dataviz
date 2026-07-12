# Working paper — Método de un retrato reproducible de la transformación urbana: Donostia / San Sebastián a escala de barrio (DOC-6)

> **Qué es este documento.** El *working paper* metodológico del proyecto
> Donostia Dataviz (DOC-6): una exposición autocontenida de **cómo** se
> construyó el retrato de la ciudad — datos, supuestos, métricas derivadas,
> estrategia inferencial con N pequeño y límites — pensada para que un lector
> externo pueda **replicar, criticar o reutilizar** el método. No sustituye a
> los documentos operativos (`NOTA-METODOLOGICA.md`, `TESIS-CIUDAD.md`,
> `intermedia/ANALISIS-INFERENCIAL.md`): los sintetiza y los referencia. Todos
> los números citados son reproducibles desde `data-pipeline/` y
> `analysis/*.py`.
>
> **Estado:** cerrado con la regla de parada de jul-2026 (`PLAN-CIERRE.md`).
> La puerta a datos nuevos está congelada; este paper documenta el método con
> el que se llegó al cierre.

---

## Resumen

Con ~20 fuentes de datos abiertos (padrón, alquiler EMA, renta Eustat, Inside
Airbnb, censo VUT, AEMET, Landsat, INE, EPA, registros forales) unificadas
sobre una única geometría de 19 barrios, el proyecto construye 41 métricas por
barrio con *provenance* y nivel de confianza explícitos, y las articula en una
tesis con cuatro hipótesis contrastables. El problema metodológico central es
inferir con **N = 13–19 unidades espaciales**: se resuelve no con un modelo
grande, sino con una batería de comprobaciones baratas y transparentes
(leave-one-out, bootstrap, permutación, efectos fijos, autocorrelación
espacial, análisis de sensibilidad de pesos) y con una **disciplina de
enunciación** — cada afirmación declara si habla de estado, cambio o
trayectoria; cada correlación es de barrios, no de personas; cada fuente
declara si es registro completo, ventana parcial o proxy. El resultado
sustantivo cabe en una frase: la presión turística vive en el centro acomodado
y la presión residencial en el este de renta baja — dos geografías distintas
que un único «índice de gentrificación» habría fundido — mientras la brecha de
renta *entre* barrios permanece estable. El resultado metodológico es el
método mismo: un patrón replicable para retratos municipales con datos
abiertos, incluida la parte que casi nunca se publica — los análisis que
**tumbaron** hallazgos propios (el indicio lead/lag turismo→alquiler no
sobrevivió al control por shocks comunes de año) y las preguntas que los datos
públicos no pueden responder.

---

## 1. Motivación y pregunta

El punto de partida no es «un dashboard con todos los datos de Donostia», sino
una pregunta: **¿cómo se está transformando la ciudad, y sobre quién recaen
las presiones?** La distinción importa porque fija una regla de parada (§9):
un dato entra solo si prueba, matiza o refuta una hipótesis — no porque
exista. El proyecto tiene tres productos: un pipeline reproducible
(`data-pipeline/`), un panel interactivo (`web/`) y — el entregable principal
— un **relato con datos** (`output/historias.html`, siete capítulos en formato
scrollytelling con los supuestos manipulables por el lector).

## 2. La tesis y las hipótesis

La lectura integrada (DOC-4, `TESIS-CIUDAD.md`) se condensa así:

> La touristificación se concentra en el centro acomodado y se asocia a
> alquileres altos, pero la presión de vivienda más dura recae en el este
> obrero, donde las rentas no acompañan; la brecha de renta *entre* barrios no
> se ensancha, así que lo que cambia no es tanto cuánto gana cada zona como
> quién puede permitirse vivir dónde — con el clima calentándose de fondo.

De ella salen cuatro hipótesis explícitas, cada una con sus tests:

- **H1 — La presión turística anticipa el alquiler (~1 año).** *Debilitada dos
  veces* (§6.4): el indicio direccional no sobrevive al control macro (AN-16)
  y la segunda señal independiente (licencias REATE) tampoco lo reabre.
- **H2 — Transformación turística y social siguen geografías distintas.**
  *Reforzada dos veces*: robusta a los pesos del índice (AN-9) y con
  estructura espacial real (Moran's I, AN-15).
- **H3 — La desigualdad territorial permanece estable mientras cambia la
  accesibilidad.** *Reforzada*: la beta-convergencia (AN-13) no encuentra ni
  convergencia ni divergencia; queda declarado lo que el dato no ve
  (desigualdad intra-barrio, quien se marcha).
- **H4 — El centro pierde población sin dejar de concentrar actividad.**
  *Cerrada*: la pérdida es vegetativa, no de expulsión (AN-12), y la
  concentración es real (1,20 empleos localizados por residente ocupado,
  REC-17).

El proyecto se encuadra deliberadamente como **generador de hipótesis**: donde
los datos abiertos no alcanzan, el entregable es la pregunta bien formulada,
no una respuesta forzada.

## 3. Diseño de datos

### 3.1 Una sola geometría, un solo join

Toda fuente se proyecta **una vez, en ingestión**, sobre la geometría oficial
de 19 barrios (`mapa_auzoak`). Los datos puntuales (VUT, Airbnb, escuelas,
salud, promociones de vivienda protegida) entran por join espacial
punto→barrio; los tabulares, por clave de barrio normalizada. Esto elimina la
fuente de error más común en proyectos multi-fuente: joins ad hoc repetidos
con criterios distintos. Existe además una vista **sub-barrio** (censo VUT ×
callejero municipal, 301 calles) que se usa exactamente para lo que la media
de barrio no puede mostrar: los ejes saturados (las 10 calles más cargadas
reúnen el 19 % del censo VUT).

### 3.2 Registro completo, ventana parcial o proxy

Cada fuente se clasifica por su relación con el universo que dice medir. La
auditoría de parcialidad (jul-2026) revisó las ~20 fuentes con una sola
pregunta — *¿registro completo o ventana parcial?* — y obligó a declarar
cuatro parcialidades que faltaban:

| Fuente | Naturaleza | Consecuencia en el texto |
|---|---|---|
| Padrón municipal | registro completo | lectura directa |
| Alquiler EMA | ventana parcial (contratos nuevos con fianza; 6/19 barrios sin dato) | «no se puede afirmar nada» de los barrios sin mercado registrado |
| Inside Airbnb | una plataforma (suelo, no total) | «suelo del alquiler turístico online» |
| INE EOH | solo hoteles | pensiones/apartamentos fuera, dicho en la fuente |
| EPA por nacionalidad | encuesta, submuestras pequeñas | «el orden es robusto; el decimal, no» |
| Promociones Etxebide | ≤~⅓ del solo alquiler protegido | «sus ceros no son ceros de VPO» |
| Reseñas Airbnb | proxy con sesgo de adopción | cuantificado ×1,22 (§5.4) |
| Precios de venta idealista | precios de oferta, no transacción | «un techo de lo que se paga» |

La regla operativa: **un registro parcial no es el universo**, y cuando el
riesgo de sobreinterpretación es alto, el aviso va en el texto del relato, no
solo en la ficha técnica.

### 3.3 Provenance y fichas de confianza

Cada una de las **41 métricas** publicadas lleva, definido en un único módulo
(`data-pipeline/.../provenance.py`) y aplicado centralmente en el build, un
nivel de confianza — **17 observadas, 19 derivadas, 5 proxy** — más la lista
de supuestos (el 30 m²/persona de la presión, el k-means con N=13, el join
punto→barrio…). La UI y el relato muestran la ficha; el lector nunca tiene que
adivinar qué clase de número está mirando.

### 3.4 Reproducibilidad

- Pipeline: `python -m donostia_pipeline.build` regenera todas las tablas
  (formato *long* en `datos/procesado/tablas/`; contrato estable en
  `DATA-CONTRACT.md`).
- Análisis: cada resultado citado tiene script propio en `analysis/*.py`, con
  tests (`analysis/tests/`).
- Relato: `output/historias.html` embebe sus datos en un blob `window.DONO`;
  dos suites de tests (jsdom) verifican el documento publicado —
  `web/tests/historias.test.ts` (estructura, scrollytelling, sincronía de
  controles) y `web/tests/historias-facts.test.ts` (**fact-check**: cada cifra
  citada y derivable del blob se re-deriva y compara a la precisión de la
  cita, contra la desincronización dato↔narrativa).

## 4. Decisiones metodológicas (MET-1…MET-8)

Las ocho reglas que gobiernan el proyecto, con su porqué (detalle en
`NOTA-METODOLOGICA.md`; MET-6…8 proceden de la ronda de revisión externa de
jul-2026):

1. **MET-1 · La presión de vivienda es un índice relativo, no un % de gasto
   familiar.** `alquiler €/m² × 12 × m²/persona ÷ renta pc` descansa en un
   supuesto (m²/persona) que se expone como **control manipulable** (20–50) en
   vez de esconderse, y se acompaña de una familia de medidas (cuota;
   z(alquiler)−z(renta); percentil−percentil). El hallazgo honesto: la familia
   **no converge del todo** — la cuota señala el este de renta baja, los
   desajustes estandarizados iluminan también el centro caro — y esa
   divergencia es información (miden cosas distintas), no un fallo. Egia es el
   único barrio arriba en las tres.
2. **MET-2 · «Transformación», nunca «gentrificación».** Sin rotación de
   residentes no se puede demostrar sustitución; el índice se llama de
   Transformación Urbana, con definiciones múltiples y componentes a la vista.
3. **MET-3 · Correlaciones robustas como invariante.** Con N=13–19 toda r
   publicada lleva Pearson + Spearman + leave-one-out del centro turístico
   (Erdialdea, Gros); si el coeficiente se desploma al quitarlos, se dice.
4. **MET-4 · Fichas de confianza** (observado / derivado / proxy + supuestos)
   en cada métrica (§3.3).
5. **MET-5 · Invariantes:** normalizar per cápita antes de mapear; `%
   extranjeros` **no** es proxy de gentrificación (fuera del centro se asocia a
   *menor* renta: r=−0,58, −0,72 sin el centro); el ruido nocturno **no** es
   proxy de turismo (sus correlaciones con VUT/Airbnb se desmoronan sin el
   centro: mide tráfico).
6. **MET-6 · Falacia ecológica.** Toda correlación es **entre barrios**;
   ninguna autoriza lecturas individuales. El caso delicado
   (tensión ↔ % extranjeros, r=0,74) lleva el aviso en el propio texto.
7. **MET-7 · El proxy de reseñas arrastra sesgo de adopción.** Parte del
   «Airbnb ×6 vs hotel ×1,7» es migración de canal, no turistas nuevos. Se
   cuantificó (§5.4): el proxy exagera el crecimiento de oferta **×1,22**.
8. **MET-8 · Estado ≠ cambio ≠ trayectoria.** Erdialdea encabeza el *estado*
   turístico; Loiola/Egia encabezan el *cambio* social; la *trayectoria*
   2000–2025 añade una tercera lectura. Cada frase del proyecto declara cuál
   de las tres cosas afirma.

## 5. Métricas derivadas centrales

### 5.1 Presión de vivienda (familia MET-1)

Descrita en §4.1. Resultado: esfuerzo máximo en Altza (21,9 %), Egia (21,3 %)
e Intxaurrondo (20,9 %) con el supuesto base; el *ranking* es insensible al
supuesto de m². La correlación esfuerzo↔renta es la más fuerte del sistema
(−0,81; **−0,89** sin el centro): la tensión es, ante todo, renta baja.

### 5.2 Velocidad de cambio

Tasas anualizadas 2016→último año por indicador (%/año o pp/año). Separa la
marea general (alquiler: +3–4 %/año en todas partes) de los movimientos con
geografía (población: Gros −0,60 %/año; % extranjeros: Intxaurrondo +0,92
pp/año).

### 5.3 Índice de Transformación Urbana (AN-8)

Multi-definición y transparente: modo **socioeconómico** (estilo Freeman:
partir por debajo de la mediana y subir más que la media en estudios y
alquiler) y modo **presión turística** (nivel de VUT + Airbnb + alquiler en
z-scores), con los componentes visibles y pesos iguales. Resultado: los dos
modos **no coinciden** (r≈0,25) — Loiola es el único «en transformación»
social (score 1,02) mientras Erdialdea (+2,48) y Gros (+1,39) lideran la
presión turística siendo «consolidados» en lo social. La sensibilidad se
testeó (AN-9, §6.2).

### 5.4 Triangulación del proxy turístico (REC-13/REC-12)

Nueve fotos de anuncios activos de Inside Airbnb (dic-2023→jun-2026) muestran
la **oferta activa plana** (+1,3 %) mientras las reseñas-12m crecían +23,6 %:
leer reseñas como oferta exagera ×1,22. La huella regulatoria es visible: el %
de anuncios con licencia declarada pasó de 58,5 % a 88,5 % mientras los
activos caían −10 % (2025) sin rebote posterior; y las altas nuevas de
licencias del registro REATE caen de 300/año (2017) a 18 (2025). Lo que crece
no es el parque: es la actividad por anuncio.

### 5.5 Dimensión espacial del clima (REC-14)

A la serie de Igeldo (1981–2025: +0,31 °C/década, R²=0,39; días ≥30 °C
+0,81/década; máxima 39,7 °C en 2022) se añade la anomalía de temperatura
superficial por barrio (45 escenas de verano Landsat 8/9, banda térmica 30 m,
2015–2025): **Gros +4,8 °C**, Amara Berri +4,3, Egia +4,1 sobre la media de
ciudad; el anillo verde queda 3–5 °C por debajo. Es un rasgo estructural de la
morfología urbana (superficie, mediodía), no una tendencia — y su mapa
coincide con el este denso donde carga la presión residencial.

## 6. Estrategia inferencial con N pequeño

La restricción dura del proyecto: 13–19 unidades. La respuesta no es un modelo
multivariante ambicioso (AN-19 lo confirma: con N=13, añadir Airbnb a
renta+universitarios no aporta información sobre el alquiler), sino
comprobaciones simples, cada una atacando un modo de fallo concreto:

### 6.1 Robustez de correlaciones (MET-3, AN-10)
Pearson + Spearman + leave-one-out sistemático + IC bootstrap. Ejemplo: VUT↔
alquiler r=0,64 (IC95 % bootstrap 0,42–0,87; 0,62 sin Erdialdea/Gros; Spearman
0,75) — la asociación turismo↔alquiler caro no es un espejismo de dos
outliers.

### 6.2 Sensibilidad de supuestos (AN-9, MET-1)
Los resultados que dependen de pesos o parámetros se someten a barrido: en
1.000 combinaciones aleatorias de pesos del índice AN-8, Loiola nunca baja del
3.er puesto social y Erdialdea es 1.º turístico el 100 % de las veces; el
ranking de presión apenas se mueve con m²/persona ∈ [20, 50].

### 6.3 Estructura espacial (AN-15) y de agrupamiento (AN-11)
Moran's I confirma que las geografías narradas son autocorrelación espacial
real (alquiler I=0,58, p=0,003; también renta, % universitarios, VUT, Airbnb).
El clustering jerárquico, como control del k-means, sostiene mejor k=3 que
k=4 (silhouette 0,455 vs 0,416) con estructura *moderada*: por eso las
tipologías se publican como **perfiles descriptivos**, nunca como clases
naturales — y la línea divisoria más profunda de la ciudad resulta ser
renta/estudios, no turismo.

### 6.4 Contra el propio hallazgo: el caso lead/lag (AN-6 → AN-16)
El resultado metodológicamente más valioso es uno que se retiró. El análisis
exploratorio AN-6 encontró que la actividad turística *precedía* al alquiler
un año (r≈0,27, mayor que la contemporánea y que el sentido inverso). El
blindaje AN-16 — efectos fijos de año (restar la marea macro común) + test de
permutación — la redujo a r≈0,10, p≈0,30: covariación de toda la ciudad, no
señal direccional. Una segunda señal independiente del proxy (el flujo de
licencias REATE cruzado con el alquiler, con detrend y permutación) tampoco la
reabre. H1 queda debilitada y **el relato lo cuenta así**, con el veredicto en
el capítulo turístico y en el epílogo. Publicar la retirada de un hallazgo
propio vale más, en credibilidad, que el hallazgo.

### 6.5 Descomposición demográfica por residuo (AN-12)
Para acercarse a la pregunta del desplazamiento sin microdatos: la pérdida de
población del centro se descompone en saldo vegetativo vs migratorio
(pirámide del padrón + mortalidad provincial). Erdialdea **atrae** migración
neta (+2.162 en 2000–2025) y mengua por puro déficit vegetativo (−3.435);
solo Gros suma las dos sangrías, con éxodo de 25–39 años en las cinco
ventanas quinquenales. Si hay desplazamiento, es selectivo — joven y de Gros —
no un vaciado del centro. Es una estimación por residuo y se publica como tal.

### 6.6 Percepción contrastada (HU-1, H6, H8)
La encuesta municipal de 2026 (vivienda, inseguridad, turismo como top-3 de
preocupaciones) se contrasta ítem a ítem: la inseguridad «de toda la vida» es
falsa a largo plazo (35,4 % de familias con problemas en 1989 → 14,6 % en
2019) pero el repunte reciente es real (21,5 % en 2024, con la criminalidad de
Gipuzkoa +34 % 2019–2024); el ruido percibido va con el tráfico y el calor
(r≈0,7), no con el turismo (0,47, confundido por el centro); la preocupación
turística sube justo cuando el *flujo* de licencias se desploma — lo que pesa
es el *stock* en máximos y el volumen récord (2,2 M de pernoctaciones).

## 7. Resultados principales (síntesis)

1. **Touristificación concentrada**, no urbana-general: Erdialdea ~30 VUT/1000
   y ~33 anuncios Airbnb/1000; el este obrero, casi cero. Calle a calle, más:
   10 calles = 19 % del censo.
2. **La presión residencial se invierte respecto al precio**: máxima donde la
   renta es baja (este), no donde el alquiler es caro (centro). El alquiler
   además gana la carrera al salario (2016–2023: +24,8 % vs +21,8 %; IPC
   +20,4 %) y la vivienda en venta corre aún más (+60 % desde 2016).
3. **Dos transformaciones, dos geografías** (H2): el cambio social vive en la
   periferia interior (Loiola, Egia); la presión turística, en el centro
   consolidado. Un índice único las habría fundido.
4. **La brecha entre barrios no se ensancha** (H3): Gini territorial ponderado
   estable (~0,10), beta-convergencia nula — con la «ilusión de equidad» como
   cautela declarada (el Gini no ve a quien se marcha).
5. **La pérdida del centro es vegetativa** (H4) y la ciudad importa
   trabajadores (1,20 empleos/residente ocupado).
6. **El clima se calienta y el calor tiene mapa**: +0,31 °C/década en serie, y
   una isla de calor superficial que se solapa con el este denso — la misma
   geografía sobre la que convergen alquiler gravoso y migración económica.
7. **El turismo crece como actividad, no como parque** (×1,22 de sesgo del
   proxy; oferta plana; licencias en goteo): el «boom» de 2016–2025 es sobre
   todo intensificación y regularización.

## 8. Limitaciones — lo que este método no puede afirmar

- **Desplazamiento individual** (gentrificación en sentido estricto): sin
  microdatos de movilidad residencial, solo transformación observable.
- **Causalidad turismo→alquiler**: el indicio direccional no superó los
  controles; reabrirlo exige datos sub-anuales que no son públicos.
- **Nada intra-barrio ni individual**: correlaciones ecológicas (MET-6);
  renta solo como media de barrio (por eso se rechazó estimar «% de hogares
  sobre el 30 % de esfuerzo» — habría exigido inventar la distribución).
- **Los huecos declarados**: 6/19 barrios sin mercado de alquiler registrado;
  el mapa completo de la vivienda protegida (⅔ del parque, patronato
  municipal) no es público; sinhogarismo y economía informal fuera del radar
  de cualquier encuesta de hogares.

## 9. Regla de parada

`PLAN-CIERRE.md` fija el criterio que evita el proyecto infinito: **un dato
entra solo si prueba, matiza o refuta H1–H4, o corrige un error**. Con la
última tanda dirigida (REC-15 vivienda protegida, REC-18 equipamientos)
ejecutada y presupuestada («si una fuente no rinde un indicador útil en ~½
jornada, se aparca y se documenta como laguna»), la puerta de datos quedó
congelada. Las preguntas abiertas no son fallos: son las hipótesis formuladas,
listas para datos mejores (alquiler trimestral, microdatos de movilidad,
registro de VPO georreferenciado).

## 10. Qué es reutilizable de este método

Para otro municipio con datos abiertos comparables, el patrón exportable es:

1. Geometría única + join en ingestión + provenance por valor.
2. Clasificar cada fuente (completa / parcial / proxy) **antes** de narrar.
3. Supuestos como controles manipulables, no como notas al pie.
4. Familia de medidas en vez de índice único; componentes a la vista.
5. Batería de robustez barata (LOO, bootstrap, permutación, FE, Moran) en
   lugar de modelos que el N no soporta.
6. Estado/cambio/trayectoria como disciplina de enunciación.
7. Publicar las retiradas (AN-16) y las lagunas con el mismo protagonismo que
   los hallazgos.
8. Tests sobre el entregable narrativo (estructura + fact-check de cifras
   citadas), no solo sobre el pipeline.

---

## Referencias del repositorio

| Tema | Documento |
|---|---|
| Decisiones MET-1…8 | `docs/NOTA-METODOLOGICA.md` |
| Lectura integrada y H1–H4 | `docs/TESIS-CIUDAD.md` |
| Análisis inferencial AN-11…20, REC-13/14 | `docs/intermedia/ANALISIS-INFERENCIAL.md` |
| Índice de Transformación (AN-8, AN-9) | `docs/intermedia/INDICE-TRANSFORMACION.md` |
| Lead/lag y su blindaje (AN-6, AN-16) | `docs/intermedia/ANALISIS-LEADLAG.md` |
| Correlaciones y perfiles (Sprint A) | `docs/intermedia/ANALISIS-SPRINT-A.md` |
| Regla de parada | `docs/PLAN-CIERRE.md` |
| Fuentes y estado de acceso | `docs/SOURCES.md` · `datos/input/FUENTES.md` |
| Contrato de datos | `docs/DATA-CONTRACT.md` |
| Hipótesis futuras y semáforo | `docs/HIPOTESIS-FUTURAS.md` |
| Entregable narrativo | `output/historias.html` (+ `metodologia.html`, `datos.html`, `resumen.md`) |
| Tests del relato | `web/tests/historias.test.ts` · `web/tests/historias-facts.test.ts` |
