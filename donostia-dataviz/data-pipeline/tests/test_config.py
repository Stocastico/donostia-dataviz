"""Unit tests for barrio identity (slug + alias)."""

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
