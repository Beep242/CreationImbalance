"""
Visible-sector (ordinary matter / antimatter) bookkeeping.

ESTABLISHED PHYSICS convention: the matter/antimatter asymmetry is defined
as

    eta = (N_matter - N_antimatter) / (N_matter + N_antimatter)

This is a *fractional* asymmetry among baryons themselves (bounded in
[-1, 1]), distinct from the observationally measured baryon-to-photon ratio
eta_B ~ 6e-10 (see cosmology.constants.OBSERVED_BARYON_TO_PHOTON_RATIO),
which compares baryons to photons rather than matter to antimatter. The two
are related but not identical, and this project deliberately tracks the
former because it is the quantity the dark-sector mechanism under test can
plausibly influence directly.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VisibleSectorInit:
    """Initial condition for the matter/antimatter populations at the start
    of the hot early-universe phase (comoving number densities, model
    units)."""

    N_matter0: float
    N_antimatter0: float

    @classmethod
    def symmetric(cls, N0: float, seed_asymmetry: float = 0.0) -> "VisibleSectorInit":
        """
        Construct a near-symmetric initial condition.

        seed_asymmetry: fractional imbalance to inject *by hand* at t=0,
        default 0.0 (exactly symmetric). Per the project's scientific
        requirement, this should remain 0 unless a model explicitly chooses
        to test an externally-imposed initial asymmetry (e.g. as a
        sensitivity check) -- the asymmetry the pipeline reports on should
        otherwise emerge dynamically from the reaction network, not be
        planted here.
        """
        half = N0 / 2.0
        return cls(
            N_matter0=half * (1.0 + seed_asymmetry),
            N_antimatter0=half * (1.0 - seed_asymmetry),
        )


def eta_from_numbers(N_matter: float, N_antimatter: float) -> float:
    """eta = (N_m - N_a) / (N_m + N_a), with a floor to avoid 0/0."""
    total = N_matter + N_antimatter
    if total <= 0.0:
        return 0.0
    return (N_matter - N_antimatter) / total
