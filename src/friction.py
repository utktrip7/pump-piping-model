import math


def reynolds_number(rho, velocity, diameter, viscosity):
    """Calculate Reynolds number (dimensionless).

    Re = rho * velocity * diameter / viscosity

    rho       : density in kg/m3
    velocity  : average velocity in m/s
    diameter  : pipe inner diameter in m
    viscosity : dynamic viscosity in Pa.s
    """
    return rho * diameter * velocity / viscosity


def flow_regime(re):
    """Classify the flow from its Reynolds number.

    re : Reynolds number (dimensionless, must be positive)

    Returns "laminar" (Re < 2300), "transitional" (2300 <= Re <= 4000)
    or "turbulent" (Re > 4000).
    Raises ValueError if re <= 0.
    """
    if re <= 0:
        raise ValueError("Reynolds number must be positive")
    elif re < 2300:
        return "laminar"
    elif re <= 4000:
        return "transitional"
    else:
        return "turbulent"


def laminar_friction_factor(re):
    """Darcy friction factor for laminar flow (Hagen-Poiseuille): f = 64 / Re.

    re : Reynolds number (dimensionless), valid for 0 < Re < 2300

    Raises ValueError if re <= 0 or re >= 2300.
    """
    if re <= 0:
        raise ValueError("Reynolds number must be positive")
    if re >= 2300:
        raise ValueError("Laminar formula only valid for Re < 2300")
    return 64 / re


def _swamee_jain(re, diameter, roughness):
    """Swamee-Jain formula with no range checks (internal helper).

    Kept separate so friction_factor() can evaluate it exactly at Re = 4000
    for the transitional interpolation, while turbulent_friction_factor()
    still refuses Re <= 4000.
    """
    term1 = roughness / (3.7 * diameter)
    term2 = 5.74 / (re ** 0.9)
    denominator = math.log10(term1 + term2) ** 2
    return 0.25 / denominator


def turbulent_friction_factor(re, diameter, roughness):
    """Darcy friction factor for turbulent flow (Swamee-Jain approximation).

    f = 0.25 / [log10(roughness / (3.7 * diameter) + 5.74 / Re**0.9)]**2

    re        : Reynolds number (dimensionless), must be > 4000
    diameter  : pipe inner diameter in m (must be positive)
    roughness : absolute pipe roughness in m (must not be negative)

    Accurate to about 1-2% against the Colebrook equation for
    5000 < Re < 1e8 and 1e-6 < roughness/diameter < 1e-2.
    Raises ValueError for invalid inputs or Re <= 4000.
    """
    if re <= 0:
        raise ValueError("Reynolds number must be positive")
    if diameter <= 0:
        raise ValueError("Diameter must be positive")
    if roughness < 0:
        raise ValueError("Roughness cannot be negative")
    if re <= 4000:
        raise ValueError("Turbulent formula only valid for Re > 4000")
    return _swamee_jain(re, diameter, roughness)


def friction_factor(re, diameter, roughness):
    """Darcy friction factor for any flow regime.

    re        : Reynolds number (dimensionless)
    diameter  : pipe inner diameter in m
    roughness : absolute pipe roughness in m

    Re < 2300          : laminar, f = 64 / Re
    2300 <= Re <= 4000 : transitional, straight-line interpolation between the
                         laminar value at Re = 2300 and the Swamee-Jain value
                         at Re = 4000 (an approximation, a warning is printed)
    Re > 4000          : turbulent, Swamee-Jain

    Raises ValueError for re <= 0, diameter <= 0 or roughness < 0.
    """
    if re <= 0:
        raise ValueError("Reynolds number must be positive")
    if diameter <= 0:
        raise ValueError("Diameter must be positive")
    if roughness < 0:
        raise ValueError("Roughness cannot be negative")

    if re < 2300:
        return laminar_friction_factor(re)

    if re <= 4000:
        print("Warning: transitional flow (2300 <= Re <= 4000), "
              "friction factor is an interpolated approximation")
        re_a, re_b = 2300, 4000
        f_a = 64 / re_a  # laminar value at the lower end
        f_b = _swamee_jain(re_b, diameter, roughness)  # helper, no range check
        return f_a + (f_b - f_a) * (re - re_a) / (re_b - re_a)

    return turbulent_friction_factor(re, diameter, roughness)