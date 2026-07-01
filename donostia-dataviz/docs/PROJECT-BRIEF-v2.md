> **Nota:** versión actualizada y ampliada del brief de proyecto (backlog). Amplía
> `PROJECT-BRIEF.md` (v1) con nuevas dimensiones de datos, la corrección sobre el
> catastro foral, secciones MICE/visitantes/gasto, ideas avanzadas y la
> recomendación del indicator store unificado. El estado de avance y la
> priorización se siguen en `../BACKLOG.md` (histórico en `archive/GAP-ANALYSIS.md`).
>
> *(Traducido del italiano al español, junio 2026, manteniendo el contenido.)*

# Donostia Dataviz — Plan de proyecto

## Objetivo

Dashboard interactiva que muestra la evolución de Donostia/San Sebastián desde
múltiples puntos de vista — principalmente mediante mapas coropléticos por barrio
con slider temporal, complementados con series temporales y gráficos comparativos.

---

## Stack técnico sugerido

- **Mapas**: MapLibre GL JS (choropleth) o D3.js + GeoJSON
- **Gráficos**: D3.js o Recharts
- **Datos**: CSV/GeoJSON locales (preprocesados con Python/pandas)
- **Framework**: React + Vite (alineado con el sitio existente) o HTML/JS standalone
- **GIS base**: GeoJSON de barrios desde Open Data Donostia

---

## Geometrías base (GIS)

| Recurso | URL | Formato | Notas |
|---|---|---|---|
| Barrios (polígonos) | `https://www.donostia.eus/datosabiertos/catalogo/mapa_auzoak` | Shapefile / GeoJSON | 17 barrios oficiales |
| Unidades menores | Open Data Donostia | Shapefile | Granularidad sub-barrio |
| Distritos censales | `https://www.donostia.eus/datosabiertos/catalogo/delimitaciones_censales` | Shapefile | |
| WMS límites administrativos | `https://www.donostia.eus/datosabiertos/` (WMS) | WMS tile | EPSG:25830 o 3857 |

> ⚠️ **Problema conocido**: la subdivisión en barrios varía entre datasets del mismo Ayuntamiento. Elegir UNA única geometría de referencia y hacer join sobre ella.

---

## Datasets por categoría

### 🏠 Vivienda y alquileres

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Precios venta €/m² por barrio | Indomio | Barrio | Mensual (2023–hoy) | `indomio.es/en/mercado-inmobiliario/pais-vasco/san-sebastian-donostia/` |
| Precios alquiler €/m² por barrio | Indomio | Barrio | Mensual (2023–hoy) | misma URL |
| Precios históricos €/m² (serie larga) | Eustat / Ministerio Vivienda | Municipio | Trimestral (2000–hoy) | `eustat.eus` → Vivienda |
| Renta disponible por barrio | Open Data Donostia | Barrio | Anual | `donostia.eus/datosabiertos/catalogo/eustat_renta` |
| Renta familiar mediana por barrio | Eustat | Barrio | Anual | `eustat.eus` → renta familiar |

**Visualización sugerida**: choropleth animada (slider de año) + line chart comparativo de barrios seleccionados.

---

### 🏘️ Turismo y Airbnb

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| VUT/HUT (viviendas uso turístico) por barrio | Open Data Donostia | Barrio + dirección | Mensual | `donostia.eus/datosabiertos/catalogo/censo-viviendas-turisticas` |
| Snapshot Airbnb (listings geolocalizados) | Inside Airbnb | Punto (lat/lon) | Snapshots periódicos | `insideairbnb.com/get-the-data/` → buscar San Sebastián |
| Pernoctaciones en alojamientos turísticos | INE | Municipio | Mensual | `ine.es` → Encuesta de Ocupación en Alojamientos Turísticos |
| Viajeros por nacionalidad | INE | Municipio | Mensual | misma encuesta INE |
| Hotel: plazas y ocupación | INE / Eustat | Municipio | Mensual | `eustat.eus` → Turismo |

**Visualización sugerida**:
- Mapa de densidad VUT por barrio (choropleth) con slider temporal
- Heatmap Airbnb puntual (listings como puntos en el mapa)
- Bar chart de estacionalidad turística (meses)

---

### 👥 Demografía

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Población por barrio / edad / género | Open Data Donostia | Barrio + unidad menor | Anual (desde 2000) | `donostia.eus/datosabiertos/catalogo/demografia-origen` |
| Población extranjera por nacionalidad | Open Data Donostia | Barrio | Anual | mismo dataset |
| Nivel de estudios (>16 años) | Open Data Donostia | Barrio + unidad menor | Anual (desde 2000) | `donostia.eus/datosabiertos/recursos/demografia-nivelestudios/demografianivelestudiosciudad.csv` |
| Índice de envejecimiento | calculable desde Eustat | Barrio | Anual | razón pob >64 / pob <15 |
| Tasa de natalidad | Eustat | Municipio | Anual | |

