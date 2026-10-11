import numpy as np
from pipe import *
from pump import *

print("Numpy works")
print("Square root of 16 is", int(np.sqrt(16)))
from pipe import *

FITTINGS = {"elbow_90": 4, "globe_valve": 1, "entrance": 1, "exit": 1}
coeffs = fit_pump_curve([0, 0.0005, 0.001, 0.0015, 0.002], [20, 19, 16, 11, 4])
print("coeffs:", coeffs)

q, h = operating_point(coeffs, 5, 998, 0.001, 0.0254, 10, 0.0000015, FITTINGS, 0.002)
print("operating point:", q, h)
print("pump:", pump_head(q, coeffs), "system:", system_head(q, 5, 998, 0.001, 0.0254, 10, 0.0000015, FITTINGS))
