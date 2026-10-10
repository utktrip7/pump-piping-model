import math

from friction import reynolds_number, friction_factor

G = 9.81  # gravitational acceleration, m/s2


def velocity_from_flow(flow_rate, diameter):
    """Average velocity in a circular pipe: v = Q / (pi * D^2 / 4).

    flow_rate : volumetric flow rate in m3/s (must not be negative)
    diameter  : pipe inner diameter in m (must be positive)

    Returns velocity in m/s.
    """
    if diameter <= 0:
        raise ValueError("Diameter must be positive")
    if flow_rate < 0:
        raise ValueError("Flow rate cannot be negative")
    return 4 * flow_rate / (math.pi * diameter ** 2)


def head_loss_straight(velocity, diameter, length, f):
    """Head loss in a straight pipe (Darcy-Weisbach): h_f = f * (L/D) * v^2 / (2g).

    velocity : average velocity in m/s (must not be negative)
    diameter : pipe inner diameter in m (must be positive)
    length   : pipe length in m (must not be negative)
    f        : Darcy friction factor (must be positive)

    Returns head loss in metres of fluid.
    """
    if diameter <= 0:
        raise ValueError("Diameter must be positive")
    if length < 0:
        raise ValueError("Length cannot be negative")
    if velocity < 0:
        raise ValueError("Velocity cannot be negative")
    if f <= 0:
        raise ValueError("Friction factor must be positive")
    return f * (length / diameter) * velocity ** 2 / (2 * G)


def pressure_drop_straight(rho, viscosity, velocity, diameter, length, roughness):
    """Frictional pressure drop in a straight pipe: dP = rho * g * h_f.

    rho       : fluid density in kg/m3 (must be positive)
    viscosity : dynamic viscosity in Pa.s (must be positive)
    velocity  : average velocity in m/s (must not be negative)
    diameter  : pipe inner diameter in m (must be positive)
    length    : pipe length in m (must not be negative)
    roughness : absolute pipe roughness in m (must not be negative)

    Returns pressure drop in Pa. Zero velocity or zero length gives 0.
    """
    if rho <= 0:
        raise ValueError("Density must be positive")
    if viscosity <= 0:
        raise ValueError("Viscosity must be positive")
    if diameter <= 0:
        raise ValueError("Diameter must be positive")
    if velocity < 0:
        raise ValueError("Velocity cannot be negative")
    if length < 0:
        raise ValueError("Length cannot be negative")
    if roughness < 0:
        raise ValueError("Roughness cannot be negative")

    if velocity == 0 or length == 0:
        return 0.0  # no flow or no pipe means no friction loss

    re = reynolds_number(rho, velocity, diameter, viscosity)
    f = friction_factor(re, diameter, roughness)
    return rho * G * head_loss_straight(velocity, diameter, length, f)