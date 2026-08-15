import pytest

from src.dark_sector.dark_sector import DarkSectorMode, PreBigBangState
from src.transition.transition import TransitionConfig, TransitionType, run_transition


def test_visible_sector_always_symmetric_out_of_transition():
    """Scientific requirement: the transition must never inject a seed
    matter/antimatter asymmetry by fiat, regardless of how lopsided the
    dark-sector coupling parameters are configured."""
    pre = PreBigBangState(density_pre=100.0)
    cfg = TransitionConfig(
        coupling_to_matter=0.9, coupling_to_antimatter=0.001,  # wildly asymmetric
        visible_sector_seed_number=200.0,
    )
    hot = run_transition(pre, cfg)
    assert hot.N_matter0 == pytest.approx(hot.N_antimatter0)
    assert hot.N_matter0 == pytest.approx(100.0)


def test_survival_fraction_scales_dark_sector_linearly():
    pre = PreBigBangState(density_pre=100.0)
    for f in (0.0, 0.25, 0.5, 1.0):
        cfg = TransitionConfig(dark_sector_survival_fraction=f)
        hot = run_transition(pre, cfg)
        assert hot.N_dark0 == pytest.approx(100.0 * f)


def test_survival_fraction_is_clamped_to_valid_range():
    pre = PreBigBangState(density_pre=100.0)
    cfg = TransitionConfig(dark_sector_survival_fraction=5.0)  # out of [0,1]
    hot = run_transition(pre, cfg)
    assert hot.N_dark0 == pytest.approx(100.0)

    cfg_neg = TransitionConfig(dark_sector_survival_fraction=-1.0)
    hot_neg = run_transition(pre, cfg_neg)
    assert hot_neg.N_dark0 == pytest.approx(0.0)


def test_non_particle_population_mode_not_yet_wired_into_transition():
    pre = PreBigBangState(mode=DarkSectorMode.FIELD_BACKGROUND, density_pre=10.0)
    with pytest.raises(ValueError):
        run_transition(pre, TransitionConfig())


def test_transition_provenance_records_choices():
    pre = PreBigBangState(density_pre=50.0)
    cfg = TransitionConfig(transition_type=TransitionType.BOUNCE,
                            dark_sector_survival_fraction=0.7)
    hot = run_transition(pre, cfg)
    assert hot.provenance["transition_type"] == "bounce"
    assert hot.provenance["dark_sector_survival_fraction"] == pytest.approx(0.7)
    assert hot.provenance["visible_sector_seeded_symmetric"] is True
