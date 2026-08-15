"""
Sakharov-condition switches.

ESTABLISHED PHYSICS: Sakharov (1967) showed that generating a baryon
asymmetry from a symmetric initial state requires ALL THREE of:

  1. Baryon-number violation.
  2. C and CP violation.
  3. Departure from thermal equilibrium (or, in some scenarios, from CPT
     invariance).

This module turns those three conditions into explicit, independently
togglable switches that gate the raw reaction rates computed in
src/reactions/dark_interactions.py, and it is the one place in the
codebase where "does merely having a different rate constant produce
baryogenesis" is interrogated directly (it should NOT, if condition 1 or 3
is disabled -- see tests/test_baryogenesis_switches.py).

SPECULATIVE ASSUMPTION: the specific channel that violates baryon number
here (D -> M / D -> A, see dark_interactions.py) is a toy stand-in. Nothing
in this module claims it corresponds to a specific UV completion (it is
structurally similar in spirit to out-of-equilibrium decay baryogenesis,
e.g. GUT baryogenesis or leptogenesis via heavy neutrino decay, but is not
a fit to any specific such model).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..reactions.dark_interactions import DarkInteractionParams


@dataclass
class SakharovSwitches:
    baryon_number_violation_enabled: bool = True
    cp_violation_enabled: bool = True
    thermal_equilibrium: bool = False  # False = departure from equilibrium (freeze-out)

    def all_satisfied(self) -> bool:
        return (
            self.baryon_number_violation_enabled
            and self.cp_violation_enabled
            and not self.thermal_equilibrium
        )

    def summary(self) -> str:
        return (
            f"B-violation={'ON' if self.baryon_number_violation_enabled else 'off'}, "
            f"C/CP-violation={'ON' if self.cp_violation_enabled else 'off'}, "
            f"departure-from-equilibrium="
            f"{'ON' if not self.thermal_equilibrium else 'off (in equilibrium)'} "
            f"=> Sakharov conditions fully satisfied: {self.all_satisfied()}"
        )


def build_effective_dark_interaction_params(
    sigma_DM_matter: float,
    sigma_DM_antimatter: float,
    switches: SakharovSwitches,
    coupling_to_visible: float = 0.0,
    sigma_DD: float = 0.0,
    m_dark: float = 1.0,
    m_matter: float = 1.0,
    m_antimatter: float = 1.0,
) -> DarkInteractionParams:
    """
    Apply the Sakharov switches to raw configured rate constants and return
    the *effective* DarkInteractionParams actually fed to the ODE system.

    - If cp_violation_enabled is False: C/CP conservation forces the two
      rates to be equal by symmetry, regardless of the configured R. We
      enforce this by symmetrizing: both channels get the geometric mean of
      the two configured rates, so R_eff = 1 exactly.
    - If baryon_number_violation_enabled is False: the D<->M and D<->A
      channels are disabled entirely downstream (DarkInteractionParams
      itself carries this flag and gates on it), independent of what rate
      constants are configured.
    - equilibrium_factor is 1.0 if thermal_equilibrium is True (full
      washout: forward and reverse reactions balance, suppressing any net
      asymmetry) and 0.0 otherwise (complete departure from equilibrium:
      reverse/washout reactions are frozen out).
    """
    if switches.cp_violation_enabled:
        eff_matter, eff_antimatter = sigma_DM_matter, sigma_DM_antimatter
    else:
        symmetric_rate = (max(sigma_DM_matter, 0.0) * max(sigma_DM_antimatter, 0.0)) ** 0.5
        eff_matter, eff_antimatter = symmetric_rate, symmetric_rate

    equilibrium_factor = 1.0 if switches.thermal_equilibrium else 0.0

    return DarkInteractionParams(
        sigma_DM_matter=eff_matter,
        sigma_DM_antimatter=eff_antimatter,
        equilibrium_factor=equilibrium_factor,
        coupling_to_visible=coupling_to_visible,
        sigma_DD=sigma_DD,
        m_dark=m_dark,
        m_matter=m_matter,
        m_antimatter=m_antimatter,
        baryon_number_violation_enabled=switches.baryon_number_violation_enabled,
    )
