import pytest

from src.cosmology.expansion import FriedmannExpansion, SimplifiedExpansion


def test_simplified_expansion_power_law():
    model = SimplifiedExpansion(H0=2.0, a0=1.0, power=2.0)
    assert model.hubble_rate(1.0) == pytest.approx(2.0)
    assert model.hubble_rate(2.0) == pytest.approx(2.0 / 4.0)


def test_simplified_expansion_floors_scale_factor():
    model = SimplifiedExpansion(H0=1.0, a0=1.0, power=2.0)
    # Should not raise or divide by zero for a=0.
    assert model.hubble_rate(0.0) > 0


def test_friedmann_expansion_requires_energy_density():
    model = FriedmannExpansion()
    with pytest.raises(ValueError):
        model.hubble_rate(1.0)


def test_friedmann_expansion_scales_with_sqrt_rho():
    model = FriedmannExpansion(M_pl=1.0)
    H1 = model.hubble_rate(1.0, total_energy_density=1.0)
    H4 = model.hubble_rate(1.0, total_energy_density=4.0)
    assert H4 == pytest.approx(2.0 * H1)