**Visualización sugerida**: choropleth % población extranjera por barrio; pirámide demográfica animada para la ciudad.

---

### 💼 Empleo y sectores laborales

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Ocupados por sector | Open Data Donostia / Eustat | Barrio / municipio | Anual | `donostia.eus/datosabiertos/tema/empleo` |
| Tasa de desempleo | SEPE / Eustat | Municipio | Mensual | `eustat.eus` → Mercado laboral |
| Salarios por sector y género | Eustat | Barrio (parcial) | Anual | gender pay gap documentado por barrio |

**Visualización sugerida**: stacked bar chart de evolución de sectores (hostelería vs industria vs tecnología); choropleth de salario mediano con evidencia de brecha de género.

---

### 🌡️ Meteo y clima

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Temperaturas medias mensuales históricas | AEMET — estación Igeldo | Una estación | Mensual (desde 1981) | `aemet.es/es/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=1024E` |
| Precipitaciones acumuladas mensuales | AEMET — estación Igeldo | Una estación | Mensual (desde 1981) | misma URL |
| Datos climatológicos Euskalmet | Euskalmet | Redes de estaciones | Horario/diario | `euskalmet.euskadi.eus` |
| API AEMET OpenData | AEMET | Estación | Diario (reciente) | `opendata.aemet.es` — requiere API key gratuita |

> ⚠️ **Límite**: una sola estación → no hay choropleth intraurbana. Solo series temporales.

**Visualización sugerida**: line chart de temperatura media anual con tendencia (regresión lineal); heatmap mes × año con color = temperatura media.

---

### 🚨 Seguridad y calidad de vida

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Delitos registrados por barrio | Open Data Donostia (Guardia Municipal) | Barrio | Anual | `donostia.eus/datosabiertos/tema/seguridad` |
| Uso del suelo / verde urbano | Open Data Donostia | GIS polígonos | Snapshot | `donostia.eus/datosabiertos/tema/urbanismo-infraestructuras` |

---

### 🚌 Movilidad

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Pasajeros DBus totales | Open Data Donostia | Línea / parada | Anual (desde 2011) | `donostia.eus/datosabiertos/tema/transporte` |
| Aparcamientos en superficie (ubicación y tipo) | Open Data Donostia | Punto | Snapshot | mismo portal |

---

### 🎪 Turismo MICE (Congresos, Incentivos, Reuniones, Ferias)

El sector MICE es estratégicamente prioritario para Donostia y tiene un Observatorio dedicado. Los datos están más fragmentados que el turismo leisure, pero existen fuentes específicas.

**Fuente principal**: **Donostia San Sebastián Convention Bureau** (`conventionbureau.sansebastianturismoa.eus`) — publica ranking y estadísticas congresuales anuales. El 63% de los eventos organizados en la ciudad es internacional.

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Número de congresos/eventos por año | Convention Bureau / ICCA | Ciudad | Anual | `conventionbureau.sansebastianturismoa.eus` → publicaciones; base de datos ICCA |
| Participantes en congresos | Convention Bureau / Memoria anual | Ciudad | Anual | Memorias anuales DSS Turismoa (PDF) en `press.sansebastianturismoa.eus` |
| Ranking internacional MICE | ICCA (International Congress & Convention Assoc.) | Ciudad mundial | Anual | ICCA Statistics Report — Donostia en pos. 221 mundial (2019) |
| Sedes congresuales (Kursaal, Victoria Eugenia, Reale Arena, BCC...) | Convention Bureau | Punto GIS | Snapshot | lista completa en el sitio del CB |
| Pernoctaciones turistas MICE vs leisure | Eustat / Observatorio | Municipio | Anual | serie Ibiltur (Eustat) con motivo de visita |

> ⚠️ **Límite**: los datos MICE granulares (número de eventos por sede, participantes por congreso) están en las Memorias anuales en PDF — requieren extracción manual o scraping. No existe un dataset estructurado abierto.

**Visualización sugerida**: bar chart de número de eventos por año (con desglose internacionales vs nacionales); line chart comparando pernoctaciones MICE vs leisure en el tiempo.

---

### 🧳 Perfil y segmentación de los visitantes

