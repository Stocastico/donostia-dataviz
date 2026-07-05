# La tesis de la ciudad — lectura integrada (DOC-4)

> **Qué es.** Una lectura de conjunto, *causal pero cauta*, de lo que dicen los
> datos ya procesados sobre la transformación de Donostia. Integra los hallazgos
> verificados de `intermedia/ANALISIS-SPRINT-A.md`, `intermedia/INDICE-TRANSFORMACION.md` y el análisis
> de distribución (AN-4/AN-5). Todos los números son reproducibles
> (`analysis/*.py`). Distingue de forma explícita lo que **se puede afirmar** de
> lo que **no**.

## La tesis en una frase

> La touristificación se concentra en el centro acomodado y empuja los
> alquileres, pero la **presión de vivienda más dura recae en el este obrero**,
> donde las rentas no acompañan; mientras tanto la brecha de renta **entre**
> barrios no se ensancha, así que lo que cambia no es tanto "cuánto gana cada
> zona" como **quién puede permitirse vivir dónde** — con el clima calentándose
> de fondo.

*Matiz (jul-2026):* la parte de "quién puede permitirse vivir dónde" es una
**lectura sugerida por señales convergentes** (tensión invertida, envejecimiento
del centro, pérdida de población), no un hecho demostrado: sin microdatos de
movilidad residencial no se puede afirmar desplazamiento (MET-2). El mejor
proxy alcanzable — descomponer la pérdida de población del centro en saldo
vegetativo vs migratorio y éxodo de 25–39 — **ya está hecho (AN-12)** y
matiza la imagen: en 2000–2025 Erdialdea **atrae** migración neta (+2.162) y
pierde población por puro déficit vegetativo (−3.435); la doble sangría
(vegetativa y migratoria, con éxodo 25–39 sostenido en las cinco ventanas)
es de **Gros**. El desplazamiento neto, si existe, es selectivo por edad y
barrio, no un vaciado del centro (`ANALISIS-INFERENCIAL.md` §AN-12).

## Los eslabones (con su evidencia)

**1. El turismo está concentrado, no repartido.** Erdialdea (29,9 VUT/1000 ab.)
y Gros (20,7) concentran la vivienda turística; el resto de la ciudad está muy
por debajo. Es un fenómeno de dos barrios, no urbano-general.

**2. Donde hay turismo, hay alquileres altos — y la relación es robusta.**
`densidad VUT ↔ alquiler` da r = 0,64 (Pearson) y **aguanta** al quitar
Erdialdea y Gros (0,62) y sube en rangos (Spearman 0,75). No es un espejismo de
dos outliers. *Cautela:* es asociación, no prueba de causalidad — el turismo pudo
concentrarse donde el alquiler ya era alto (causalidad inversa); resolverlo
necesita serie temporal de presión turística (hoy no la hay; ver §"lo que falta").

**3. La presión de vivienda se invierte respecto al precio.** El alquiler
absoluto manda en el centro, pero el **esfuerzo** alquiler/renta es máximo en el
este obrero: Altza 21,9 %, Egia 21,3 %, Intxaurrondo 20,9 %. La correlación
`tensión ↔ renta` es **−0,81, y −0,89 sin el centro** — la relación más fuerte y
robusta de todo el sistema. La tensión es, ante todo, un problema de renta baja.
*El contrapeso público ya tiene mapa (REC-15, jul-2026):* la vivienda protegida
de las promociones de Etxebide se concentra en Loiola (**22,3‰**), Amara Berri
(18,7), Intxaurrondo (16,3) e Ibaeta (15,5) y es **cero en los otros 14 barrios**
con dato, incluidos el centro caro y Gros. Bien orientada hacia la geografía de
la presión, pero sin tocar a los dos barrios más tensionados (Altza y Egia, 0‰
en este registro). *(Proxy: solo promociones Etxebide — suelo del parque
protegido, no censo de toda la VPO.)*

**4. La población extranjera crece más rápido en ese mismo este.** Intxaurrondo
+0,92 puntos/año, Mirakruz +0,68, Martutene +0,65, frente a Aiete +0,27. Y
`renta ↔ % extranjeros` es −0,58 (−0,72 sin el centro): salvo en el centro
turístico (expatriados acomodados), la población extranjera se asienta donde la
renta es menor. Es inmigración económica, **no** una señal de gentrificación
(ver `NOTA-METODOLOGICA.md`, MET-5). El desglose por región de origen (REC-21, jul-2026)
lo afina: dentro de ese −0,58 conviven una correlación de **−0,69** (América Latina) y
**−0,48** (Norte de África) con la renta del barrio, frente a **+0,24** de Europa occidental
(y +0,59 con % universitarios). No hay "un" extranjero: hay al menos dos poblaciones con
relación **opuesta** con la renta, que el agregado «% extranjeros» funde en una sola cifra.

