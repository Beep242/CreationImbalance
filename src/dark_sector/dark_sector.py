"""
Dark-sector representations.

SPECULATIVE ASSUMPTION: everything in this module describes a hypothetical
pre-Big-Bang dark-sector degree of freedom. None of these representations
are claims about what dark matter "actually is" -- they are alternative
modeling choices offered so the rest of the pipeline is not locked into one
picture of the dark sector. See docs/pre_big_bang_assumptions.md.

Three conceptual modes are supported, selected via `DarkSectorMode`:

1. PARTICLE_POPULATION
   The dark sector is a population of discrete quanta with a number
   density n_D that can be produced, destroyed, and diluted by expansion.
   This is the mode used by the full reaction network in src/reactions and
   src/simulation, because Sakharov-condition bookkeeping (baryon-number
   violation as a counting statement) is most naturally expressed in terms
   of discrete quanta converting into matter/antimatter quanta.

2. FIELD_BACKGROUND
   The dark sector is a homogeneous background field-like energy density
   rho_D with an equation-of-state parameter w_D, diluting as
   rho_D ~ a^{-3(1+w_D)}. No discrete "particle number" is defined.

3. GENERIC_ENERGY_DENSITY
   The dark sector is reduced to a single bookkeeping energy density with a
   configurable dilution exponent, with no assumed microphysics at all.
   This is the most agnostic option.

Modes 2 and 3 are provided for completeness and are exercised directly in
tests/test_dark_sector_modes.py; the twelve headline experiments in
src/simulation/run_experiments.py use mode 1 because it is the only mode
detailed enough to host a baryon-number-violating interaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DarkSectorMode(Enum):
    PARTICLE_POPULATION = "particle_population"
    FIELD_BACKGROUND = "field_background"
    GENERIC_ENERGY_DENSITY = "generic_energy_density"


@dataclass
class PreBigBangState:
    """
    The hypothetical state of the dark sector *before* the Big-Bang
    transition.

    SPECULATIVE ASSUMPTION: by construction this object carries NO
    ordinary-matter, antimatter, or conventional-spacetime attributes.
    There is deliberately no scale factor, no temperature-of-radiation, and
    no matter/antimatter population here -- only a dark-sector quantity and
    (optionally) a dark-sector-internal temperature, which need not have
    any relation to a thermodynamic temperature in the usual sense.

    Attributes
    ----------
    mode:
        Which conceptual representation of the dark sector is in use.
    density_pre:
        Pre-transition dark-sector density in model units. For
        PARTICLE_POPULATION this is a number density n_D; for the other two
        modes it is an energy density rho_D.
    temperature_pre:
        Optional dark-sector-internal temperature (model units). Not
        required to exist -- some pre-Big-Bang pictures (e.g. a cold
        pre-bounce condensate) have no meaningful temperature. Leave as
        None to represent "not applicable."
    equation_of_state:
        Only used by FIELD_BACKGROUND. w_D such that rho_D ~ a^{-3(1+w_D)}
        post-transition, before any coupling to the visible sector.
    label:
        Free-text tag identifying which conceptual transition
        interpretation this pre-BB state is meant to feed into (e.g.
        "bounce", "vacuum_transition"). Purely descriptive.
    """

    mode: DarkSectorMode = DarkSectorMode.PARTICLE_POPULATION
    density_pre: float = 1.0
    temperature_pre: float | None = None
    equation_of_state: float = 0.0
    label: str = "unspecified"
    metadata: dict = field(default_factory=dict)

    def describe(self) -> str:
        temp_str = "n/a" if self.temperature_pre is None else f"{self.temperature_pre:.4g}"
        return (
            f"PreBigBangState[{self.label}] mode={self.mode.value} "
            f"density_pre={self.density_pre:.4g} temperature_pre={temp_str} "
            f"w={self.equation_of_state:.3g} "
            f"(SPECULATIVE: no ordinary matter/antimatter/spacetime assumed "
            f"to exist at this stage)"
        )


def field_background_density(rho0: float, a: float, a0: float, w: float) -> float:
    """rho_D(a) = rho0 * (a0/a)^(3(1+w)) for FIELD_BACKGROUND mode."""
    a = max(a, 1e-12)
    return rho0 * (a0 / a) ** (3.0 * (1.0 + w))


def generic_energy_density(rho0: float, a: float, a0: float, dilution_exponent: float) -> float:
    """rho_DS(a) = rho0 * (a0/a)^dilution_exponent for GENERIC_ENERGY_DENSITY mode."""
    a = max(a, 1e-12)
    return rho0 * (a0 / a) ** dilution_exponent
