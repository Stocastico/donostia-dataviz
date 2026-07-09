# Hipótesis futuras — a partir de encuestas de percepción (borrador para revisar)

> **Qué es.** Notas de trabajo, sin analizar todavía. Recoge (1) las cuatro
> hipótesis ya investigadas en el proyecto, (2) lo que dicen las encuestas de
> percepción ciudadana más recientes sobre Donostia, y (3) hipótesis candidatas
> que esas encuestas sugieren, para contrastar (o desmentir) con los datos del
> proyecto. **Nada de esto se ha analizado aún** — es punto de partida para
> decidir qué merece la pena investigar.

---

## 1. Las cuatro hipótesis ya investigadas (resumen)

Detalle completo en `docs/TESIS-CIUDAD.md` §"Las hipótesis que estos datos generan".

- **H1 — El turismo anticipa el alquiler (~1 año).** ⚠️ Debilitada: el
  lead/lag inicial (r≈0,27) casi desaparece al controlar por shocks anuales
  comunes de toda la ciudad (r≈0,10, AN-16). Ni cerrada ni confirmada.
- **H2 — La transformación turística y la social siguen geografías
  distintas.** ✅ Confirmada (robusta a pesos del índice y a autocorrelación
  espacial, AN-9/AN-15). Turismo en el centro (Erdialdea/Gros), cambio social
  en Loiola/Egia.
- **H3 — La desigualdad territorial se mantiene estable mientras cambia la
  accesibilidad.** ✅ Confirmada por beta-convergencia (AN-13). Pendiente:
  desigualdad intra-barrio y quién se marcha del municipio.
- **H4 — El centro pierde población sin dejar de concentrar actividad.**
  ✅ Cerrada (AN-12 + REC-17): la pérdida es vegetativa en Erdialdea, no
  migratoria; Gros es el único barrio con doble sangría; la ciudad importa
  1,20 empleos por residente ocupado.

---

## 2. Encuestas de percepción ciudadana — fuentes para revisar

### 2.1 Encuesta de Percepción Ciudadana (Ayto. Donostia, seguimiento Plan
Estratégico 2030)

- Ejecución: Data Key, 1.213 entrevistas, personas de 16 a 84 años,
  mayo–julio 2026.
- **Fuentes:**
  - Presentación / resultados (PDF, ayuntamiento):
    https://www.donostia.eus/home.nsf/0/A372CB8CFD600611C1258BA1003C0BED/$file/Presentaci%C3%B3n%20encuesta.pdf
  - Noticia del ayuntamiento:
    https://www.donostia.eus/home.nsf/0/A372CB8CFD600611C1258BA1003C0BED?OpenDocument=&idioma=cas
  - Estrategia San Sebastián / Donostia Futura (histórico de la serie, incl.
    ediciones 2006 y 2017 para comparar evolución):
    https://www.donostiafutura.com/es/tags/Encuesta-de-percepcion-ciudadana
    https://www.donostiafutura.com/es/publicaciones/encuesta-percepcion-ciudadana-2006
    https://www.donostiafutura.com/es/publicaciones/encuesta-de-percepcion-ciudadana-2017-primera-parte
  - Cobertura de prensa con el ranking de preocupaciones:
    https://www.ondavasca.com/vivienda-seguridad-y-turismo-principales-preocupaciones-de-los-donostiarras/
  - Nota: existe también una encuesta específica de seguridad 2026
    (formulario Netquest, sin resultados públicos localizados todavía):
    https://es.research.net/r/PERCEPCION_CIUDADANA_2026

**Datos clave (a nivel ciudad, sin desglose por barrio en las fuentes
encontradas):**

- 94 % satisfechos de vivir en Donostia; 89 % satisfechos con la calidad de
  vida (vs. 86 % media europea).
- **Ranking de preocupaciones: 1º vivienda, 2º inseguridad ciudadana (sube
  con fuerza), 3º turismo** (entra nuevo al top-3).
- Peor valorado: sanidad (56 %), ruido (63,5 %), limpieza viaria (68,3 %).
- Transporte público 85 %, educación 84 %, cultura 82 %, deporte 82 %,
  espacio público 78 %, zonas verdes 69 %.
- Turismo: 80 % lo considera importante para la ciudad; 82 % dice "que no
  crezca más".
- Apoyo a Zona de Bajas Emisiones 83 %; necesidad de acción climática 98 %.

