> ⚠️ **ARCHIVADO** — documento histórico: superado por una versión más reciente o ya volcado en la documentación activa. Se conserva como referencia. Punto de entrada actualizado en `../../README.md`.

# Donostia Dataviz — Piano di progetto

> Documento di brief originale fornito da Stefano. Conservato verbatim come
> riferimento. La verifica/integrazione delle fonti è in `SOURCES.md`.

## Obiettivo

Dashboard interattiva che mostra l'evoluzione di Donostia/San Sebastián da molteplici punti di vista — principalmente tramite mappe coropletiche per barrio con slider temporale, integrate da time-series e grafici comparativi.

---

## Stack tecnico suggerito

- **Mappe**: MapLibre GL JS (choropleth) oppure D3.js + GeoJSON
- **Grafici**: D3.js o Recharts
- **Dati**: CSV/GeoJSON locali (pre-processati da Python/pandas)
- **Framework**: React + Vite (allineato al sito esistente) o standalone HTML/JS
- **GIS base**: GeoJSON barrios da Open Data Donostia

---

## Geometrie base (GIS)

| Risorsa | URL | Formato | Note |
|---|---|---|---|
| Barrios (poligoni) | `https://www.donostia.eus/datosabiertos/catalogo/mapa_auzoak` | Shapefile / GeoJSON | 17 barrios ufficiali |
| Unidades menores | Open Data Donostia | Shapefile | Granularità sub-barrio |
| Distretti censali | `https://www.donostia.eus/datosabiertos/catalogo/delimitaciones_censales` | Shapefile | |
| WMS limiti amministrativi | `https://www.donostia.eus/datosabiertos/` (WMS) | WMS tile | EPSG:25830 o 3857 |

> ⚠️ **Problema noto**: la suddivisione in barrios varia tra dataset dello stesso Comune. Scegliere UN'unica geometria di riferimento e fare join su quella.

---

## Dataset per categoria

### 🏠 Abitazioni e affitti

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Prezzi vendita €/m² per barrio | Indomio | Barrio | Mensile (2023–oggi) | `indomio.es/en/mercado-inmobiliario/pais-vasco/san-sebastian-donostia/` |
| Prezzi affitto €/m² per barrio | Indomio | Barrio | Mensile (2023–oggi) | stessa URL |
| Prezzi storici €/m² (serie lunga) | Eustat / Ministerio Vivienda | Municipio | Trimestrale (2000–oggi) | `eustat.eus` → Vivienda |
| Renta disponibile per barrio | Open Data Donostia | Barrio | Annuale | `donostia.eus/datosabiertos/catalogo/eustat_renta` |
| Reddito familiare mediano per barrio | Eustat | Barrio | Annuale | `eustat.eus` → renta familiar |

**Visualizzazione suggerita**: choropleth animata (slider anno) + line chart comparativo barrios selezionati.

---

### 🏘️ Turismo e Airbnb

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| VUT/HUT (viviendas uso turístico) per barrio | Open Data Donostia | Barrio + indirizzo | Mensile | `donostia.eus/datosabiertos/catalogo/censo-viviendas-turisticas` |
| Snapshot Airbnb (listings geolocalizzati) | Inside Airbnb | Punto (lat/lon) | Snapshot periodici | `insideairbnb.com/get-the-data/` → cercare San Sebastián |
| Pernottamenti in alloggi turistici | INE | Municipio | Mensile | `ine.es` → Encuesta de Ocupación en Alojamientos Turísticos |
| Viaggiatori per nazionalità | INE | Municipio | Mensile | stessa indagine INE |
| Hotel: posti letto e occupazione | INE / Eustat | Municipio | Mensile | `eustat.eus` → Turismo |

**Visualizzazione suggerita**: 
- Mappa densità VUT per barrio (choropleth) con slider temporale
- Heatmap Airbnb puntuale (listings come punti su mappa) 
- Bar chart stagionalità turistica (mesi)

---

### 👥 Demografia

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Popolazione per barrio / età / genere | Open Data Donostia | Barrio + unidad menor | Annuale (dal 2000) | `donostia.eus/datosabiertos/catalogo/demografia-origen` |
| Popolazione straniera per nazionalità | Open Data Donostia | Barrio | Annuale | stesso dataset |
| Livello d'istruzione (>16 anni) | Open Data Donostia | Barrio + unidad menor | Annuale (dal 2000) | `donostia.eus/datosabiertos/recursos/demografia-nivelestudios/demografianivelestudiosciudad.csv` |
| Indice di invecchiamento | calcolabile da Eustat | Barrio | Annuale | rapporto pop >64 / pop <15 |
| Tasso di natalità | Eustat | Municipio | Annuale | |

