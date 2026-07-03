# Plan de cierre — *cuándo el proyecto tiene datos suficientes*

> **Por qué existe este documento.** El `PROJECT-BRIEF-v2.md` cataloga decenas de
> datasets posibles y la estadística pública vasca/española publica más cada año.
> Sin una regla de parada, «recoger un dato más» no termina nunca: cada fuente
> abre otras tres. Este documento fija **qué falta para dar el proyecto por
> terminado** y **cuándo se cierra la puerta a datos nuevos**.
>
> Decisión del usuario (jul-2026): **una última tanda dirigida** de datos y luego
> congelar. Este plan concreta esa tanda y define el «hecho».

---

## 1. Principio de parada

El proyecto **no** es «un dashboard con todos los datos de Donostia». Es **una
tesis con evidencia**: *Donostia se transforma por presión turística y
residencial, de forma desigual sobre una geografía este-obrero / centro-caro*,
articulada en cuatro hipótesis (H1–H4, ver `TESIS-CIUDAD.md`).

De ahí la regla:

> **Un dato entra solo si permite *probar, matizar o refutar* una de H1–H4, o
> corrige un error. No entra porque exista.**

Con este criterio el proyecto ya está **casi completo**: las cuatro hipótesis
tienen al menos una fuente que las interroga (muchas, varias e independientes —
ver la tanda inferencial AN-9…AN-20). Lo que falta es (a) **una laguna real** en
la columna vertebral «tensión residencial» y (b) **rematar y publicar**.

---

## 2. La última tanda dirigida (y su presupuesto)

Dos RECs desbloqueadas, elegidas porque cada una cierra una laguna concreta de
una hipótesis. **Todo lo demás queda fuera** (§4). Presupuesto duro: **si una
fuente no rinde un indicador con grano útil en ~½ jornada de trabajo, se aparca y
se documenta como laguna declarada** — no se fuerza un proxy (misma disciplina
que ya aplicó REC-8/REC-11).

### 2.1 REC-15 · Vivienda protegida (VPO) — ✅ hecho (jul-2026)
- **Resuelto mejor de lo esperado: grano barrio, no municipio.** La fuente viva
  es **Promociones de Etxebide** (Open Data Euskadi, CSV con coords UTM + nº de
  viviendas), geocodificable punto→barrio. Métrica `vpo_dwellings_per_1000`
  (proxy, snapshot). **Hallazgo:** la huella protegida se concentra en el este
  obrero/periférico (Loiola 22,3‰, Amara Berri, Intxaurrondo, Ibaeta) y es cero
  en 14 barrios, incluido el centro caro y Gros → el contrapeso H2/H3 que faltaba.
- Caveat: solo promociones Etxebide (no todo el parque VPO ni el patronato
  municipal) → suelo del parque, no censo. Documentado como proxy (MET-4).

### 2.2 REC-18 · Equipamientos y accesibilidad — ✅ hecho (jul-2026, primer corte)
- **Entregado:** `health_per_1000` (equipamientos de salud, 29 puntos, join
  punto→barrio, por 1000 hab.), el lado «ciudad vivida» de H4 junto a
  `schools_per_1000`. Nuevo tema «Sanità» en el picker.
- **Alcance acotado por el presupuesto:** densidad de servicios, **no** isócrona
  a pie (15-min city queda fuera). Bibliotecas / zonas verdes / socio-asistencial
  no añadidas (un URL dio 500); se suman con el mismo patrón `salud_gis.py` si se
  retoma. Miramón-Zorroaga alto por el hospital con poca población (artefacto
  per cápita, documentado).

> Si el usuario quiere cambiar el par (p. ej. REC-16 comercio-OSM en vez de
> REC-18), la regla §1 sigue mandando: se elige lo que interrogue una hipótesis.

---

## 3. Definición de «hecho» (checklist de cierre)

El proyecto se declara **terminado** cuando todo esto está en verde. Estado a
jul-2026 anotado.

**Datos**
- [x] Cuatro hipótesis H1–H4 con ≥1 fuente que las interroga.
- [x] Última tanda dirigida **cerrada**: REC-15 ✅ (VPO por barrio) + REC-18 ✅
  (salud por barrio). **Puerta a datos nuevos congelada** salvo regla §1/§4.
