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
