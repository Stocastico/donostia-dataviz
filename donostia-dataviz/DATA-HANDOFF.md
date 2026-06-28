# Donostia Dataviz — documento di handoff per revisione esterna

> **Scopo di questo documento.** È un riepilogo autosufficiente del progetto
> "Donostia Dataviz" da passare a un'altra IA per una **revisione critica**.
> Vorrei sapere: (1) **mancano dimensioni di dati importanti?** (2) si possono
> **estrarre altri insight** dai dati che già abbiamo? (3) **dove altro** posso
> prendere dati (in particolare per le fonti che si sono rivelate non
> disponibili)? (4) **miglioramenti metodologici**? (5) quali **analisi avanzate**
> conviene prioritizzare? Le domande puntuali sono in fondo (§7).

---

## 1. Cos'è il progetto

Dashboard interattiva (React + Vite + TypeScript; MapLibre per le coropletiche,
Recharts/D3 per i grafici) che mostra l'evoluzione di **Donostia / San Sebastián**
(Gipuzkoa, Paesi Baschi) **per barrio** e nel tempo. Pipeline dati in
**Python/pandas** che trasforma fonti pubbliche aperte in JSON/CSV statici; il
frontend non ha dipendenze runtime (legge dati committati).

**Principi architetturali adottati:**
- **Indicator store unificato**: tabelle "lunghe" tidy
  (`barrio_id, periodo, metrica, valore, unità, fonte`) in CSV — riusabili da
  qualsiasi linguaggio. Aggiungere una metrica = aggiungere righe, **nessuna
  modifica al frontend**.
- **Geometria di riferimento unica**: i 19 barrios ufficiali (`mapa_auzoak`);
  ogni dataset fa join su `barrio_id` (per codice o nome, con alias) — una sola
  volta, in fase di ingestion. Per i dati GIS senza campo barrio c'è un **modulo
  di join spaziale** (point-in-polygon, interpolazione areale, riproiezione
  EPSG:25830→4326).
- **Normalizzazione per popolazione**: i conteggi vanno sempre per 1000 abitanti.
- **Provenienza esplicita**: ogni valore porta la sua fonte.

---

## 2. Dimensioni dei dati acquisiti (stato attuale)

Legenda granularità: **barrio** = 19 quartieri; **città** = livello municipio.

### 🏠 Abitazioni
| Dato | Fonte | Geo | Tempo | Output |
|---|---|---|---|---|
| Affitto medio €/m² | Gobierno Vasco — EMA/EMAL (contratti registrati reali) | barrio | 2016–2024 | metrica `rent_eur_m2` |
| Reddito disponibile pro capite | Eustat (via Open Data Donostia `eustat_renta`) | barrio | 2016–2023 | `income_total` |
| Divario di reddito di genere | derivato da renta per genere | barrio | 2016–2023 | `income_gender_gap` |
| **Sforzo affitto/reddito** (housing stress) | derivato (affitto×12×30 m²/persona ÷ reddito) | barrio | 2016–2023 | `housing_tension` |

### 🏘️ Turismo
| Dato | Fonte | Geo | Tempo | Output |
|---|---|---|---|---|
| Viviendas uso turístico (VUT/HUT) — n° e posti letto | Open Data Donostia (censo) | barrio | snapshot | `vut_count`, `vut_plazas` |
| Densità VUT per 1000 ab. | derivato (VUT/popolazione) | barrio | snapshot | `vut_density` |
| Pernottamenti hotel | INE — EOH (wstempus tab. 2078) | città | mensile 2005–2026 | serie `overnight_stays` |
| MICE: eventi, partecipanti, congressi ICCA | Convention Bureau / ICCA (curato, citato per riga) | città | annuale | indicatori `mice_*` |

### 👥 Demografia
| Dato | Fonte | Geo | Tempo | Output |
|---|---|---|---|---|
| Popolazione residente | Open Data Donostia (demografia-origen) | barrio | 2000–2025 | `population` |
| % popolazione straniera | stessa fonte | barrio | 2000–2025 | `pct_foreign` |

### 🏫 Istruzione
| Dato | Fonte | Geo | Tempo | Output |
|---|---|---|---|---|
| % con studi universitari | Open Data Donostia (nivel estudios) | barrio | 2000–2025 | `pct_university` |
| Centri educativi per 1000 ab. | Open Data Donostia (GeoJSON punti) — **join spaziale** | barrio | snapshot | `schools_per_1000` |

### 🌡️ Clima
| Dato | Fonte | Geo | Tempo | Output |
|---|---|---|---|---|
| Temperatura media mensile | AEMET — stazione Igeldo `1024E` | città (1 stazione) | mensile 1981–2025 | `temp_avg` |
| Temperatura massima assoluta mensile | AEMET (`ta_max`) | città | mensile 1981–2025 | `temp_max` |
| Precipitazioni mensili | AEMET (`p_mes`) | città | mensile 1981–2025 | `precip` |
| Giorni caldi (max ≥ 30 °C) | AEMET (`nt_30`) | città | mensile 1981–2025 | `hot_days_30` |

