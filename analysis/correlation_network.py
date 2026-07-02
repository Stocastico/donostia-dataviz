"""AN-17 — Red de correlaciones variable↔variable.

Grafo donde los nodos son las métricas de corte transversal del Sprint A y
hay arista solo si la correlación es **robusta**: |Pearson| ≥ umbral **y**
|Spearman| ≥ umbral (la exigencia doble filtra correlaciones sostenidas por
un outlier) con un n mínimo de barrios. La "fuerza" de cada nodo (suma de |r|
de sus aristas) identifica las variables centrales del sistema: ¿la renta
conecta todo?

Solo pandas + numpy. Uso:
    python analysis/correlation_network.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import sprint_a
from sprint_a import CROSS_METRICS, latest_cross, spearman

OUTDIR = Path(__file__).resolve().parent / "output"
THRESHOLD = 0.5
MIN_N = 10


def robust_edges(X: pd.DataFrame, threshold: float = THRESHOLD,
                 min_n: int = MIN_N) -> list[dict]:
    """Aristas robustas entre columnas de X (doble umbral Pearson+Spearman)."""
    cols = list(X.columns)
    edges = []
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            j = X[[a, b]].dropna()
            if len(j) < min_n:
                continue
            p = j[a].corr(j[b])
            s = spearman(j[a], j[b])
            if abs(p) >= threshold and abs(s) >= threshold:
                edges.append({"var_a": a, "var_b": b, "n": len(j),
                              "pearson": round(float(p), 3),
                              "spearman": round(float(s), 3)})
    return sorted(edges, key=lambda e: -abs(e["pearson"]))


def node_strength(edges: list[dict]) -> pd.DataFrame:
    """Grado y fuerza (suma de |pearson|) por nodo, ordenado por fuerza."""
    acc: dict[str, dict[str, float]] = {}
    for e in edges:
        for v in (e["var_a"], e["var_b"]):
            d = acc.setdefault(v, {"grado": 0, "fuerza": 0.0})
            d["grado"] += 1
            d["fuerza"] += abs(e["pearson"])
    tab = pd.DataFrame(acc).T
    tab["grado"] = tab["grado"].astype(int)
    tab["fuerza"] = tab["fuerza"].round(2)
    return tab.sort_values("fuerza", ascending=False)


def build_network() -> list[dict]:
    df = sprint_a.load()
    X = pd.concat([latest_cross(df, m) for m in CROSS_METRICS], axis=1)
    return robust_edges(X)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    edges = build_network()
    print("=" * 74)
    print(f"AN-17 · RED DE CORRELACIONES  (|Pearson| y |Spearman| ≥ {THRESHOLD}, n ≥ {MIN_N})")
    print("=" * 74)
    print(f"\n## Aristas robustas ({len(edges)})\n")
    print(pd.DataFrame(edges).to_string(index=False))

    print("\n## Centralidad (fuerza = Σ|r| de las aristas del nodo)\n")
    print(node_strength(edges).to_string())

    print("\nLectura: doble umbral Pearson+Spearman → una arista no puede deberse")
    print("a un solo outlier. Correlación ≠ causalidad (MET-3); N=13–18 barrios.")

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        pd.DataFrame(edges).to_csv(OUTDIR / "correlation_network_edges.csv", index=False)
        node_strength(edges).to_csv(OUTDIR / "correlation_network_nodes.csv")
        print(f"\n[guardado] {OUTDIR/'correlation_network_edges.csv'} · "
              f"{OUTDIR/'correlation_network_nodes.csv'}")


if __name__ == "__main__":
    main()
