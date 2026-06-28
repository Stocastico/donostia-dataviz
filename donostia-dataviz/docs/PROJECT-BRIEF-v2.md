> **Nota:** versione aggiornata e ampliata del brief di progetto (backlog). Espande
> `PROJECT-BRIEF.md` (v1) con nuove dimensioni dati, la correzione sul catastro
> foral, sezioni MICE/visitatori/gasto, idee avanzate e la raccomandazione
> dell'indicator store unificato. Lo stato di avanzamento e la prioritizzazione
> sono tracciati in `GAP-ANALYSIS.md`.

# Donostia Dataviz — Piano di progetto

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

### 🚨 Criminalità (espansione)

Il dato esiste ed è open. Ci sono due fonti complementari con granularità diversa.

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Delitti per barrio (Guardia Municipal) | Open Data Donostia | Barrio | Annuale | CSV diretto: `donostia.eus/datosabiertos/catalogo/delitos-guardia/recurso/gua_delitosbarrio_ckan.csv` |
| Delitti totali per tipo (Guardia Municipal + Ertzaintza) | Gobierno Vasco — Memoria Delincuencia | Municipio | Annuale | `ertzaintza.euskadi.eus` → estadísticas delictivas; serie dal 2010 ca. |
| Tasa delincuencial (reati / 1000 abitanti) | Gobierno Vasco | Municipio | Annuale | stessa fonte; Donostia: 67,54‰ nel 2021, 2025: −5,18% vs 2024 |
| Infracciones penales per tipo (hurtos, estafas, robos…) | Ertzaintza + MIR | Municipio | Annuale | `estadisticasdecriminalidad.ses.mir.es` — Portal Estadístico Criminalidad |
| Puntos críticos de seguridad (mappa partecipativa) | Open Data Donostia | Punto GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/seguridad-ptos_criticos` (SHP + WMS) |
| Violencia de género — denúncias | Eustat / Gobierno Vasco | Municipio | Annuale | Eustat → Sociedad, dato separato da criminalità generale |

> **Nota**: il 77,7% dei delitti a Donostia sono contro il patrimonio (hurtos, robos, estafas). I dati per barrio dalla Guardia Municipal sono il dataset più granulare — scaricabile direttamente in CSV.

**Visualizzazione suggerita**: choropleth delitti per barrio normalizzati per popolazione (tasa/1000 ab.); line chart evoluzione tasa delincuencial per anno; donut/stacked bar tipi di delitto.

---

### 🏫 Educazione e giovani

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Equipamientos educativos (scuole, asili, università) con geolocalizzazione | Open Data Donostia | Punto GIS | Annuale | `donostia.eus/datosabiertos/catalogo/servicios-educativos` — GeoJSON + CSV + WMS disponibili |
| Equipamientos de juventud (gaztelekus, haurtxokos, centros jóvenes) | Open Data Donostia | Punto GIS | Annuale | `donostia.eus/datosabiertos/catalogo/equipamiento_juventud` |
| Livello di studi popolazione per barrio | Open Data Donostia | Barrio + unidad menor | Annuale (dal 2000) | `donostia.eus/datosabiertos/catalogo/demografia-nivelestudios` |
| Alunni per livello / lingua (modelo A/B/D) | Gobierno Vasco — Dpto. Educación | Municipio / centro | Annuale | `hezkuntza.euskadi.eus` → estadísticas educación; serie storica lunga |
| Tasa escolarización 0–2 anni | Eustat | Municipio | Annuale | `eustat.eus` → Educación |

> **Nota sul modello linguistico**: i modelli A (solo spagnolo), B (bilingue) e D (solo euskera) sono un dato particolarmente significativo per l'evoluzione identitaria della città. La percentuale di iscritti al modelo D è cresciuta costantemente dal 1983.

**Visualizzazione suggerita**: mappa punti scuole per livello; line chart evoluzione % alunni in ciascun modelo lingüístico; choropleth livello di studi per barrio.

---

### 🏥 Salute e servizi sociali

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Equipamientos de salud (ospedali, ambulatori, cliniche) | Open Data Donostia | Punto GIS | Annuale | `donostia.eus/datosabiertos/catalogo/servicios-salud` — GeoJSON + CSV + WMS |
| Equipamientos socio-asistenciali (centri diurni, residenze anziani) | Open Data Donostia | Punto GIS | Annuale | `donostia.eus/datosabiertos/catalogo/servicios-socio_asistencial` — GeoJSON disponibile |
| Famiglie assistite dai Servizi Sociali | Open Data Donostia | Municipio | Annuale | `donostia.eus/datosabiertos/catalogo/bso-familias-cas` — CSV; proxy della fragilità sociale |
| Ámbiti territoriali dei servizi sociali | Open Data Donostia | Zone GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/servicio-social` (SHP + WMS) |
| Speranza di vita / mortalità | Eustat | Municipio | Annuale | `eustat.eus` → Demografía → Mortalidad |
| Rifugi climatici (heatwave resilience) | Open Data Donostia | Punto GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/refugio-climatico` — nuova infrastruttura (2024) |

**Visualizzazione suggerita**: mappa accessibilità sanitaria (distanza a piedi dal centro di salute più vicino per barrio); line chart famiglie in carico ai servizi sociali vs reddito mediano.

---

### 🔊 Ambiente urbano: rumore, qualità dell'aria, rifiuti

Questa è forse la categoria più sottovalutata per una dataviz sulla qualità della vita urbana — e Donostia ha dati eccellenti.

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Mappa rumore totale (mattina/pomeriggio/notte) | Open Data Donostia | Griglia GIS | Biennale | `donostia.eus/datosabiertos/catalogo/ruido-total` (SHP + WMS) |
| Mappa rumore notturno | Open Data Donostia | Griglia GIS | Biennale | `donostia.eus/datosabiertos/catalogo/ruido-noche` |
| Qualità dell'aria | Open Data Donostia / Gobierno Vasco | Stazioni | Annuale | `donostia.eus/datosabiertos/tema/medio-ambiente` — tag `calidad_aire` |
| Raccolta differenziata rifiuti per tipo | Open Data Donostia | Municipio | Annuale | `donostia.eus/datosabiertos/catalogo/residuos` — CSV; evoluzione % raccolta differenziata |
| Localizzazione contenitori raccolta differenziata | Open Data Donostia | Punto GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/mambiente-residuos` (SHP) |
| Zona de bajas emisiones (ZBE, 2024) | Open Data Donostia | Poligono GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/mambiente-zbe` — approvata 2024 |

> La mappa del rumore notturno è particolarmente rilevante per la qualità della vita nei barrios della Parte Vieja e Gros, dove l'hostelería è concentrata.

**Visualizzazione suggerita**: choropleth livelli di rumore notturno per zona; line chart % raccolta differenziata per anno (trend sostenibilità); overlay ZBE su mappa city.

---

### 🌿 Spazio verde e uso del suolo

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Parchi e zone verdi (poligoni GIS) | Open Data Donostia | Poligono GIS | Snapshot | `donostia.eus/datosabiertos/tema/urbanismo-infraestructuras` |
| Biodiversità urbana (inventario specie) | Open Data Donostia | GIS | Biennale/triennale | tag `biodiversidad` nel portale medio-ambiente |
| Potencial fotovoltaico edifici | Open Data Donostia | Edificio GIS | Biennale | `donostia.eus/datosabiertos/catalogo/mambiente-fotovoltaico` (SHP + WMS) |
| Uso del suolo per tipo | Gobierno Vasco — Lurralde Informazioa | Poligono GIS | Quadriennale | `geo.euskadi.eus` — Mapa de Usos del Suelo (CORINE adaptato) |

---

### 🏪 Commercio e trasformazione urbana

Il portale ha pochi dataset diretti sul commercio, ma il dato più interessante è già disponibile:

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Zone sature di locali e attività ricreative | Open Data Donostia | Poligono GIS | Snapshot | `donostia.eus/datosabiertos/catalogo/urbanismo-zsaturada` (SHP + WMS) — barrios dove è stata limitata l'apertura di nuovi locali |
| Licenze di apertura per tipo di attività | Ayuntamiento (su richiesta / Hacienda) | Municipio | Annuale | dato disponibile nelle statistiche di Hacienda; non strutturato come open data CSV |
| Locali chiusi / sfitti | Non disponibile come open data | — | — | potenzialmente rilevabile da foto satellitari o street view temporali |
| Numero di ristoranti/bar per barrio | Eustat / IAE (Impuesto Actividades Económicas) | Barrio | Annuale | `eustat.eus` → Empresas → por actividad CNAE; proxy della touristificazione commerciale |

---

### 💰 Fiscalità e bilancio municipale

| Dataset | Fonte | Granularità geo | Granularità tempo | URL / Note |
|---|---|---|---|---|
| Impuestos municipali emessi (IBI, plusvalía…) | Open Data Donostia | Municipio | Annuale | `donostia.eus/datosabiertos/catalogo/impuestos_tipo` — CSV aggiornato |
| Tasas municipali per tipo | Open Data Donostia | Municipio | Annuale | `donostia.eus/datosabiertos/catalogo/tasas_tipo` — CSV aggiornato |
| Subvenciones concedidas per anno | Open Data Donostia | Municipio | Annuale | `donostia.eus/datosabiertos/catalogo/subvenciones_2023` |
| **Catastro de Gipuzkoa** (valore catastale, dati fisici immobili) | **Diputación Foral de Gipuzkoa** — NON il catastro statale | Parcela / unidad constructiva | Aggiornato ogni 15 giorni | Open data CSV su `gipuzkoairekia.eus` → Catastro urbano (Bienes Inmuebles de Naturaleza Urbana); licenza CC-BY |

> ⚠️ **Importante — competenza foral**: Gipuzkoa (come tutto il País Vasco e la Navarra) ha un regime fiscale foral. Il catastro NON è gestito dalla Dirección General del Catastro statale (`sedecatastro.gob.es`), che non restituisce dati per i territori forali. Va usato il **Catastro de la Diputación Foral de Gipuzkoa**. Vantaggio: i dati sono pubblicati come **open data CSV scaricabili in bulk** su `gipuzkoairekia.eus` (dataset "Bienes Inmuebles de Naturaleza Urbana", ~6 MB per file, aggiornato ogni 15 giorni), molto più comodo dello scraping parcela-per-parcela. Consultazione web puntuale per referencia catastral o indirizzo su `egoitza.gipuzkoa.eus/es/web/ogasuna/catastro`.

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
| **Tasa delincuencial** | delitti / pop × 1000 per barrio | Guardia Municipal CSV + demografico |
| **Indice accessibilità sanitaria** | distanza media a piedi al centro salud più vicino | GeoJSON salute + geometria barrios |
| **% raccolta differenziata** | rifiuti differenziati / totale × 100 | dataset residuos |
| **Densità hostelería** | bar+ristoranti / abitazioni per barrio | IAE/Eustat + censimento |
| **Pressione fiscale immobiliare** | valore catastale / valore mercato per zona | Catastro + Indomio |
| **% alunni modelo D** | iscritti modelo D / totale iscritti | Dpto. Educación

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

## 🚀 Idee avanzate (concetti differenzianti)

Queste sono idee che vanno oltre la choropleth classica e che renderebbero il progetto distintivo. Diverse sono ispirate a progetti analoghi di altre città (riferimenti in fondo).

### 1. Indice composito di "desplazamiento" / gentrificazione per barrio

Il contributo più forte che il progetto può dare non è mostrare una variabile alla volta, ma **costruire un indice tipologico** che classifica ogni barrio in categorie di trasformazione, sul modello dell'**Urban Displacement Project (UC Berkeley)** e di **Displaced by Design (NCRC)**.

Metodologia consolidata (Freeman 2005, adattata da Ding/Hwang): un barrio è "gentrificabile" se parte sotto la mediana cittadina di reddito; è "in gentrificazione" se in un dato periodo cresce, più della mediana cittadina, sia in (a) livello di istruzione / reddito sia in (b) prezzo affitto/vendita. Variabili operative tipiche: reddito mediano, valore casa, affitto, tasso di sfitto, livello d'istruzione.

**Adattamento a Donostia**: combinare 5 variabili già nel progetto → reddito mediano, prezzo affitto €/m², % popolazione con studi superiori, densità VUT, % stranieri (qui da interpretare con cautela: a Donostia parte degli "stranieri" sono espatriati ad alto reddito, non immigrazione economica — vedi nota etica sotto). Output: ogni barrio classificato (es. "stabile", "in gentrificazione iniziale", "gentrificazione avanzata", "esclusivo/escludente") con una mappa categorica + spiegazione interattiva dei criteri.

> Questo trasforma il progetto da "dashboard di dati" a "strumento analitico con una tesi" — molto più memorabile.

### 2. Dimensione temporale come protagonista (non solo slider)

Ispirato a **Zurich Time Travel** (Lisa Stähli, ArcGIS JS API + modello 3D edifici con anno di costruzione). Due varianti possibili:

- **Small multiples temporali**: invece di un solo slider, mostrare la stessa mappa a 4-6 istanti (es. 2000, 2008, 2015, 2020, 2025) affiancate → l'occhio coglie immediatamente la propagazione spaziale del fenomeno (es. la touristificazione che si espande da Parte Vieja-Gros verso Antiguo e Egia).
- **Animazione "play"**: pulsante che anima la transizione anno-per-anno, con un contatore. Tecnicamente facile con D3 transitions o MapLibre `setPaintProperty` interpolato.
- **3D extrusion temporale** (se vuoi usare la tua base Three.js esistente): estrudere i barrios in 3D dove l'altezza = prezzo affitto o densità VUT, animato nel tempo. Questo sarebbe il ponte naturale tra il tuo stack Three.js e il nuovo progetto.

### 3. Storia guidata (scrollytelling)

Sul modello dei pezzi del **NYT "A Decade of Urban Transformation"**: invece di lasciare l'utente solo davanti a controlli, una narrazione che scorre (scroll-driven) e pilota la mappa: "Nel 2014 il turismo supera 1,4M di pernottamenti…" → la mappa evidenzia Parte Vieja → "…e i prezzi nell'Antiguo iniziano a salire" → la mappa pana sull'Antiguo. Librerie: Scrollama.js + il tuo motore mappa. Ottimo per un sito personale dove vuoi comunicare, non solo esplorare.

### 4. Indicatore di "tensione" affitti vs salari

Una delle metriche più parlanti per "la vita di chi ci abita": il rapporto tra **costo annuale dell'affitto medio** e **reddito mediano del barrio**. Mostra dove vivere sta diventando insostenibile per i residenti storici. Si calcola interamente con dati già nel progetto. Visualizzazione: choropleth con scala che evidenzia i barrios dove l'affitto supera il 30-40% del reddito (soglia di "housing stress").

### 5. Confronto "città turistica vs città vissuta"

Idea concettuale forte: due viste affiancate della stessa mappa. A sinistra "Donostia dei turisti" (densità VUT, hotel, ristoranti, punti di interesse, foto Flickr/Instagram geolocalizzate). A destra "Donostia dei residenti" (scuole, centri di salute, servizi sociali, mercati di quartiere). Il contrasto visivo racconta la divergenza tra i due usi dello spazio urbano.

### 6. Modello di accessibilità (15-minute city)

Per ogni barrio, calcolare la distanza/tempo a piedi ai servizi essenziali (scuola, centro salute, farmacia, supermercato, fermata bus) usando i GeoJSON dei servizi già disponibili + un motore di routing (OSRM o isocrone con Valhalla/openrouteservice). Visualizzazione: isocrone o choropleth di "completezza dei servizi". Misura concreta della qualità della vita quotidiana.

### 7. Dato testuale / qualitativo (avanzato, opzionale)

Sentiment o temi dalle proposte cittadine. **Decide Madrid** e progetti simili hanno mostrato il valore di integrare la voce dei cittadini. Donostia ha processi di partecipazione (`participacion-noticias` nel portale open data). Si potrebbe fare topic modeling sulle proposte/reclami cittadini per barrio e sovrapporli alle metriche oggettive. Avanzato e rumoroso, ma differenziante.

### ⚖️ Nota etica e metodologica (importante)

Tre avvertenze, viste su tutti i progetti seri di questo tipo:

1. **"% stranieri" non è "gentrificazione"**. A Donostia la popolazione straniera include sia immigrazione economica sia espatriati benestanti (telelavoratori, pensionati europei). Usare questa variabile acriticamente come proxy di gentrificazione è scorretto e potenzialmente stigmatizzante. Meglio incrociare con reddito e nazionalità specifica.
2. **La scelta della definizione cambia il risultato**. Come mostra la letteratura (HUD Cityscape 2024), esistono molte definizioni di gentrificazione e danno mappe diverse. Un progetto onesto rende esplicita la definizione scelta e idealmente permette all'utente di cambiarla.
3. **Normalizzare sempre per popolazione**. Valori assoluti (delitti, servizi) ingannano: un barrio popoloso avrà più di tutto. Tasso per 1000 abitanti quasi sempre.

### Pattern architetturali da progetti di riferimento

- **CoreData.nyc (NYU Furman Center)**: standardizza 20+ dataset eterogenei su una griglia geografica comune di indicatori multi-anno → questo è esattamente il pattern di normalizzazione che ti serve per il problema dei barrios incoerenti. Un singolo "indicator store" (un CSV/Parquet lungo: `barrio_id, anno, metrica, valore`) da cui tutte le viste attingono.
- **Open Data BCN / Observatori del Turisme a Barcelona**: separano il portale dati dalle visualizzazioni tematiche. Conferma la scelta di tenere il dataviz come progetto separato.
- **idealista18 (R package)**: esempio di dataset immobiliare geo-referenziato con attributi catastali — modello di come arricchire i listing con dati catastali (qui: catastro foral di Gipuzkoa).

---

## Note implementative

- Usare **GeoJSON** (convertire da shapefile con `ogr2ogr` o `mapshaper`)
- Pre-processare tutti i CSV in Python/pandas → output JSON puliti per il frontend
- **Indicator store unificato**: adottare il pattern CoreData.nyc — un unico dataset "lungo" (`barrio_id, anno, metrica, valore, unità, fonte`) in CSV o Parquet, da cui tutte le viste attingono. Risolve alla radice il problema dei barrios incoerenti: il join geometrico si fa una volta sola, in fase di ingestion, contro la geometria di riferimento. Aggiungere una nuova metrica = aggiungere righe, non toccare il frontend.
- Per le choropleth: MapLibre GL JS (se si vuole base map stradale) o D3 puro (se solo mappa vettoriale)
- Colori: scala divergente per variazioni (blu=calo, rosso=aumento), sequenziale per valori assoluti
- Normalizzare sempre su geometria barrios ufficiale dal portale comunale
- Normalizzare sempre i conteggi per popolazione (tasso per 1000 ab.) prima di mappare

---

## Riferimenti accademici utili

- Aguado-Moralejo & Del Campo-Echeverría (2020) — *El fenómeno Airbnb en Donostia-San Sebastián* — CyTET 52(206)
- Etxezarreta-Etxarri et al. (2020) — *Urban touristification in Spanish cities: rental-housing sector in San Sebastian* — analisi econometrica Airbnb vs affitti
- Boletín AGE (2023) — *The touristification of urban spaces: measurement proposal* — metodologia indicatori a scala di manzana
- Eustat — *Ibiltur: Encuesta de Turismo Receptivo* — serie annuale con segmentazione motivo visita, nazionalità, gasto medio (`eustat.eus`)
- ICCA — *International Congress Statistics Report* — ranking mondiale città congressuali (Donostia pos. 221 mondiale / 112 Europa nel 2019)
- Donostia San Sebastián Turismoa — *Memorie annuali* — dati MICE, pernottamenti, soddisfazione (`press.sansebastianturismoa.eus/images/prensa_agentes/pdf/memoria/`)

### Progetti di dataviz urbana di riferimento (per ispirazione metodologica e tecnica)

- **Urban Displacement Project** (UC Berkeley) — `urbandisplacement.org` — tipologia di gentrificazione/desplazamiento per census tract, metodologia validata con organizzazioni comunitarie
- **Displaced by Design** (NCRC, 2025) — `ncrc.org/displaced-by-design` — 50 anni di cambiamento di quartiere (1970-2020) con mappa interattiva multi-variabile
- **CoreData.nyc** (NYU Furman Center) — datahub che standardizza 20+ dataset su griglia geografica comune — modello per l'indicator store
- **Zurich Time Travel** (Lisa Stähli) — `staehlli.medium.com` — visualizzazione 3D della trasformazione urbana nel tempo, ArcGIS JS API; codice su GitHub
- **NYT "A Decade of Urban Transformation, Seen From Above"** (Badger & Bui) — esempio di scrollytelling su cambiamento urbano
- **Open Data BCN + Observatori del Turisme a Barcelona** — `opendata-ajuntament.barcelona.cat` — modello di separazione portale-dati / visualizzazioni tematiche
- **HUD Cityscape vol.26** — *Mapping Gentrification: A Methodology for Measuring Neighborhood Change* — rassegna delle definizioni operative di gentrificazione

---

## Prossimi passi

1. [ ] Scaricare GeoJSON barrios da `donostia.eus/datosabiertos/catalogo/mapa_auzoak`
2. [ ] Scaricare dataset VUT (CSV mensile) e demografico (CSV annuale)
3. [ ] Registrarsi per API key AEMET gratuita → scaricare serie storica stazione Igeldo
4. [ ] Cercare snapshot Inside Airbnb per San Sebastián (o richiedere il dataset)
5. [ ] Scaricare serie INE EOH mensile per San Sebastián (tabella 2078) → dati stagionalità
6. [ ] Scaricare Memorie annuali DSS Turismoa (PDF) per estrarre dati MICE e profilo visitatori
7. [ ] Verificare accesso dati Eustat Ibiltur (motivo visita, gasto medio per segmento)
8. [ ] Scaricare CSV criminalità per barrio: `donostia.eus/datosabiertos/catalogo/delitos-guardia/recurso/gua_delitosbarrio_ckan.csv`
9. [ ] Scaricare GeoJSON centri educativi: `donostia.eus/datosabiertos/catalogo/servicios-educativos`
10. [ ] Scaricare SHP mappe rumore: `donostia.eus/datosabiertos/catalogo/ruido-total` e `ruido-noche`
11. [ ] Scaricare CSV rifiuti differenziati: `donostia.eus/datosabiertos/catalogo/residuos`
12. [ ] Scaricare CSV del Catastro de Gipuzkoa (Diputación Foral) da `gipuzkoairekia.eus` — NON il catastro statale
13. [ ] Cercare serie storica modelos lingüísticos A/B/D su `hezkuntza.euskadi.eus`
14. [ ] Script Python di pulizia e join su geometria barrios comune
15. [ ] Prototipo choropleth con D3 o MapLibre + un dataset (es. VUT density)