Fuentes que describen *quién* visita Donostia, no solo *cuántos*.

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Motivo de la visita (ocio / trabajo / congresos / visita familiar) | Eustat — Ibiltur | Municipio / zona | Anual | `eustat.eus` → Ibiltur (Encuesta de Turismo Receptivo) |
| Nacionalidad turistas alojados | INE — EOH + Eustat | Municipio | Mensual | `ine.es` tabla 2078; `eustat.eus` → Turismo |
| Turismo organizado vs individual | Eustat Ibiltur | Municipio | Anual | desglose por tipo de organización del viaje |
| Medio de transporte usado | Eustat Ibiltur | Municipio | Anual | coche / AVE / avión / autocar |
| Estimación excursionismo (visitantes diarios sin pernoctación) | Observatorio Turístico Donostia / Eustat | Ciudad | Anual | dato crítico y difícil de medir — en fase de estudio de capacidad de carga (2025) |
| Satisfacción turistas (score 0–10) | Observatorio Turístico Donostia | Ciudad | Anual | 2025: 9,2/10 con pernoctación, 9,0/10 sin |
| Pernoctaciones por tipo de alojamiento (hotel / VUT / rural / camping) | INE — EOH / Eustat | Municipio | Mensual | distinción fundamental para análisis de impacto |

**Datos clave ya conocidos** (útiles como valores de referencia para la viz):
- 2025: 2.122.612 pernoctaciones totales (−0,48% vs 2024); 66,05% internacionales (+2,83%); estancia media 2,05 noches (internacionales 2,13, estatales 1,91)
- 2024: pernoctaciones +6,0% respecto a 2023, nuevo máximo histórico; turismo internacional +10,2%, estatal +1,5%
- El turismo representa el 13,9% del PIB de la ciudad y más de 15.000 ocupados están ligados al sector

---

### 💸 Gasto turístico (capacidad de gasto)

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Gasto medio turista alojado (€/día) | Eustat — Ibiltur / Observatorio | Municipio | Anual | desglose por nacionalidad y tipo de alojamiento |
| Gasto medio excursionista (€/día) | Eustat — Ibiltur | Municipio | Anual | dato separado del turista alojado |
| Gasto medio turista MICE / trabajo (€/día) | Eustat — Ibiltur | Municipio | Anual | históricamente muy superior al turismo leisure |
| Distribución del gasto por categoría (alojamiento / restaurantes / compras / transporte) | Eustat / Gobierno Vasco | Región/municipio | Anual/irregular | serie histórica disponible desde ~2000 |
| RevPAR (Revenue per Available Room) | Eustat / informes de sector | Municipio | Anual | Donostia es el segundo destino urbano español por RevPAR, solo tras Barcelona |
| Facturación sector hostelería y restauración | Eustat | Municipio | Anual | proxy del impacto económico real |

> **Nota metodológica**: la distinción entre turista alojado, excursionista y turista de negocios es crucial porque el gasto por persona/día varía enormemente entre los tres segmentos. Eustat Ibiltur es la única fuente que los separa sistemáticamente.

**Visualización sugerida**: stacked area chart de gasto total = (turistas × días × gasto/día), descompuesto por segmento en el tiempo; scatter gasto medio vs nacionalidad (burbuja = volumen).

---

### 📅 Estacionalidad y desestacionalización

Donostia tiene un plan explícito de desestacionalización — los datos mensuales muestran esta evolución en el tiempo.

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Pernoctaciones mensuales por año (serie larga) | INE — EOH | Municipio | Mensual (desde ~2000) | `ine.es` → tabla 2078, filtro San Sebastián |
| Ocupación hotelera mensual | INE / Eustat | Municipio | Mensual | grado de ocupación % por mes |
| Viajeros por mes y nacionalidad | INE / Eustat | Municipio | Mensual | |

> En 2025 crecen los meses de temporada baja (enero, febrero, junio, diciembre) mientras cae el verano (−1,48%) — esta tendencia de desestacionalización es perfecta para una visualización tipo heatmap mes × año.

**Visualización sugerida**: heatmap mes × año con color = pernoctaciones (revela la estacionalidad y su evolución en una sola vista); line chart múltiple comparando ene-dic entre años distintos.

---

### 🚨 Criminalidad (ampliación)

