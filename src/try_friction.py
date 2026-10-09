from friction import reynolds_number

# Water at about 20 C in your lab pipe (25.4 mm)
re = reynolds_number(rho=998, velocity=1.0, diameter=0.0254, viscosity=0.001)
print("Re at 1 m/s:", re)

re_slow = reynolds_number(rho=998, velocity=0.01, diameter=0.0254, viscosity=0.001)
print("Re at 0.01 m/s:", re_slow)