**Visualizzazione suggerita**: choropleth % popolazione straniera per barrio; piramide demografica animata per la città.

---

### 💼 Occupazione e settori lavorativi

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Occupati per settore | Open Data Donostia / Eustat | Barrio / municipio | Annuale | `donostia.eus/datosabiertos/tema/empleo` |
| Tasso di disoccupazione | SEPE / Eustat | Municipio | Mensile | `eustat.eus` → Mercado laboral |
| Salari per settore e genere | Eustat | Barrio (parziale) | Annuale | gender pay gap documentato per barrio |

**Visualizzazione suggerita**: stacked bar chart evoluzione settori (hostelería vs industria vs tecnologia); choropleth salario mediano con evidenza gap di genere.

---

### 🌡️ Meteo e clima

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Temperature medie mensili storiche | AEMET — stazione Igeldo | Una stazione | Mensile (dal 1981) | `aemet.es/es/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=1024E` |
| Precipitazioni cumulate mensili | AEMET — stazione Igeldo | Una stazione | Mensile (dal 1981) | stessa URL |
| Dati climatologici Euskalmet | Euskalmet | Reti di stazioni | Orario/giornaliero | `euskalmet.euskadi.eus` |
| API AEMET OpenData | AEMET | Stazione | Giornaliero (recente) | `opendata.aemet.es` — richiede API key gratuita |

> ⚠️ **Limite**: una sola stazione → no choropleth intra-urbana. Solo time-series.

**Visualizzazione suggerita**: line chart temperatura media annuale con trend (regressione lineare); heatmap mese × anno con colore = temperatura media.

---

### 🚨 Sicurezza e qualità della vita

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Delitti registrati per barrio | Open Data Donostia (Guardia Municipal) | Barrio | Annuale | `donostia.eus/datosabiertos/tema/seguridad` |
| Uso del suolo / verde urbano | Open Data Donostia | GIS poligoni | Snapshot | `donostia.eus/datosabiertos/tema/urbanismo-infraestructuras` |

---

### 🚌 Mobilità

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Passeggeri DBus totali | Open Data Donostia | Linea / fermata | Annuale (dal 2011) | `donostia.eus/datosabiertos/tema/transporte` |
| Parcheggi in superficie (ubicazione e tipo) | Open Data Donostia | Punto | Snapshot | stesso portale |

---

### 🎪 Turismo MICE (Congressi, Incentivi, Riunioni, Fiere)

Il settore MICE è strategicamente prioritario per Donostia e ha un Observatorio dedicato. I dati sono più frammentati rispetto al turismo leisure, ma esistono fonti specifiche.

**Fonte principale**: **Donostia San Sebastián Convention Bureau** (`conventionbureau.sansebastianturismoa.eus`) — pubblica ranking e statistiche congressuali annuali. Il 63% degli eventi organizzati in città è internazionale.

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Número de congresos/eventos per anno | Convention Bureau / ICCA | Città | Annuale | `conventionbureau.sansebastianturismoa.eus` → publicaciones; ICCA database |
| Partecipanti a congressi | Convention Bureau / Memoria anual | Città | Annuale | Memorie annuali DSS Turismoa (PDF) su `press.sansebastianturismoa.eus` |
| Ranking internazionale MICE | ICCA (International Congress & Convention Assoc.) | Città mondiale | Annuale | ICCA Statistics Report — Donostia al pos. 221 mondiale (2019) |
| Sedi congressuali (Kursaal, Victoria Eugenia, Reale Arena, BCC...) | Convention Bureau | Punto GIS | Snapshot | lista completa su sito CB |
| Pernottamenti turisti MICE vs leisure | Eustat / Observatorio | Municipio | Annuale | serie Ibiltur (Eustat) con motivo visita |

> ⚠️ **Limite**: i dati MICE granulari (numero eventi per sede, partecipanti per congresso) sono nelle Memorie annuali in PDF — richiedono estrazione manuale o scraping. Non esiste un dataset strutturato open.

**Visualizzazione suggerita**: bar chart numero eventi per anno (con breakdown internazionali vs nazionali); line chart confronto pernottamenti MICE vs leisure nel tempo.

---

### 🧳 Profilo e segmentazione dei visitatori