### 2.2 Encuesta de percepción del ruido (Ayto. Donostia / ámbito ruido)

- Ejecución: 407 entrevistas, diciembre 2025 – abril 2026.
- **Fuente (prensa):**
  https://www.noticiasdegipuzkoa.eus/donostia/2026/06/29/donostiarras-perciben-parte-vieja-barrio-11263448.html
- Nota lateral con demanda ciudadana asociada:
  https://www.donostitik.com/los-donostiarras-piden-menos-trafico-para-reducir-el-ruido-en-la-ciudad/

**Datos clave (sí hay desglose por barrio):**

- A nivel ciudad: 53,7 % considera su barrio tranquilo, 27,5 % ruidoso.
- **Más ruidosos:** Parte Vieja (71,4 % lo percibe ruidoso), seguida de
  Amara Berri, Egia, Gros y Añorga.
- **Más tranquilos:** Igeldo (100 %), Ibaeta (92,3 %), Bidebieta-Miracruz
  (91,7 %), Aiete-Miramón (83,3 %).
- Demanda ciudadana principal para reducir ruido: menos tráfico.

### 2.3 Pendiente de revisar

- El PDF completo de la Encuesta de Percepción Ciudadana 2026 (el enlace de
  arriba puede redirigir a la home del ayuntamiento en vez de al PDF
  directo — comprobar acceso y, si hace falta, buscar el informe extenso en
  la sección de transparencia/gardentasun, donde podría haber desglose por
  barrio para vivienda e inseguridad).
- Comparar con ediciones anteriores (2006, 2017) para ver evolución real del
  ranking de preocupaciones, no solo el dato de este año.
- Deustobarómetro (referencia comparativa con Álava/Gipuzkoa, no específico
  de Donostia): https://gasteizberri.com/2026/06/alava-inseguridad-vivienda-deustobarometro-verano-2026

---

## 3. Hipótesis candidatas que sugieren estas encuestas

Ninguna analizada todavía. Ordenadas de más a menos inmediata con los datos
que ya están en el repo.

**H6 — El ruido percibido coincide con la isla de calor y con la densidad
VUT.** Ya tenemos ambos datos en el proyecto: Gros (+4,8 °C) y Egia
(+4,1 °C) destacan en la isla de calor superficial (Landsat, REC-14) *y*
están en el top-5 de barrios más ruidosos de la encuesta. Cruce directo,
sin necesidad de datos nuevos — candidata a hacerse primero.

**H5 — La inseguridad percibida no sigue el patrón socioeconómico
esperado** (p. ej. se concentra en el centro turístico/ocio nocturno más
que en el este obrero de renta baja). Necesita el desglose por barrio de la
encuesta de percepción de seguridad, que **no** hemos localizado todavía
(ver §2.3) — sin eso no es contrastable.

**H7 — La preocupación por vivienda cara no es uniforme: barrios pequeños o
periféricos pueden tener dinámicas de precio propias, distintas del este
obrero.** El ejemplo que propuso el usuario (Zubieta más barato) es
plausible en la forma pero **no verificado**: `metrics_long.csv` no tiene
fila de alquiler para Zubieta, probablemente por tamaño de muestra
insuficiente en la EMA — habría que comprobar cobertura antes de afirmar
nada (mismo problema de fuente parcial que ya documentamos para VPO/Etxebide
en REC-15).

**H8 — La preocupación por el turismo sube justo cuando la presión bruta
(altas de licencias VUT nuevas) baja.** Contraintuitivo: REC-13 mostró que
las altas de licencias REATE caen de 300/año (2017) a 18/año (2025), pero el
turismo entra nuevo al top-3 de preocupaciones en 2026. Posible relato: lo
que preocupa ya no es el flujo de nuevas licencias sino el stock acumulado o
la masificación en temporada alta, no el ritmo de crecimiento.

---

## 4. Siguiente paso (cuando se decida)

Revisar esta nota con calma y decidir: (a) si merece la pena perseguir el
PDF completo de la encuesta 2026 para buscar desgloses por barrio de
vivienda/inseguridad, y (b) cuál de H5–H8 se prioriza. Criterio del
proyecto (ver `BACKLOG.md`): un dato entra solo si prueba/matiza/refuta una
hipótesis, no porque exista.

---

## 5. Plan de trabajo priorizado — 7 hipótesis del usuario (jul-2026)

