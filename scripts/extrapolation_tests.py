import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "data", "surrogate_data.csv"))
FEATURES = ["static_head_m", "length_m", "diameter_mm",
            "roughness_mm", "n_elbows", "n_globe_valves"]

train = df[df["diameter_mm"] < 40]     # BLANK 1: training pipes below this size (mm)
test = df[df["diameter_mm"] >= 40]      # pipes the model has never seen

for name, model in [("Linear", LinearRegression()),
                    ("Random Forest", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))]:
    model.fit(train[FEATURES], train["flow_Ls"])
    pred = model.predict(test[FEATURES])    # BLANK 2: the prediction method
    err = np.abs(pred - test["flow_Ls"]) / test["flow_Ls"] * 100
    print(name, "MAE:", round(mean_absolute_error(test["flow_Ls"], pred), 4),
          "mean % err:", round(err.mean(), 2), "worst:", round(err.max(), 1))