**5. Pero la brecha de renta ENTRE barrios no se ensancha.** El Gini territorial
de la renta (ponderado por población) es estable: ~0,10 en 2016 y ~0,10 en 2023;
el P90/P10 ronda 1,5 todo el periodo. *(El pico de 2022 sin ponderar es un
outlier de Miramón-Zorroaga, barrio pequeño y volátil.)* Conclusión importante:
**el relato no es "los ricos se separan de los pobres"**; las posiciones relativas
de los barrios son estables. Lo que cambia es la *asequibilidad* y la composición.
*Cautela (jul-2026):* este Gini mide desigualdad **entre** los 13 barrios, no la
desigualdad *dentro* de cada barrio ni la de quien se marcha del municipio — si
las rentas bajas salen de la ciudad, el Gini interno puede quedarse estable
creando una **ilusión de equidad**. La beta-convergencia (AN-13) lo testearía
con más rigor.

**6. El alquiler sube en todas partes, pero el este es "barato y calentándose".**
Las tasas de subida 2016–2024 son parecidas (~3–4 %/año). En la matriz
niveles×variaciones, el este (Loiola, Intxaurrondo, Altza, Mirakruz) cae en
"alquiler bajo · crecimiento rápido": asequible aún, pero erosionándose; el
centro (Erdialdea, Gros, Antiguo) es "alto · lento" (caro y en meseta, con menos
margen de subida).

**7. Dos transformaciones, dos geografías distintas.** El Índice de
Transformación Urbana lo deja claro: el modo *presión turística* lo lideran
Erdialdea y Gros; el modo *socioeconómico* (Freeman) lo lidera **Loiola** (único
"en transformación") seguido de **Egia** ("incipiente", con el mayor crecimiento
de universitarios de la ciudad). Los centros turísticos **no** se transforman
"desde abajo" (ya eran acomodados). Es decir: **el turismo y el cambio social
ocurren en barrios diferentes** — un único "índice de gentrificación" lo habría
ocultado.

**8. El telón de fondo: el clima se calienta.** Igeldo 1981–2025: +0,31 °C/década,
de 13,1 a 14,7 °C de media; días ≥30 °C al alza (+0,81/década); picos hasta
39,7 °C (2022). No es espacial (una estación), pero es la dimensión temporal más
sólida del proyecto.

## Qué se puede afirmar y qué no

**Se puede afirmar:** touristificación concentrada (y, calle a calle, aún más:
las 10 calles más cargadas reúnen el 19 % del censo VUT); asociación robusta
turismo↔alquiler; que la tensión de vivienda recae en el este de renta baja; que
el contrapeso público (VPO Etxebide) aterrizó en el este obrero y es cero en el
centro y en los barrios más tensionados (REC-15); que la brecha territorial de
renta es estable; que el cambio social (Loiola/Egia) y la presión turística
(centro) son geografías distintas; que el clima se calienta.

**No se puede afirmar (todavía):**

- **Desplazamiento / sustitución de residentes** (gentrificación en sentido
  estricto): falta rotación de población. Por eso hablamos de *transformación*.
- **Causalidad turismo → alquiler**: necesita una serie temporal de presión
  turística por barrio (VUT es un *snapshot*).
- **Que el turismo cause el envejecimiento del centro**: el centro ya estaba
  envejecido antes del boom turístico de 2016 (la serie 2000–2025 lo muestra), y
  es un patrón común a muchas ciudades europeas. El turismo se implanta sobre
  una estructura demográfica preexistente, no la crea.
- **Nada a nivel individual**: todas las correlaciones son entre barrios
  (falacia ecológica, MET-6) — describen geografía, no comportamiento de hogares.
- Nada a escala fina sobre **trabajo, comercio o movilidad** (no integrados).

## Las hipótesis que estos datos generan

*(jul-2026, del feedback ChatGPT §8: el proyecto ya no solo responde preguntas —
empieza a generar hipótesis empíricas contrastables. Hacerlas explícitas es parte
del encuadre.)*

**H1 — La presión turística anticipa el alquiler (~1 año).** Lo sugería el
lead/lag AN-6 (r(+1)=0,27, mayor que la contemporánea y que el sentido inverso).
⚠️ **Primer test superado en contra (jul-2026):** el blindaje AN-16 muestra que
la señal no sobrevive al control por shocks comunes de año (r cae a ≈0,10,
p permutación ≈0,30) — la mayor parte era covariación macro de toda la ciudad.
H1 queda **debilitada pero no cerrada**: el diseño con efectos fijos de año no
puede ver un efecto uniforme en toda la ciudad; la reabrirían el alquiler
mensual/trimestral y el histórico de licencias VUT (REC-12) como segunda señal.

