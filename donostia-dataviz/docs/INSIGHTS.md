# Donostia Dataviz — insights dai dati

Sintesi delle scoperte emerse dai dati **realmente processati** nella pipeline
(non aneddoti): ogni numero viene dalle tabelle in `../data/` ed è riproducibile
con `python -m donostia_pipeline.build`. Aggiornare quando si aggiungono metriche.

> **Avvertenze metodologiche** (valgono per tutto il documento):
> - I conteggi sono sempre **normalizzati per popolazione** (tasso/1000 ab.).
> - **"% stranieri" non è "gentrificazione"**: a Donostia include sia
>   immigrazione economica sia espatriati benestanti — da leggere con cautela,
>   mai come proxy diretto di trasformazione.
> - Le metriche derivate hanno assunzioni esplicite (vedi `SOURCES.md`).

---

## 🏘️ Turismo e touristificazione
- Le **viviendas de uso turístico** sono fortemente concentrate nel centro:
  **Erdialdea 664** unità e **Gros 359** dominano (su ~1.490 totali in città).
- Densità VUT per 1000 ab.: **Erdialdea 29,9**, **Gros 20,7**, poi Antigua 8,5 —
  i barrios centrali sono di gran lunga i più turisticizzati.
- **Stagionalità (pernottamenti hotel, INE EOH 2005–2026)**: picco estivo
  **Lug/Ago ~245k**, minimo **Gen ~116k**; il **2020 (COVID)** è un crollo netto
  visibile come striscia pallida; dal 2021 forte ripresa **+ de-stagionalizzazione**
  (i mesi di spalla si scaldano). Totale 2025 ≈ **2,2 milioni** di pernottamenti.

## 🏠 Abitazioni
- **Affitto €/m² (EMA, 2024)**: più caro nel **Centro/Erdialdea 16,6**, poi
  **Aiete 16,2** e **Gros 15,9**; est più economico. Erdialdea **+29%** dal 2016.
- **Sforzo affitto/reddito** (derivato): **inverte** la mappa degli affitti
  assoluti. Lo sforzo massimo è nei barrios **operai** — **Altza 21,9%**,
  **Egia 21,3%**, **Intxaurrondo 20,9%** (2023) — perché i redditi bassi pesano
  più degli affitti bassi; minimo nei ricchi **Ategorrieta-Ulia 14,5%** e
  **Aiete 16,7%**. È il segnale di "dove vivere sta diventando insostenibile".

## 💶 Economia e disuguaglianza
- **Reddito pro capite (2023)**: forte gradiente — **Aiete ~30.440 €** contro
  **Altza ~18.371 €** (~1,7×).
- **Divario di reddito di genere**: marcato, es. **Aiete ~29,9%** (reddito pro
  capite maschile superiore a quello femminile).

## 👥 Demografia
- **% popolazione straniera** in crescita ovunque: es. **Gros 1,3% (2000) →
  9,9% (2025)**.
- Correlazione **reddito ↔ % stranieri: r = −0,58** — i barrios a reddito più
  alto hanno meno residenti stranieri (e viceversa). *Da non leggere come
  gentrificazione (vedi avvertenza).*

## 🏫 Istruzione
- **Studi universitari** in aumento: **Aiete 25,3% (2000) → 35,0% (2025)**.
- **Centri educativi per 1000 ab.** (join spaziale): la normalizzazione cambia
  la storia — **Ibaeta** è prima in valore assoluto (24 centri, campus
  universitario) ma scende a **3ª** per-capita, mentre **Zubieta** (rurale, pochi
  abitanti) risulta prima per-capita.

## 🌡️ Clima e cambiamento climatico (AEMET Igeldo, 1981–2025)
- **Riscaldamento netto**: trend **+0,31 °C/decennio (R² = 0,39)**; media annua
  da **13,1 °C (1981–85)** a **14,7 °C (2021–25)**, ~**+1,4 °C** in 45 anni.
- **Cicli mensili per anno**: nella viz a linee, gli anni recenti (rossi/caldi)
  stanno visibilmente **sopra** l'inviluppo storico (grigio) in quasi tutti i
  mesi — il riscaldamento è leggibile a colpo d'occhio.
- **Giorni caldi (max ≥ 30 °C)**: in aumento, **+0,81 giorni/decennio**; dai
  ~4–5/anno degli anni '80–'90 ai **12–15** del 2003, 2022 e 2023 (2022 = 15).
- **Picchi estremi**: la massima assoluta sale fino a **39,7 °C (2022)** e
  38,6 °C (2003) — valori notevoli per una località costiera mite.
- **Precipitazioni**: nessun trend significativo (**+40,9 mm/decennio, R² = 0,06**)
  — molto variabili anno su anno; ~**1.900 mm** nel 2024 (città piovosa).

> **Lettura d'insieme**: media in lento ma chiaro aumento, **estremi più
> frequenti e più intensi** negli ultimi 20–30 anni — il segno tipico del
> cambiamento climatico, non solo "più caldo in media" ma più ondate di calore.

## ♻️ Ambiente
- **Raccolta differenziata** in netto miglioramento: dal **28,8% (2010)** al
  **41,0% (2023)** dei rifiuti urbani (selettiva + autocompostaje sul totale).
  Tendenza di sostenibilità chiara, anche se sotto gli obiettivi UE (55%).
  *(Il 2024 è escluso perché incompleto: "Rechazo" non ancora caricato.)*

## 🎪 Turismo MICE
- **Record 2024**: **188 eventi professionali**, **259.000 partecipanti**,
  **50% internazionali** (Convention Bureau).
- **Congressi internazionali ICCA** (criteri stretti, comparabili nel ranking
  mondiale): 16 (2018) → 12 (2019) → 15 (2023) → 13 (2025).

## 🔗 Correlazioni tra barrios
- **Densità VUT ↔ affitto €/m²: r = 0,64** — i barrios turisticizzati hanno
  affitti più alti (la tesi centrale "touristificazione → pressione immobiliare"
  quantificata).
- **Reddito ↔ % stranieri: r = −0,58** (vedi sopra).

---

## La tesi che emerge
Mettendo insieme i segnali: la **touristificazione** è concentrata nel centro
(Erdialdea/Gros), dove spinge gli **affitti** più in alto; ma la **pressione
abitativa** più dura ricade sui barrios **operai** dell'est, dove i redditi non
tengono il passo. Il clima intanto si scalda in modo misurabile. È più di una
dashboard: è una lettura della trasformazione della città — da approfondire con
l'indice composito di gentrificazione (idea #1) una volta integrate le altre
dimensioni.
