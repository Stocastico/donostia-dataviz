# Plan de recolección de datos — tareas REC (verificado)

> **Qué es este documento.** Convierte las tareas de recolección del backlog
> (`GAP-ANALYSIS.md` §3.A) en especificaciones de adquisición **verificadas
> online en junio 2026**: para cada fuente, si existe y es accesible hoy, su
> handle/URL exacto, formato, granularidad, cobertura temporal, columnas clave,
> licencia y los pasos concretos para integrarla.
>
> **Alcance.** Este proyecto es solo-documentación: aquí se *define y verifica*
> la adquisición, **no se modifica el pipeline ni se descargan datos**. Las
> fuentes ya cableadas están en `SOURCES.md`; esto cubre solo lo **pendiente**.
> Fuentes verificadas al final (§ Fuentes).

**Leyenda de estado:**
✅ disponible y accesible · 🟡 disponible con *caveats* (granularidad/formato) ·
🔴 difícil / requiere extracción manual · ⛔ descartada.

---

## Resumen

| Tarea | Dimensión | Estado | Granularidad real | Sprint |
|---|---|---|---|---|
| REC-1 | Edad / envejecimiento | ✅ | **barrio** (dataset propio) | B |
| REC-2 | Ruido | ✅ | barrio (vía join espacial) | B |
| REC-3 | Fiscalidad | ✅ | ciudad | B |
| REC-4 | Inside Airbnb | ✅ | punto → barrio | C |
| REC-5 | Trabajo / paro | 🟡 | ciudad (posible barrio 2016–19) | F |
| REC-6 | Movilidad (DBus/Dbizi) | 🟡 | por línea/parada (no barrio directo) | F |
| REC-7 | Tejido comercial | 🔴 | proxy vía catastro/IAE | F |
| REC-8 | Catastro foral | ✅ | parcela → barrio | F |
| REC-9 | Modelos lingüísticos | 🟡 | provincia/municipio (no barrio) | F |
| REC-10 | Ibiltur (gasto/segmentos) | 🟡 | municipio, tablas | F |
| REC-X | Criminalidad por barrio | ⛔ | — (descartada) | — |

**Conclusión de la verificación:** las cuatro tareas de los sprints B–C
(edad, ruido, fiscalidad, Inside Airbnb) están **confirmadas y accesibles hoy**;
ninguna depende de fuentes muertas. Los *caveats* de granularidad que anticipaba
el feedback consolidado se confirman: modelos lingüísticos y trabajo son
mayoritariamente municipales/provinciales, y movilidad viene por línea (no por
barrio). Edad, en cambio, es **mejor de lo esperado**: hay dataset propio por
barrio.

---

## Sprint B — quick wins confirmados

### REC-1 ✅ Estructura por edad por barrio
- **Fuente:** Donostia Open Data — *Población por edad y género* (Padrón).
  Dataset `demografia-piramideedad`; recurso CSV por barrio
  `demografiapiramideedadbarrio.csv`.
- **Formato:** CSV (CKAN). **Geo:** barrio. **Tiempo:** anual (serie larga,
  alineada con el resto del padrón). **Tramos:** quinquenales.
- **Columnas esperadas:** año, código de barrio, tramo de edad, sexo, nº personas.
- **Licencia:** open data municipal (CKAN Donostia).
- **Integración:** mismo join por `AuzoKodea` que `demografia.py`; derivar
  **índice de envejecimiento** (pob ≥65 / pob <15 ×100), **cuota 25–40**, edad
  mediana y su evolución. *No requiere join espacial ni alias nuevos.*
- **Nota:** es un dataset **distinto** del de nacionalidad ya integrado
  (`demografianacionalidadbarrio.csv`); no es "comprobar si ya está", es añadir
  este CSV.

### REC-2 ✅ Ruido por barrio
- **Fuente:** Donostia Open Data — `ruido-noche` y `ruido-total` (mapas
  estratégicos de ruido).
- **Formato:** **SHP** (rejilla) + WMS. **CRS:** ETRS89 / UTM 30N **EPSG:25830**
  → el módulo `gis_io` ya reproyecta a 4326. **Tiempo:** snapshots **2008, 2017,
  2022** (actualización bienal). **Geo origen:** rejilla; → barrio por
  interpolación areal (`spatial.py`).
- **Columnas esperadas:** nivel sonoro por celda (rangos dB, p.ej. Lden/Lnight).
- **Licencia:** open data municipal.
- **Integración:** P0.2 ya soporta SHP+reproyección+interpolación areal →
  **dB medio nocturno por barrio**. Cruce de alto valor con densidad VUT/Airbnb
  (relato turismo↔ruido en Parte Vieja/Gros).

### REC-3 ✅ Fiscalidad municipal
- **Fuente:** Donostia Open Data — `impuestos_tipo` (recurso CSV
  `pfi_impuestos_tipo_ciudad_ckan.csv`), `tasas_tipo` (CSV ciudad) y
  `subvenciones`.
