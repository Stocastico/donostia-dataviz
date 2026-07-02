"""Tests de AN-17 — red de correlaciones robustas entre variables."""
import numpy as np
import pandas as pd

import correlation_network as cn


def _frame(n: int = 30, seed: int = 42) -> pd.DataFrame:
    """a≈b (fuerte +), c≈−a (fuerte −), d ruido independiente."""
    rng = np.random.default_rng(seed)
    a = pd.Series(rng.normal(size=n))
    return pd.DataFrame({
        "a": a,
        "b": a + rng.normal(scale=0.2, size=n),
        "c": -a + rng.normal(scale=0.2, size=n),
        "d": rng.normal(size=n),
    })


def test_edges_detect_strong_pairs_and_skip_noise():
    edges = cn.robust_edges(_frame(), threshold=0.5, min_n=10)
    pairs = {frozenset((e["var_a"], e["var_b"])) for e in edges}
    assert frozenset(("a", "b")) in pairs
    assert frozenset(("a", "c")) in pairs
    assert not any("d" in p for p in pairs)


def test_edges_carry_signed_r_and_n():
    edges = cn.robust_edges(_frame(), threshold=0.5, min_n=10)
    ab = next(e for e in edges if {e["var_a"], e["var_b"]} == {"a", "b"})
    ac = next(e for e in edges if {e["var_a"], e["var_b"]} == {"a", "c"})
    assert ab["pearson"] > 0.9
    assert ac["pearson"] < -0.9
    assert ab["n"] == 30


def test_edge_requires_both_pearson_and_spearman():
    """Un par con Pearson alto solo por un outlier (Spearman bajo) no es arista."""
    x = pd.Series([0.0] * 14 + [100.0])
    y = pd.Series(list(np.linspace(1, -1, 14)) + [100.0])  # rango invertido salvo outlier
    df = pd.DataFrame({"x": x, "y": y})
    assert df["x"].corr(df["y"]) > 0.5          # Pearson engañado por el outlier
    edges = cn.robust_edges(df, threshold=0.5, min_n=10)
    assert edges == []


def test_node_strength_orders_by_connectivity():
    tab = cn.node_strength(cn.robust_edges(_frame(), threshold=0.5, min_n=10))
    assert tab.index[0] == "a"          # conecta con b y con c
    assert "d" not in tab.index
    assert tab.loc["a", "grado"] == 2


def test_real_data_network_structure():
    edges = cn.build_network()
    assert len(edges) >= 3
    for e in edges:
        assert abs(e["pearson"]) >= cn.THRESHOLD
        assert abs(e["spearman"]) >= cn.THRESHOLD
        assert e["n"] >= cn.MIN_N
