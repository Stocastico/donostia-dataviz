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

### 2.1 REC-15 · Vivienda protegida (VPO) — *prioridad 1*
- **Qué hipótesis toca:** H2/H3 y la espina «tensión residencial». Pregunta:
  ¿amortigua la VPO la presión de alquiler, y dónde? Es el contrapeso que hoy
  falta al relato de accesibilidad (MET-1 mide la presión; nada mide el alivio).
- **Fuente candidata:** Observatorio Vasco de la Vivienda (Etxebide / Gobierno
  Vasco) y Open Data Euskadi. **Primer paso del sprint = localizar el recurso
  vivo** (el endpoint CKAN estándar de `opendata.euskadi.eus` no respondió en la
  probe de jul-2026; usar el buscador del portal o el Observatorio directamente).
- **Grano esperado:** probablemente municipio, no barrio (como REC-5/7/9). Aun a
  grano ciudad cierra la laguna: serie de VPO / adjudicaciones / demanda
  registrada. Si hubiera grano barrio, es coroplética.
- **Riesgo:** que solo exista a grano C.A. de Euskadi → seguiría valiendo como
  indicador de ciudad, con el caveat de grano documentado.

### 2.2 REC-18 · Equipamientos y accesibilidad — *prioridad 2*
- **Qué hipótesis toca:** el lado «ciudad vivida» de H4 / de las dos ciudades
  (VIZ-10). Un **índice de accesibilidad por barrio** (distancia/# de
  equipamientos esenciales) cruzable con renta/tensión da la cara de servicios
  que hoy solo está insinuada (`schools_per_1000`).
- **Fuente:** Donostia Open Data — equipamientos GIS. **Verificado vivo
  (jul-2026):** `servicios-salud/osasunekipamenduak.json` responde 200. Faltan por
  confirmar los recursos de socio-asistencial / bibliotecas / zonas verdes (un
  URL probado dio 500 → localizar el nombre correcto en el catálogo).
- **Método:** ya existe el join espacial punto→barrio en el pipeline
  (`spatial.BarrioIndex`, usado por `educacion_gis`, `ruido_gis`). Un
  «# equipamientos / 1000 hab.» por barrio es coroplético y de bajo riesgo; una
  isócrona a pie real (15-min city) es mayor esfuerzo y **queda fuera del
  presupuesto** salvo que sobre tiempo.

> Si el usuario quiere cambiar el par (p. ej. REC-16 comercio-OSM en vez de
> REC-18), la regla §1 sigue mandando: se elige lo que interrogue una hipótesis.

---

## 3. Definición de «hecho» (checklist de cierre)

El proyecto se declara **terminado** cuando todo esto está en verde. Estado a
jul-2026 anotado.

**Datos**
- [x] Cuatro hipótesis H1–H4 con ≥1 fuente que las interroga.
- [ ] Última tanda dirigida cerrada (REC-15 + REC-18) **o** cada una aparcada con
  laguna declarada (§2).
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

1. **REC-15 VPO** — localizar fuente viva → 1 indicador ciudad (o barrio) + tests.
2. **REC-18 accesibilidad** — # equipamientos/1000 hab. por barrio (join ya existe).
3. **Indicador de accesibilidad residencial** (% >30 % esfuerzo) — sin dato nuevo.
4. **A11y del app React** — cierra el frente de accesibilidad.
5. **Integración narrativa** de 1–3 (Cowork) + `resumen`/`TESIS` al día.
6. **Publicar** (deploy + README) → **cierre**.

Pasos 1–4 son Code; 5 es Cowork; 6 es conjunto. Con esto la casilla «Publicación»
del §3 se completa y el proyecto queda **terminado, no abandonado**.