- **Formato:** CSV. **Geo:** **ciudad** (no barrio). **Tiempo:** recibos por
  tipo, desglose mensual/anual.
- **Caveat:** subvenciones puede tener pocos años cargados (se vieron 2020/2021);
  verificar cobertura antes de prometer serie larga.
- **Integración:** reutiliza la **viz genérica de indicadores anuales** ya
  existente (`IndicatorsSection`). Casi inmediato. Es indicador-ciudad, no mapa.

---

## Sprint C — presión turística real

### REC-4 ✅ Inside Airbnb
- **Fuente:** Inside Airbnb — página de región **Euskadi**
  (`insideairbnb.com/euskadi/`), filtrar San Sebastián (~1.496 listings activos
  a 2025; cifra coherente con los VUT del proyecto).
- **Formato:** CSV/GeoJSON: `listings.csv` (punto lat/lon + atributos),
  `reviews.csv`, `calendar.csv`. **Geo:** punto → barrio (join espacial).
  **Tiempo:** snapshots periódicos; **`reviews.csv` da fecha por reseña**.
- **Licencia:** Inside Airbnb (CC BY 4.0; revisar términos de la descarga).
- **Integración:**
  1. `listings` → join espacial (P0.2) → **densidad Airbnb por barrio**
     (comparar con VUT legales: los VUT son solo una fracción).
  2. `reviews` por mes → **proxy de serie temporal de ocupación por barrio** →
     **desbloquea el lead/lag (AN-6)** hoy imposible con VUT (que es snapshot).
- **Caveat ético/metodológico:** reseñas ≠ ocupación real; documentar como proxy
  (ficha de confianza, MET-4).

---

## Sprint F — dimensiones difíciles / granularidad limitada

### REC-5 🟡 Trabajo / paro / sectores
- **Fuentes:** Eustat (*paro registrado por ámbitos territoriales*, *tasa de
  paro por capitales*, LANBIDE), Donostia data (sección *enplegua*), SEPE.
- **Granularidad:** mayormente **municipio/capital**. ⚠️ *Pista a verificar:* el
  portal Donostia data menciona paro por **sexo/nacionalidad/edad a nivel barrio
  y unidad menor para 2016–2019** (fuente Eustat) — si se confirma, habría una
  ventana barrio-nivel, aunque corta. Resto: serie ciudad.
- **Integración:** como **contexto-ciudad** (indicador), salvo que se confirme la
  ventana 2016–19 por barrio. No prometer coropleta sostenida.

### REC-6 🟡 Movilidad (DBus / Dbizi)
- **Fuentes:** Donostia Open Data (tema transporte; viajeros DBus totales desde
  2011), Open Data Euskadi *Autobusen erabilera (DBus)* (por mes/hora/línea),
  WMS transporte (estaciones Dbizi).
- **Granularidad:** **por línea/parada**, no por barrio. Ej.: 2025 línea 13-Altza
  4,20 M viajes; 28-Amara-Ospitaleak 4,16 M; 5-Benta Berri 3,13 M.
- **Caveat:** asignar líneas/paradas a barrios es posible pero **imperfecto**
  (una línea cruza varios barrios). Verificar agregabilidad antes de prometer
  coropleta; alternativa: densidad de paradas por barrio (join espacial de
  paradas, sí es limpio) + viajeros por línea como contexto.

### REC-7 🔴 Tejido comercial (sustitución residente→turista)
- **Realidad:** **no hay** dataset abierto limpio de licencias por categoría y
  barrio. Requiere proxy:
  - **Bajos comerciales vía catastro foral** (REC-8): uso de los locales en
    planta baja por barrio.
  - **IAE/CNAE** (Eustat *Actividades Económicas*): nº de establecimientos por
    actividad, granularidad a confirmar.
- **Estado:** coste medio-alto; narrativamente potente pero **no** quick win.

### REC-8 ✅ Catastro Foral de Gipuzkoa
- **Fuente:** **gipuzkoairekia** — *Bienes Inmuebles de Naturaleza Urbana
  (DONOSTIA-SAN SEBASTIAN)*. **NO** el catastro estatal (`sedecatastro.gob.es`),
  que no cubre territorios forales.
- **Formato:** CSV (dos ficheros: *locales*; *parcelas y unidades
  constructivas*). **Geo:** parcela → barrio (join espacial, P0.2).
  **Actualización:** cada 15 días. **Licencia:** **CC BY**.
- **Usos:** superficie construida por barrio → **m²/persona real** para mejorar
  `housing_tension` (MET-1); valor catastral → **proxy de venta €/m²** (relativo,
  defendible); uso de bajos → insumo de REC-7.

### REC-9 🟡 Modelos lingüísticos A/B/D (euskera)
- **Fuentes:** Eustat / Gobierno Vasco — *Alumnado matriculado… por modelo
  lingüístico* (tablas; serie histórica desde 1983/84) y *Mapa Sociolingüístico*
  (V 2011, VI 2016).
