import pandas as pd
import matplotlib.pyplot as plt


# ==========================================================
# 1. LOAD OPTIMIZATION RESULTS
# ==========================================================

FILE = "data/optimization_results.csv"

df = pd.read_csv(FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])


# ==========================================================
# 2. BUILDING-LEVEL POWER
# ==========================================================

building_power = (
    df.groupby("timestamp")
    .agg({
        "total_power_kw": "sum",
        "optimized_total_power_kw": "sum"
    })
    .reset_index()
)


# ==========================================================
# 3. CALCULATE SAVINGS
# ==========================================================

building_power["power_saving_kw"] = (
    building_power["total_power_kw"]
    - building_power["optimized_total_power_kw"]
)


building_power["saving_percentage"] = (
    building_power["power_saving_kw"]
    / building_power["total_power_kw"]
) * 100


# ==========================================================
# 4. SUMMARY
# ==========================================================

baseline = (
    building_power["total_power_kw"]
    .sum()
)

optimized = (
    building_power["optimized_total_power_kw"]
    .sum()
)

saving = baseline - optimized

saving_percentage = (
    saving / baseline
) * 100


print("\nBASELINE VS OPTIMIZED")
print("---------------------")

print(
    f"Baseline energy total: "
    f"{baseline:.2f} kW"
)

print(
    f"Optimized energy total: "
    f"{optimized:.2f} kW"
)

print(
    f"Energy reduction: "
    f"{saving:.2f} kW"
)

print(
    f"Reduction percentage: "
    f"{saving_percentage:.2f}%"
)


# ==========================================================
# 5. POWER COMPARISON GRAPH
# ==========================================================

plt.figure(figsize=(14, 6))

plt.plot(
    building_power["timestamp"],
    building_power["total_power_kw"],
    label="Baseline"
)

plt.plot(
    building_power["timestamp"],
    building_power["optimized_total_power_kw"],
    label="Optimized"
)

plt.title(
    "Baseline vs Optimized Building Power"
)

plt.xlabel("Time")

plt.ylabel("Power (kW)")

plt.legend()

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()


# ==========================================================
# 6. POWER SAVINGS GRAPH
# ==========================================================

plt.figure(figsize=(14, 5))

plt.plot(
    building_power["timestamp"],
    building_power["power_saving_kw"]
)

plt.axhline(
    y=0,
    linestyle="--"
)

plt.title(
    "Power Savings from Smart Building Optimization"
)

plt.xlabel("Time")

plt.ylabel("Power Saved (kW)")

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()


# ==========================================================
# 7. DAILY COMPARISON
# ==========================================================

building_power["date"] = (
    building_power["timestamp"].dt.date
)


daily = (
    building_power.groupby("date")
    .agg({
        "total_power_kw": "sum",
        "optimized_total_power_kw": "sum"
    })
)


daily["saving"] = (
    daily["total_power_kw"]
    - daily["optimized_total_power_kw"]
)


print("\nDAILY RESULTS")
print("-------------")

print(daily)


print("\nVisualization complete.")