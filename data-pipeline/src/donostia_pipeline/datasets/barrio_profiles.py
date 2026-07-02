"""Derived categorical metric: barrio typology / profiles (AN-3).

Surfaces the Sprint A neighbourhood typology (``docs/ANALISIS-SPRINT-A.md`` §3)
as a *categorical* choropleth: each barrio is assigned one of four descriptive
profiles by k-means (k=4) over four standardized variables already in the store
— income, % university, VUT density, rent. Reads no raw files (same pattern as
``housing_tension``/``change_velocity``).

This intentionally re-runs the **exact** deterministic clustering of
``analysis/sprint_a.py`` (same variables, standardization, fixed seed and
``n_init``) so the map mirrors the documented, reviewed analysis byte-for-byte;
``tests/test_barrio_profiles.py`` locks the resulting assignment.

Caveat (documented, not hidden): with only ~13 barrios carrying all four
variables, cluster boundaries are sensitive to scaling and seed. These are
**descriptive profiles, not a hard classification** — read alongside the
analysis note. Cluster *labels* are assigned from each cluster's centroid (not
k-means' arbitrary internal index), then mapped to a fixed profile order so the
category indices are stable across rebuilds.
"""

from __future__ import annotations

import numpy as np

from ..model import Metric

# The four standardized variables (same as analysis/sprint_a.py).
CLUSTER_VARS = ["income_total", "pct_university", "vut_density", "rent_eur_m2"]
K = 4
SEED = 42
N_INIT = 50

# Profile labels (Italian, to match the dashboard) in a fixed order →
# the category index a barrio gets is its position in this list.
PROFILES = [
    "Centrale turistico, reddito alto",
    "Residenziale benestante",
    "Transizionale / misto",
    "Popolare / in tensione",
]
PROFILE_INDEX = {name: i for i, name in enumerate(PROFILES)}

SOURCE = (
    "Derivata — tipologia di barrio (k-means k=4 su reddito, % laureati, "
    "densità VUT, affitto standardizzati; cfr. ANALISIS-SPRINT-A.md §3)"
)


def _latest(metric: Metric, barrio_id: str) -> float | None:
    """Latest non-null value for a barrio (max period by sort order)."""
    by_period = metric.values.get(barrio_id, {})
    for period in sorted(by_period, reverse=True):
        v = by_period[period]
        if v is not None:
            return float(v)
    return None


def _kmeans(X: np.ndarray, k: int, seed: int, n_init: int, max_iter: int = 300) -> np.ndarray:
    """Lloyd's k-means, best of ``n_init`` (verbatim from analysis/sprint_a.py)."""
    rng = np.random.default_rng(seed)
    best_labels, best_inertia = None, np.inf
    for _ in range(n_init):
        centers = X[rng.choice(len(X), k, replace=False)]
        labels = np.zeros(len(X), dtype=int)
        for _ in range(max_iter):
            d = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
            labels = d.argmin(1)
            new = np.array([X[labels == j].mean(0) if (labels == j).any()
                            else centers[j] for j in range(k)])
            if np.allclose(new, centers):
                break
            centers = new
        inertia = ((X - centers[labels]) ** 2).sum()
        if inertia < best_inertia:
            best_inertia, best_labels = inertia, labels
    return best_labels


def _name(centroid: dict[str, float]) -> str:
    """Map a cluster's z-score centroid to a profile name (as in sprint_a)."""
    if centroid["vut_density"] > 0.6 and centroid["rent_eur_m2"] > 0.3:
        return "Centrale turistico, reddito alto"
    if centroid["income_total"] > 0.5 and centroid["vut_density"] < 0.2:
        return "Residenziale benestante"
    if centroid["income_total"] < -0.3:
        return "Popolare / in tensione"
    return "Transizionale / misto"


def build_from_metrics(metrics: dict[str, Metric]) -> list[Metric]:
    bases = [metrics.get(v) for v in CLUSTER_VARS]
    if any(b is None for b in bases):
        return []

    # Barrios with all four variables present (latest value each).
    ids: list[str] = []
    rows: list[list[float]] = []
    candidate_ids = set().union(*(b.values for b in bases))
    for bid in sorted(candidate_ids):
        vals = [_latest(b, bid) for b in bases]
        if any(v is None for v in vals):
            continue
        ids.append(bid)
        rows.append([float(v) for v in vals])  # type: ignore[arg-type]

    if len(ids) < K:
        return []

    X = np.array(rows, dtype=float)
    # Standardize with sample std (ddof=1) to match pandas .std() in sprint_a.
    Z = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
    labels = _kmeans(Z, k=K, seed=SEED, n_init=N_INIT)

    # Name each cluster from its centroid, then map to the fixed profile index.
    period = "perfil"  # single snapshot period
    values: dict[str, dict[str, float | None]] = {}
    for cluster in range(K):
        members = labels == cluster
        if not members.any():
            continue
        centroid = {var: Z[members, i].mean() for i, var in enumerate(CLUSTER_VARS)}
        idx = PROFILE_INDEX[_name(centroid)]
        for bid in (b for b, m in zip(ids, members) if m):
            values[bid] = {period: float(idx)}

    return [
        Metric(
            id="barrio_profile",
            label="Profilo del barrio (tipologia)",
            unit="",
            kind="categorical",
            theme="change",
            source=SOURCE,
            geo_grain="barrio",
            time_grain="snapshot",
            periods=[period],
            values=values,
            categories=list(PROFILES),
        )
    ]
