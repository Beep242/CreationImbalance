"""
Cosmic expansion models.

Provides a common `ExpansionModel` interface so that the simplified
power-law expansion used by default can later be swapped for a full
Friedmann-equation cosmology without touching the reaction network in
src/reactions or src/simulation.

ESTABLISHED PHYSICS: the Friedmann equation H^2 = (8 pi G / 3) rho for a
flat, single-fluid-dominated FRW universe, and the radiation-domination
solution H ~ 1/(2t) <=> a ~ t^(1/2).

NUMERICAL APPROXIMATION: `SimplifiedExpansion` (the default used everywhere
in this project unless explicitly stated) prescribes H(a) as a fixed
power law instead of deriving it self-consistently from the evolving
energy content. This is faster, numerically gentler, and keeps the
transition module decoupled from the reaction network, but it means the
expansion rate does NOT respond to energy injected or removed by
annihilation, dark-sector decay, etc. This is a real limitation, documented
in docs/physics_limitations.md, and is exactly why `FriedmannExpansion` is
provided as a structurally interchangeable alternative.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .constants import M_PL_MODEL_UNITS


class ExpansionModel(ABC):
    """Common interface: given model state, return H = (da/dt)/a."""

    @abstractmethod
    def hubble_rate(self, a: float, total_energy_density: float | None = None) -> float:
        """Return the Hubble expansion rate at scale factor `a`."""
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> str:
        """Human-readable description of the model and its assumptions."""
        raise NotImplementedError


@dataclass
class SimplifiedExpansion(ExpansionModel):
    """
    H(a) = H0 * (a0 / a) ** power

    power = 2.0 reproduces radiation-domination scaling (H ~ a^-2, i.e.
    a ~ t^1/2) which is the standard leading-order behavior of the early,
    radiation-dominated universe. This is NOT derived from the simulated
    energy content -- it is an externally imposed kinematic history.
    """

    H0: float = 1.0
    a0: float = 1.0
    power: float = 2.0

    def hubble_rate(self, a: float, total_energy_density: float | None = None) -> float:
        a = max(a, 1e-12)
        return self.H0 * (self.a0 / a) ** self.power

    def describe(self) -> str:
        return (
            f"SimplifiedExpansion(power-law): H(a) = {self.H0:.4g} * "
            f"({self.a0:.4g}/a)^{self.power:.3g}. Imposed kinematically; "
            f"does not respond to the simulated energy budget. "
            f"NUMERICAL APPROXIMATION."
        )


@dataclass
class FriedmannExpansion(ExpansionModel):
    """
    H(a) = sqrt(8 * pi * rho_total / (3 * M_PL^2))

    Self-consistently derived from the total energy density actually being
    tracked by the ODE system (matter + antimatter + dark sector +
    radiation), in flat-FRW form. This is structurally what a "real"
    cosmological treatment would use; it is offered as a drop-in
    alternative to SimplifiedExpansion via the same ExpansionModel
    interface. It is still approximate because it ignores curvature,
    anisotropy, and any dark-energy component, and because M_PL is
    expressed in the model's internal unit system rather than fit to
    physical GeV units (see docs/physics_limitations.md).
    """

    M_pl: float = M_PL_MODEL_UNITS

    def hubble_rate(self, a: float, total_energy_density: float | None = None) -> float:
        if total_energy_density is None:
            raise ValueError(
                "FriedmannExpansion requires total_energy_density to evaluate H(a)."
            )
        rho = max(total_energy_density, 0.0)
        return ((8.0 * 3.14159265358979323846 * rho) / (3.0 * self.M_pl**2)) ** 0.5

    def describe(self) -> str:
        return (
            f"FriedmannExpansion: H^2 = 8*pi*rho_total/(3 M_pl^2), "
            f"M_pl={self.M_pl:.4g} (model units). Self-consistent with "
            f"tracked energy density; flat FRW, single-sector, no curvature "
            f"or dark energy term."
        )
