from pipe import *


def fit_pump_curve(flows, heads):
    # 1. Check the inputs
    if len(flows) != len(heads):
        raise ValueError("flows and heads must have the same length")
    if len(flows) < 3:
        raise ValueError("Need at least 3 points to fit a quadratic")
    if any(q < 0 for q in flows):
        raise ValueError("Flow rates cannot be negative")

    # 2. Fit a quadratic (degree 2) through the points
    c, b, a = np.polyfit(flows, heads, 2)

    # 3. Return in the order a, b, c
    return a, b, c


def pump_head(q, coeffs):
    """Head delivered by the pump at flow rate q (the pump curve).

    H = a + b*q + c*q^2

    q      : flow rate in m3/s (must not be negative)
    coeffs : (a, b, c) from fit_pump_curve

    Returns the pump head in m.
    """
    if q < 0:
        raise ValueError("Flow rate cannot be negative")
    a, b, c = coeffs
    return a + b * q + c * q ** 2


def system_head(q, static_head, rho, viscosity, diameter, length, roughness, fittings):
    """Head the piping system requires at flow rate q (the system curve).

    H_system = H_static + dP_total / (rho * g)

    q           : flow rate in m3/s (must not be negative)
    static_head : height the fluid is lifted, in m (can be zero or negative)
    rho         : fluid density in kg/m3
    viscosity   : dynamic viscosity in Pa.s
    diameter    : pipe inner diameter in m
    length      : pipe length in m
    roughness   : absolute pipe roughness in m
    fittings    : dict of {fitting name: count}, e.g. {"elbow_90": 4} (may be empty)

    Returns the required head in m. At q = 0 this is just the static head.
    """
    velocity = velocity_from_flow(q, diameter)  # raises ValueError if q < 0
    pressure_drop = total_pressure_drop(rho, viscosity, velocity, diameter,
                                        length, roughness, fittings)
    return static_head + pressure_drop / (rho * G)


from scipy.optimize import brentq


def operating_point(coeffs, static_head, rho, viscosity, diameter,
                    length, roughness, fittings, q_max):
    """Find where the pump curve meets the system curve.

    coeffs      : (a, b, c) pump curve coefficients from fit_pump_curve
    static_head : height the fluid is lifted, in m
    rho, viscosity, diameter, length, roughness, fittings : the piping system,
                  as in system_head
    q_max       : upper flow limit to search, in m3/s (must be positive)

    Returns (q, head): flow in m3/s and head in m at the operating point.
    Raises ValueError if the pump cannot overcome the static head, or if
    the curves do not cross between 0 and q_max.
    """
    if q_max <= 0:
        raise ValueError("q_max must be positive")

    def gap(q):
        return (pump_head(q, coeffs)
                - system_head(q, static_head, rho, viscosity, diameter,
                              length, roughness, fittings))

    if gap(0) < 0:
        raise ValueError("Pump cannot overcome the static head")
    if gap(q_max) > 0:
        raise ValueError("Curves do not cross below q_max, try a larger q_max")

    q = brentq(gap, 0, q_max)
    return q, pump_head(q, coeffs)
