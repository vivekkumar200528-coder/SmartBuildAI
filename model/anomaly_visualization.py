import pandas as pd
import matplotlib.pyplot as plt


# ==========================================================
# 1. LOAD ANOMALY RESULTS
# ==========================================================

FILE = "data/anomaly_detection_results.csv"

df = pd.read_csv(FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])


# ==========================================================
# 2. SEPARATE NORMAL AND ANOMALOUS DATA
# ==========================================================

normal = df[
    df["status"] == "Normal"
]

anomalies = df[
    df["status"] == "Anomaly"
]


print("ANOMALY VISUALIZATION")
print("---------------------")

print(
    f"Total records: {len(df)}"
)

print(
    f"Normal records: {len(normal)}"
)

print(
    f"Anomalies: {len(anomalies)}"
)


# ==========================================================
# 3. BUILDING POWER + ANOMALIES
# ==========================================================

building_power = (
    df.groupby("timestamp")["total_power_kw"]
    .sum()
)

anomaly_power = (
    anomalies.groupby("timestamp")["total_power_kw"]
    .sum()
)


plt.figure(figsize=(14, 6))

plt.plot(
    building_power.index,
    building_power.values,
    label="Building Power"
)

plt.scatter(
    anomaly_power.index,
    anomaly_power.values,
    label="Detected Anomaly"
)

plt.title(
    "Smart Building Power Consumption "
    "and Detected Anomalies"
)

plt.xlabel("Time")

plt.ylabel("Power (kW)")

plt.legend()

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()


# ==========================================================
# 4. ROOM-LEVEL ANOMALIES
# ==========================================================

anomaly_count = (
    anomalies["room_id"]
    .value_counts()
    .sort_index()
)


plt.figure(figsize=(10, 5))

plt.bar(
    anomaly_count.index,
    anomaly_count.values
)

plt.title(
    "Number of Detected Anomalies by Room"
)

plt.xlabel("Room")

plt.ylabel("Number of Anomalies")

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()


# ==========================================================
# 5. ANOMALY SCORE DISTRIBUTION
# ==========================================================

plt.figure(figsize=(10, 5))

plt.hist(
    normal["anomaly_score"],
    bins=40,
    alpha=0.7,
    label="Normal"
)

plt.hist(
    anomalies["anomaly_score"],
    bins=40,
    alpha=0.7,
    label="Anomaly"
)

plt.title(
    "Anomaly Score Distribution"
)

plt.xlabel("Anomaly Score")

plt.ylabel("Number of Records")

plt.legend()

plt.tight_layout()

plt.show()


print("\nVisualization complete.")