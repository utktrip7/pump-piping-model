import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from pump import fit_pump_curve, pump_head, system_head, operating_point
from pipe import FITTING_K
from meters import manometer_dp, meter_flow
from validation import lab_results, error_table, TEXTBOOK

st.title("Pump-Piping System Model")

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

# --- tabs ---
tab1, tab2, tab3 = st.tabs(["Pump & system", "Meter calculator", "Lab validation"])

with tab1:
    try:
        flows = [float(x) / 1000 for x in flows_txt.split(",")]   # L/s -> m3/s
        heads = [float(x) for x in heads_txt.split(",")]
        coeffs = fit_pump_curve(flows, heads)
        q_op, h_op = operating_point(coeffs, static, rho, mu, d, length, eps,
                                     fittings, max(flows))
    except ValueError as e:
        st.error(str(e))
    else:
        col1, col2 = st.columns(2)
        col1.metric("Flow at operating point", f"{q_op * 1000:.2f} L/s")
        col2.metric("Head at operating point", f"{h_op:.1f} m")
        q = np.linspace(0, max(flows), 100)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(q * 1000, [pump_head(x, coeffs) for x in q], label="Pump curve")
        ax.plot(q * 1000, [system_head(x, static, rho, mu, d, length, eps, fittings)
                           for x in q], label="System curve")
        ax.scatter([x * 1000 for x in flows], heads, color="grey", label="Pump data")
        ax.scatter([q_op * 1000], [h_op], color="red", s=60, zorder=4,
                   label="Operating point")
        ax.set_xlabel("Flow rate (L/s)")
        ax.set_ylabel("Head (m)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        st.pyplot(fig)

with tab2:
    st.caption("Uses the fluid density and pipe diameter from the sidebar.")
    meter = st.selectbox("Meter type", ["venturi", "orifice"])
    meter_defaults = {"venturi": (14.67, 0.98), "orifice": (14.6, 0.61)}
    throat = st.number_input("Throat / orifice diameter (mm)", 1.0, 1000.0,
                             meter_defaults[meter][0], key=f"t_{meter}") / 1000
    cd = st.number_input("Discharge coefficient Cd", 0.01, 1.0,
                         meter_defaults[meter][1], key=f"c_{meter}")
    rho_m = st.number_input("Manometer fluid density (kg/m3)", 1.0, 20000.0, 1594.0)
    h = st.number_input("Manometer reading (mm)", 0.0, 2000.0, 100.0) / 1000
    try:
        dp = manometer_dp(h, rho_m, rho)
        q_m = meter_flow(dp, rho, d, throat, cd)
        c1, c2 = st.columns(2)
        c1.metric("Pressure difference", f"{dp:.1f} Pa")
        c2.metric("Flow rate", f"{q_m * 60000:.2f} L/min")
    except ValueError as e:
        st.error(str(e))

with tab3:
    df = lab_results(os.path.join(os.path.dirname(__file__), "data", "lab_data.csv"))
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    for m, color, marker in [("venturi", "blue", "o"), ("orifice", "orange", "s")]:
        sub = df[df["meter"] == m]
        ax2.scatter(sub[sub["used"]]["Re_pipe"], sub[sub["used"]]["Cd"], color=color,
                    marker=marker, s=60, label=f"{m} (used)")
        ax2.scatter(sub[~sub["used"]]["Re_pipe"], sub[~sub["used"]]["Cd"],
                    facecolors="none", edgecolors=color, marker=marker, s=60,
                    alpha=0.5, label=f"{m} (excluded)")
        ax2.axhline(TEXTBOOK[m], color=color, linestyle="--", alpha=0.6)
    ax2.set_xlabel("Pipe Reynolds number")
    ax2.set_ylabel("Cd")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)
    st.dataframe(error_table(df))
    st.caption("Used = data consistent and Cd < 1 (Cd above 1 is physically "
               "impossible). Dashed lines: textbook Cd (0.98 Venturi, 0.61 orifice).")
    st.dataframe(df.round(3))