Fonti che descrivono *chi* visita Donostia, non solo *quanti*.

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Motivo della visita (ocio / lavoro / congresos / visita familiar) | Eustat — Ibiltur | Municipio / zona | Annuale | `eustat.eus` → Ibiltur (Encuesta de Turismo Receptivo) |
| Nazionalità turisti alojados | INE — EOH + Eustat | Municipio | Mensile | `ine.es` tabella 2078; `eustat.eus` → Turismo |
| Turismo organizzato vs individuale | Eustat Ibiltur | Municipio | Annuale | breakdown per tipo di organizzazione del viaggio |
| Mezzo di trasporto usato | Eustat Ibiltur | Municipio | Annuale | coche / AVE / avión / autocar |
| Stima excursionismo (visitatori giornalieri senza pernottamento) | Observatorio Turístico Donostia / Eustat | Città | Annuale | dato critico e difficile da misurare — in fase di studio capacity carga (2025) |
| Soddisfazione turisti (score 0–10) | Observatorio Turístico Donostia | Città | Annuale | 2025: 9,2/10 con pernottamento, 9,0/10 senza |
| Pernottamenti per tipo alloggio (hotel / VUT / rural / camping) | INE — EOH / Eustat | Municipio | Mensile | distinzione fondamentale per analisi impatto |

**Dati chiave già noti** (utili come valori di riferimento per il viz):
- 2025: 2.122.612 pernottamenti totali (−0,48% vs 2024); 66,05% internazionali (+2,83%); stanza media 2,05 notti (internazionali 2,13, statali 1,91)
- 2024: pernottamenti +6,0% rispetto al 2023, nuovo massimo storico; turismo internazionale +10,2%, statale +1,5%
- Il turismo rappresenta il 13,9% del PIL cittadino e più di 15.000 occupati sono legati al settore

---

### 💸 Gasto turístico (capacità di spesa)

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Gasto medio turista alojado (€/giorno) | Eustat — Ibiltur / Observatorio | Municipio | Annuale | breakdown per nazionalità e tipo alloggio |
| Gasto medio excursionista (€/giorno) | Eustat — Ibiltur | Municipio | Annuale | dato separato da turista alojado |
| Gasto medio turista MICE / lavoro (€/giorno) | Eustat — Ibiltur | Municipio | Annuale | storicamente molto superiore a turismo leisure |
| Distribuzione spesa per categoria (alloggio / ristoranti / acquisti / trasporto) | Eustat / Gobierno Vasco | Regione/municipio | Annuale/irregolare | serie storica disponibile dal 2000 ca. |
| RevPAR (Revenue per Available Room) | Eustat / rapporti settore | Municipio | Annuale | Donostia è il secondo destino urbano spagnolo per RevPAR, solo dietro Barcellona |
| Fatturato settore hostelería e ristorazione | Eustat | Municipio | Annuale | proxy dell'impatto economico reale |

> **Nota metodologica**: la distinzione tra turista alojado, excursionista e turista de negocios è cruciale perché la spesa per persona/giorno varia enormemente tra i tre segmenti. Eustat Ibiltur è l'unica fonte che li separa sistematicamente.

**Visualizzazione suggerita**: stacked area chart gasto totale = (turisti × giorni × spesa/giorno), decomposto per segmento nel tempo; scatter gasto medio vs nazionalità (bolla = volume).

---

### 📅 Stagionalità e de-stagionalizzazione

Donostia ha un piano esplicito di de-stagionalizzazione — i dati mensili mostrano questa evoluzione nel tempo.

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Pernottamenti mensili per anno (serie lunga) | INE — EOH | Municipio | Mensile (dal ~2000) | `ine.es` → tabella 2078, filtro San Sebastián |
| Occupazione alberghiera mensile | INE / Eustat | Municipio | Mensile | grado di ocupación % per mese |
| Viaggiatori per mese e nazionalità | INE / Eustat | Municipio | Mensile | |

> Nel 2025 crescono i mesi di bassa stagione (gennaio, febbraio, giugno, dicembre) mentre cala l'estate (−1,48%) — questo trend de-stagionalizzazione è perfetto per una visualizzazione tipo heatmap mese × anno.

