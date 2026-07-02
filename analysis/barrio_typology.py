"""AN-11 — Tipologías de barrio: clustering jerárquico + silhouette.

Refina el k-means k=4 del Sprint A con un método que no exige fijar k a
priori: clustering jerárquico aglomerativo (enlace promedio, distancia
euclídea sobre variables estandarizadas — Lance-Williams, numpy puro) +
coeficiente de silhouette por k para ver qué partición sostienen los datos.
Extras del backlog: "barrio más parecido" (matriz de distancias) y el ranking
multivariable de cambio ya existente (speed_index del Sprint A).

Variables: las mismas CLUSTER_VARS del Sprint A (renta, % universitarios,
densidad VUT, alquiler), último valor por barrio, estandarizadas.

Solo pandas + numpy. Uso:
    python analysis/barrio_typology.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import sprint_a
from sprint_a import CLUSTER_VARS, latest_cross

OUTDIR = Path(__file__).resolve().parent / "output"

Merge = tuple[int, int, float, int]  # (id_a, id_b, altura, tamaño resultante)


# ---------------------------------------------------------------------------
# clustering jerárquico (enlace promedio, Lance-Williams)
# ---------------------------------------------------------------------------
def _pairwise(X: np.ndarray) -> np.ndarray:
    diff = X[:, None, :] - X[None, :, :]
    return np.sqrt((diff**2).sum(-1))


def linkage_average(X: np.ndarray) -> list[Merge]:
    """Fusiones aglomerativas (average linkage). Ids: 0..n-1 hojas; n.. internos."""
    n = len(X)
    D = _pairwise(X)
    dist: dict[tuple[int, int], float] = {
        (i, j): float(D[i, j]) for i in range(n) for j in range(i + 1, n)
    }
    sizes = {i: 1 for i in range(n)}
    active = set(range(n))
    merges: list[Merge] = []
    next_id = n
    while len(active) > 1:
        (a, b), h = min(
            ((p, d) for p, d in dist.items()
             if p[0] in active and p[1] in active),
            key=lambda t: t[1],
        )
        new_size = sizes[a] + sizes[b]
        merges.append((a, b, h, new_size))
        for c in active - {a, b}:
            d_ac = dist[(min(a, c), max(a, c))]
            d_bc = dist[(min(b, c), max(b, c))]
            dist[(c, next_id)] = (sizes[a] * d_ac + sizes[b] * d_bc) / new_size
        active -= {a, b}
        active.add(next_id)
        sizes[next_id] = new_size
        next_id += 1
    return merges


def cut_labels(merges: list[Merge], n: int, k: int) -> np.ndarray:
    """Etiquetas 0..k-1 al cortar el árbol en k clusters (aplica n−k fusiones)."""
    clusters: dict[int, list[int]] = {i: [i] for i in range(n)}
    next_id = n
    for a, b, _h, _s in merges[: n - k]:
        clusters[next_id] = clusters.pop(a) + clusters.pop(b)
        next_id += 1
    labels = np.empty(n, dtype=int)
    for j, cid in enumerate(sorted(clusters)):
        for m in clusters[cid]:
            labels[m] = j
    return labels


# ---------------------------------------------------------------------------
# silhouette
# ---------------------------------------------------------------------------
def silhouette_mean(X: np.ndarray, labels: np.ndarray) -> float:
    """Silhouette media; los singletons puntúan 0 (convención estándar)."""
    D = _pairwise(np.asarray(X, float))
    labels = np.asarray(labels)
    scores = []
    for i in range(len(X)):
        same = labels == labels[i]
        n_same = same.sum() - 1
        if n_same == 0:
            scores.append(0.0)
            continue
        a = D[i, same].sum() / n_same
        b = min(D[i, labels == other].mean()
                for other in set(labels) - {labels[i]})
        scores.append((b - a) / max(a, b))
    return float(np.mean(scores))


def silhouette_by_k(X: pd.DataFrame, ks=range(2, 7)) -> pd.DataFrame:
    Xn = X.to_numpy(float)
    merges = linkage_average(Xn)
    rows = {k: {"silhouette": round(silhouette_mean(Xn, cut_labels(merges, len(X), k)), 3)}
            for k in ks}
    return pd.DataFrame(rows).T.rename_axis("k")


# ---------------------------------------------------------------------------
# vecino más parecido
# ---------------------------------------------------------------------------
def nearest_neighbour(X: pd.DataFrame) -> pd.DataFrame:
    """Barrio más parecido (euclídea sobre las columnas tal cual se pasan)."""
    M = _pairwise(X.to_numpy(float))
    np.fill_diagonal(M, np.inf)
    D = pd.DataFrame(M, index=X.index, columns=X.index)
    return pd.DataFrame({"vecino": D.idxmin(axis=1),
                         "distancia": D.min(axis=1).round(3)})


# ---------------------------------------------------------------------------
# datos reales
# ---------------------------------------------------------------------------
def load_typology_vars() -> pd.DataFrame:
    """CLUSTER_VARS del Sprint A, último valor por barrio, estandarizadas."""
    df = sprint_a.load()
    X = pd.concat([latest_cross(df, m) for m in CLUSTER_VARS], axis=1).dropna()
    return (X - X.mean()) / X.std()


def _dendro_text(merges: list[Merge], names: list[str]) -> list[str]:
    """Dendrograma como lista de fusiones legibles (de más cercana a más lejana)."""
    label = {i: names[i] for i in range(len(names))}
    out = []
    next_id = len(names)
    for a, b, h, _s in merges:
        la, lb = label.pop(a), label.pop(b)
        label[next_id] = f"({la} + {lb})"
        out.append(f"h={h:5.2f}  {la}  +  {lb}")
        next_id += 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    X = load_typology_vars()
    names = list(X.index)
    merges = linkage_average(X.to_numpy(float))

    print("=" * 74)
    print("AN-11 · TIPOLOGÍAS DE BARRIO — clustering jerárquico (average linkage)")
    print("=" * 74)
    print(f"\nVariables (z): {CLUSTER_VARS} · N={len(X)} barrios\n")

    sil = silhouette_by_k(X)
    best_k = int(sil["silhouette"].idxmax())
    print("## Silhouette por k (¿qué partición sostienen los datos?)\n")
    print(sil.to_string())
    print(f"\nMejor k por silhouette: {best_k} · el k-means del Sprint A usa k=4 "
          f"(silhouette jerárquico {sil.loc[4, 'silhouette']}).")

    print(f"\n## Clusters al corte k={best_k}\n")
    labels = cut_labels(merges, len(X), best_k)
    for j in sorted(set(labels)):
        members = [names[i] for i in range(len(X)) if labels[i] == j]
        print(f"  cluster {j}: {', '.join(members)}")

    print("\n## Dendrograma (fusiones, de más parecidos a más lejanos)\n")
    for line in _dendro_text(merges, names):
        print("  " + line)

    print("\n## Barrio más parecido (euclídea sobre variables z)\n")
    nn = nearest_neighbour(X)
    print(nn.to_string())

    print("\n## Ranking multivariable de cambio 2016→ (speed_index, Sprint A)\n")
    vel = sprint_a.velocity(sprint_a.load())
    print(vel["speed_index"].head(8).round(2).to_string())

    if args.save:
        OUTDIR.mkdir(exist_ok=True)
        sil.to_csv(OUTDIR / "typology_silhouette.csv")
        out = X.copy()
        out["cluster_jerarquico"] = labels
        out.join(nn).to_csv(OUTDIR / "typology_clusters.csv")
        print(f"\n[guardado] {OUTDIR/'typology_silhouette.csv'} · "
              f"{OUTDIR/'typology_clusters.csv'}")


if __name__ == "__main__":
    main()
