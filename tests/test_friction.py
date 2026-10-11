import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from friction import (reynolds_number, flow_regime, laminar_friction_factor,
                      turbulent_friction_factor, friction_factor)

D = 0.0254  # pipe diameter, m
EPS = 0.0000254  # pipe roughness, m (eps/D = 0.001)


def test_reynolds_number():
    # water at about 20 C, 1 m/s in the 25.4 mm lab pipe
    assert reynolds_number(998, 1.0, 0.0254, 0.001) == pytest.approx(25349.2, rel=1e-4)


def test_flow_regime():
    assert flow_regime(1000) == "laminar"
    assert flow_regime(2300) == "transitional"  # lower boundary
    assert flow_regime(4000) == "transitional"  # upper boundary
    assert flow_regime(4001) == "turbulent"


def test_laminar():
    assert laminar_friction_factor(1000) == pytest.approx(0.064)


def test_turbulent_values():
    assert turbulent_friction_factor(100000, D, EPS) == pytest.approx(0.0223, rel=0.01)


def test_friction_factor_is_continuous():
    # no sudden jumps at the regime boundaries
    assert friction_factor(2299, D, EPS) == pytest.approx(friction_factor(2300, D, EPS), rel=0.01)
    assert friction_factor(3999, D, EPS) == pytest.approx(friction_factor(4001, D, EPS), rel=0.01)


def test_bad_inputs_raise():
    with pytest.raises(ValueError):
        laminar_friction_factor(0)
    with pytest.raises(ValueError):
        laminar_friction_factor(5000)
    with pytest.raises(ValueError):
        turbulent_friction_factor(3000, D, EPS)
    with pytest.raises(ValueError):
        turbulent_friction_factor(100000, 0, EPS)
    with pytest.raises(ValueError):
        friction_factor(100000, D, -1)


def test_transitional_warning():
    with pytest.warns(UserWarning):
        friction_factor(3000, D, EPS)
