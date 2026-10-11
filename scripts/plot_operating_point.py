import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import matplotlib.pyplot as plt

from pump import fit_pump_curve, pump_head, system_head, operating_point

# --- inputs (same example system as the tests) ---
RHO, MU = 998, 0.001
D, L, EPS = 0.0254, 10, 0.0000015
STATIC = 5
FITTINGS = {"elbow_90": 4, "globe_valve": 1, "entrance": 1, "exit": 1}
FLOWS = [0, 0.0005, 0.001, 0.0015, 0.002]   # m3/s
HEADS = [20, 19, 16, 11, 4]                 # m

coeffs = fit_pump_curve(FLOWS, HEADS)
q_op, h_op = operating_point(coeffs, STATIC, RHO, MU, D, L, EPS, FITTINGS, 0.002)

# --- curves ---
q = np.linspace(0, 0.002, 100)
pump = [pump_head(x, coeffs) for x in q]
system = [system_head(x, STATIC, RHO, MU, D, L, EPS, FITTINGS) for x in q]

# --- plot (flow shown in L/s for readability) ---
plt.figure(figsize=(8, 5))
plt.plot(q * 1000, pump, label="Pump curve")
plt.plot(q * 1000, system, label="System curve")
plt.scatter([x * 1000 for x in FLOWS], HEADS, color="grey", zorder=3,
            label="Pump data points")
plt.scatter([q_op * 1000], [h_op], color="red", zorder=4, s=60,
            label=f"Operating point ({q_op * 1000:.2f} L/s, {h_op:.1f} m)")
plt.xlabel("Flow rate (L/s)")
plt.ylabel("Head (m)")
plt.title("Pump and system curves")
plt.grid(True, alpha=0.3)
plt.legend()

os.makedirs(os.path.join(os.path.dirname(__file__), "..", "docs"), exist_ok=True)
plt.savefig(os.path.join(os.path.dirname(__file__), "..", "docs", "operating_point.png"),
            dpi=150, bbox_inches="tight")
plt.show()