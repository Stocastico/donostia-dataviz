#!/usr/bin/env bash
# Descarga los datos crudos de input a datos/input/raw/.
# Refleja exactamente RAW_DOWNLOADS de data-pipeline/.../build.py.
#
# Uso:   bash datos/input/descargar_raw.sh
# AEMET: exporta AEMET_API_KEY para incluir el clima (clave gratis en opendata.aemet.es).
#
# Nota: ejecútalo en tu máquina. No puede correr desde Cowork (el portal agota
# el tiempo de web_fetch y la política prohíbe curl/wget como alternativa allí).

set -euo pipefail
DEST="$(cd "$(dirname "$0")" && pwd)/raw"
mkdir -p "$DEST"

dl () { # dl <fichero> <url>
  local f="$1" url="$2"
  if [ -f "$DEST/$f" ]; then echo "· ya existe $f"; return; fi
  echo "↓ $f"
  curl -fsSL "$url" -o "$DEST/$f" || echo "  ⚠ fallo al descargar $f"
}

dl_post () { # dl_post <fichero> <url> <json-body>
  local f="$1" url="$2" body="$3"
  if [ -f "$DEST/$f" ]; then echo "· ya existe $f"; return; fi
  echo "↓ $f"
  curl -fsSL -X POST -H "Content-Type: application/json" -d "$body" "$url" -o "$DEST/$f" \
    || echo "  ⚠ fallo al descargar $f"
}

BASE="https://www.donostia.eus/datosabiertos/recursos"

dl auzoak.json                "$BASE/mapa_auzoak/auzoak.json"
dl vtur_censo.csv             "$BASE/censo-viviendas-turisticas/urb_ckan_vtur_censo.csv"
dl demo_barrio.csv            "$BASE/demografia-origen/demografianacionalidadbarrio.csv"
dl edad_barrio.csv            "$BASE/demografia-piramideedad/demografiapiramideedadbarrio.csv"
dl renta_barrio.csv           "$BASE/eustat_renta/eustatrentabarrio.csv"
dl estudios_barrio.csv        "$BASE/demografia-nivelestudios/demografianivelestudiosbarrio.csv"
dl residuos.csv              "$BASE/residuos/datos-residuos.csv"
dl educativos.json            "$BASE/servicios-educativos/hezkuntzaekipamenduak.json"

dl ine_pernoct_esp.json       "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EOT2721?nult=600"
dl ine_pernoct_ext.json       "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/EOT2722?nult=600"

dl emal_barrios.xlsx          "https://euskadi.eus/contenidos/estadistica/122417_emal_tablas_estad/opendata/EMAL.-Barrios-Municipios.-2016-2025_es.xlsx"

dl ruido_noche_2022.zip       "https://www.donostia.eus/ide/INGURUMENA-MEDIO_AMBIENTE/shp/Zarata_Ruido/2022_DSS_IZT_totala_gau.zip"

dl impuestos_ciudad.csv       "https://www.donostia.eus/datosabiertos/dataset/36ef69b9-b2f9-4ebc-b5e9-a7e6e8f32d37/resource/8b821f48-2add-4d61-a0bc-98f1749925da/download/pfi_impuestos_tipo_ciudad_ckan.csv"
dl tasas_ciudad.csv           "https://www.donostia.eus/datosabiertos/dataset/7c0f2bf4-00b6-44bf-bf24-c9bdbc9bd00c/resource/cde02a4c-8113-45b9-ba59-614855e18919/download/pfi_tasas_tipo_ciudad_ckan.csv"

dl airbnb_listings.csv.gz     "https://data.insideairbnb.com/spain/pv/euskadi/2025-09-29/data/listings.csv.gz"
dl airbnb_reviews.csv.gz      "https://data.insideairbnb.com/spain/pv/euskadi/2025-09-29/data/reviews.csv.gz"

# Gobierno Vasco REATE (REC-12): viviendas (VUT) y habitaciones (HUT) de uso
# turístico con fecha de alta en el registro. Snapshot vivo: las bajas no se
# publican (las curvas derivadas son de licencias supervivientes).
dl reate_viviendas.json       "https://opendata.euskadi.eus/contenidos/ds_recursos_turisticos/habitaciones_viviendas_turisti/opendata/viviendas.json"
dl reate_habitaciones.json    "https://opendata.euskadi.eus/contenidos/ds_recursos_turisticos/habitaciones_viviendas_turisti/opendata/habitaciones.json"

# Open Data Euskadi (REC-15): promociones de Etxebide (vivienda protegida) con
# coords UTM y nº de viviendas. Se geocodifica punto→barrio (solo Donostia).
dl promociones_etxebide.csv   "https://opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.csv"

# Eustat PxWeb (REC-9): modelo lingüístico A/B/D, Donostia (municipio 20069),
# serie completa 1983/1984–. Filtro server-side vía POST (sin clave).
dl_post eustat_modelos_linguisticos.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_040601_ceens_mun01.px" \
  '{"query":[{"code":"municipio","selection":{"filter":"item","values":["20069"]}},{"code":"titularidad del centro","selection":{"filter":"item","values":["10"]}},{"code":"nivel de enseñanza","selection":{"filter":"item","values":["100"]}},{"code":"modelo lingüistico","selection":{"filter":"item","values":["10","20","30","40","50"]}},{"code":"características","selection":{"filter":"item","values":["10"]}}],"response":{"format":"json"}}'