- **Granularidad:** **Territorio Histórico / provincia / municipio**, a veces
  centro escolar. **No por barrio.** El Mapa Sociolingüístico da competencia/uso
  del euskera por municipio (y a veces sección censal → agregable a barrio con
  esfuerzo).
- **Integración:** tratar como **serie ciudad/Gipuzkoa** (historia identitaria),
  no forzar narrativa por barrio que la fuente no sostiene.

### REC-10 🟡 Ibiltur (Eustat) — gasto y segmentos
- **Fuente:** Eustat — *Ibiltur (Encuesta de Turismo Receptivo)*: motivo de
  visita, nacionalidad, gasto medio por segmento (turista alojado /
  excursionista / negocios-MICE).
- **Granularidad:** municipio/zona, anual; **tablas** (extracción semi-manual).
- **Integración:** indicadores-ciudad; permite descomponer gasto total y separar
  segmentos (gasto MICE ≫ leisure).

---

## Descartada

### REC-X ⛔ Criminalidad por barrio
Descartada formalmente (decisión junio 2026). El CSV de la Guardia Municipal ya
no está en el catálogo (403/404); la escala sub-municipal está blindada por
protección de datos. Alternativas solo municipales (Portal Estadístico de
Criminalidad del MIR; Ertzaintza) o proxies (quejas ciudadanas, locales vacíos),
fuera del alcance actual. No se invierte esfuerzo en un equivalente por barrio.

---

## Próximos pasos sugeridos (orden de ejecución)

1. **REC-1, REC-2, REC-3** (Sprint B): fuentes confirmadas y baratas. Definir el
   contrato de datos de cada una (columnas → métrica) en `DATA-CONTRACT.md`.
2. **REC-4** (Sprint C): descargar snapshot de Inside Airbnb y `reviews.csv`;
   define la métrica de densidad por barrio y la serie-proxy mensual.
3. **REC-8** cuando se aborde MET-1 (m²/persona real) o el proxy de venta.
4. El resto (REC-5/6/7/9/10) como **contexto-ciudad** o proxies, sin prometer
   coropleta por barrio salvo verificación puntual (ventana paro 2016–19).

> Estas son tareas de **definición**: el siguiente paso de implementación
> (descarga + cableado en el pipeline) implica tocar código, que este proyecto
> mantiene fuera de alcance salvo decisión explícita.

---

## Fuentes (verificadas, junio 2026)

- Donostia Open Data — Población por edad y género por barrio: [demografia-piramideedad](https://www.donostia.eus/datosabiertos/catalogo/demografia-piramideedad)
- Donostia Open Data — Mapa de ruido (noche): [ruido-noche](https://www.donostia.eus/datosabiertos/catalogo/ruido-noche) · [Medio Ambiente — Mapa de ruido](https://www.donostia.eus/ataria/es/web/ingurumena/ruido/mapa-de-ruido)
- Donostia Open Data — Emisión de impuestos por tipo (CSV): [impuestos_tipo](https://www.donostia.eus/datosabiertos/catalogo/impuestos_tipo/recurso/pfi_impuestos_tipo_ciudad_ckan.csv)
- Inside Airbnb — Euskadi (San Sebastián): [insideairbnb.com/euskadi](https://insideairbnb.com/euskadi/)
- gipuzkoairekia — Bienes Inmuebles de Naturaleza Urbana (Donostia): [catastro foral](https://www.gipuzkoairekia.eus/es/datu-irekien-katalogoa/-/openDataSearcher/detail/detailView/f249fd69-9765-4850-9bf8-c3ad457d848e)
- Eustat — Alumnado por modelo lingüístico (avance 2025/26): [tablas Eustat](https://www.eustat.eus/elementos/ele0002400/ti_alumnado-matriculado-en-ensenanzas-de-regimen-general-no-universitarias-en-la-ca-de-euskadi-por-territorio-historico-y-nivel-de-ensenanza-segun-titularidad-del-centro-y-modelo-linguistico-avance-de-datos-202526/tbl0002427_i.html) · [VI Mapa Sociolingüístico 2016](https://www.eustat.eus/elementos/ele0018800/vi-mapa-sociolinguistico/inf0018828_c.pdf)
- Donostia data — Transporte DBus: [donostia-data/dbus](https://www.donostia.eus/ataria/es/web/donostia-data/dbus) · Open Data Euskadi — [Autobusen erabilera (DBus)](https://opendata.euskadi.eus/catalogo/-/autobusen-erabilera-dbus/)
- Eustat — Paro registrado por ámbitos territoriales (LANBIDE): [tabla Eustat](https://www.eustat.eus/elementos/ele0000800/Paro_registrado_en_la_CA_de_Euskadi_por_ambitos_territoriales_segun_sexo_y_sector_de_actividad_LANBIDE/tbl0000854_c.html) · Donostia data — [Empleo](https://www.donostia.eus/ataria/es/web/donostia-data/enplegua)
