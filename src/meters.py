import math
from pipe import G


def manometer_dp(h, rho_manometer, rho_fluid):
    """Pressure difference read from a U-tube manometer.

    dP = (rho_manometer - rho_fluid) * g * h

    h             : height difference of the manometer fluid in m (must not be negative)
    rho_manometer : manometer fluid density in kg/m3 (e.g. CCl4 = 1594)
    rho_fluid     : density of the flowing fluid in kg/m3 (e.g. water = 1000)

    The manometer fluid must be denser than the flowing fluid.
    Returns the pressure difference in Pa.
    """
    if h < 0:
        raise ValueError("Manometer height cannot be negative")
    if rho_fluid <= 0:
        raise ValueError("Fluid density must be positive")
    if rho_manometer <= rho_fluid:
        raise ValueError("Manometer fluid must be denser than the flowing fluid")
    return (rho_manometer - rho_fluid) * G * h


def _ideal_flow(dp, rho, pipe_diameter, throat_diameter):
    """Ideal (frictionless) flow through a meter, before applying Cd (internal helper).

    Q_ideal = A_throat * sqrt( 2*dP / (rho * (1 - beta^4)) ),  beta = d / D
    """
    if rho <= 0:
        raise ValueError("Density must be positive")
    if pipe_diameter <= 0 or throat_diameter <= 0:
        raise ValueError("Diameters must be positive")
    if throat_diameter >= pipe_diameter:
        raise ValueError("Throat diameter must be smaller than pipe diameter")
    beta = throat_diameter / pipe_diameter
    area_throat = math.pi * throat_diameter ** 2 / 4
    return area_throat * math.sqrt(2 * dp / (rho * (1 - beta ** 4)))


def meter_flow(dp, rho, pipe_diameter, throat_diameter, cd):
    """Actual flow rate through a Venturi or orifice meter.

    Q = Cd * A_throat * sqrt( 2*dP / (rho * (1 - beta^4)) )

    dp             : pressure difference across the meter in Pa (must not be negative)
    rho            : fluid density in kg/m3
    pipe_diameter  : pipe inner diameter in m
    throat_diameter: throat (or orifice) diameter in m, smaller than the pipe
    cd             : discharge coefficient (must be positive)

    Returns the flow rate in m3/s.
    """
    if dp < 0:
        raise ValueError("Pressure difference cannot be negative")
    if cd <= 0:
        raise ValueError("Discharge coefficient must be positive")
    return cd * _ideal_flow(dp, rho, pipe_diameter, throat_diameter)


def meter_cd(q, dp, rho, pipe_diameter, throat_diameter):
    """Discharge coefficient from a measured flow rate: Cd = Q_actual / Q_ideal.

    q              : measured (actual) flow rate in m3/s (must be positive)
    dp             : pressure difference across the meter in Pa (must be positive)
    rho            : fluid density in kg/m3
    pipe_diameter  : pipe inner diameter in m
    throat_diameter: throat (or orifice) diameter in m, smaller than the pipe

    Returns Cd (dimensionless).
    """
    if q <= 0:
        raise ValueError("Flow rate must be positive")
    if dp <= 0:
        raise ValueError("Pressure difference must be positive")
    return q / _ideal_flow(dp, rho, pipe_diameter, throat_diameter)