### ♻️ Ambiente
| Dato | Fonte | Geo | Tempo | Output |
|---|---|---|---|---|
| Tasso di raccolta differenziata | Open Data Donostia (residuos) | città | annuale 2010–2023 | indicatore `recycling_rate` |

**Totale attuale:** 11 metriche coropletiche per barrio · 5 serie mensili città ·
4 indicatori annuali città.

---

## 3. Tipi di analisi e visualizzazioni realizzate

- **Coropletica per barrio** con slider temporale, legenda, tooltip con Δ
  rispetto all'anno precedente; scala sequenziale (assoluti) o divergente (Δ).
- **Confronto barrios**: line chart di 2–3 barrios su una metrica, con marker
  COVID-19 (2020).
- **Scatter / correlazioni**: due metriche qualsiasi all'ultimo anno, punti
  dimensionati per popolazione, **coefficiente di Pearson** calcolato dal vivo.
- **Serie temporali città** (mese × anno):
  - **heatmap** stagionalità (palette per serie: calda/blu);
  - **cicli mensili per anno** (una linea/anno, passato in grigio, ultimi anni
    caldi, ultimo anno in rosso);
  - **warming stripes** (anomalia annuale, blu→rosso);
  - **trend annuale con regressione lineare** (pendenza per decennio + R²).
- **Indicatori annuali**: bar chart (MICE) e line chart generico (raccolta
  differenziata); stat card per i valori chiave.
- **Metriche derivate** calcolate combinando le altre (densità VUT, gender gap,
  tension affitto/reddito) e **join spaziale** GIS (point-in-polygon,
  interpolazione areale `mean`/`sum`, riproiezione 25830→4326, lettura SHP).
- **Export tidy CSV** di tutto (per riuso in altri stack/linguaggi).

---

## 4. Insight principali ottenuti (dai dati reali)

- **Touristificazione concentrata nel centro**: Erdialdea (664 VUT) e Gros (359)
  dominano; densità VUT Erdialdea 29,9 e Gros 20,7 per 1000 ab.
- **Pressione abitativa "invertita"**: l'affitto assoluto è massimo in
  centro/Aiete, ma lo **sforzo affitto/reddito** è massimo nei barrios **operai**
  (Altza 21,9%, Egia 21,3%, Intxaurrondo 20,9% nel 2023) perché i redditi bassi
  pesano più degli affitti bassi.
- **Gradiente di reddito** forte: Aiete ~30.440 € vs Altza ~18.371 € (2023);
  **gender income gap** marcato (Aiete ~29,9%).
- **Correlazioni**: densità VUT ↔ affitto **r = 0,64**; reddito ↔ % stranieri
  **r = −0,58** (da leggere con cautela, vedi §5).
- **Stagionalità turistica**: picco estivo ~245k pernottamenti, minimo invernale
  ~116k; crollo COVID 2020; ripresa + **de-stagionalizzazione** post-2021;
  ~2,2 M pernottamenti nel 2025.
- **Cambiamento climatico (Igeldo 1981–2025)**: riscaldamento **+0,31 °C/decennio**
  (media 13,1→14,7 °C); **giorni caldi ≥30 °C in aumento** (+0,81/decennio; 12–15
  nel 2003/2022/2023 vs 4–5 negli anni '80–'90); **picchi** fino a **39,7 °C
  (2022)**. Precipitazioni senza trend (alta variabilità).
- **Sostenibilità**: raccolta differenziata 28,8% (2010) → 41,0% (2023), ancora
  sotto gli obiettivi UE (55%).
- **MICE**: record 2024 con 188 eventi / 259.000 partecipanti (50% internazionali).

---

## 5. Metodologia e cautele

- **"% stranieri" ≠ "gentrificazione"**: a Donostia include sia immigrazione
  economica sia espatriati benestanti — mai usata come proxy diretto.
- **Sempre normalizzare per popolazione** (tasso/1000) prima di mappare conteggi.
- **Metriche derivate con assunzioni esplicite** (es. tension: 30 m²/persona;
  affitto EMA = solo locatari mentre il reddito copre tutti i residenti → indice
  *relativo*, non budget familiare preciso).
- **Una sola geometria di riferimento** per evitare il problema dei barrios
  incoerenti tra dataset comunali.
- Fonti tecniche: AEMET OpenData (endpoint mensile, finestre 3 anni, API key
  gratuita); INE wstempus (tabella 2078); Gobierno Vasco EMA (xlsx); Open Data
  Donostia (CKAN: CSV/GeoJSON/SHP).

---

## 6. Dimensioni NON ancora coperte / gap noti