**Visualizzazione suggerita**: heatmap mese × anno con colore = pernottamenti (rivela stagionalità e sua evoluzione in un'unica vista); line chart multiplo confronto gen-dic tra anni diversi.

---

## Metriche derivate interessanti (calcolate)

Queste non esistono come dataset pronti ma si calcolano combinando i dati sopra:

| Metrica | Formula | Dati necessari |
|---|---|---|
| **Tasso touristificazione** | VUT / abitazioni totali per barrio | VUT + censimento abitazioni |
| **Pressione immobiliare** | Δ prezzo affitto / Δ reddito mediano per barrio | Prezzi + reddito |
| **Airbnb intensity** | Listings Airbnb / abitazioni totali | Inside Airbnb + censimento |
| **Indice di invecchiamento** | Pop >64 / Pop <15 × 100 | Dataset demografico |
| **Gender pay gap** | (salario_uomo - salario_donna) / salario_uomo | Eustat per barrio |
| **Trend temperatura annuale** | regressione lineare su medie annuali | AEMET |
| **Indice de-stagionalizzazione** | coefficiente di variazione mensile pernottamenti per anno | INE — EOH mensile |
| **Peso MICE sul turismo totale** | pernottamenti MICE / pernottamenti totali | Ibiltur + INE |
| **Gasto totale stimato** | visitatori × durata media × spesa media/giorno | Ibiltur multi-segmento |
| **Rapporto excursionisti / turisti** | escursionistas / turistas alojados | Observatorio + Eustat |

---

## Visualizzazioni prioritarie

### Fase 1 — Mappa coropletica con slider
- Selezione metrica (dropdown): affitto €/m², VUT density, % stranieri, reddito mediano
- Slider anno
- Tooltip al hover con barrio + valore + Δ rispetto anno precedente
- Legenda con scala colori

### Fase 2 — Panel comparativo barrios
- Seleziona 2–3 barrios → line chart affiancati per metrica scelta
- Evidenzia COVID-19 (2020) e turismo post-COVID

### Fase 3 — Time-series meteo e turismo
- Heatmap mese × anno (temperatura, precipitazioni)
- **Heatmap stagionalità**: mese × anno, colore = pernottamenti → mostra evoluzione de-stagionalizzazione
- Bar chart stagionalità turistica con overlay trend annuale
- Stacked area chart segmenti turisti (leisure / lavoro / MICE) nel tempo

### Fase 4 — Scatter e correlazioni
- Scatter: densità VUT vs prezzo affitto per barrio (colore = barrio, dimensione = popolazione)
- Scatter: reddito mediano vs % stranieri

---

## Note implementative

- Usare **GeoJSON** (convertire da shapefile con `ogr2ogr` o `mapshaper`)
- Pre-processare tutti i CSV in Python/pandas → output JSON puliti per il frontend
- Per le choropleth: MapLibre GL JS (se si vuole base map stradale) o D3 puro (se solo mappa vettoriale)
- Colori: scala divergente per variazioni (blu=calo, rosso=aumento), sequenziale per valori assoluti
- Normalizzare sempre su geometria barrios ufficiale dal portale comunale

---

## Riferimenti accademici utili

- Aguado-Moralejo & Del Campo-Echeverría (2020) — *El fenómeno Airbnb en Donostia-San Sebastián* — CyTET 52(206)
- Etxezarreta-Etxarri et al. (2020) — *Urban touristification in Spanish cities: rental-housing sector in San Sebastian* — analisi econometrica Airbnb vs affitti
- Boletín AGE (2023) — *The touristification of urban spaces: measurement proposal* — metodologia indicatori a scala di manzana
- Eustat — *Ibiltur: Encuesta de Turismo Receptivo* — serie annuale con segmentazione motivo visita, nazionalità, gasto medio (`eustat.eus`)
- ICCA — *International Congress Statistics Report* — ranking mondiale città congressuali (Donostia pos. 221 mondiale / 112 Europa nel 2019)
- Donostia San Sebastián Turismoa — *Memorie annuali* — dati MICE, pernottamenti, soddisfazione (`press.sansebastianturismoa.eus/images/prensa_agentes/pdf/memoria/`)

---

## Prossimi passi

1. [ ] Scaricare GeoJSON barrios da `donostia.eus/datosabiertos/catalogo/mapa_auzoak`
2. [ ] Scaricare dataset VUT (CSV mensile) e demografico (CSV annuale)
3. [ ] Registrarsi per API key AEMET gratuita → scaricare serie storica stazione Igeldo
4. [ ] Cercare snapshot Inside Airbnb per San Sebastián (o richiedere il dataset)
5. [ ] Scaricare serie INE EOH mensile per San Sebastián (tabella 2078) → dati stagionalità
6. [ ] Scaricare Memorie annuali DSS Turismoa (PDF) per estrarre dati MICE e profilo visitatori
7. [ ] Verificare accesso dati Eustat Ibiltur (motivo visita, gasto medio per segmento)
8. [ ] Script Python di pulizia e join su geometria barrios comune
9. [ ] Prototipo choropleth con D3 o MapLibre + un dataset (es. VUT density)