**H2 — La transformación turística y la social siguen geografías distintas.**
Lo sugiere la correlación débil entre ambos scores (≈0,25) y el mapa: turismo en
el centro acomodado, cambio social en la periferia interior. ✅ **Primer test
superado a favor (jul-2026):** AN-9 muestra que el patrón no depende de los
pesos del índice (Loiola nunca baja del 3º puesto social en 1.000 permutaciones;
Erdialdea es 1º turístico en el 100 %). ✅ **Segundo test a favor:** AN-15
(Moran's I) confirma que las dos geografías son estructura espacial real —
autocorrelación positiva significativa en alquiler (I=0,58, p=0,003),
% universitarios, renta, VUT y Airbnb; el este obrero y el centro turístico
salen como clusters locales nítidos (`ANALISIS-INFERENCIAL.md`).

**H3 — La desigualdad territorial permanece estable mientras cambia la
accesibilidad.** Lo sugieren el Gini plano (~0,10) junto a la tensión invertida
respecto al precio. ✅ **Primer test superado a favor (jul-2026):** AN-13
(beta-convergencia) no encuentra ni convergencia ni divergencia — el nivel de
2016 no predice la tasa posterior en renta, alquiler ni % universitarios (los
tres IC95 % de β cruzan el 0; `ANALISIS-INFERENCIAL.md`). Sigue pendiente lo
que este dato no ve: desigualdad intra-barrio y quien se marcha del municipio.
*Matiz de política pública (REC-15):* el instrumento que podría mover la
accesibilidad —la vivienda protegida— está bien orientado hacia el este obrero
pero es cero justo donde el esfuerzo es máximo (Altza, Egia), así que hoy no
altera la foto de H3.

**H4 — El centro pierde población sin dejar de concentrar actividad.** Lo
sugieren la pérdida de población (Gros −0,60 %/año) simultánea al máximo de
presión turística y actividad económica. ✅ **Descompuesta (jul-2026):** AN-12
(residuo por cohortes) muestra que la pérdida es ante todo **vegetativa** —
Erdialdea atrae migración neta (+2.162 en 2000–2025) y aun así pierde
población (déficit nacimientos−defunciones de −3.435); Gros es el único
barrio con saldo vegetativo Y migratorio negativos, con éxodo 25–39 en las
cinco ventanas quinquenales (`ANALISIS-INFERENCIAL.md` §AN-12). El "sin
dejar de concentrar actividad" **ya tiene dato (REC-17, jul-2026)**: Donostia cuenta
**1,20 empleos localizados por residente ocupado** (2024) — la ciudad *importa* trabajadores
cada día. Las dos mitades de H4 quedan cerradas: la pérdida de población es vegetativa y la
concentración de actividad, real.

Ninguna es una conclusión: son las **preguntas de investigación** que este
proyecto deja formuladas con datos abiertos, listas para datos mejores.

## Lo que falta para cerrar la tesis

- **Edad por barrio (REC-1)** → ¿el centro que pierde población gana qué perfil?
  Señal indirecta de sustitución.
- **Inside Airbnb (REC-4)** → presión turística real + **serie temporal** →
  permite el lead/lag (¿el turismo *precede* a la subida de alquiler?).
- **Ruido (REC-2)** → calidad de vida y conflicto residente-turista en el centro.

> En suma: el proyecto ya sostiene con datos una lectura coherente de las
> **presiones** que moldean Donostia. Para pasar de "presiones" a "transformación
> demostrada" faltan, sobre todo, la dimensión temporal del turismo y la
> estructura por edad.

---

## Anexo — hallazgos por eje (digest reproducible)

> Resumen temático que antes vivía en `INSIGHTS.md` (archivado en `archive/`).
> Cada número viene de las tablas en `../data/` y es reproducible con
> `python -m donostia_pipeline.build`.

**🏘️ Turismo y turistificación.** VUT concentradas en el centro: Erdialdea **664**
y Gros **359** (de ~1.490 en la ciudad); densidad Erdialdea **29,9**/1000 hab.,
Gros **20,7**, Antiguo 8,5. Estacionalidad hotelera (INE EOH 2005–2026): pico
jul/ago ~245k, mínimo ene ~116k; desplome 2020 (COVID) y recuperación + ligera
**desestacionalización** desde 2021; total 2025 ≈ **2,2 M** de pernoctaciones. Proxy de reseñas: exagera
el crecimiento de oferta **×1,18** (2023–2025: oferta activa +2,0 % vs reseñas +20,2 %) y las altas nuevas de
licencias VUT del registro REATE caen de **300/año (2017) a 18 (2025)** (REC-13/REC-12). Calle a calle
(censo VUT × callejero municipal, 301 calles): Zabaleta **35** unidades, Urbieta 34, Easo 33, San Marcial 31;
las 10 calles más cargadas = **19 %** del censo — la media de barrio borra los ejes saturados.

**🏠 Vivienda.** Alquiler €/m² (EMA 2024): Erdialdea **16,6**, Aiete 16,2, Gros
15,9; este más barato; Erdialdea **+29 %** desde 2016. Esfuerzo alquiler/renta
máximo en el este obrero (Altza 21,9 %, Egia 21,3 %, Intxaurrondo 20,9 %), mínimo
en Ategorrieta-Ulia 14,5 % y Aiete 16,7 %. Vivienda protegida Etxebide (REC-15,
snapshot): Loiola **22,3‰**, Amara Berri 18,7, Intxaurrondo 16,3, Ibaeta 15,5;
**0 en los otros 14 barrios** con dato (proxy: solo promociones Etxebide).

**💶 Economía.** Renta per cápita 2023: Aiete ~30.440 € vs. Altza ~18.371 €
(~1,7×). Brecha de género marcada (Aiete ~29,9 %). Gini territorial **estable**
(~0,10 en 2016 y 2023): la brecha *entre* barrios no se ensancha. Intensidad investigadora Gipuzkoa
**31,0‰** de ocupados en I+D vs. **13,6‰** España (REC-21); abanico salarial ancho: dirección 65.657 € vs. servicios 18.044 € (×3,6).

**👥 Demografía.** % extranjeros al alza en todas partes (Gros 1,3 %→9,9 %,
2000→2025), más rápido en el este (Intxaurrondo +0,92 pp/año). Edad: centro
envejecido (índice de vejez Gros **370**, Erdialdea **350**), este joven
(Intxaurrondo 21 % de 25–39); Antiguo +203 puntos de índice en 25 años;
Miramón-Zorroaga rejuvenece (387→151). Origen (REC-21): la cuota latinoamericana crece **×19** desde 2000
(0,25 %→4,81 %, >½ de la población extranjera), concentrada en el este de renta baja (r=−0,69); Europa occidental,
en el centro (+0,24 con renta). Paro extranjero en Gipuzkoa **9,4 %** vs **4,3 %** español; africano **18,4 %**.

**🏫 Educación.** Universitarios al alza (Aiete 25,3 %→35,0 %). Centros educativos
per cápita: la normalización cambia el ranking (Ibaeta 1ª en absoluto, 3ª per
cápita; Zubieta 1ª per cápita por población baja).

**🏥 Salud (REC-18).** 29 equipamientos de salud, densidad por 1.000 hab.
(snapshot): Loiola **0,31** y Egia 0,21 encabezan los 13 barrios urbanos —la
sanidad de proximidad acompaña a la ciudad residente—; Miramón-Zorroaga (3,4)
es artefacto per cápita del hospital. Densidad de servicios, no isócrona.

**🌡️ Clima (AEMET Igeldo, 1981–2025).** +0,31 °C/década (R²=0,39), media 13,1→14,7 °C;
días ≥30 °C **+0,81/década** (15 en 2022); máx absoluta **39,7 °C (2022)**, 38,6 °C
(2003); precipitación sin tendencia clara (R²=0,06). Isla de calor superficial (Landsat 2015–2025, REC-14):
**Gros +4,8 °C**, Amara Berri +4,3, Egia +4,1 sobre la media de ciudad; anillo verde −3…−5 °C (el calor urbano vive en el este denso).

**♻️ Medio ambiente.** Recogida selectiva del 28,8 % (2010) al **41,0 % (2023)**;
tendencia clara de mejora, aún bajo el objetivo UE (55 %).

**🎪 MICE.** Récord 2024: **188 eventos**, **259.000 participantes**, 50 %
internacionales. Congresos ICCA: 16 (2018) → 12 (2019) → 15 (2023) → 13 (2025).

**🔗 Correlaciones clave.** Densidad VUT ↔ alquiler **r = 0,64** (0,62 sin el
centro; Spearman 0,75); esfuerzo ↔ renta **r = −0,81** (−0,89 sin el centro), la
más fuerte del sistema; renta ↔ % extranjeros **r = −0,58** (−0,72 sin el centro); por origen (REC-21) renta ↔ Latinoamérica **−0,69**, ↔ Europa occidental **+0,24** (y +0,59 con % universitarios).