El dato existe y es abierto. Hay dos fuentes complementarias con granularidad distinta.

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Delitos por barrio (Guardia Municipal) | Open Data Donostia | Barrio | Anual | CSV directo: `donostia.eus/datosabiertos/catalogo/delitos-guardia/recurso/gua_delitosbarrio_ckan.csv` |
| Delitos totales por tipo (Guardia Municipal + Ertzaintza) | Gobierno Vasco — Memoria Delincuencia | Municipio | Anual | `ertzaintza.euskadi.eus` → estadísticas delictivas; serie desde ~2010 |
| Tasa delincuencial (delitos / 1000 habitantes) | Gobierno Vasco | Municipio | Anual | misma fuente; Donostia: 67,54‰ en 2021, 2025: −5,18% vs 2024 |
| Infracciones penales por tipo (hurtos, estafas, robos…) | Ertzaintza + MIR | Municipio | Anual | `estadisticasdecriminalidad.ses.mir.es` — Portal Estadístico Criminalidad |
| Puntos críticos de seguridad (mapa participativo) | Open Data Donostia | Punto GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/seguridad-ptos_criticos` (SHP + WMS) |
| Violencia de género — denuncias | Eustat / Gobierno Vasco | Municipio | Anual | Eustat → Sociedad, dato separado de la criminalidad general |

> **Nota**: el 77,7% de los delitos en Donostia son contra el patrimonio (hurtos, robos, estafas). Los datos por barrio de la Guardia Municipal son el dataset más granular — descargable directamente en CSV.
>
> ⚠️ **Actualización (junio 2026):** la criminalidad por barrio ha quedado **descartada** del camino crítico — el CSV de la Guardia Municipal ya no está en el catálogo y la escala sub-municipal está blindada por protección de datos. Ver `archive/GAP-ANALYSIS.md` §5 y `archive/FEEDBACK-CONSOLIDADO.md`.

**Visualización sugerida**: choropleth de delitos por barrio normalizados por población (tasa/1000 ab.); line chart de evolución de la tasa delincuencial por año; donut/stacked bar de tipos de delito.

---

### 🏫 Educación y juventud

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Equipamientos educativos (escuelas, guarderías, universidad) con geolocalización | Open Data Donostia | Punto GIS | Anual | `donostia.eus/datosabiertos/catalogo/servicios-educativos` — GeoJSON + CSV + WMS disponibles |
| Equipamientos de juventud (gaztelekus, haurtxokos, centros jóvenes) | Open Data Donostia | Punto GIS | Anual | `donostia.eus/datosabiertos/catalogo/equipamiento_juventud` |
| Nivel de estudios de la población por barrio | Open Data Donostia | Barrio + unidad menor | Anual (desde 2000) | `donostia.eus/datosabiertos/catalogo/demografia-nivelestudios` |
| Alumnos por nivel / lengua (modelo A/B/D) | Gobierno Vasco — Dpto. Educación | Municipio / centro | Anual | `hezkuntza.euskadi.eus` → estadísticas educación; serie histórica larga |
| Tasa escolarización 0–2 años | Eustat | Municipio | Anual | `eustat.eus` → Educación |

> **Nota sobre el modelo lingüístico**: los modelos A (solo español), B (bilingüe) y D (solo euskera) son un dato particularmente significativo para la evolución identitaria de la ciudad. El porcentaje de matriculados en el modelo D ha crecido de forma constante desde 1983.

**Visualización sugerida**: mapa de puntos de escuelas por nivel; line chart de evolución del % de alumnos en cada modelo lingüístico; choropleth de nivel de estudios por barrio.

---

### 🏥 Salud y servicios sociales

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Equipamientos de salud (hospitales, ambulatorios, clínicas) | Open Data Donostia | Punto GIS | Anual | `donostia.eus/datosabiertos/catalogo/servicios-salud` — GeoJSON + CSV + WMS |
| Equipamientos socio-asistenciales (centros de día, residencias de mayores) | Open Data Donostia | Punto GIS | Anual | `donostia.eus/datosabiertos/catalogo/servicios-socio_asistencial` — GeoJSON disponible |
| Familias atendidas por los Servicios Sociales | Open Data Donostia | Municipio | Anual | `donostia.eus/datosabiertos/catalogo/bso-familias-cas` — CSV; proxy de fragilidad social |
| Ámbitos territoriales de los servicios sociales | Open Data Donostia | Zonas GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/servicio-social` (SHP + WMS) |
| Esperanza de vida / mortalidad | Eustat | Municipio | Anual | `eustat.eus` → Demografía → Mortalidad |
| Refugios climáticos (resiliencia ante olas de calor) | Open Data Donostia | Punto GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/refugio-climatico` — nueva infraestructura (2024) |

**Visualización sugerida**: mapa de accesibilidad sanitaria (distancia a pie al centro de salud más cercano por barrio); line chart de familias atendidas por servicios sociales vs renta mediana.

---

### 🔊 Entorno urbano: ruido, calidad del aire, residuos

Esta es quizá la categoría más infravalorada para una dataviz sobre calidad de vida urbana — y Donostia tiene datos excelentes.

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Mapa de ruido total (mañana/tarde/noche) | Open Data Donostia | Rejilla GIS | Bienal | `donostia.eus/datosabiertos/catalogo/ruido-total` (SHP + WMS) |
| Mapa de ruido nocturno | Open Data Donostia | Rejilla GIS | Bienal | `donostia.eus/datosabiertos/catalogo/ruido-noche` |
| Calidad del aire | Open Data Donostia / Gobierno Vasco | Estaciones | Anual | `donostia.eus/datosabiertos/tema/medio-ambiente` — tag `calidad_aire` |
| Recogida selectiva de residuos por tipo | Open Data Donostia | Municipio | Anual | `donostia.eus/datosabiertos/catalogo/residuos` — CSV; evolución % recogida selectiva |
| Localización de contenedores de recogida selectiva | Open Data Donostia | Punto GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/mambiente-residuos` (SHP) |
| Zona de bajas emisiones (ZBE, 2024) | Open Data Donostia | Polígono GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/mambiente-zbe` — aprobada 2024 |

> El mapa de ruido nocturno es particularmente relevante para la calidad de vida en los barrios de la Parte Vieja y Gros, donde se concentra la hostelería. *(Caveat verificado después: los mapas estratégicos están dominados por ruido de transporte, no de ocio — ver `archive/GAP-ANALYSIS.md` REC-2.)*

**Visualización sugerida**: choropleth de niveles de ruido nocturno por zona; line chart % recogida selectiva por año (tendencia de sostenibilidad); overlay ZBE sobre el mapa de la ciudad.

---

### 🌿 Espacio verde y uso del suelo

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Parques y zonas verdes (polígonos GIS) | Open Data Donostia | Polígono GIS | Snapshot | `donostia.eus/datosabiertos/tema/urbanismo-infraestructuras` |
| Biodiversidad urbana (inventario de especies) | Open Data Donostia | GIS | Bienal/trienal | tag `biodiversidad` en el portal medio-ambiente |
| Potencial fotovoltaico de edificios | Open Data Donostia | Edificio GIS | Bienal | `donostia.eus/datosabiertos/catalogo/mambiente-fotovoltaico` (SHP + WMS) |
| Uso del suelo por tipo | Gobierno Vasco — Lurralde Informazioa | Polígono GIS | Cuatrienal | `geo.euskadi.eus` — Mapa de Usos del Suelo (CORINE adaptado) |

---

### 🏪 Comercio y transformación urbana

El portal tiene pocos datasets directos sobre comercio, pero el dato más interesante ya está disponible:

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Zonas saturadas de locales y actividades recreativas | Open Data Donostia | Polígono GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/urbanismo-zsaturada` (SHP + WMS) — barrios donde se ha limitado la apertura de nuevos locales |
| Licencias de apertura por tipo de actividad | Ayuntamiento (a petición / Hacienda) | Municipio | Anual | dato disponible en las estadísticas de Hacienda; no estructurado como open data CSV |
| Locales cerrados / vacíos | No disponible como open data | — | — | potencialmente detectable desde fotos satelitales o street view temporales |
| Número de restaurantes/bares por barrio | Eustat / IAE (Impuesto Actividades Económicas) | Barrio | Anual | `eustat.eus` → Empresas → por actividad CNAE; proxy de la turistificación comercial |