**a) Fonti che si sono rivelate NON disponibili / spostate (servono alternative):**
- **Criminalità per barrio** (Guardia Municipal): il CSV indicato nei piani non
  è più nel catalogo CKAN (403/404; rimosso/riorganizzato ~2026). Alternativa
  nota solo a livello **municipio** (Ertzaintza / Ministerio del Interior, portal
  `estadisticasdecriminalidad.ses.mir.es`).
- **Modelos lingüísticos A/B/D** (euskera): non nel portale Donostia; fonte è
  **Gobierno Vasco / Eustat** (hezkuntza.euskadi.eus), a livello città/centro.
- **Prezzi di vendita €/m²** per barrio: non aperti; Indomio (scraping, ToS) o
  Eustat a livello municipio.

**b) Dati disponibili ma non ancora integrati:**
- **Fiscalità municipale** (impuestos_tipo, tasas_tipo, subvenciones) — CSV nel
  catalogo, città, annuale. *Pronti da integrare (viz indicatori già esiste).*
- **Rumore** (`ruido-noche/dia/tarde/total`, SHP griglia, EPSG:25830) — sbloccato
  dal modulo di join spaziale (interpolazione areale → dB per barrio). Alto
  valore qualità-vita (Parte Vieja/Gros).
- **Sanità e servizi sociali** (servicios-salud, servicio-social — punti/zone
  GeoJSON/SHP) — come le scuole (conteggio/accessibilità per barrio).
- **Spazio verde, ZBE, zone sature commerciali** (poligoni GIS).
- **Mobilità** (passeggeri DBus, parcheggi).
- **Catastro foral di Gipuzkoa** (`gipuzkoairekia.eus`, CSV bulk parcela — NON il
  catastro statale): valori catastali, dati fisici immobili → aggregabili a barrio.
- **Inside Airbnb** (punti geolocalizzati) → densità Airbnb per barrio.

**c) Dimensioni del piano originale non ancora toccate:**
- **Occupazione / settori lavorativi / disoccupazione / salari** (Eustat/SEPE).
- **Gasto turístico e segmentazione visitatori** (Eustat **Ibiltur**: motivo
  visita, nazionalità, spesa media per segmento turista/excursionista/MICE).
- **Qualità dell'aria, biodiversità, potenziale fotovoltaico** (medio ambiente).
- **Indice di invecchiamento, natalità, speranza di vita** (demografia/Eustat).

**d) Analisi avanzate proposte ma non realizzate:**
- **Indice composito di gentrificazione/desplazamiento** per barrio (modello
  Urban Displacement Project / NCRC), combinando reddito + affitto + istruzione +
  densità VUT (+ % stranieri con cautela). *Quasi tutti gli input già esistono.*
- **Dimensione temporale come protagonista**: small multiples per anno,
  animazione "play", 3D extrusion (altezza = affitto/densità).
- **Scrollytelling** (narrazione che pilota la mappa).
- **Modello 15-minute city** (accessibilità ai servizi via routing/isocrone).
- **Confronto "città turistica vs città vissuta"** (due mappe affiancate).

---

## 7. Domande puntuali per l'IA revisora

1. **Dimensioni mancanti**: tra quelle in §6 (o altre non elencate), quali sono
   le più rilevanti per raccontare la trasformazione di una città turistica
   media europea? C'è una dimensione "ovvia" che abbiamo dimenticato?
2. **Nuovi insight dai dati esistenti**: con le metriche/serie del §2, quali
   analisi/incroci aggiuntivi suggerisci (oltre alle correlazioni e all'indice di
   gentrificazione già previsto)? Es. cluster di barrios, indici compositi,
   decomposizioni, lead/lag temporali tra touristificazione e affitti.
3. **Fonti alternative** per i dati non disponibili (§6a): criminalità a livello
   barrio, prezzi di **vendita**, modelos lingüísticos — conosci dataset aperti o
   API affidabili (anche europei/spagnoli generali) utilizzabili per Donostia?
4. **Metodologia**: l'indice `housing_tension` (assunzione 30 m²/persona, reddito
   pro capite) è difendibile? Suggerisci una formulazione migliore con i dati che
   abbiamo? E sulla definizione operativa di gentrificazione (molte in
   letteratura), quale consigli di esporre/rendere selezionabile?
5. **Priorità**: dato lo stato attuale, su cosa investiremmo meglio il prossimo
   blocco di lavoro — completare dimensioni mancanti (fiscalità, rumore, salute),
   costruire l'indice di gentrificazione, o le narrazioni avanzate
   (scrollytelling / temporal)?

---

*Contesto tecnico per riferimento: pipeline Python (`data-pipeline/`) →
JSON+CSV; frontend React/Vite/TS (`web/`); tabelle riusabili in `data/`;
documentazione in `docs/` (SOURCES, INSIGHTS, DATA-CONTRACT, GAP-ANALYSIS,
PROJECT-BRIEF). Città: Donostia/San Sebastián, 19 barrios ufficiali.*
