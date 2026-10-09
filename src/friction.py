def reynolds_number(rho, velocity, diameter, viscosity):
    """Calculate Reynolds number (dimensionless).

    rho       : density in kg/m3
    velocity  : average velocity in m/s
    diameter  : pipe inner diameter in m
    viscosity : dynamic viscosity in Pa.s
    """
    return rho * diameter * velocity / viscosity


def flow_regime(re):
    if re <= 0:
        raise ValueError("Reynolds number must be positive")
    elif re < 2300:
        return "laminar"
    elif re >= 2300 and re <= 4000:
        return "transitional"
    else:
        return "turbulent"


def laminar_friction_factor(re):
    if re <= 0:
        raise ValueError("Reynolds number must be positive")
    elif re < 2300:
        return 64 / re
    else:
        raise ValueError("Laminar formula only valid for Re < 2300")