---

### 💰 Fiscalidad y presupuesto municipal

| Dataset | Fuente | Granularidad geo | Granularidad tiempo | URL / Notas |
|---|---|---|---|---|
| Impuestos municipales emitidos (IBI, plusvalía…) | Open Data Donostia | Municipio | Anual | `donostia.eus/datosabiertos/catalogo/impuestos_tipo` — CSV actualizado |
| Tasas municipales por tipo | Open Data Donostia | Municipio | Anual | `donostia.eus/datosabiertos/catalogo/tasas_tipo` — CSV actualizado |
| Subvenciones concedidas por año | Open Data Donostia | Municipio | Anual | `donostia.eus/datosabiertos/catalogo/subvenciones_2023` |
| **Catastro de Gipuzkoa** (valor catastral, datos físicos de inmuebles) | **Diputación Foral de Gipuzkoa** — NO el catastro estatal | Parcela / unidad constructiva | Actualizado cada 15 días | Open data CSV en `gipuzkoairekia.eus` → Catastro urbano (Bienes Inmuebles de Naturaleza Urbana); licencia CC-BY |

> ⚠️ **Importante — competencia foral**: Gipuzkoa (como todo el País Vasco y Navarra) tiene un régimen fiscal foral. El catastro NO lo gestiona la Dirección General del Catastro estatal (`sedecatastro.gob.es`), que no devuelve datos para los territorios forales. Hay que usar el **Catastro de la Diputación Foral de Gipuzkoa**. Ventaja: los datos se publican como **open data CSV descargables en bulk** en `gipuzkoairekia.eus` (dataset "Bienes Inmuebles de Naturaleza Urbana", ~6 MB por fichero, actualizado cada 15 días), mucho más cómodo que el scraping parcela a parcela. Consulta web puntual por referencia catastral o dirección en `egoitza.gipuzkoa.eus/es/web/ogasuna/catastro`.

---

## Métricas derivadas interesantes (calculadas)

Estas no existen como datasets listos, sino que se calculan combinando los datos anteriores:

