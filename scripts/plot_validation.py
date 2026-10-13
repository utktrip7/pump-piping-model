import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd
import matplotlib.pyplot as plt

from meters import manometer_dp, meter_cd
from friction import reynolds_number
from pipe import velocity_from_flow

# --- constants ---
RHO_W = 1000.0
RHO_M = 1594.0
MU = 0.901e-3  # Pa.s (0.901 cP)
D_PIPE = 0.0254
THROAT = {"venturi": 0.01467, "orifice": 0.0146}
TEXTBOOK = {"venturi": 0.98, "orifice": 0.61}

# --- load data and compute Cd and Re for every row ---
base = os.path.dirname(__file__)
df = pd.read_csv(os.path.join(base, "..", "data", "lab_data.csv"))

cds, res = [], []
for _, r in df.iterrows():
    q = r.q_actual_lpm / 60000.0  # LPM -> m3/s
    dp = manometer_dp(r.dh_mm / 1000.0, RHO_M, RHO_W)
    cds.append(meter_cd(q, dp, RHO_W, D_PIPE, THROAT[r.meter]))
    res.append(reynolds_number(RHO_W, velocity_from_flow(q, D_PIPE), D_PIPE, MU))

df["Cd"] = cds
df["Re_pipe"] = res

# Exclusion rule (applied by code, not by hand):
#   keep == 0 : data conflict (collected volume disagrees with rotameter setting)
#   Cd >= 1   : physically impossible
df["used"] = (df["keep"] == 1) & (df["Cd"] < 1)

print("--- ALL READINGS ---")
print(df.round(3).to_string(index=False))

# --- plot Cd vs Re ---
plt.figure(figsize=(10, 6))
for meter_type, color, marker, name in [
    ("venturi", "blue", "o", "Venturi"),
    ("orifice", "orange", "s", "Orifice"),
]:
    subset = df[df["meter"] == meter_type]
    used = subset[subset["used"]]
    excluded = subset[~subset["used"]]
    plt.scatter(used["Re_pipe"], used["Cd"], color=color, marker=marker,
                s=80, label=f"{name} (used)")
    plt.scatter(excluded["Re_pipe"], excluded["Cd"], facecolors="none",
                edgecolors=color, marker=marker, s=80, alpha=0.5,
                label=f"{name} (excluded)")

plt.axhline(0.98, color="blue", linestyle="--", alpha=0.7, label="Textbook Venturi Cd (~0.98)")
plt.axhline(0.61, color="orange", linestyle="--", alpha=0.7, label="Textbook Orifice Cd (~0.61)")
plt.xlabel("Pipe Reynolds Number (Re)", fontsize=12)
plt.ylabel("Discharge Coefficient (Cd)", fontsize=12)
plt.title("Discharge Coefficient vs Reynolds Number (Lab Validation)", fontsize=14)
plt.grid(True, linestyle=":", alpha=0.6)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()

os.makedirs(os.path.join(base, "..", "docs"), exist_ok=True)
plot_path = os.path.join(base, "..", "docs", "cd_vs_re_validation.png")
plt.savefig(plot_path, dpi=300)
print(f"\nPlot saved to: {plot_path}")

# --- error table (used readings only) ---
summary = df[df["used"]].groupby("meter").agg(
    Mean_Cd=("Cd", "mean"), Count=("Cd", "count")).reset_index()
summary["Textbook_Cd"] = summary["meter"].map(TEXTBOOK)
summary["Pct_Error"] = (summary["Mean_Cd"] - summary["Textbook_Cd"]) / summary["Textbook_Cd"] * 100

print("\n--- ERROR TABLE (used readings only) ---")
print(summary[["meter", "Count", "Mean_Cd", "Textbook_Cd", "Pct_Error"]].round(3).to_string(index=False))
print(f"\nExcluded: {int((~df['used']).sum())} of {len(df)} readings")
