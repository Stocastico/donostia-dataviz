# Gap analysis — brief v2 vs stato del repo (backlog prioritizzato)

Confronto tra `PROJECT-BRIEF-v2.md` (documento aggiornato) e lo stato implementato.
Serve da **backlog**: lo aggiorneremo man mano che le voci passano a "fatto".

**Stato repo di riferimento:** branch `claude/donostia-dataviz-plan-p7ef1x`,
commit `ede6d1e`. 9 metriche coropletiche per barrio, 3 serie mensili città,
3 indicatori annuali (MICE), export CSV "long", 41 test pipeline + 26 frontend.

> **Avanzamento (aggiornato):** **P0.2 — modulo di join spaziale: COMPLETO** ✅
> - `spatial.py` — point-in-polygon (STRtree) + interpolazione areale
>   `mean`/`sum` + `rate_per_1000` (normalizzazione per popolazione).
> - `gis_io.py` — loader GeoJSON; **riproiezione 25830→4326** (pyproj, validata
>   sul ground-truth reale ETRS89↔WGS84) e **lettura SHP** (pyshp), così anche
>   le fonti **solo-SHP** (es. mappe del rumore) sono ingeribili.
> - Denominatore per-capita condiviso (`population_latest_by_barrio`).
>
> Prima metrica GIS live: **`schools_per_1000`** (centri educativi → join
> spaziale → tasso/1000 ab.), che chiude anche parte di **P2.9**. 58 test
> pipeline. P0.2 non ha più caveat aperti.

---

## 1. Cosa è già fatto e resta valido

| Area del documento | Stato nel repo | Valido? |
|---|---|---|
| **Geometria di riferimento unica** (mapa_auzoak, join su una sola geometria) | `geometry.py` → 19 barrios, `barrio_id` slug stabile + `kod_auzo`; join via `canonical_barrio_id` / `code_to_id` / alias map | ✅ è il fondamento richiesto dal doc |
| Fase 1 — choropleth + slider + tooltip (Δ) + legenda | `ChoroplethMap`, `TimeSlider`, `MetricPicker`, `Legend` | ✅ |
| Fase 2 — confronto 2–3 barrios + marker COVID | `BarrioCompareChart` | ✅ |
| Fase 3 — heatmap mese×anno + trend annuale regressione | `SeasonalityHeatmap` + `AnnualTrendChart` | ✅ |
| Fase 4 — scatter/correlazioni | `ScatterSection` (VUT↔affitto r=0,64; reddito↔%stranieri r=−0,58) | ✅ |
| Abitazioni: renta per barrio | `renta.py` (income_total, gender_gap) | ✅ |
| Abitazioni: **affitto €/m² per barrio** | `rent.py` — Gobierno Vasco EMA (dati reali registrati 2016–24). Migliore di Indomio | ✅ (supera il doc) |
| Turismo: VUT density/count/plazas | `vut.py`, `vut_density.py` | ✅ |
| Demografia: popolazione, % stranieri | `demografia.py` | ✅ |
| Istruzione: livello di studi (% universitari) | `estudios.py` | ✅ (parziale: vedi modelos A/B/D in §3) |
| Clima AEMET Igeldo 1024E (temp+precip+trend) | `aemet_climate.py` | ✅ |
| Stagionalità INE EOH (tabella 2078) | `ine_eoh.py` | ✅ |
| MICE (eventi/partecipanti/ICCA) | `mice.py` curato da fonti citate | ✅ |
| Metriche derivate: touristificazione, gender gap, trend temp | implementate | ✅ |
| **Indicator store "lungo"** | `export_tables.py` → `metrics_long.csv`, `series_long.csv`, `indicators_long.csv`, `barrios.csv` | 🟡 esiste già in forma quasi completa — vedi §2a |

**Nessuna cosa fatta finora viene invalidata dal documento v2.**

---

## 2. Cosa è fatto ma andrebbe rivisto

### a) Architettura indicator store — compatibile, NON serve rifattorizzare (solo evoluzione)
Siamo già ~85% allineati al pattern CoreData.nyc. Già rispettato:
- ✅ Join geometrico una volta sola, in ingestion, contro la geometria di riferimento.
- ✅ "Aggiungere una metrica = aggiungere righe, non toccare il frontend" (dimostrato 6 volte: un nuovo modulo dataset compare via `metrics.json` con zero modifiche al codice mappa).
- ✅ Tabella lunga `barrio_id, period, metric, value, unit` già presente.

Scostamenti leggeri da chiudere (non un rewrite):
1. ✅ **FATTO** — colonna **`source`** aggiunta a `metrics_long.csv`/`series_long.csv` (già presente in `indicators_long.csv`). Le tabelle long ora corrispondono allo schema raccomandato `barrio_id, periodo, metrica, valore, unità, fonte`.
2. La tabella lunga è un *export*, non la sorgente canonica che il frontend legge (frontend usa i `metric_<id>.json` per lazy-load). Per aderire al pattern si può promuovere la tabella lunga a artefatto canonico intermedio. *(opzionale)*
3. **Parquet**: suggerito dal doc; oggi solo CSV. Aggiunta banale con pandas.
4. **Naming periodo**: usiamo `period` (anno / `actual` / `YYYY-MM`); lo store del doc parla di `anno`. Da normalizzare/documentare.
5. Generalizzare il loader "CSV curato → metrica" (oggi solo per MICE) così si aggiungono metriche barrio×anno editando un CSV.

