"""
Matter-antimatter annihilation: M + Abar -> radiation.

ESTABLISHED PHYSICS (functional form): a two-body annihilation process has
a rate per unit volume proportional to the product of the two numbers
densities and a thermally-averaged cross-section <sigma v>:

    d n_M/dt |_ann = -sigma_ann * n_M * n_A
    d n_A/dt |_ann = -sigma_ann * n_M * n_A

with each annihilation event depositing the rest-mass-equivalent energy of
one matter + one antimatter quantum into radiation. sigma_ann itself
(magnitude, temperature dependence) is a NUMERICAL APPROXIMATION -- held
constant rather than computed from an underlying particle-physics matrix
element.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AnnihilationParams:
    sigma_ann: float = 1.0
    m_matter: float = 1.0
    m_antimatter: float = 1.0

    def comoving_rate(self, N_matter: float, N_antimatter: float, a: float) -> float:
        """
        Comoving-number-density annihilation rate: d N_matter/dt |_ann (and
        equally for N_antimatter), where N = n * a^3.

        In comoving variables: -sigma_ann * n_M * n_A * a^3
                              = -sigma_ann * N_M * N_A / a^3
        """
        a = max(a, 1e-12)
        N_matter = max(N_matter, 0.0)
        N_antimatter = max(N_antimatter, 0.0)
        return -self.sigma_ann * N_matter * N_antimatter / (a**3)

    def comoving_energy_release_rate(
        self, N_matter: float, N_antimatter: float, a: float
    ) -> float:
        """
        Rate of (m_M + m_A)-worth of comoving energy deposited into
        radiation per unit time.

        The extra factor of `a` converts a comoving *number* source
        (N ~ n a^3) into a comoving *radiation energy* source
        (E_rad ~ rho a^4): physical energy source = mass * physical rate,
        comoving energy source = a^4 * physical_rate * mass
        = a * (a^3 * physical_rate) * mass = a * (comoving number rate) * mass.
        See src/analysis/conservation_checks.py for the derivation and the
        self-consistency test this guarantees.
        """
        loss = self.comoving_rate(N_matter, N_antimatter, a)  # negative
        return -loss * (self.m_matter + self.m_antimatter) * a