| Métrica | Fórmula | Datos necesarios |
|---|---|---|
| **Tasa de turistificación** | VUT / viviendas totales por barrio | VUT + censo de viviendas |
| **Presión inmobiliaria** | Δ precio alquiler / Δ renta mediana por barrio | Precios + renta |
| **Airbnb intensity** | Listings Airbnb / viviendas totales | Inside Airbnb + censo |
| **Índice de envejecimiento** | Pob >64 / Pob <15 × 100 | Dataset demográfico |
| **Gender pay gap** | (salario_hombre − salario_mujer) / salario_hombre | Eustat por barrio |
| **Tendencia temperatura anual** | regresión lineal sobre medias anuales | AEMET |
| **Índice de desestacionalización** | coeficiente de variación mensual de pernoctaciones por año | INE — EOH mensual |
| **Peso MICE sobre turismo total** | pernoctaciones MICE / pernoctaciones totales | Ibiltur + INE |
| **Gasto total estimado** | visitantes × duración media × gasto medio/día | Ibiltur multi-segmento |
| **Ratio excursionistas / turistas** | excursionistas / turistas alojados | Observatorio + Eustat |
| **Tasa delincuencial** | delitos / pob × 1000 por barrio | Guardia Municipal CSV + demográfico |
| **Índice de accesibilidad sanitaria** | distancia media a pie al centro de salud más cercano | GeoJSON salud + geometría barrios |
| **% recogida selectiva** | residuos selectivos / total × 100 | dataset residuos |
| **Densidad de hostelería** | bares+restaurantes / viviendas por barrio | IAE/Eustat + censo |
| **Presión fiscal inmobiliaria** | valor catastral / valor de mercado por zona | Catastro + Indomio |
| **% alumnos modelo D** | matriculados modelo D / total matriculados | Dpto. Educación |

---

## Visualizaciones prioritarias

### Fase 1 — Mapa coroplético con slider
- Selección de métrica (dropdown): alquiler €/m², densidad VUT, % extranjeros, renta mediana
- Slider de año
- Tooltip al hover con barrio + valor + Δ respecto al año anterior
- Leyenda con escala de colores

### Fase 2 — Panel comparativo de barrios
- Seleccionar 2–3 barrios → line chart en paralelo por la métrica elegida
- Resaltar COVID-19 (2020) y turismo post-COVID

### Fase 3 — Series temporales de meteo y turismo
- Heatmap mes × año (temperatura, precipitaciones)
- **Heatmap de estacionalidad**: mes × año, color = pernoctaciones → muestra la evolución de la desestacionalización
- Bar chart de estacionalidad turística con overlay de tendencia anual
- Stacked area chart de segmentos de turistas (leisure / trabajo / MICE) en el tiempo

### Fase 4 — Scatter y correlaciones
- Scatter: densidad VUT vs precio alquiler por barrio (color = barrio, tamaño = población)
- Scatter: renta mediana vs % extranjeros

---

## 🚀 Ideas avanzadas (conceptos diferenciadores)

Estas son ideas que van más allá del choropleth clásico y que harían el proyecto distintivo. Varias se inspiran en proyectos análogos de otras ciudades (referencias al final).

### 1. Índice compuesto de "desplazamiento" / gentrificación por barrio

La aportación más fuerte que puede hacer el proyecto no es mostrar una variable cada vez, sino **construir un índice tipológico** que clasifique cada barrio en categorías de transformación, sobre el modelo del **Urban Displacement Project (UC Berkeley)** y de **Displaced by Design (NCRC)**.

Metodología consolidada (Freeman 2005, adaptada por Ding/Hwang): un barrio es "gentrificable" si parte por debajo de la mediana de renta de la ciudad; está "en gentrificación" si en un periodo dado crece, más que la mediana de la ciudad, tanto en (a) nivel de estudios / renta como en (b) precio alquiler/venta. Variables operativas típicas: renta mediana, valor de la vivienda, alquiler, tasa de vacancia, nivel de estudios.

**Adaptación a Donostia**: combinar 5 variables ya en el proyecto → renta mediana, precio alquiler €/m², % población con estudios superiores, densidad VUT, % extranjeros (aquí a interpretar con cautela: en Donostia parte de los "extranjeros" son expatriados de alto ingreso, no inmigración económica — ver nota ética abajo). Output: cada barrio clasificado (p.ej. "estable", "gentrificación inicial", "gentrificación avanzada", "exclusivo/excluyente") con un mapa categórico + explicación interactiva de los criterios.

> Esto transforma el proyecto de "dashboard de datos" a "herramienta analítica con una tesis" — mucho más memorable.

### 2. La dimensión temporal como protagonista (no solo slider)

Inspirado en **Zurich Time Travel** (Lisa Stähli, ArcGIS JS API + modelo 3D de edificios con año de construcción). Dos variantes posibles:

- **Small multiples temporales**: en vez de un solo slider, mostrar el mismo mapa en 4-6 instantes (p.ej. 2000, 2008, 2015, 2020, 2025) en paralelo → el ojo capta de inmediato la propagación espacial del fenómeno (p.ej. la turistificación expandiéndose desde Parte Vieja-Gros hacia Antiguo y Egia).
- **Animación "play"**: botón que anima la transición año a año, con un contador. Técnicamente fácil con D3 transitions o MapLibre `setPaintProperty` interpolado.
- **Extrusión 3D temporal** (si quieres usar tu base Three.js existente): extruir los barrios en 3D donde la altura = precio alquiler o densidad VUT, animado en el tiempo. Sería el puente natural entre tu stack Three.js y el nuevo proyecto.