### b) Correzione catastro foral — nessun codice da correggere
Verificato: **nessun riferimento al catastro nel repo** (né statale né foral). Azione preventiva: quando si aggiungerà, usare il **Catastro de la Diputación Foral de Gipuzkoa** (`gipuzkoairekia.eus`, CSV bulk, CC-BY), NON `sedecatastro.gob.es`. Da annotare in `SOURCES.md`.

### c) Nota etica su "% stranieri"
`pct_foreign` oggi è esposta come metrica demografica neutra (non etichettata come gentrificazione). Da fare: avvertenza metodologica nella UI dove compare; e **non** usarla acriticamente nell'indice di gentrificazione (idea #1).

### d) Normalizzazione per popolazione
`vut_density` è già per-1000-ab. Fissare come invariante per i nuovi conteggi (criminalità, servizi): mai valori assoluti su mappa → tasso/1000 (abbiamo già `population`).

### e) Dettaglio minore
Il doc dice "17 barrios"; noi ne abbiamo correttamente 19. Già risolto.

---

## 3. Cosa resta da fare — per priorità

> **Dipendenza bloccante.** "Normalizzazione geometrie barrios sull'indicator store" va distinta:
> - **Dati barrio-attributo** (CSV con colonna barrio): normalizzazione **già pronta** (join codice/nome + alias) → NON bloccati.
> - **Dati GIS** (punti/griglia/poligoni/parcelas): richiedono una capacità che **oggi non abbiamo** — il **join spaziale** (point-in-polygon, interpolazione areale) sulla geometria di riferimento. **Questo è il vero blocco** per le dimensioni GIS.

### 🔴 P0 — Fondamenta (sbloccano il resto)
1. ✅ **FATTO** — Allineato l'indicator store: colonna `source` aggiunta alle tabelle long (schema completo `barrio_id, periodo, metrica, valore, unità, fonte`). Store canonico + Parquet restano opzionali.
2. ✅ **FATTO** — **Modulo di join spaziale** (`spatial.py` + `gis_io.py`): punti/poligoni in GeoJSON/SHP, riproiezione 25830→4326, interpolazione areale, normalizzazione per popolazione. Sblocca tutte le dimensioni GIS.
3. Verificare copertura alias barrio per ogni nuova fonte barrio-grain (es. CSV criminalità) — si fa per-dataset quando lo si aggiunge.

### 🟠 P1 — Alto valore, accesso diretto, barrio-grain (quasi sbloccati)
4. ⛔ **Criminalità per barrio** — **fonte non più disponibile**: il CSV del brief
   dà 403/404 e il dataset non è più nel catalogo CKAN (138 dataset). Da
   rivalutare con la serie municipio Ertzaintza/MIR (non barrio) o se il Comune
   ripubblica il dato. *Era il "miglior ROI", ora bloccato dai dati.*
5. ✅ **FATTO** — **Indice tensione affitto/reddito** (`housing_tension`, idea
   #4): `affitto €/m² × 12 × 30 m²/persona / reddito pro capite × 100`.
   Metrica derivata dai dati già in casa; rivela che lo sforzo è massimo nei
   barrios operai (Altza, Egia, Intxaurrondo), invertendo la mappa degli affitti
   assoluti.
6. **% raccolta differenziata** (`residuos` CSV) → serie città annuale.
7. **Modelos lingüísticos A/B/D** (hezkuntza.euskadi.eus) → serie città (storia identitaria).
8. **Fiscalità** (impuestos/tasas/subvenciones CSV) → serie città.

### 🟡 P2 — Dimensioni GIS (richiedono P0.2)
9. **Equipamientos** (educativi, sanità, socio-assistenziali) come punti → conteggi/accessibilità per barrio.
10. **Mappe rumore** (griglia → interpolazione areale a barrio).
11. **Spazio verde** (% verde per barrio), **ZBE**, **zone sature** (overlay).
12. **Accessibilità 15-minuti** (idea #6): isocrone/distanze ai servizi → motore routing (OSRM/openrouteservice).

### 🟢 P3 — Analitico / differenziante (con le metriche di P1)
13. **Indice composito di gentrificazione** (idea #1): reddito + affitto + istruzione + VUT (+ % stranieri con cautela etica). Quasi tutti gli input esistono già. Definizione esplicita e selezionabile (nota HUD Cityscape).
14. **Dimensione temporale** (idea #2): small multiples + "play" animato; eventuale 3D extrusion (stack Three.js).
15. **Scrollytelling** (idea #3, Scrollama).
16. **Città turistica vs vissuta** (idea #5) — richiede servizi GIS (P2).

### 🔵 P4 — Dati più ostici
17. **Ibiltur** (gasto/segmenti, motivo visita) — tabelle Eustat, municipio.
18. **Catastro foral Gipuzkoa** — CSV bulk parcela → aggregazione spaziale a barrio (richiede P0.2). Fonte foral.
19. **Inside Airbnb** (punti) → join spaziale (P0.2).
20. Qualità aria, biodiversità, fotovoltaico.

---

## Sintesi
Architettura **già allineata** all'indicator store (nessun rewrite); catastro **mai
implementato** → solo da registrare come foral; il vero blocco nuovo è il **modulo
di join spaziale** per i dataset GIS. Criminalità, tensione affitto/reddito, rifiuti,
modelos lingüísticos e l'indice di gentrificazione sono in gran parte già sbloccati.
