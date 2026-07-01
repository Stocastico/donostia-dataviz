"""Shared configuration: paths, the barrio-id slugger, and source URLs.

Keeping these in one place means a dataset module only needs its own source URL
and transform; everything else (where to read raw, where to write JSON, how to
slug a barrio name) is shared and consistent.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PIPELINE_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PIPELINE_ROOT / "raw"
# Hand-curated, source-cited inputs that aren't auto-fetched (e.g. MICE).
CURATED_DIR = PIPELINE_ROOT.parent / "datos" / "input"
# Pipeline writes cleaned JSON straight into the web app's data folder.
WEB_DATA_DIR = PIPELINE_ROOT.parent / "web" / "src" / "data"
# …and language-agnostic tidy CSV tables here, for reuse outside the app.
TABLES_DIR = PIPELINE_ROOT.parent / "datos" / "procesado" / "tablas"

# ---------------------------------------------------------------------------
# Source URLs (see docs/SOURCES.md for access status)
# ---------------------------------------------------------------------------
BARRIOS_GEOJSON_URL = (
    "https://www.donostia.eus/datosabiertos/recursos/mapa_auzoak/auzoak.json"
)
VUT_CENSUS_URL = (
    "https://www.donostia.eus/datosabiertos/catalogo/censo-viviendas-turisticas"
)

# AEMET OpenData needs a free key; absent → AEMET build is skipped (registered
# as "planned"). Read from the environment so the key is never committed.
AEMET_API_KEY_ENV = "AEMET_API_KEY"
AEMET_IGELDO_STATION = "1024E"

# ---------------------------------------------------------------------------
# Barrio identity
# ---------------------------------------------------------------------------
# Some source datasets spell barrio names differently from the reference
# geometry. Map their raw spelling -> reference name here, never drop silently.
BARRIO_NAME_ALIASES: dict[str, str] = {
    "amara berri": "amaraberri",
    "amara": "amaraberri",
    "centro": "erdialdea",
    "parte vieja": "erdialdea",
}


def slugify_barrio(name: str) -> str:
    """Stable ``barrio_id`` slug: lowercased, accent-stripped, hyphenated.

    ``"MIRAMON - ZORROAGA"`` -> ``"miramon-zorroaga"``. Applied to both the
    geometry and every dataset so the join key is identical on both sides.
    """
    text = unicodedata.normalize("NFKD", name)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def canonical_barrio_id(name: str) -> str:
    """Slug a raw barrio name after applying the alias map."""
    aliased = BARRIO_NAME_ALIASES.get(name.lower().strip(), name)
    return slugify_barrio(aliased)