# Eustat PxWeb (REC-5): tasa de paro por capitales, Donostia, promedio anual
# 2015–. Filtro server-side vía POST (sin clave).
dl_post eustat_paro_donostia.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_050403_cpra_tab19.px" \
  '{"query":[{"code":"tasa (%)","selection":{"filter":"item","values":["30"]}},{"code":"capital","selection":{"filter":"item","values":["30"]}},{"code":"sexo","selection":{"filter":"item","values":["10","20","30"]}},{"code":"trimestre","selection":{"filter":"item","values":["10"]}}],"response":{"format":"json"}}'

# Eustat PxWeb (REC-7): establecimientos por CNAE-2009, Donostia (municipio
# 20069), serie completa 2008–. Filtro server-side vía POST (sin clave).
dl_post eustat_comercio_donostia.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_200163_cdirae_est04b.px" \
  '{"query":[{"code":"municipio","selection":{"filter":"item","values":["20069"]}},{"code":"CNAE-2009","selection":{"filter":"all","values":["*"]}},{"code":"periodo","selection":{"filter":"all","values":["*"]}}],"response":{"format":"json"}}'

# Eustat PxWeb (REC-17): movilidad laboral/estudios (categórica: lugar de
# trabajo/estudio, 2021–) + empleo localizado DIRAE (1995–), Donostia (20069).
# No existe matriz O-D municipio×municipio en el banco PxWeb.
dl_post eustat_empa_movilidad.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_050407_cempa_empa_mt02.px" \
  '{"query":[{"code":"ámbitos territoriales","selection":{"filter":"item","values":["20069"]}}],"response":{"format":"json"}}'
dl_post eustat_eme_movilidad.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_040606_ceme_me02.px" \
  '{"query":[{"code":"ámbitos territoriales","selection":{"filter":"item","values":["20069"]}}],"response":{"format":"json"}}'
dl_post eustat_dirae_empleo.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_200163_cdirae_est07.px" \
  '{"query":[{"code":"ámbitos territoriales","selection":{"filter":"item","values":["20069"]}}],"response":{"format":"json"}}'

# Eustat PxWeb (REC-21): paro por nacionalidad + personal I+D + población
# ocupada, Gipuzkoa (sin grano municipio — ver datasets/empleo_nacionalidad_gipuzkoa.py).
dl_post eustat_tasas_nacionalidad_gipuzkoa.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_050403_cpra_tab17.px" \
  '{"query":[{"code":"tasa (%)","selection":{"filter":"item","values":["10","20","30"]}},{"code":"territorio histórico","selection":{"filter":"item","values":["20"]}},{"code":"nacionalidad","selection":{"filter":"item","values":["10","20","30"]}},{"code":"trimestre","selection":{"filter":"item","values":["10"]}}],"response":{"format":"json"}}'
dl_post eustat_id_personal_gipuzkoa.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_043201_cid_res08c.px" \
  '{"query":[{"code":"territorio histórico","selection":{"filter":"item","values":["20"]}},{"code":"sector de ejecución","selection":{"filter":"item","values":["00","10","20","30"]}},{"code":"ocupación","selection":{"filter":"item","values":["100","200","300","400"]}},{"code":"sexo","selection":{"filter":"item","values":["10"]}}],"response":{"format":"json"}}'
dl_post eustat_poblacion_ocupada_total.json \
  "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_050403_cpra_tab04.px" \
  '{"query":[{"code":"relación con la actividad (OIT)","selection":{"filter":"item","values":["30"]}},{"code":"territorio histórico","selection":{"filter":"item","values":["00","20"]}},{"code":"sexo","selection":{"filter":"item","values":["10"]}},{"code":"trimestre","selection":{"filter":"item","values":["10"]}}],"response":{"format":"json"}}'

# Inside Airbnb snapshots trimestrales (REC-13): anuncios activos por fecha
# (CSV resumen, uno por snapshot). Solo lo usa analysis/airbnb_snapshots.py.
# Los snapshots 2021-12-30…2023-09-24 ya no se sirven (403; data request).
for d in 2023-12-29 2024-03-31 2024-06-30 2024-09-29 2024-12-31 2025-03-27 2025-06-28 2025-09-29; do
  dl "airbnb_snapshot_$d.csv" "https://data.insideairbnb.com/spain/pv/euskadi/$d/visualisations/listings.csv"
done

# INE Tablas de Mortalidad (AN-12): riesgo de muerte quinquenal (qx, ‰) de
# Gipuzkoa por sexo y grupo de edad, 1991–. Solo lo usa analysis/ (no es un
# input del pipeline). Filtro server-side: tv=115:21 (prov. Gipuzkoa),
# tv=260:311511 (función "Riesgo de muerte").
dl ine_mortalidad_gipuzkoa.json "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/67235?tv=115:21&tv=260:311511&nult=600"

if [ -n "${AEMET_API_KEY:-}" ]; then
  echo "· AEMET: usa el pipeline (ventanas de 3 años + backoff): cd data-pipeline && python -m donostia_pipeline.build"
else
  echo "· AEMET omitido (exporta AEMET_API_KEY para incluir el clima)"
fi

echo "Hecho. Crudos en: $DEST"
