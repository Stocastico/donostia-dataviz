"""TDD: REC-15 — protected-housing (Etxebide/VPO) footprint per barrio.

Source CSV has a shifted header: the dwelling count sits in the column labelled
``Tipologia`` (``NumViviendas`` is empty in every row), and coordinates are UTM
(EPSG:25830) with comma decimals. These tests pin that parsing plus the
per-barrio dwelling sum and per-1000 normalization; reprojection itself is
covered by test_gis_io.
"""

import json

from conftest import write_csv

from donostia_pipeline.datasets import vpo_etxebide as mod
from donostia_pipeline.gis_io import reproject_point
from donostia_pipeline.model import BuildContext
from donostia_pipeline.spatial import BarrioIndex

# Two Donostia-like rows; note: dwellings in the "Tipologia" column, empty
# NumViviendas, comma decimals in UTMX/UTMY, and a Bizkaia row that must survive
# parsing but fall outside the city geometry.
FIXTURE = (
    "ID_PROM;Cod_Prov;Territorio;CODMUNI;Municipio;Expediente;Ubicacion;"
    "NumViviendas;Tipologia;Reg Acceso;UTMX;UTMY;UTMA;Sorteo;EstadoObra;"
    "Promotor;Expediente_eu;Ubicacion_eu;Tipologia_eu;RegAcceso_eu;"
    "EstadoObra_eu;Promotor_eu\n"
    "1;20;GIPUZKOA;069;DONOSTIA-SAN SEBASTIAN;X;calle A;;80;Propiedad;"
    "583452,35;4796012,02;30;;Terminada;VISESA;;;;;;\n"
    "2;20;GIPUZKOA;069;DONOSTIA-SAN SEBASTIAN;Y;calle B;;20;Arrendamiento;"
    "583460,00;4796020,00;30;;En Curso;ALOKABIDE;;;;;;\n"
    "3;48;BIZKAIA;029;ETXEBARRI;Z;calle C;;10;Propiedad;"
    "508650,67;4788060,89;30;;Terminada;VISESA;;;;;;\n"
)


def test_parse_rows_reads_dwellings_from_tipologia_column(tmp_path):
    write_csv(tmp_path, mod.CSV_NAME, FIXTURE)
    rows = mod.parse_rows(tmp_path / mod.CSV_NAME)
    assert len(rows) == 3
    r = rows[0]
    assert r.dwellings == 80
    assert r.utmx == 583452.35 and r.utmy == 4796012.02  # comma → dot


def test_aggregate_sums_dwellings_not_counts_points():
    def sq(x0, x1):
        return [[[x0, 0], [x1, 0], [x1, 10], [x0, 10], [x0, 0]]]

    geo = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"barrio_id": "a"},
         "geometry": {"type": "Polygon", "coordinates": sq(0, 10)}},
        {"type": "Feature", "properties": {"barrio_id": "b"},
         "geometry": {"type": "Polygon", "coordinates": sq(10, 20)}},
    ]}
    index = BarrioIndex(geo)
    located = [(5.0, 5.0, 80), (6.0, 6.0, 20), (15.0, 5.0, 7)]
    assert mod.aggregate(index, located) == {"a": 100, "b": 7}


def _ctx_with_geometry_around(tmp_path):
    # Place barrio "a" as a small WGS84 box around the reprojected fixture coords
    # so both Donostia rows land in it; "b" sits elsewhere with none.
    lon, lat = reproject_point(583455.0, 4796015.0)
    d = 0.01
    def box(clon, clat):
        return [[[clon - d, clat - d], [clon + d, clat - d],
                 [clon + d, clat + d], [clon - d, clat + d], [clon - d, clat - d]]]
    geo = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"barrio_id": "a"},
         "geometry": {"type": "Polygon", "coordinates": box(lon, lat)}},
        {"type": "Feature", "properties": {"barrio_id": "b"},
         "geometry": {"type": "Polygon", "coordinates": box(lon + 1, lat + 1)}},
    ]}
    write_csv(tmp_path, mod.CSV_NAME, FIXTURE)
    return BuildContext(
        raw_dir=tmp_path, barrio_ids={"a", "b"}, code_to_id={},
        barrio_index=BarrioIndex(geo),
        population_latest={"a": 5000, "b": 1000},
    )


def test_build_metric_shape_and_per_1000(tmp_path):
    (m,) = mod.build(_ctx_with_geometry_around(tmp_path))
    assert m.id == "vpo_dwellings_per_1000"
    assert m.unit == "per 1000 ab."
    assert m.theme == "housing"
    assert m.time_grain == "snapshot"
    # a: (80+20) dwellings / 5000 * 1000 = 20.0 ; b: no promotions → 0/1000 = 0.0
    assert m.values["a"]["actual"] == 20.0
    assert m.values["b"]["actual"] == 0.0
    # Bizkaia row reprojects outside both boxes → dropped, not an error.


def test_returns_nothing_without_spatial_index(tmp_path):
    ctx = _ctx_with_geometry_around(tmp_path)
    ctx.barrio_index = None
    assert mod.build(ctx) == []