### 3. Historia guiada (scrollytelling)

Sobre el modelo de las piezas del **NYT "A Decade of Urban Transformation"**: en vez de dejar al usuario solo ante controles, una narración que se desplaza (scroll-driven) y pilota el mapa: "En 2014 el turismo supera 1,4M de pernoctaciones…" → el mapa resalta Parte Vieja → "…y los precios en el Antiguo empiezan a subir" → el mapa se desplaza al Antiguo. Librerías: Scrollama.js + tu motor de mapas. Excelente para un sitio personal donde quieres comunicar, no solo explorar.

### 4. Indicador de "tensión" alquileres vs salarios

Una de las métricas más elocuentes para "la vida de quien habita": la razón entre el **coste anual del alquiler medio** y la **renta mediana del barrio**. Muestra dónde vivir se está volviendo insostenible para los residentes históricos. Se calcula enteramente con datos ya en el proyecto. Visualización: choropleth con escala que resalta los barrios donde el alquiler supera el 30-40% de la renta (umbral de "housing stress").

### 5. Comparación "ciudad turística vs ciudad vivida"

Idea conceptual fuerte: dos vistas en paralelo del mismo mapa. A la izquierda "Donostia de los turistas" (densidad VUT, hoteles, restaurantes, puntos de interés, fotos Flickr/Instagram geolocalizadas). A la derecha "Donostia de los residentes" (escuelas, centros de salud, servicios sociales, mercados de barrio). El contraste visual cuenta la divergencia entre los dos usos del espacio urbano.

### 6. Modelo de accesibilidad (ciudad de los 15 minutos)

Para cada barrio, calcular la distancia/tiempo a pie a los servicios esenciales (escuela, centro de salud, farmacia, supermercado, parada de bus) usando los GeoJSON de servicios ya disponibles + un motor de routing (OSRM o isócronas con Valhalla/openrouteservice). Visualización: isócronas o choropleth de "completitud de servicios". Medida concreta de la calidad de vida cotidiana.

### 7. Dato textual / cualitativo (avanzado, opcional)

Sentimiento o temas a partir de las propuestas ciudadanas. **Decide Madrid** y proyectos similares han mostrado el valor de integrar la voz de la ciudadanía. Donostia tiene procesos de participación (`participacion-noticias` en el portal open data). Se podría hacer topic modeling sobre las propuestas/quejas ciudadanas por barrio y superponerlas a las métricas objetivas. Avanzado y ruidoso, pero diferenciador.

### ⚖️ Nota ética y metodológica (importante)

Tres advertencias, vistas en todos los proyectos serios de este tipo:

1. **"% extranjeros" no es "gentrificación"**. En Donostia la población extranjera incluye tanto inmigración económica como expatriados acomodados (teletrabajadores, pensionistas europeos). Usar esta variable acríticamente como proxy de gentrificación es incorrecto y potencialmente estigmatizante. Mejor cruzar con renta y nacionalidad específica.
2. **La elección de la definición cambia el resultado**. Como muestra la literatura (HUD Cityscape 2024), existen muchas definiciones de gentrificación y dan mapas distintos. Un proyecto honesto hace explícita la definición elegida e idealmente permite al usuario cambiarla.
3. **Normalizar siempre por población**. Los valores absolutos (delitos, servicios) engañan: un barrio poblado tendrá más de todo. Tasa por 1000 habitantes casi siempre.

### Patrones arquitectónicos de proyectos de referencia

- **CoreData.nyc (NYU Furman Center)**: estandariza 20+ datasets heterogéneos sobre una rejilla geográfica común de indicadores multi-año → este es exactamente el patrón de normalización que necesitas para el problema de los barrios incoherentes. Un único "indicator store" (un CSV/Parquet largo: `barrio_id, año, métrica, valor`) del que beben todas las vistas.
- **Open Data BCN / Observatori del Turisme a Barcelona**: separan el portal de datos de las visualizaciones temáticas. Confirma la decisión de mantener la dataviz como proyecto separado.
- **idealista18 (paquete R)**: ejemplo de dataset inmobiliario geo-referenciado con atributos catastrales — modelo de cómo enriquecer los listings con datos catastrales (aquí: catastro foral de Gipuzkoa).

---

## Notas de implementación

