import pandas as pd

from meters import manometer_dp, meter_cd
from friction import reynolds_number
from pipe import velocity_from_flow

RHO_W, RHO_M, MU = 1000.0, 1594.0, 0.901e-3
D_PIPE = 0.0254
THROAT = {"venturi": 0.01467, "orifice": 0.0146}
TEXTBOOK = {"venturi": 0.98, "orifice": 0.61}


def lab_results(csv_path):
    """Cd and pipe Re for every lab reading. 'used' = data ok and Cd < 1."""
    df = pd.read_csv(csv_path)
    cds, res = [], []
    for _, r in df.iterrows():
        q = r.q_actual_lpm / 60000.0
        dp = manometer_dp(r.dh_mm / 1000.0, RHO_M, RHO_W)
        cds.append(meter_cd(q, dp, RHO_W, D_PIPE, THROAT[r.meter]))
        res.append(reynolds_number(RHO_W, velocity_from_flow(q, D_PIPE), D_PIPE, MU))
    df["Cd"], df["Re_pipe"] = cds, res
    df["used"] = (df["keep"] == 1) & (df["Cd"] < 1)
    return df


def error_table(df):
    """Mean Cd of used readings vs textbook, with percent error."""
    t = df[df["used"]].groupby("meter").agg(
        Count=("Cd", "count"), Mean_Cd=("Cd", "mean")).reset_index()
    t["Textbook_Cd"] = t["meter"].map(TEXTBOOK)
    t["Pct_Error"] = (t["Mean_Cd"] - t["Textbook_Cd"]) / t["Textbook_Cd"] * 100
    return t.round(3)