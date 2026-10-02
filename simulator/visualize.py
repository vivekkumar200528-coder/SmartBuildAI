import pandas as pd
import matplotlib.pyplot as plt


# Load dataset
df = pd.read_csv("data/virtual_building_data.csv")

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])


# ==========================================================
# 1. TOTAL BUILDING ENERGY OVER TIME
# ==========================================================

building_energy = (
    df.groupby("timestamp")["total_power_kw"]
    .sum()
)

plt.figure(figsize=(12, 5))

plt.plot(
    building_energy.index,
    building_energy.values
)

plt.title("Smart Building - Total Power Consumption")
plt.xlabel("Time")
plt.ylabel("Power (kW)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()


# ==========================================================
# 2. TOTAL OCCUPANCY OVER TIME
# ==========================================================

building_occupancy = (
    df.groupby("timestamp")["occupancy"]
    .sum()
)

plt.figure(figsize=(12, 5))

plt.plot(
    building_occupancy.index,
    building_occupancy.values
)

plt.title("Smart Building - Total Occupancy")
plt.xlabel("Time")
plt.ylabel("Number of People")
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()


# ==========================================================
# 3. TEMPERATURE VS OCCUPANCY
# ==========================================================

plt.figure(figsize=(8, 5))

plt.scatter(
    df["occupancy"],
    df["temperature_c"],
    alpha=0.3
)

plt.title("Temperature vs Occupancy")
plt.xlabel("Occupancy")
plt.ylabel("Temperature (°C)")
plt.tight_layout()

plt.show()


# ==========================================================
# 4. ENERGY CONSUMPTION BY ROOM
# ==========================================================

room_energy = (
    df.groupby("room_id")["total_power_kw"]
    .mean()
    .sort_values()
)

plt.figure(figsize=(10, 5))

plt.bar(
    room_energy.index,
    room_energy.values
)

plt.title("Average Power Consumption by Room")
plt.xlabel("Room")
plt.ylabel("Average Power (kW)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()


# ==========================================================
# 5. CO2 VS OCCUPANCY
# ==========================================================

plt.figure(figsize=(8, 5))

plt.scatter(
    df["occupancy"],
    df["co2_ppm"],
    alpha=0.3
)

plt.title("CO2 vs Occupancy")
plt.xlabel("Occupancy")
plt.ylabel("CO2 (ppm)")
plt.tight_layout()

plt.show()


print("\nVisualization complete.")