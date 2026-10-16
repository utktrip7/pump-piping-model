import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from pump import fit_pump_curve, pump_head, system_head, operating_point
from pipe import FITTING_K

st.title("Pump-Piping System Simulator")

# --- inputs ---
st.sidebar.header("Fluid")
rho = st.sidebar.number_input("Density (kg/m3)", 1.0, 5000.0, 998.0)
mu = st.sidebar.number_input("Viscosity (Pa.s)", 0.00001, 10.0, 0.001, format="%.5f")

st.sidebar.header("Piping")
d = st.sidebar.number_input("Pipe diameter (mm)", 1.0, 1000.0, 25.4) / 1000
length = st.sidebar.number_input("Length (m)", 0.0, 10000.0, 10.0)
eps = st.sidebar.number_input("Roughness (mm)", 0.0, 5.0, 0.0015, format="%.4f") / 1000
static = st.sidebar.number_input("Static head (m)", -100.0, 500.0, 5.0)

st.sidebar.header("Fittings (count)")
defaults = {"elbow_90": 4, "globe_valve": 1, "entrance": 1, "exit": 1}
fittings = {name: int(st.sidebar.number_input(name, 0, 100, defaults.get(name, 0)))
            for name in FITTING_K}

st.sidebar.header("Pump data")
flows_txt = st.sidebar.text_input("Flow (L/s)", "0, 0.5, 1.0, 1.5, 2.0")
heads_txt = st.sidebar.text_input("Head (m)", "20, 19, 16, 11, 4")

# --- calculation ---
try:
    flows = [float(x) / 1000 for x in flows_txt.split(",")]   # L/s -> m3/s
    heads = [float(x) for x in heads_txt.split(",")]
    coeffs = fit_pump_curve(flows, heads)
    q_op, h_op = operating_point(coeffs, static, rho, mu, d, length, eps,
                                 fittings, max(flows))
except ValueError as e:
    st.error(str(e))
    st.stop()

# --- results ---
col1, col2 = st.columns(2)
col1.metric("Flow at operating point", f"{q_op * 1000:.2f} L/s")
col2.metric("Head at operating point", f"{h_op:.1f} m")

q = np.linspace(0, max(flows), 100)
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(q * 1000, [pump_head(x, coeffs) for x in q], label="Pump curve")
ax.plot(q * 1000, [system_head(x, static, rho, mu, d, length, eps, fittings) for x in q],
        label="System curve")
ax.scatter([x * 1000 for x in flows], heads, color="grey", label="Pump data")
ax.scatter([q_op * 1000], [h_op], color="red", s=60, zorder=4, label="Operating point")
ax.set_xlabel("Flow rate (L/s)")
ax.set_ylabel("Head (m)")
ax.grid(True, alpha=0.3)
ax.legend()
st.pyplot(fig)