- Usar **GeoJSON** (convertir desde shapefile con `ogr2ogr` o `mapshaper`)
- Preprocesar todos los CSV en Python/pandas → output JSON limpios para el frontend
- **Indicator store unificado**: adoptar el patrón CoreData.nyc — un único dataset "largo" (`barrio_id, año, métrica, valor, unidad, fuente`) en CSV o Parquet, del que beben todas las vistas. Resuelve de raíz el problema de los barrios incoherentes: el join geométrico se hace una sola vez, en ingestión, contra la geometría de referencia. Añadir una métrica nueva = añadir filas, no tocar el frontend.
- Para las choropleth: MapLibre GL JS (si se quiere base map de calles) o D3 puro (si solo mapa vectorial)
- Colores: escala divergente para variaciones (azul=baja, rojo=sube), secuencial para valores absolutos
- Normalizar siempre sobre la geometría de barrios oficial del portal municipal
- Normalizar siempre los conteos por población (tasa por 1000 ab.) antes de mapear

---

## Referencias académicas útiles

- Aguado-Moralejo & Del Campo-Echeverría (2020) — *El fenómeno Airbnb en Donostia-San Sebastián* — CyTET 52(206)
- Etxezarreta-Etxarri et al. (2020) — *Urban touristification in Spanish cities: rental-housing sector in San Sebastian* — análisis econométrico Airbnb vs alquileres
- Boletín AGE (2023) — *The touristification of urban spaces: measurement proposal* — metodología de indicadores a escala de manzana
- Eustat — *Ibiltur: Encuesta de Turismo Receptivo* — serie anual con segmentación por motivo de visita, nacionalidad, gasto medio (`eustat.eus`)
- ICCA — *International Congress Statistics Report* — ranking mundial de ciudades congresuales (Donostia pos. 221 mundial / 112 Europa en 2019)
- Donostia San Sebastián Turismoa — *Memorias anuales* — datos MICE, pernoctaciones, satisfacción (`press.sansebastianturismoa.eus/images/prensa_agentes/pdf/memoria/`)

### Proyectos de dataviz urbana de referencia (para inspiración metodológica y técnica)

- **Urban Displacement Project** (UC Berkeley) — `urbandisplacement.org` — tipología de gentrificación/desplazamiento por census tract, metodología validada con organizaciones comunitarias
- **Displaced by Design** (NCRC, 2025) — `ncrc.org/displaced-by-design` — 50 años de cambio de barrio (1970-2020) con mapa interactivo multivariable
- **CoreData.nyc** (NYU Furman Center) — datahub que estandariza 20+ datasets sobre una rejilla geográfica común — modelo para el indicator store
- **Zurich Time Travel** (Lisa Stähli) — `staehlli.medium.com` — visualización 3D de la transformación urbana en el tiempo, ArcGIS JS API; código en GitHub
- **NYT "A Decade of Urban Transformation, Seen From Above"** (Badger & Bui) — ejemplo de scrollytelling sobre cambio urbano
- **Open Data BCN + Observatori del Turisme a Barcelona** — `opendata-ajuntament.barcelona.cat` — modelo de separación portal-datos / visualizaciones temáticas
- **HUD Cityscape vol.26** — *Mapping Gentrification: A Methodology for Measuring Neighborhood Change* — repaso de las definiciones operativas de gentrificación

---

## Próximos pasos

1. [ ] Descargar GeoJSON de barrios desde `donostia.eus/datosabiertos/catalogo/mapa_auzoak`
2. [ ] Descargar dataset VUT (CSV mensual) y demográfico (CSV anual)
3. [ ] Registrarse para la API key gratuita de AEMET → descargar serie histórica de la estación Igeldo
4. [ ] Buscar snapshot Inside Airbnb para San Sebastián (o solicitar el dataset)
5. [ ] Descargar serie INE EOH mensual para San Sebastián (tabla 2078) → datos de estacionalidad
6. [ ] Descargar Memorias anuales DSS Turismoa (PDF) para extraer datos MICE y perfil de visitantes
7. [ ] Verificar acceso a datos Eustat Ibiltur (motivo de visita, gasto medio por segmento)
8. [ ] Descargar CSV de criminalidad por barrio: `donostia.eus/datosabiertos/catalogo/delitos-guardia/recurso/gua_delitosbarrio_ckan.csv` *(descartado, ver §criminalidad)*
9. [ ] Descargar GeoJSON de centros educativos: `donostia.eus/datosabiertos/catalogo/servicios-educativos`
10. [ ] Descargar SHP de mapas de ruido: `donostia.eus/datosabiertos/catalogo/ruido-total` y `ruido-noche`
11. [ ] Descargar CSV de residuos selectivos: `donostia.eus/datosabiertos/catalogo/residuos`
12. [ ] Descargar CSV del Catastro de Gipuzkoa (Diputación Foral) desde `gipuzkoairekia.eus` — NO el catastro estatal
13. [ ] Buscar serie histórica de modelos lingüísticos A/B/D en `hezkuntza.euskadi.eus`
14. [ ] Script Python de limpieza y join sobre geometría de barrios común
15. [ ] Prototipo de