"""
Asymmetry bookkeeping and persistence diagnostics.

eta(t) = (N_matter(t) - N_antimatter(t)) / (N_matter(t) + N_antimatter(t))

is computed directly from src.visible_sector.particles.eta_from_numbers at
every solver timestep by the simulation module. This module adds
diagnostics that operate on a *finished* time series: whether the
asymmetry, once generated, actually survives to the end of the run (i.e.
persists through annihilation rather than being erased by it), and how
close it gets to (not "tuned to match") the observed baryon-to-photon
scale.
"""

from __future__ import annotations

import numpy as np


def asymmetry_persists(eta_series: np.ndarray, tail_fraction: float = 0.1) -> bool:
    """
    True if eta in the final `tail_fraction` of the run stays within 10% of
    its own value at the start of that tail window (i.e. has settled to a
    persistent value rather than still decaying/oscillating toward zero).
    """
    n = len(eta_series)
    if n < 10:
        return False
    tail_start = max(int(n * (1.0 - tail_fraction)), 1)
    tail = eta_series[tail_start:]
    if len(tail) < 2:
        return False
    ref = tail[0]
    if abs(ref) < 1e-12:
        return abs(tail[-1]) < 1e-9
    rel_drift = abs(tail[-1] - ref) / abs(ref)
    return rel_drift < 0.10


def classify_outcome(eta_final: float, N_matter_final: float, N_antimatter_final: float,
                      n_floor: float = 1e-8, N_total_initial: float | None = None,
                      relative_floor: float = 1e-3) -> str:
    """
    Classify the terminal state of a run into one of the outcome categories
    the project is explicitly required to be able to produce:
    'no_asymmetry', 'matter_dominated', 'antimatter_dominated',
    'complete_annihilation', 'persistent_intermediate_asymmetry'.

    "Complete annihilation" is judged relative to the initial visible-sector
    population when `N_total_initial` is supplied (relic abundance from
    freeze-out asymptotically approaches, but mathematically never exactly
    reaches, zero -- this is standard thermal-relic physics, not a modeling
    artifact -- so an absolute floor alone would never trigger for any
    finite annihilation rate). Falls back to the absolute floor if no
    initial population is given.
    """
    total = N_matter_final + N_antimatter_final
    floor = n_floor
    if N_total_initial is not None:
        floor = max(n_floor, relative_floor * N_total_initial)
    if total < floor:
        return "complete_annihilation"
    if abs(eta_final) < 1e-6:
        return "no_asymmetry"
    if eta_final >= 0.999:
        return "matter_dominated"
    if eta_final <= -0.999:
        return "antimatter_dominated"
    return "persistent_intermediate_asymmetry"
