import numpy as np
import pytest

from src.baryogenesis.asymmetry import asymmetry_persists, classify_outcome
from src.visible_sector.particles import VisibleSectorInit, eta_from_numbers


def test_eta_symmetric_is_zero():
    assert eta_from_numbers(50.0, 50.0) == pytest.approx(0.0)


def test_eta_matter_dominated():
    assert eta_from_numbers(100.0, 0.0) == pytest.approx(1.0)


def test_eta_antimatter_dominated():
    assert eta_from_numbers(0.0, 100.0) == pytest.approx(-1.0)


def test_eta_zero_total_floor():
    assert eta_from_numbers(0.0, 0.0) == 0.0


def test_visible_sector_symmetric_default_has_no_seed():
    init = VisibleSectorInit.symmetric(N0=100.0)
    assert init.N_matter0 == pytest.approx(init.N_antimatter0)
    assert init.N_matter0 == pytest.approx(50.0)


def test_visible_sector_symmetric_with_explicit_seed():
    init = VisibleSectorInit.symmetric(N0=100.0, seed_asymmetry=0.1)
    assert init.N_matter0 > init.N_antimatter0


def test_classify_outcome_no_asymmetry():
    assert classify_outcome(0.0, 50.0, 50.0) == "no_asymmetry"


def test_classify_outcome_matter_dominated():
    assert classify_outcome(0.999, 100.0, 0.0001) == "matter_dominated"


def test_classify_outcome_antimatter_dominated():
    assert classify_outcome(-0.999, 0.0001, 100.0) == "antimatter_dominated"


def test_classify_outcome_persistent_intermediate():
    assert classify_outcome(0.4, 70.0, 30.0) == "persistent_intermediate_asymmetry"


def test_classify_outcome_complete_annihilation_absolute_floor():
    assert classify_outcome(0.0, 1e-10, 1e-10) == "complete_annihilation"


def test_classify_outcome_complete_annihilation_relative_floor():
    # Absolute values (0.02) would look "fine" without the relative floor,
    # but relative to a large initial population it is a near-total wipeout.
    assert classify_outcome(0.0, 0.01, 0.01, N_total_initial=100.0) == "complete_annihilation"
    assert classify_outcome(0.0, 0.01, 0.01, N_total_initial=0.001) != "complete_annihilation"


def test_asymmetry_persists_detects_settled_series():
    settled = np.concatenate([np.linspace(0, 0.3, 50), np.full(50, 0.3)])
    assert asymmetry_persists(settled) == True  # noqa: E712 (numpy bool)


def test_asymmetry_persists_detects_still_decaying_series():
    decaying = np.linspace(0.5, 0.0, 100)
    assert asymmetry_persists(decaying) == False  # noqa: E712 (numpy bool)
