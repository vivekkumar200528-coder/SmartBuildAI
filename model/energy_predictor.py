import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================================
# 1. LOAD DATA
# ==========================================================

INPUT_FILE = "data/virtual_building_data.csv"

print("Loading building data...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])


# ==========================================================
# 2. CREATE BUILDING-LEVEL DATA
# ==========================================================

building_data = (
    df.groupby("timestamp")
    .agg({
        "occupancy": "sum",
        "temperature_c": "mean",
        "humidity_percent": "mean",
        "co2_ppm": "mean",
        "hvac_kw": "sum",
        "lighting_kw": "sum",
        "equipment_kw": "sum",
        "total_power_kw": "sum"
    })
    .reset_index()
)


print(
    f"Building-level records: "
    f"{len(building_data)}"
)


# ==========================================================
# 3. CREATE TIME FEATURES
# ==========================================================

building_data["hour"] = (
    building_data["timestamp"].dt.hour
)

building_data["day_of_week"] = (
    building_data["timestamp"].dt.dayofweek
)


# ==========================================================
# 4. CREATE FUTURE ENERGY TARGET
# ==========================================================

# The target is the building's power
# consumption 15 minutes into the future.

building_data["future_power_kw"] = (
    building_data["total_power_kw"].shift(-1)
)


# Remove the final row because
# it has no future value.

building_data = building_data.dropna()


# ==========================================================
# 5. SELECT FEATURES
# ==========================================================

features = [
    "occupancy",
    "temperature_c",
    "humidity_percent",
    "co2_ppm",
    "hvac_kw",
    "lighting_kw",
    "equipment_kw",
    "total_power_kw",
    "hour",
    "day_of_week"
]


X = building_data[features]

y = building_data["future_power_kw"]


# ==========================================================
# 6. TIME-BASED TRAIN/TEST SPLIT
# ==========================================================

# We use the first 80% for training
# and the final 20% for testing.

split_index = int(len(building_data) * 0.8)

X_train = X.iloc[:split_index]

X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]

y_test = y.iloc[split_index:]


print("\nDATA SPLIT")
print("----------")

print(
    f"Training records: {len(X_train)}"
)

print(
    f"Testing records: {len(X_test)}"
)


# ==========================================================
# 7. CREATE MODEL
# ==========================================================

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)


# ==========================================================
# 8. TRAIN MODEL
# ==========================================================

print("\nTraining energy prediction model...")

model.fit(
    X_train,
    y_train
)


# ==========================================================
# 9. MAKE PREDICTIONS
# ==========================================================

predictions = model.predict(X_test)


# ==========================================================
# 10. EVALUATE MODEL
# ==========================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

mse = mean_squared_error(
    y_test,
    predictions
)

rmse = mse ** 0.5

r2 = r2_score(
    y_test,
    predictions
)


print("\nMODEL PERFORMANCE")
print("-----------------")

print(
    f"MAE: {mae:.3f} kW"
)

print(
    f"RMSE: {rmse:.3f} kW"
)

print(
    f"R² Score: {r2:.3f}"
)


# ==========================================================
# 11. CREATE RESULT TABLE
# ==========================================================

results = building_data.iloc[
    split_index:
].copy()

results["predicted_power_kw"] = predictions


# ==========================================================
# 12. SAVE RESULTS
# ==========================================================

OUTPUT_FILE = (
    "data/energy_prediction_results.csv"
)

results.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"\nPredictions saved to: "
    f"{OUTPUT_FILE}"
)


# ==========================================================
# 13. SHOW SAMPLE PREDICTIONS
# ==========================================================

print("\nSAMPLE PREDICTIONS")
print("------------------")

print(
    results[
        [
            "timestamp",
            "total_power_kw",
            "future_power_kw",
            "predicted_power_kw"
        ]
    ].head(10)
)