import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from pipe import *

RHO = 998  # water density, kg/m3
MU = 0.001  # water viscosity, Pa.s
D = 0.0254  # pipe diameter, m
L = 10  # pipe length, m
EPS = 0.0000015  # drawn tubing roughness, m


def test_velocity_from_flow():
    assert velocity_from_flow(0.0005067, D) == pytest.approx(1.0, rel=0.01)
    assert velocity_from_flow(0, D) == 0


def test_head_loss_straight():
    # f = 0.0245 is the turbulent friction factor at Re = 25349
    assert head_loss_straight(1.0, D, L, 0.0245) == pytest.approx(0.49, rel=0.02)


def test_pressure_drop_turbulent():
    assert pressure_drop_straight(RHO, MU, 1.0, D, L, EPS) == pytest.approx(4800, rel=0.02)


def test_pressure_drop_laminar():
    # Hagen-Poiseuille: 32 * mu * L * v / D^2 = about 5 Pa
    assert pressure_drop_straight(RHO, MU, 0.01, D, L, EPS) == pytest.approx(5, rel=0.02)


def test_zero_velocity_gives_zero():
    assert pressure_drop_straight(RHO, MU, 0, D, L, EPS) == 0


def test_longer_pipe_doubles_pressure_drop():
    dp10 = pressure_drop_straight(RHO, MU, 1.0, D, 10, EPS)
    dp20 = pressure_drop_straight(RHO, MU, 1.0, D, 20, EPS)
    assert dp20 == pytest.approx(2 * dp10)


def test_bad_inputs_raise():
    with pytest.raises(ValueError):
        velocity_from_flow(0.001, 0)
    with pytest.raises(ValueError):
        head_loss_straight(1.0, D, -5, 0.0245)
    with pytest.raises(ValueError):
        pressure_drop_straight(RHO, 0, 1.0, D, L, EPS)
    with pytest.raises(ValueError):
        pressure_drop_straight(RHO, MU, -1.0, D, L, EPS)


FITTINGS = {"elbow_90": 4, "globe_valve": 1, "entrance": 1, "exit": 1}


def test_total_k():
    # 4 * 0.75 + 6.0 + 0.5 + 1.0
    assert total_k(FITTINGS) == pytest.approx(10.5)
    assert total_k({}) == 0
    assert total_k({"elbow_90": 2}) == pytest.approx(2 * total_k({"elbow_90": 1}))


def test_fittings_losses():
    assert pressure_drop_fittings(RHO, 1.0, 1.0) == pytest.approx(499, rel=0.01)
    assert head_loss_fittings(1.0, 1.0) == pytest.approx(0.051, rel=0.02)


def test_fittings_drop_scales_with_velocity_squared():
    dp1 = pressure_drop_fittings(RHO, 1.0, 10.5)
    dp2 = pressure_drop_fittings(RHO, 2.0, 10.5)
    assert dp2 == pytest.approx(4 * dp1)


def test_total_pressure_drop():
    # straight pipe (about 4,800 Pa) plus fittings (about 5,240 Pa)
    assert total_pressure_drop(RHO, MU, 1.0, D, L, EPS, FITTINGS) == pytest.approx(10050, rel=0.02)
    # no fittings means just the straight pipe
    assert total_pressure_drop(RHO, MU, 1.0, D, L, EPS, {}) == pytest.approx(
        pressure_drop_straight(RHO, MU, 1.0, D, L, EPS))


def test_fitting_errors():
    with pytest.raises(ValueError):
        total_k({"banana_valve": 1})
    with pytest.raises(ValueError):
        total_k({"elbow_90": -1})
    with pytest.raises(ValueError):
        pressure_drop_fittings(RHO, -1.0, 1.0)
