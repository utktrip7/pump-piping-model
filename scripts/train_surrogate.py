import os
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

path = os.path.join(os.path.dirname(__file__), "..", "data", "surrogate_data.csv")
df = pd.read_csv(path)

FEATURES = ["static_head_m", "length_m", "diameter_mm",
            "roughness_mm", "n_elbows", "n_globe_valves"]
TARGET = "flow_Ls"

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

models = [("Linear", LinearRegression()),
          ("Random Forest", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))]

for name, model in models:
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print(name, "R2:", round(r2_score(y_test, pred), 4),
          "MAE (L/s):", round(mean_absolute_error(y_test, pred), 4))

# --- Step 3: look past the single score ---
rf = models[1][1]
pred = rf.predict(X_test)

pct_err = np.abs(pred - y_test) / y_test * 100
print("Mean % error:", round(pct_err.mean(), 2))
print("95th percentile % error:", round(np.percentile(pct_err, 95), 2))
print("Worst case % error:", round(pct_err.max(), 2))

# which inputs matter most to the model
for name, imp in sorted(zip(FEATURES, rf.feature_importances_), key=lambda t: -t[1]):
    print(name, round(imp, 3))

# speed: predict all test cases at once
t0 = time.perf_counter()
rf.predict(X_test)
print("Predict time for", len(X_test), "cases:", round(time.perf_counter() - t0, 3), "s")