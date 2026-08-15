import pytest

from src.reactions.annihilation import AnnihilationParams
from src.reactions.dark_interactions import DarkInteractionParams


def test_annihilation_loss_symmetric_between_matter_and_antimatter():
    ann = AnnihilationParams(sigma_ann=0.1)
    rate = ann.comoving_rate(N_matter=10.0, N_antimatter=4.0, a=1.0)
    assert rate < 0.0
    # Both species lose at exactly the same rate (the ODE system adds this
    # same `rate` to both dN_matter/dt and dN_antimatter/dt).
    assert rate == pytest.approx(-0.1 * 10.0 * 4.0)


def test_annihilation_rate_zero_if_either_species_absent():
    ann = AnnihilationParams(sigma_ann=0.1)
    assert ann.comoving_rate(0.0, 4.0, a=1.0) == pytest.approx(0.0)
    assert ann.comoving_rate(10.0, 0.0, a=1.0) == pytest.approx(0.0)


def test_dark_interaction_R_property():
    params = DarkInteractionParams(sigma_DM_matter=0.08, sigma_DM_antimatter=0.02)
    assert params.R == pytest.approx(4.0)


def test_baryon_number_violation_gate_zeroes_all_number_changing_channels():
    on = DarkInteractionParams(sigma_DM_matter=0.5, sigma_DM_antimatter=0.1,
                                baryon_number_violation_enabled=True)
    off = DarkInteractionParams(sigma_DM_matter=0.5, sigma_DM_antimatter=0.1,
                                 baryon_number_violation_enabled=False)
    assert on.comoving_D_to_M_net(N_D=10.0, N_M=1.0, a=1.0) != 0.0
    assert off.comoving_D_to_M_net(N_D=10.0, N_M=1.0, a=1.0) == 0.0
    assert off.comoving_D_to_A_net(N_D=10.0, N_A=1.0, a=1.0) == 0.0


def test_equilibrium_factor_controls_washout():
    equilibrium = DarkInteractionParams(sigma_DM_matter=0.5, sigma_DM_antimatter=0.5,
                                         equilibrium_factor=1.0)
    departed = DarkInteractionParams(sigma_DM_matter=0.5, sigma_DM_antimatter=0.5,
                                      equilibrium_factor=0.0)
    # Equal forward/reverse rates at N_D == N_M => exact cancellation in equilibrium.
    net_eq = equilibrium.comoving_D_to_M_net(N_D=10.0, N_M=10.0, a=1.0)
    assert net_eq == pytest.approx(0.0)
    net_departed = departed.comoving_D_to_M_net(N_D=10.0, N_M=10.0, a=1.0)
    assert net_departed > 0.0


def test_energy_conservation_helper_matches_number_loss_when_masses_equal():
    dark = DarkInteractionParams(sigma_DM_matter=0.3, m_dark=1.0, m_matter=1.0)
    # When m_dark == m_matter, no energy should be released by the D->M channel.
    assert dark.comoving_energy_release_D_to_M(N_D=10.0, N_M=0.0, a=1.0) == pytest.approx(0.0)
