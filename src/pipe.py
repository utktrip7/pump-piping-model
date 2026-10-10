import math

from friction import *

G = 9.81  # gravitational acceleration, m/s2

# Loss coefficients K for common fittings (typical textbook values;
# cite your own source in the README, since values vary slightly by book)
FITTING_K = {
    "entrance": 0.5,  # sharp-edged pipe entrance
    "exit": 1.0,
    "elbow_90": 0.75,  # standard 90 degree elbow
    "elbow_45": 0.35,
    "tee_run": 0.4,  # tee, flow through the run
    "tee_branch": 1.0,  # tee, flow through the branch
    "gate_valve": 0.17,  # fully open
    "ball_valve": 0.05,  # fully open
    "globe_valve": 6.0,  # fully open
    "check_valve": 2.0,  # swing check
}


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


def total_k(fittings):
    """Sum the loss coefficients of all fittings in a series.

    fittings : dict of {fitting name: count}, e.g. {"elbow_90": 4, "globe_valve": 1}
               names must be keys of FITTING_K, counts must not be negative

    Returns K_total (dimensionless). An empty dict gives 0.
    """
    k_total = 0.0
    for name, count in fittings.items():
        if name not in FITTING_K:
            raise ValueError(f"Unknown fitting: {name}")
        if count < 0:
            raise ValueError("Fitting count cannot be negative")
        k_total += count * FITTING_K[name]
    return k_total


def head_loss_fittings(velocity, k_total):
    """Head loss through fittings: h = K * v^2 / (2g).

    velocity : average velocity in m/s (must not be negative)
    k_total  : total loss coefficient (must not be negative)

    Returns head loss in metres of fluid.
    """
    if velocity < 0:
        raise ValueError("Velocity cannot be negative")
    if k_total < 0:
        raise ValueError("K cannot be negative")
    return k_total * velocity ** 2 / (2 * G)


def pressure_drop_fittings(rho, velocity, k_total):
    """Pressure drop through fittings: dP = K * rho * v^2 / 2.

    rho      : fluid density in kg/m3 (must be positive)
    velocity : average velocity in m/s (must not be negative)
    k_total  : total loss coefficient (must not be negative)

    Returns pressure drop in Pa.
    """
    if rho <= 0:
        raise ValueError("Density must be positive")
    if velocity < 0:
        raise ValueError("Velocity cannot be negative")
    if k_total < 0:
        raise ValueError("K cannot be negative")
    return k_total * rho * velocity ** 2 / 2


def total_pressure_drop(rho, viscosity, velocity, diameter, length, roughness, fittings):
    """Total pressure drop: straight pipe friction plus fittings.

    rho, viscosity, velocity, diameter, length, roughness : as in pressure_drop_straight
    fittings : dict of {fitting name: count}, as in total_k (may be empty)

    Returns pressure drop in Pa.
    """
    straight = pressure_drop_straight(rho, viscosity, velocity, diameter, length, roughness)
    k_total = total_k(fittings)
    return straight + pressure_drop_fittings(rho, velocity, k_total)
