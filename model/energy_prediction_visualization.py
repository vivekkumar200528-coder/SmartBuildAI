import pandas as pd
import matplotlib.pyplot as plt


# ==========================================================
# 1. LOAD PREDICTION RESULTS
# ==========================================================

FILE = "data/energy_prediction_results.csv"

df = pd.read_csv(FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])


# ==========================================================
# 2. DISPLAY BASIC INFORMATION
# ==========================================================

print("ENERGY PREDICTION VISUALIZATION")
print("--------------------------------")

print(f"Records: {len(df)}")

print(
    f"Actual average power: "
    f"{df['future_power_kw'].mean():.2f} kW"
)

print(
    f"Predicted average power: "
    f"{df['predicted_power_kw'].mean():.2f} kW"
)


# ==========================================================
# 3. ACTUAL VS PREDICTED POWER
# ==========================================================

plt.figure(figsize=(14, 6))

plt.plot(
    df["timestamp"],
    df["future_power_kw"],
    label="Actual Power"
)

plt.plot(
    df["timestamp"],
    df["predicted_power_kw"],
    label="Predicted Power"
)

plt.title(
    "Smart Building - Actual vs Predicted Energy Demand"
)

plt.xlabel("Time")

plt.ylabel("Power (kW)")

plt.legend()

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()


# ==========================================================
# 4. PREDICTION ERROR
# ==========================================================

df["prediction_error"] = (
    df["future_power_kw"]
    - df["predicted_power_kw"]
)


plt.figure(figsize=(14, 5))

plt.plot(
    df["timestamp"],
    df["prediction_error"]
)

plt.axhline(
    y=0,
    linestyle="--"
)

plt.title(
    "Energy Prediction Error"
)

plt.xlabel("Time")

plt.ylabel("Error (kW)")

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()


print("\nVisualization complete.")