"""
Dark-sector <-> visible-sector interaction channels.

This module implements the mechanical rate equations for a toy reaction
network:

    D -> M      (rate sigma_DM_matter * n_D)        [baryon-number +1]
    M -> D      (rate eq_factor * sigma_DM_matter * n_M)   [reverse/washout]
    D -> A      (rate sigma_DM_antimatter * n_D)     [baryon-number -1]
    A -> D      (rate eq_factor * sigma_DM_antimatter * n_A)  [reverse/washout]
    D + D -> radiation   (rate sigma_DD * n_D^2, optional dark self-annihilation)
    D -> radiation (elastic/heating only, rate coupling_to_visible * n_D,
                    does NOT change any particle number -- represents a
                    number-conserving energy exchange with the visible
                    sector, e.g. dark-sector quanta scattering off the
                    thermal bath and depositing kinetic energy)

SPECULATIVE ASSUMPTION: none of these channels correspond to a specific,
UV-complete particle-physics model. D is a stand-in "dark-sector quantum"
that is here assigned baryon number 0, while M (matter) and A (antimatter)
are assigned baryon number +1 and -1 respectively. D -> M and D -> A are
therefore, by construction, baryon-number-violating processes (Sakharov
condition 1) -- this is the ONLY baryon-number-violating channel in the
model, and it is exactly the channel the `baryon_number_violation_enabled`
switch in baryogenesis.sakharov turns off.

Whether sigma_DM_matter can differ from sigma_DM_antimatter is a
C/CP-violation question (Sakharov condition 2), gated separately in
baryogenesis.sakharov -- this module does not decide that; it simply
computes rates from whatever effective parameters it is given.

Whether the reverse (washout) reactions run at full strength (eq_factor=1,
true thermal equilibrium) or are suppressed (eq_factor -> 0, departure from
equilibrium / freeze-out) is Sakharov condition 3, again decided upstream
and passed in as `equilibrium_factor`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DarkInteractionParams:
    sigma_DM_matter: float = 1.0
    sigma_DM_antimatter: float = 1.0
    equilibrium_factor: float = 0.0  # 0 = full departure from equilibrium, 1 = full washout
    coupling_to_visible: float = 0.0  # elastic/number-conserving heating strength
    sigma_DD: float = 0.0  # dark-sector self-annihilation
    m_dark: float = 1.0
    m_matter: float = 1.0
    m_antimatter: float = 1.0
    baryon_number_violation_enabled: bool = True

    @property
    def R(self) -> float:
        """R = sigma_DM_matter / sigma_DM_antimatter."""
        if self.sigma_DM_antimatter == 0.0:
            return float("inf") if self.sigma_DM_matter != 0.0 else float("nan")
        return self.sigma_DM_matter / self.sigma_DM_antimatter

    def _bviol_gate(self) -> float:
        return 1.0 if self.baryon_number_violation_enabled else 0.0

    def comoving_D_to_M_net(self, N_D: float, N_M: float, a: float) -> float:
        """Net comoving d N_M/dt contribution from D<->M (forward - reverse)."""
        gate = self._bviol_gate()
        N_D = max(N_D, 0.0)
        N_M = max(N_M, 0.0)
        forward = self.sigma_DM_matter * N_D
        reverse = self.equilibrium_factor * self.sigma_DM_matter * N_M
        return gate * (forward - reverse)

    def comoving_D_to_A_net(self, N_D: float, N_A: float, a: float) -> float:
        """Net comoving d N_A/dt contribution from D<->A (forward - reverse)."""
        gate = self._bviol_gate()
        N_D = max(N_D, 0.0)
        N_A = max(N_A, 0.0)
        forward = self.sigma_DM_antimatter * N_D
        reverse = self.equilibrium_factor * self.sigma_DM_antimatter * N_A
        return gate * (forward - reverse)

    def comoving_dark_self_annihilation(self, N_D: float, a: float) -> float:
        """d N_D/dt |_self-ann = -sigma_DD * n_D^2 * a^3 = -sigma_DD * N_D^2 / a^3."""
        a = max(a, 1e-12)
        N_D = max(N_D, 0.0)
        return -self.sigma_DD * N_D * N_D / (a**3)

    def comoving_elastic_heating_rate(self, N_D: float, a: float) -> float:
        """
        Number-conserving energy transfer rate from D into radiation,
        expressed as comoving energy per unit time:
            a^4 * coupling_to_visible * n_D * m_dark
          = coupling_to_visible * m_dark * N_D * a
        """
        a = max(a, 1e-12)
        N_D = max(N_D, 0.0)
        return self.coupling_to_visible * self.m_dark * N_D * a

    def comoving_energy_release_D_to_M(self, N_D: float, N_M: float, a: float) -> float:
        """Comoving radiation-energy source from the D<->M channel:
        (m_dark - m_matter) per net forward event, in comoving-energy units
        (multiplied by an extra factor of a, matching comoving E_rad = rho*a^4
        vs comoving N = n*a^3 bookkeeping)."""
        net = self.comoving_D_to_M_net(N_D, N_M, a)
        return net * (self.m_dark - self.m_matter) * a

    def comoving_energy_release_D_to_A(self, N_D: float, N_A: float, a: float) -> float:
        net = self.comoving_D_to_A_net(N_D, N_A, a)
        return net * (self.m_dark - self.m_antimatter) * a

    def comoving_energy_release_self_annihilation(self, N_D: float, a: float) -> float:
        """
        NOTE: `comoving_dark_self_annihilation` already returns the *total*
        comoving D-number loss rate (the n_D^2 rate law is conventionally
        the full depletion rate for a self-annihilating species, matching
        how `AnnihilationParams.comoving_rate` already gives the full loss
        for both matter and antimatter). So the mass-energy released here
        is m_dark * |loss|, not 2 * m_dark * |loss| -- do not double count.
        """
        loss = self.comoving_dark_self_annihilation(N_D, a)  # negative
        return -loss * self.m_dark * a
