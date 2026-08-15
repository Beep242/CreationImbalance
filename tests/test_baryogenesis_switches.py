"""
End-to-end tests of the Sakharov-condition switches, run through the full
Model B pipeline. These are the tests that matter most scientifically: they
confirm that merely having sigma_DM_matter != sigma_DM_antimatter is NOT
sufficient by itself to produce an asymmetry unless baryon-number violation
and CP violation are both switched on and the system is out of equilibrium.
"""

import pytest

from src.simulation.model_a import build_model_a
from src.simulation.model_b import build_model_b
from src.simulation.runner import run_simulation

UNEQUAL_COUPLING = dict(coupling_to_matter=0.08, coupling_to_antimatter=0.02)  # R = 4


def _final_eta(cfg):
    res = run_simulation(cfg)
    assert res.success
    return float(res.df["eta"].iloc[-1])


def test_model_a_baseline_produces_no_asymmetry():
    """The standard-cosmology control has no B-violating channel at all and
    must never generate an asymmetry from a symmetric start."""
    cfg = build_model_a()
    assert _final_eta(cfg) == pytest.approx(0.0, abs=1e-9)


def test_equal_coupling_alone_is_not_sufficient():
    """R = 1: dark sector couples to both matter and antimatter, but
    identically -- must not produce an asymmetry."""
    cfg = build_model_b(coupling_to_matter=0.05, coupling_to_antimatter=0.05)
    assert _final_eta(cfg) == pytest.approx(0.0, abs=1e-9)


def test_zero_coupling_control_is_not_sufficient():
    """Pre-existing dark sector with NO coupling to the visible sector must
    not produce an asymmetry -- merely having pre-Big-Bang dark matter is
    not enough."""
    cfg = build_model_b(coupling_to_matter=0.0, coupling_to_antimatter=0.0)
    assert _final_eta(cfg) == pytest.approx(0.0, abs=1e-9)


def test_unequal_coupling_with_all_conditions_on_produces_asymmetry():
    cfg = build_model_b(**UNEQUAL_COUPLING)
    eta = _final_eta(cfg)
    assert abs(eta) > 1e-3


def test_asymmetry_sign_tracks_which_channel_is_stronger():
    cfg_pos = build_model_b(coupling_to_matter=0.08, coupling_to_antimatter=0.02)  # R>1
    cfg_neg = build_model_b(coupling_to_matter=0.02, coupling_to_antimatter=0.08)  # R<1
    assert _final_eta(cfg_pos) > 0
    assert _final_eta(cfg_neg) < 0
    assert _final_eta(cfg_pos) == pytest.approx(-_final_eta(cfg_neg), rel=1e-6)


def test_baryon_number_violation_off_forces_zero_asymmetry():
    cfg = build_model_b(**UNEQUAL_COUPLING, baryon_number_violation_enabled=False)
    assert _final_eta(cfg) == pytest.approx(0.0, abs=1e-9)


def test_cp_violation_off_forces_R_to_one():
    """With CP conservation enforced, the effective rates must be
    symmetrized regardless of the configured (asymmetric) input rates."""
    cfg = build_model_b(**UNEQUAL_COUPLING, cp_violation_enabled=False)
    assert cfg.physics.dark_params.R == pytest.approx(1.0)
    assert _final_eta(cfg) == pytest.approx(0.0, abs=1e-9)


def test_thermal_equilibrium_suppresses_relative_to_departure():
    cfg_eq = build_model_b(**UNEQUAL_COUPLING, thermal_equilibrium=True)
    cfg_non_eq = build_model_b(**UNEQUAL_COUPLING, thermal_equilibrium=False)
    eta_eq = abs(_final_eta(cfg_eq))
    eta_non_eq = abs(_final_eta(cfg_non_eq))
    assert eta_eq < eta_non_eq


def test_all_three_conditions_required_simultaneously():
    """Removing any one of the three Sakharov conditions while holding the
    others fixed should reduce |eta| relative to having all three on."""
    baseline = abs(_final_eta(build_model_b(**UNEQUAL_COUPLING)))
    no_bviol = abs(_final_eta(build_model_b(**UNEQUAL_COUPLING,
                                             baryon_number_violation_enabled=False)))
    no_cp = abs(_final_eta(build_model_b(**UNEQUAL_COUPLING, cp_violation_enabled=False)))
    in_equilibrium = abs(_final_eta(build_model_b(**UNEQUAL_COUPLING, thermal_equilibrium=True)))

    assert no_bviol < baseline
    assert no_cp < baseline
    assert in_equilibrium < baseline
