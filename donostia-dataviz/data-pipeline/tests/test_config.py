"""Unit tests for barrio identity (slug + alias) and shared paths."""

from donostia_pipeline import config
from donostia_pipeline.config import canonical_barrio_id, slugify_barrio


def test_slugify_strips_accents_and_spaces():
    assert slugify_barrio("AÑORGA") == "anorga"
    assert slugify_barrio("MIRAMON - ZORROAGA") == "miramon-zorroaga"
    assert slugify_barrio("  Egia ") == "egia"


def test_alias_maps_alternate_spellings():
    # Different sources spell the same barrio differently.
    assert canonical_barrio_id("Amara Berri") == "amaraberri"
    assert canonical_barrio_id("AMARABERRI") == "amaraberri"
    assert canonical_barrio_id("Centro") == "erdialdea"


def test_unaliased_name_falls_back_to_slug():
    assert canonical_barrio_id("GROS") == "gros"


def test_curated_dir_points_at_datos_input():
    # Single source of truth for hand-curated inputs: datos/input/, not the
    # pipeline's own (now-removed) curated/ copy.
    assert config.CURATED_DIR == config.PIPELINE_ROOT.parent / "datos" / "input"
    assert (config.CURATED_DIR / "mice_donostia.csv").is_file()
