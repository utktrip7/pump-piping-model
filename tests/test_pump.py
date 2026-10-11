import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from pump import fit_pump_curve, pump_head, system_head, operating_point

RHO = 998
MU = 0.001
D = 0.0254
L = 10
EPS = 0.0000015
STATIC = 5
FITTINGS = {"elbow_90": 4, "globe_valve": 1, "entrance": 1, "exit": 1}

FLOWS = [0, 0.0005, 0.001, 0.0015, 0.002]
HEADS = [20, 19, 16, 11, 4]   # exactly H = 20 - 4,000,000 * Q^2
COEFFS = fit_pump_curve(FLOWS, HEADS)


def test_fit_pump_curve():
    a, b, c = COEFFS
    assert a == pytest.approx(20, rel=1e-3)
    assert b == pytest.approx(0, abs=1e-3)
    assert c == pytest.approx(-4_000_000, rel=1e-3)


def test_pump_head():
    assert pump_head(0, COEFFS) == pytest.approx(20, rel=1e-3)
    assert pump_head(0.001, COEFFS) == pytest.approx(16, rel=1e-3)
    assert pump_head(0.002, COEFFS) == pytest.approx(4, rel=1e-3)


def test_system_head_at_zero_flow_is_static_head():
    assert system_head(0, STATIC, RHO, MU, D, L, EPS, FITTINGS) == pytest.approx(STATIC)


def test_system_head_value():
    assert system_head(0.0014, STATIC, RHO, MU, D, L, EPS, FITTINGS) == pytest.approx(12.1, rel=0.03)


def test_system_curve_rises_with_flow():
    qs = [0, 0.0005, 0.001, 0.0015, 0.002]
    heads = [system_head(q, STATIC, RHO, MU, D, L, EPS, FITTINGS) for q in qs]
    assert heads == sorted(heads)


def test_operating_point_values():
    q, h = operating_point(COEFFS, STATIC, RHO, MU, D, L, EPS, FITTINGS, 0.002)
    assert q == pytest.approx(0.0014, rel=0.03)
    assert h == pytest.approx(12.1, rel=0.03)


def test_curves_meet_at_operating_point():
    q, h = operating_point(COEFFS, STATIC, RHO, MU, D, L, EPS, FITTINGS, 0.002)
    assert pump_head(q, COEFFS) == pytest.approx(
        system_head(q, STATIC, RHO, MU, D, L, EPS, FITTINGS), rel=1e-6)


def test_higher_static_head_lowers_flow():
    q_low, _ = operating_point(COEFFS, 5, RHO, MU, D, L, EPS, FITTINGS, 0.002)
    q_high, _ = operating_point(COEFFS, 8, RHO, MU, D, L, EPS, FITTINGS, 0.002)
    assert q_high < q_low


def test_more_valves_lower_flow_but_raise_head():
    more = {"elbow_90": 4, "globe_valve": 4, "entrance": 1, "exit": 1}
    q1, h1 = operating_point(COEFFS, STATIC, RHO, MU, D, L, EPS, FITTINGS, 0.002)
    q2, h2 = operating_point(COEFFS, STATIC, RHO, MU, D, L, EPS, more, 0.002)
    assert q2 < q1
    assert h2 > h1


def test_bad_inputs_raise():
    with pytest.raises(ValueError):
        fit_pump_curve([0, 1, 2], [20, 19])             # different lengths
    with pytest.raises(ValueError):
        fit_pump_curve([0, 1], [20, 19])                # fewer than 3 points
    with pytest.raises(ValueError):
        fit_pump_curve([-1, 0, 1], [20, 19, 18])        # negative flow
    with pytest.raises(ValueError):
        pump_head(-1, COEFFS)
    with pytest.raises(ValueError):
        system_head(-1, STATIC, RHO, MU, D, L, EPS, FITTINGS)


def test_operating_point_errors():
    with pytest.raises(ValueError):   # pump shut-off head is only 20 m
        operating_point(COEFFS, 25, RHO, MU, D, L, EPS, FITTINGS, 0.002)
    with pytest.raises(ValueError):   # q_max too small to reach the crossing
        operating_point(COEFFS, STATIC, RHO, MU, D, L, EPS, FITTINGS, 0.0005)
    with pytest.raises(ValueError):   # q_max must be positive
        operating_point(COEFFS, STATIC, RHO, MU, D, L, EPS, FITTINGS, 0)