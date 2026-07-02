> ⚠️ **ARCHIVADO** — documento histórico: superado por una versión más reciente o ya volcado en la documentación activa. Se conserva como referencia. Punto de entrada actualizado en `../../README.md`.

# Donostia Dataviz — insights de los datos

Síntesis de los hallazgos que emergen de los datos **realmente procesados** en el
pipeline (no anécdotas): cada número viene de las tablas en `../data/` y es
reproducible con `python -m donostia_pipeline.build`. Actualizar al añadir métricas.

> **Avisos metodológicos** (válidos para todo el documento):
> - Los conteos van siempre **normalizados por población** (tasa/1000 hab.).
> - **"% extranjeros" no es "gentrificación"**: en Donostia incluye tanto
>   inmigración económica como expatriados acomodados — leer con cautela, nunca
>   como proxy directo de transformación.
> - Las métricas derivadas tienen supuestos explícitos (ver `SOURCES.md` y
>   `NOTA-METODOLOGICA.md`).

---

## 🏘️ Turismo y turistificación
- Las **viviendas de uso turístico** están fuertemente concentradas en el centro:
  **Erdialdea 664** unidades y **Gros 359** dominan (sobre ~1.490 en toda la ciudad).
- Densidad VUT por 1000 hab.: **Erdialdea 29,9**, **Gros 20,7**, luego Antigua 8,5
  — los barrios centrales son con diferencia los más turistificados.
- **Estacionalidad (pernoctaciones hotel, INE EOH 2005–2026)**: pico estival
  **jul/ago ~245k**, mínimo **ene ~116k**; **2020 (COVID)** es un desplome neto,
  visible como franja pálida; desde 2021 fuerte recuperación **+ desestacionalización**
  (los meses de hombro se "calientan"). Total 2025 ≈ **2,2 millones** de pernoctaciones.

## 🏠 Vivienda
- **Alquiler €/m² (EMA, 2024)**: más caro en el **centro/Erdialdea 16,6**, luego
  **Aiete 16,2** y **Gros 15,9**; el este, más barato. Erdialdea **+29 %** desde 2016.
- **Esfuerzo alquiler/renta** (derivado): **invierte** el mapa de los alquileres
  absolutos. El esfuerzo máximo está en los barrios **obreros** — **Altza 21,9 %**,
  **Egia 21,3 %**, **Intxaurrondo 20,9 %** (2023) — porque las rentas bajas pesan
  más que los alquileres bajos; mínimo en los acomodados **Ategorrieta-Ulia 14,5 %**
  y **Aiete 16,7 %**. Es la señal de "dónde vivir se está volviendo insostenible".

## 💶 Economía y desigualdad
- **Renta per cápita (2023)**: fuerte gradiente — **Aiete ~30.440 €** frente a
  **Altza ~18.371 €** (~1,7×).
- **Brecha de renta de género**: marcada, p. ej. **Aiete ~29,9 %** (renta per
  cápita masculina superior a la femenina).
- **La brecha entre barrios NO se ensancha** (AN-5): el Gini territorial ponderado
  por población es estable (~0,10 en 2016 y ~0,10 en 2023) y el P90/P10 ronda 1,5
  todo el periodo. Lo que cambia no es "cuánto gana cada zona", sino la
  asequibilidad y la composición.

## 👥 Demografía
- **% población extranjera** en aumento en todas partes: p. ej. **Gros 1,3 % (2000)
  → 9,9 % (2025)**. Crece **más rápido en el este obrero** (Intxaurrondo
  +0,92 pp/año; Mirakruz +0,68; Martutene +0,65).
- Correlación **renta ↔ % extranjeros: r = −0,58** (−0,72 sin el centro) — los
  barrios de renta más alta tienen menos residentes extranjeros (y viceversa).
  *No leer como gentrificación (ver aviso).*
- **Estructura por edad (REC-1)**: los barrios **centrales y turísticos son los más
  envejecidos** de los urbanos (índice de vejez Gros **370**, Erdialdea **350**),
  mientras el **este obrero tiene la población adulta más joven** (Intxaurrondo
  **21 %** de 25–39, Loiola). Antigua **envejece rápido** (+203 puntos de índice
  2000→2025); Miramón-Zorroaga **rejuvenece** por desarrollo residencial nuevo.

## 🏫 Educación
- **Estudios universitarios** en aumento: **Aiete 25,3 % (2000) → 35,0 % (2025)**.
- **Centros educativos por 1000 hab.** (join espacial): la normalización cambia la
  historia — **Ibaeta** es primera en valor absoluto (24 centros, campus
  universitario) pero baja a **3ª** per cápita, mientras **Zubieta** (rural, pocos
  habitantes) resulta primera per cápita.

## 🌡️ Clima y cambio climático (AEMET Igeldo, 1981–2025)
- **Calentamiento neto**: tendencia **+0,31 °C/década (R² = 0,39)**; media anual de
  **13,1 °C (1981–85)** a **14,7 °C (2021–25)**, ~**+1,4 °C** en 45 años.
- **Ciclos mensuales por año**: en la viz de líneas, los años recientes
  (rojos/cálidos) quedan visiblemente **por encima** de la envolvente histórica
  (gris) en casi todos los meses — el calentamiento se lee de un vistazo.
- **Días de calor (máx ≥ 30 °C)**: en aumento, **+0,81 días/década**; de los
  ~4–5/año de los 80–90 a los **12–15** de 2003, 2022 y 2023 (2022 = 15).
- **Picos extremos**: la máxima absoluta sube hasta **39,7 °C (2022)** y
  38,6 °C (2003) — valores notables para una localidad costera templada.
- **Precipitación**: sin tendencia significativa (**+40,9 mm/década, R² = 0,06**)
  — muy variable año a año; ~**1.900 mm** en 2024 (ciudad lluviosa).

> **Lectura de conjunto**: media en aumento lento pero claro, **extremos más
> frecuentes e intensos** en los últimos 20–30 años — el signo típico del cambio
> climático, no solo "más calor de media" sino más olas de calor.

## ♻️ Medio ambiente
- **Recogida selectiva** en clara mejora: del **28,8 % (2010)** al **41,0 % (2023)**
  de los residuos urbanos (selectiva + autocompostaje sobre el total). Tendencia de
  sostenibilidad clara, aunque por debajo del objetivo UE (55 %).
  *(2024 excluido por incompleto: "Rechazo" aún no cargado.)*

## 🎪 Turismo MICE
- **Récord 2024**: **188 eventos profesionales**, **259.000 participantes**,
  **50 % internacionales** (Convention Bureau).
- **Congresos internacionales ICCA** (criterios estrictos