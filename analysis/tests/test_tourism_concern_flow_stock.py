"""Tests de H8 — la preocupación por el turismo sube cuando el FLUJO de altas baja.

Idea: lo que preocupa (encuesta 2026, turismo entra al top-3) no es el flujo de
licencias nuevas (que se ha desplomado) sino el STOCK acumulado y el volumen
real, ambos en máximos. Funciones puras + integración con los indicadores REATE
y las pernoctaciones reales.
"""
import pandas as pd
import pytest

import tourism_concern_flow_stock as fs


# --------------------------------------------------------- funciones puras ----
def test_stock_growth_rate():
    new = pd.Series({2017: 300, 2018: 189})
    cum = pd.Series({2016: 175, 2017: 475, 2018: 664})
    g = fs.stock_growth_rate(new, cum)
    assert g[2017] == pytest.approx(300 / 175)   # altas / stock previo
    assert g[2018] == pytest.approx(189 / 475)


def test_change_sign():
    assert fs.change_sign(pd.Series({2017: 300, 2025: 18})) == "baja"
    assert fs.change_sign(pd.Series({2017: 475, 2025: 1329})) == "sube"


def test_divergence_flow_down_stock_up():
    flow = pd.Series({2017: 300, 2025: 18})
    stock = pd.Series({2017: 475, 2025: 1329})
    d = fs.divergence(flow, stock, 2017, 2025)
    assert d["flow"] == "baja"
    assert d["stock"] == "sube"
    assert d["diverge"] is True          # flujo y stock en sentidos opuestos


# ------------------------------------------------------- integración real ----
def test_real_flow_collapses_from_peak():
    flow = fs.read_indicator("vut_licenses_new")
    assert flow.idxmax() == 2017 and flow[2017] == 300
    assert flow[2025] == 18
    assert (flow[2025] / flow[2017] - 1) < -0.9      # -94 %


def test_real_stock_at_record_while_flow_falls():
    flow = fs.read_indicator("vut_licenses_new")
    stock = fs.read_indicator("vut_licenses_cumulative")
    d = fs.divergence(flow, stock, 2017, 2025)
    assert d["diverge"] is True
    assert stock.idxmax() == 2025                     # stock en máximo histórico


def test_real_stock_growth_rate_near_zero_recently():
    new = fs.read_indicator("vut_licenses_new")
    cum = fs.read_indicator("vut_licenses_cumulative")
    g = fs.stock_growth_rate(new, cum)
    assert g[2017] > 1.0        # en 2017 el parque casi triplicaba
    assert g[2025] < 0.03       # en 2025 el stock apenas se mueve


def test_real_volume_at_record():
    ov = fs.annual_overnight()
    assert ov.idxmax() == 2025                       # pernoctaciones en récord
    assert ov[2025] > ov[2019]
