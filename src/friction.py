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
        return "ValueError"
    elif re < 2300:
        return "Laminar FLow"
    elif re >= 2300 and re <= 4000:
        return "Transitonal Flow"
    else:
        return "Turbulent Flow"

def laminar_friction_factor(re):
    if re <= 0:
        return "ValueError"
    elif re < 2300:
        return 64/re
    elif re >= 2300 and re <= 4000:
        return "n/a"
    else:
        return "n/a"