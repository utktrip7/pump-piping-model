import sys
import os
from meters import manometer_dp, meter_flow, meter_cd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from meters import manometer_dp


def test_manometer_dp():
    assert manometer_dp(0.10, 1594, 1000) == pytest.approx(582.7, rel=0.01)
    assert manometer_dp(0, 1594, 1000) == 0


def test_manometer_dp_scales_with_height():
    assert manometer_dp(0.20, 1594, 1000) == pytest.approx(2 * manometer_dp(0.10, 1594, 1000))


def test_manometer_dp_errors():
    with pytest.raises(ValueError):
        manometer_dp(-0.1, 1594, 1000)
    with pytest.raises(ValueError):
        manometer_dp(0.1, 1594, 0)
    with pytest.raises(ValueError):
        manometer_dp(0.1, 900, 1000)  # manometer fluid lighter than water


DP = 582.7  # Pa, from h = 0.10 m of CCl4 under water
D_PIPE = 0.0254
D_VENTURI = 0.01467
D_ORIFICE = 0.0146


def test_venturi_flow():
    assert meter_flow(DP, 1000, D_PIPE, D_VENTURI, 0.98) == pytest.approx(1.90e-4, rel=0.02)


def test_orifice_flow():
    assert meter_flow(DP, 1000, D_PIPE, D_ORIFICE, 0.61) == pytest.approx(1.17e-4, rel=0.02)


def test_flow_scales_with_sqrt_dp():
    q1 = meter_flow(DP, 1000, D_PIPE, D_VENTURI, 0.98)
    q4 = meter_flow(4 * DP, 1000, D_PIPE, D_VENTURI, 0.98)
    assert q4 == pytest.approx(2 * q1)


def test_zero_dp_gives_zero_flow():
    assert meter_flow(0, 1000, D_PIPE, D_VENTURI, 0.98) == 0


def test_cd_round_trip():
    q = meter_flow(DP, 1000, D_PIPE, D_VENTURI, 0.98)
    assert meter_cd(q, DP, 1000, D_PIPE, D_VENTURI) == pytest.approx(0.98)


def test_meter_errors():
    with pytest.raises(ValueError):
        meter_flow(-1, 1000, D_PIPE, D_VENTURI, 0.98)  # negative dP
    with pytest.raises(ValueError):
        meter_flow(DP, 1000, D_PIPE, D_VENTURI, 0)  # Cd must be positive
    with pytest.raises(ValueError):
        meter_flow(DP, 1000, D_PIPE, 0.03, 0.98)  # throat bigger than pipe
    with pytest.raises(ValueError):
        meter_cd(0, DP, 1000, D_PIPE, D_VENTURI)  # zero flow
    with pytest.raises(ValueError):
        meter_cd(1e-4, 0, 1000, D_PIPE, D_VENTURI)  # zero dP
