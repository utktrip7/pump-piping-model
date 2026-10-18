import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from pump import fit_pump_curve, operating_point

RHO, MU = 998, 0.001
COEFFS = fit_pump_curve([0, 0.0005, 0.001, 0.0015, 0.002], [20, 19, 16, 11, 4])
FEATURES = ["static_head_m", "length_m", "diameter_mm",
            "roughness_mm", "n_elbows", "n_globe_valves"]
RANGES = {"static_head_m": (0.0, 15.0), "length_m": (5.0, 100.0),
          "diameter_mm": (20.0, 50.0), "roughness_mm": (0.0015, 0.2)}


def physics_flow(static, length, d_mm, eps_mm, n_elbow, n_globe):
    """Operating flow in L/s from the physics code (fixed pump, water)."""
    fittings = {"elbow_90": n_elbow, "globe_valve": n_globe, "entrance": 1, "exit": 1}
    q, _ = operating_point(COEFFS, static, RHO, MU, d_mm / 1000, length,
                           eps_mm / 1000, fittings, 0.002)
    return q * 1000


def train(n=20000, seed=42):
    """Generate n random systems with the physics code and fit a Random Forest."""
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        x = [rng.uniform(*RANGES["static_head_m"]), rng.uniform(*RANGES["length_m"]),
             rng.uniform(*RANGES["diameter_mm"]), rng.uniform(*RANGES["roughness_mm"]),
             int(rng.integers(0, 11)), int(rng.integers(0, 6))]
        try:
            rows.append(x + [physics_flow(*x)])
        except ValueError:          # no valid operating point for this system
            continue
    df = pd.DataFrame(rows, columns=FEATURES + ["flow_Ls"])
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(df[FEATURES], df["flow_Ls"])
    return model