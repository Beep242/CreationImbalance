import pytest

from src.dark_sector.dark_sector import (
    DarkSectorMode,
    PreBigBangState,
    field_background_density,
    generic_energy_density,
)


def test_pre_big_bang_state_defaults_to_particle_population():
    state = PreBigBangState()
    assert state.mode == DarkSectorMode.PARTICLE_POPULATION


def test_pre_big_bang_state_carries_no_visible_sector_attributes():
    state = PreBigBangState(density_pre=42.0)
    # By construction, PreBigBangState has no matter/antimatter fields.
    assert not hasattr(state, "N_matter")
    assert not hasattr(state, "N_antimatter")
    assert not hasattr(state, "scale_factor")


def test_field_background_dilutes_correctly_for_radiation_like_w():
    # w = 1/3 (radiation-like): rho ~ a^-4
    rho = field_background_density(rho0=1.0, a=2.0, a0=1.0, w=1.0 / 3.0)
    assert rho == pytest.approx(2.0 ** -4.0)


def test_field_background_constant_for_dark_energy_like_w():
    # w = -1 (cosmological-constant-like): rho stays constant with a.
    rho = field_background_density(rho0=5.0, a=10.0, a0=1.0, w=-1.0)
    assert rho == pytest.approx(5.0)


def test_generic_energy_density_dilution_exponent():
    rho = generic_energy_density(rho0=3.0, a=2.0, a0=1.0, dilution_exponent=3.0)
    assert rho == pytest.approx(3.0 / 8.0)