- [x] Toda métrica con ficha de confianza (observado/derivado/proxy, MET-4).
- [x] Crudos no versionados; input curado + `FUENTES.md` + `descargar_raw.sh`.

**Análisis**
- [x] Tanda inferencial AN-9…AN-20 (blindaje de índice, correlaciones, lead/lag).
- [ ] Cada REC de la última tanda con su lectura frente a H1–H4.
- [ ] **Indicador de accesibilidad residencial** (% hogares que superarían el 30 %
  de esfuerzo) — pieza Code pendiente de la espina «tensión residencial»,
  derivable de renta+alquiler ya en el proyecto (no requiere dato nuevo).

**Frontend (`web/`)**
- [x] Mapa coroplético + slider + play + small multiples + dos-ciudades.
- [x] Ficha de país por barrio (REC-21-web).
- [ ] **A11y del app React**: foco de teclado, texto alternativo / tabla-espejo de
  los mapas, leyendas legibles sin color (paralelo a la pasada de `historias.html`).
- [ ] Métrica(s) de la última tanda seleccionables en el picker (si son coropléticas).

**Narrativa (`output/`)**
- [x] 7 historias + epílogo con H1–H4 y sus tests propuestos.
- [ ] Integración narrativa de la última tanda (Cowork).
- [ ] `resumen.md` / `TESIS-CIUDAD.md` mencionan la última tanda.

**Publicación** *(no empezado — el verdadero «último» paso)*
- [ ] Build de producción desplegado (dónde: GitHub Pages / Netlify — decidir).
- [ ] README con enlace vivo + cómo reproducir el pipeline.
- [ ] Pasada final de enlaces y de contraste de todo el sitio.

**Opcional (no bloquea el cierre)**
- [ ] DOC-6 working paper metodológico.
- [ ] VIZ-9 scrollytelling.
- [ ] AN-6 reabierto con más serie REATE (H1) — depende de que pase el tiempo.

---

## 4. Congelado / fuera del alcance (con motivo)

Tras la última tanda, **estas no vuelven a abrirse** salvo que aparezca una
fuente que interrogue una hipótesis:

| REC | Estado | Motivo del cierre |
|---|---|---|
| REC-6 movilidad DBus | cerrado | fuente dada de baja (403, 0 resultados CKAN) |
| REC-8 catastro foral | congelado | sin barrio ni coordenadas; geocodificación fuera de presupuesto |
| REC-11 locales vacíos | congelado | sin fuente pública verificable (campo `Om` sin manual) |
| REC-16 comercio OSM | fuera de la tanda | ruidoso; REC-7 ya da el proxy a ciudad |
| REC-19 percepción ciudadana | fuera | probable grano municipio; capa subjetiva, no toca H1–H4 |
| REC-20 cajón de ideas | fuera | menor prioridad por definición |
| Criminalidad, €/m² venta, «índice de gentrificación» caja negra | descartado firme | ver `BACKLOG.md` §Descartado |

**Regla de gobernanza post-congelación:** cualquier dato nuevo propuesto pasa por
una sola pregunta — *¿qué hipótesis H1–H4 prueba, matiza o refuta?* Si la
respuesta es «ninguna, pero es interesante», va a un `IDEAS-FUTURO.md`, no al
pipeline. Esto evita que el proyecto crezca sin cerrarse.

---

## 5. Secuencia sugerida hasta el cierre

1. ~~**REC-15 VPO**~~ ✅ hecho (grano barrio).
2. ~~**REC-18 accesibilidad**~~ ✅ hecho (`health_per_1000`).
3. **Indicador de accesibilidad residencial** (% >30 % esfuerzo) — sin dato nuevo.
4. **A11y del app React** — cierra el frente de accesibilidad *(dejado para el
   final por decisión del usuario)*.
5. **Integración narrativa** de 1–3 (Cowork) + `resumen`/`TESIS` al día.
6. **Publicar** (deploy + README) → **cierre**.

Pasos 1–4 son Code; 5 es Cowork; 6 es conjunto. Con esto la casilla «Publicación»
del §3 se completa y el proyecto queda **terminado, no abandonado**.
