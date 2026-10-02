import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ==========================================================
# 1. LOAD DATA
# ==========================================================

INPUT_FILE = "data/virtual_building_data_with_anomalies.csv"

OUTPUT_FILE = "data/anomaly_detection_results.csv"


print("Loading building data...")

df = pd.read_csv(INPUT_FILE)


# ==========================================================
# 2. SELECT FEATURES
# ==========================================================

features = [
    "occupancy",
    "temperature_c",
    "humidity_percent",
    "co2_ppm",
    "hvac_kw",
    "lighting_kw",
    "equipment_kw",
    "total_power_kw"
]


X = df[features]


# ==========================================================
# 3. SCALE DATA
# ==========================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ==========================================================
# 4. CREATE ANOMALY DETECTOR
# ==========================================================

model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42
)


# ==========================================================
# 5. TRAIN MODEL
# ==========================================================

print("Training anomaly detection model...")

model.fit(X_scaled)


# ==========================================================
# 6. PREDICT ANOMALIES
# ==========================================================

predictions = model.predict(X_scaled)

scores = model.decision_function(X_scaled)


# ==========================================================
# 7. ADD RESULTS TO DATAFRAME
# ==========================================================

df["anomaly_prediction"] = predictions

df["anomaly_score"] = scores


# ==========================================================
# 8. CREATE READABLE LABEL
# ==========================================================

df["status"] = df["anomaly_prediction"].map(
    {
        1: "Normal",
        -1: "Anomaly"
    }
)


# ==========================================================
# 9. SAVE RESULTS
# ==========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================================
# 10. DISPLAY RESULTS
# ==========================================================

total_records = len(df)

anomalies = (
    df["anomaly_prediction"] == -1
).sum()

normal = (
    df["anomaly_prediction"] == 1
).sum()


print("\nANOMALY DETECTION RESULTS")
print("-------------------------")

print(
    f"Total records: {total_records}"
)

print(
    f"Normal records: {normal}"
)

print(
    f"Anomalies detected: {anomalies}"
)

print(
    f"Anomaly percentage: "
    f"{(anomalies / total_records) * 100:.2f}%"
)


print(
    f"\nResults saved to: "
    f"{OUTPUT_FILE}"
)


# ==========================================================
# 11. SHOW EXAMPLES
# ==========================================================

print("\nSAMPLE ANOMALIES")
print("----------------")

anomaly_data = df[
    df["anomaly_prediction"] == -1
]

print(
    anomaly_data[
        [
            "timestamp",
            "room_id",
            "occupancy",
            "temperature_c",
            "co2_ppm",
            "hvac_kw",
            "equipment_kw",
            "total_power_kw",
            "anomaly_score"
        ]
    ].head(10)
)