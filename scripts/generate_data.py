import sys
import os
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd

from pump import fit_pump_curve, operating_point

warnings.filterwarnings("ignore")   # hide the transitional-flow warning

RHO, MU = 998, 0.001
coeffs = fit_pump_curve([0, 0.0005, 0.001, 0.0015, 0.002], [20, 19, 16, 11, 4])
rng = np.random.default_rng(42)     # fixed seed = same data every run

rows, skipped = [], 0
for _ in range(100000):
    static = rng.uniform(0, 15)           # m
    length = rng.uniform(5, 100)          # m
    d_mm = rng.uniform(20, 50)            # mm
    eps_mm = rng.uniform(0.0015, 0.2)     # mm
    n_elbow = int(rng.integers(0, 11))
    n_globe = int(rng.integers(0, 6))
    fittings = {"elbow_90": n_elbow, "globe_valve": n_globe, "entrance": 1, "exit": 1}
    try:
        q, h = operating_point(coeffs, static, RHO, MU, d_mm / 1000, length,
                               eps_mm / 1000, fittings, 0.002)
    except ValueError:                    # pump cannot deliver, or curves do not cross
        skipped += 1
        continue
    rows.append([static, length, d_mm, eps_mm, n_elbow, n_globe, q * 1000, h])

df = pd.DataFrame(rows, columns=["static_head_m", "length_m", "diameter_mm",
                                 "roughness_mm", "n_elbows", "n_globe_valves",
                                 "flow_Ls", "head_m"])
df.to_csv(os.path.join(os.path.dirname(__file__), "..", "data", "surrogate_data.csv"),
          index=False)
print(f"Saved {len(df)} cases, skipped {skipped}")
print(df.describe().round(3))