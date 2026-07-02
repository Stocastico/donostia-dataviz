"""AN-9 — Sensibilidad de pesos del Índice de Transformación (AN-8).

El índice AN-8 usa pesos iguales entre componentes (decisión documentada).
Este análisis responde a la crítica del feedback externo (jul-2026, consenso
de las 3 IAs): ¿el ranking depende de esa elección de pesos?

  1. ~1000 permutaciones aleatorias de pesos (Dirichlet plano sobre el símplex)
     → distribución del rank de cada barrio (mediana, min–max, % veces top-1/3).
  2. Variantes fijas 60/40 y 40/60 (y 50/50 como referencia).
  3. PCA **solo como contraste** (frágil con N=13, nunca método principal —
     decisión firme del BACKLOG): ¿la 1ª componente ordena como el índice?

Se aplica a los dos modos del índice (ver INDICE-TRANSFORMACION.md):
  A) socioeconómico  — componentes univ_excess, rent_excess (2 pesos)
  B) presión turística — vut_density, airbnb_density, alquiler_nivel (3 pesos)

Solo pandas + numpy, como el resto de analysis/.

Uso:
    python analysis/index_sensitivity.py [--save]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import transformation_index as ti

OUTDIR = Path(__file__).resolve().parent / "output"
N_PERM = 1000
SEED = 42
# Variantes fijas pedidas por AN-9 (para 2 componentes; en el modo B de 3
# componentes la exploración la cubren las permutaciones aleatorias).
FIXED_2 = {"50/50": (0.5, 0.5), "60/40": (0.6, 0.4), "40/60": (0.4, 0.6)}


# ---------------------------------------------------------------------------
# núcleo
# ---------------------------------------------------------------------------
def zscores(components: pd.DataFrame) -> pd.DataFrame:
    return (components - components.mean()) / components.std()


def random_weights(n: int, k: int, seed: int) -> np.ndarray:
    """n vectores de k pesos ≥0 que suman 1 (Dirichlet plano: uniforme en el símplex)."""
    rng = np.random.default_rng(seed)
    return rng.dirichlet(np.ones(k), size=n)


def score(components: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Suma ponderada de z-scores. Con pesos iguales reproduce el score AN-8
    (media de z). Filas con algún componente NaN → NaN."""
    z = zscores(components)
    w = np.asarray(weights, dtype=float)
    return (z * w).sum(axis=1, min_count=len(w))


def ranks(components: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Rank 1 = score más alto; excluye barrios con componentes incompletos."""
    s = score(components, weights).dropna()
    return s.rank(ascending=False, method="min").astype(int)


def rank_stability(components: pd.DataFrame, n: int = N_PERM,
                   seed: int = SEED) -> pd.DataFrame:
    """Distribución del rank bajo n pesos aleatorios, con el 50/50 de referencia."""
    k = components.shape[1]
    base = ranks(components, np.full(k, 1.0 / k))
    idx = base.index
    R = np.vstack([ranks(components, w).loc[idx].to_numpy()
                   for w in random_weights(n, k, seed)])
    return pd.DataFrame({
        "rank_igual": base,
        "rank_mediana": np.median(R, axis=0),
        "rank_min": R.min(axis=0),
        "rank_max": R.max(axis=0),
        "pct_top1": (R == 1).mean(axis=0).round(3),
        "pct_top3": (R <= 3).mean(axis=0).round(3),
    }, index=idx).sort_values("rank_igual")


def fixed_variants(components: pd.DataFrame,
                   variants: dict[str, tuple[float, ...]]) -> pd.DataFrame:
    """Ranks bajo cada variante fija de pesos (columnas en el orden dado)."""
    return pd.DataFrame({name: ranks(components, np.array(w))
                         for name, w in variants.items()})


def pca_contrast(components: pd.DataFrame) -> tuple[pd.Series, pd.Series, float]:
    """PC1 sobre la matriz de correlación (solo contraste, frágil con N=13).

    Devuelve (scores PC1, cargas, % varianza explicada). Signo fijado para que
    la suma de cargas sea positiva (más componente = más transformación).
    """
    X = components.dropna()
    z = zscores(X)
    evals, evecs = np.linalg.eigh(z.corr().to_numpy())
    v = evecs[:, -1]
    if v.sum() < 0:
        v = -v
    scores = pd.Series(z.to_numpy() @ v, index=X.index)
    loadings = pd.Series(v, index=X.columns)
    evr = float(evals[-1] / evals.sum())
    return scores, loadings, evr


# ---------------------------------------------------------------------------
# datos reales (componentes del AN-8)
# ---------------------------------------------------------------------------
def load_components() -> dict[str, pd.DataFrame]:
    """Componentes de los dos modos del índice, restringidos a los N=13
    barrios clasificables (los mismos del ranking publicado)."""
    df = ti.load()
    out = ti.build()
    clasificables = out.dropna(subset=["renta_base", "rent_rate", "univ_rate"]).index

    a = out.loc[clasificables, ["univ_excess", "rent_excess"]]
    b = pd.DataFrame({
        "vut_density": out["vut_density"],
        "airbnb_density": ti.snapshot(df, "airbnb_density"),
        "alquiler_nivel": out["alquiler_nivel"],
    }).loc[clasificables]
    return {"socioeconomico": a, "presion_turistica": b}


def report(name: str, components: pd.DataFrame, save: bool) -> None:
    print(f"\n{'=' * 74}\n## MODO {name.upper()}  ·  componentes: {list(components.columns)}\n")
    tab = rank_stability(components)
    print(f"Estabilidad del ranking bajo {N_PERM} pesos aleatorios (rank 1 = mayor score):\n")
    print(tab.to_string())

    if components.shape[1] == 2:
        fv = fixed_variants(components, FIXED_2).loc[tab.index]
        print("\nVariantes fijas de pesos (rank por barrio):\n")
        print(fv.to_string())

    scores, loadings, evr = pca_contrast(components)
    pca_rank = scores.rank(ascending=False, method="min").astype(int)
    agree = (pca_rank.sort_index() == tab["rank_igual"].sort_index()).mean()
    print(f"\nContraste PCA (solo contraste, N={len(components.dropna())}): "
          f"PC1 explica {evr:.0%}; cargas {loadings.round(2).to_dict()}; "
          f"coincidencia de rank con 50/50: {agree:.0%}")

    if save:
        OUTDIR.mkdir(exist_ok=True)
        path = OUTDIR / f"index_sensitivity_{name}.csv"
        tab.join(pd.Series(pca_rank, name="rank_pca")).to_csv(path)
        print(f"[guardado] {path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    print("=" * 74)
    print("AN-9 · SENSIBILIDAD DE PESOS DEL ÍNDICE DE TRANSFORMACIÓN (AN-8)")
    print("=" * 74)
    print(f"\n{N_PERM} permutaciones Dirichlet (semilla {SEED}) + variantes fijas + PCA contraste.")

    for name, comps in load_components().items():
        report(name, comps, args.save)


if __name__ == "__main__":
    main()
