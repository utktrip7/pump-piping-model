def reynolds_number(rho, velocity, diameter, viscosity):
    """Calculate Reynolds number (dimensionless).

    rho       : density in kg/m3
    velocity  : average velocity in m/s
    diameter  : pipe inner diameter in m
    viscosity : dynamic viscosity in Pa.s
    """
    return rho * diameter * velocity / viscosity