> Batería nueva de hipótesis propuesta por el usuario (jul-2026), evaluada
> contra los datos que **ya** están en el repo o son localizables. Semáforo de
> disponibilidad: 🟢 datos ya en el repo · 🟡 parcial o fuente externa
> localizable · 🔴 sin datos hoy. Numeración HU-1…HU-7 (Hipótesis del Usuario)
> para no chocar con H1–H8 de arriba.

| # | Hipótesis (resumen) | Datos | Qué hay / qué falta |
|---|---|---|---|
| **HU-1** | La percepción de que la seguridad ha bajado mucho es falsa (percepción ≠ realidad) | 🟡 | Percepción: ✅ (encuesta 2026, inseguridad 2ª preocupación «sube con fuerza», §2.1). Realidad objetiva: 🔴 en el repo (criminalidad por barrio descartada, `BACKLOG` L602), pero **a nivel municipio es pública**: *Balance de Criminalidad* del Ministerio del Interior (trimestral, municipios >20k hab) y/o Ertzaintza. Contraste = tijera percepción↑ vs. delito real. |
| **HU-2** | La percepción de seguridad baja al subir el nº de personas sin techo | 🔴 | Sin techo: no en repo ni BACKLOG. Recuento INE/SIIS es municipal, esporádico y submuestra pequeña. **Riesgo alto de correlación espuria y atribución causal** (todo sube a la vez estos años) → contra la norma del proyecto. Congelada salvo recuento serio. |
| **HU-3** | El turismo transforma la Parte Vieja: cambio de tipología comercial (souvenirs/chuches ↑, ferreterías/comercio de barrio ↓) | 🟡 | Ciudad: ✅ REC-7 (retail 14,9→12,6 %, hostelería 6,0→8,1 %, 2008–2025) — proxy, no baja a barrio, e-commerce confunde. Barrio/calle: 🟡 vía **OSM `shop=*`** (REC-16): da la foto *actual* por calle (souvenir vs ferretería), sin profundidad histórica. Cruzable con `calles_vut.csv` (densidad VUT × tipo de comercio). |
| **HU-4** | El tráfico ha crecido y las políticas no lo frenan (+ mapa de calles por intensidad) | 🔴 | No hay datos de tráfico. Movilidad DBus (REC-6) **dada de baja**. Único proxy: ruido 2022 por barrio («el ruido es de tráfico», VIZ-5) — snapshot, por barrio no calle → **no** sirve para el mapa calle-a-calle ni para la tendencia. Falta: aforos municipales de tráfico (verificar si Donostia OD los publica). Contexto: 83 % apoya la ZBE (encuesta 2026). |
| **HU-5** | Turismo sostenible = desestacionalizar + estancias largas/experiencias, no excursionistas en coche; potenciar tren/avión | 🟡 | Desestacionalización: ✅ (pernoctaciones INE mensuales 2005–2026, ya se observa desde 2021 — cuantificable). Excursionista vs. estancia: 🔴 (gasto excursionista solo Euskadi-wide). Modo de transporte: 🔴. Gasto ocio pernocta: ✅ IBILTUR 2023 (un solo año). |
| **HU-6** | El turismo de mayor calidad (dinero/respeto) es el de congresos/eventos (MICE) | 🟡 | Volumen/prestigio MICE: ✅ (188 eventos, 259k participantes, 50 % int'l, 2024; serie ICCA). «Más dinero»: 🔴 (gasto por congresista de Donostia no público, solo Euskadi). **Ángulo medible fuerte**: cruzar fechas MICE × pernoctaciones mensuales → ¿MICE rellena temporada baja? = «calidad» como desestacionalización (une con HU-5). |
| **HU-7** | Vivienda (venta y alquiler) sube más que IPC y que el sueldo; imposible vivir solo | 🟢🟡 | Alquiler: ✅ (EMA 2016–2024 por barrio). Renta: ✅ (`income_total` 2016–2023 por barrio). IPC: 🟡 (INE, trivial añadir como referencia). Sueldo: 🟡 (proxy renta pc + abanico salarial Euskadi REC-21). Venta €/m²: 🔴 (solo catastro foral, descartado; nunca scraping). El alquiler cubre el grueso del relato. |

### Prioridad de ejecución (esfuerzo/valor + fidelidad a las normas)

1. **HU-7** (vivienda vs IPC vs renta) — casi listo con datos del repo + IPC INE.
2. **HU-1** (percepción vs. criminalidad real de municipio) — un dato externo
   localizable + hallazgo potente (la «tijera»).
3. **HU-3 vía OSM** — el mapa calle-a-calle de la Parte Vieja que sí es factible.
4. **HU-4** depende de encontrar aforos municipales (verificar portal).
   **HU-5/HU-6** medibles solo en su parte de desestacionalización.
   **HU-2** congelada (datos + riesgo causal).

### Estado de implementación + HALLAZGOS (jul-2026, esta sesión) ✅

Las tres son **análisis exploratorios** (`analysis/`), con TDD (43 tests nuevos,
suite total 182 pipeline + 159 analysis en verde). No se cablean al pipeline
hasta que valides el relato. Correlación ≠ causalidad; cifras externas curadas
con fuente y snapshot por fila (ver `datos/input/FUENTES.md`).

- **HU-7 — Vivienda vs. IPC vs. sueldo** → `analysis/housing_affordability.py`
  (13 tests) **+ integrado en la app**: nueva métrica de barrio `income_labor`
  (renta del trabajo, Eustat `PX_173402_crpf_rpf_rp22_2p`) en el pipeline
  (`datasets/renta_trabajo.py`) y el selector *Economia*; IPC curado en
  `datos/input/ipc_espana.csv`. **Hallazgo (cerrado con salario real):** el
  alquiler de ciudad crece **+24,8 % (2016–2023)** por encima del **salario
  (renta del trabajo) +21,8 %** y del **IPC +20,4 %**; a 2024 el alquiler llega a
  **+34,8 %** (IPC +23,7 %; alquiler real +9,0 %). El «más que el sueldo» **sí**
  se sostiene con el salario real — la confusión previa venía de usar la renta
  disponible pc (+28 %, inflada por capital/pensiones/transferencias). Venta
  €/m² sigue sin fuente (🔴).

- **HU-1 — «La seguridad ha bajado mucho» (percepción vs. realidad)** →
  `analysis/perception_vs_crime.py` (8 tests) **+ integrado en la app**:
  indicadores `perception_insecurity_donostia/_euskadi` y `crime_rate_1000`/
  `crime_infractions` (tema *Sicurezza*, `datasets/seguridad.py`) en «Altri
  indicatori cittadini». Percepción: serie **Eustat real 1989–2024**. **Hallazgo:**
  a **largo plazo es FALSO** — familias con «algún problema» de seguridad caen del
  **35,4 % (1989)** al 14–18 % (2004–2019); pero hay **repunte real 2019→2024
  (14,6 %→21,5 %)**. La criminalidad real (serie parcial) también sube → percepción
  y realidad **coinciden** en corto plazo; **la «tijera» no está demostrada**.
  *Bloqueante para cerrarla:* la serie oficial anual completa del Portal
  Estadístico de Criminalidad — laguna declarada.

- **HU-3 — Tipología comercial de la Parte Vieja (OSM)** →
  `analysis/commercial_typology.py` (23 tests). Clasifica locales OSM
  (`shop=*` + hostelería `amenity=*`) en hosteleria/turistico/cotidiano/otro/
  vacant por barrio, cruzado con densidad VUT. Carga Overpass (red, cache
  gitignored). **Hallazgo:** la **Parte Vieja (bbox) es ~82 % hostelería**
  (85 de 103 locales), con solo **3 comercios cotidianos** → distrito casi
  monofuncional de consumo de visitante. OSM infra-mapea souvenirs (`shop=gift`
  ≈ 1) → el eje real en el casco viejo es la **hostelería** (`amenity`), no la
  tienda. `corr(turistico_share ↔ VUT) = +0,39`. **Clave honesta:** OSM da la
  *geografía actual*, no el *cambio* — la prueba temporal («cierran ferreterías»)
  es la serie CNAE de ciudad (REC-7: retail 14,9→12,6 %, hostelería 6,0→8,1 %);
  se **triangulan**.

**Otras (no ejecutadas esta sesión):** HU-4 (tráfico) sigue bloqueada por falta
de aforos; verificar si Donostia OD publica intensidades por calle. HU-5/HU-6
medibles solo en desestacionalización (pernoctaciones INE ya en repo) + cruce
MICE×meses. HU-2 (sin techo) congelada por datos + riesgo causal.
