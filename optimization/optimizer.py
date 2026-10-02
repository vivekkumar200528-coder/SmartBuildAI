import pandas as pd


INPUT_FILE = "data/virtual_building_data.csv"

OUTPUT_FILE = "data/optimization_results.csv"


# ==========================================================
# COMFORT / IAQ LIMITS
# ==========================================================

MIN_COMFORT_TEMP = 22.0
MAX_COMFORT_TEMP = 26.0

MAX_CO2 = 1000


# ==========================================================
# OPTIMIZATION FUNCTION
# ==========================================================

def optimize_room(row, high_demand):

    occupancy = row["occupancy"]
    temperature = row["temperature_c"]
    co2 = row["co2_ppm"]

    current_hvac = row["hvac_kw"]
    current_lighting = row["lighting_kw"]

    optimized_hvac = current_hvac
    optimized_lighting = current_lighting

    action = "No change"

    reason = "Normal operation"


    # ======================================================
    # RULE 1 — HIGH CO2
    # ======================================================

    if co2 > MAX_CO2:

        optimized_hvac = current_hvac

        action = "Maintain HVAC"

        reason = "CO2 is above IAQ limit"


    # ======================================================
    # RULE 2 — TEMPERATURE TOO HIGH
    # ======================================================

    elif temperature > MAX_COMFORT_TEMP:

        optimized_hvac = current_hvac * 1.10

        action = "Increase HVAC"

        reason = "Temperature above comfort range"


    # ======================================================
    # RULE 3 — TEMPERATURE TOO LOW
    # ======================================================

    elif temperature < MIN_COMFORT_TEMP:

        optimized_hvac = current_hvac * 0.90

        action = "Reduce HVAC"

        reason = "Temperature below comfort range"


    # ======================================================
    # RULE 4 — ROOM EMPTY
    # ======================================================

    elif occupancy == 0:

        optimized_hvac = current_hvac * 0.40

        optimized_lighting = current_lighting * 0.10

        action = "Reduce HVAC + Lighting"

        reason = "Room is unoccupied"


    # ======================================================
    # RULE 5 — HIGH BUILDING DEMAND
    # ======================================================

    elif high_demand:

        optimized_hvac = current_hvac * 0.90

        optimized_lighting = current_lighting * 0.80

        action = "Reduce flexible loads"

        reason = "Predicted building demand is high"


    # ======================================================
    # RULE 6 — NORMAL OPERATION
    # ======================================================

    else:

        action = "No change"

        reason = "Comfort and IAQ within limits"


    return (
        optimized_hvac,
        optimized_lighting,
        action,
        reason
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("Loading building data...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Records loaded: {len(df)}"
    )


    # ======================================================
    # BUILDING POWER
    # ======================================================

    building_power = (
        df.groupby("timestamp")["total_power_kw"]
        .sum()
    )


    # ======================================================
    # DEFINE HIGH DEMAND
    # ======================================================

    demand_threshold = building_power.quantile(
        0.80
    )


    print(
        f"High-demand threshold: "
        f"{demand_threshold:.2f} kW"
    )


    # ======================================================
    # OPTIMIZE EACH ROOM
    # ======================================================

    optimized_hvac = []

    optimized_lighting = []

    actions = []

    reasons = []


    for index, row in df.iterrows():

        current_building_power = (
            building_power[row["timestamp"]]
        )

        high_demand = (
            current_building_power
            >= demand_threshold
        )


        hvac, lighting, action, reason = (
            optimize_room(
                row,
                high_demand
            )
        )


        optimized_hvac.append(hvac)

        optimized_lighting.append(lighting)

        actions.append(action)

        reasons.append(reason)


    # ======================================================
    # ADD RESULTS
    # ======================================================

    df["optimized_hvac_kw"] = optimized_hvac

    df["optimized_lighting_kw"] = optimized_lighting

    df["optimization_action"] = actions

    df["optimization_reason"] = reasons


    # ======================================================
    # CALCULATE OPTIMIZED POWER
    # ======================================================

    df["optimized_total_power_kw"] = (
        df["optimized_hvac_kw"]
        + df["optimized_lighting_kw"]
        + df["equipment_kw"]
    )


    # ======================================================
    # ENERGY SAVINGS
    # ======================================================

    df["power_saving_kw"] = (
        df["total_power_kw"]
        - df["optimized_total_power_kw"]
    )


    # ======================================================
    # SAVE RESULTS
    # ======================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    # ======================================================
    # SUMMARY
    # ======================================================

    original_power = (
        df["total_power_kw"].sum()
    )

    optimized_power = (
        df["optimized_total_power_kw"].sum()
    )

    savings = (
        original_power
        - optimized_power
    )

    savings_percentage = (
        savings / original_power
    ) * 100


    print("\nOPTIMIZATION RESULTS")
    print("--------------------")

    print(
        f"Original power total: "
        f"{original_power:.2f} kW"
    )

    print(
        f"Optimized power total: "
        f"{optimized_power:.2f} kW"
    )

    print(
        f"Power reduction: "
        f"{savings:.2f} kW"
    )

    print(
        f"Reduction percentage: "
        f"{savings_percentage:.2f}%"
    )


    print("\nACTIONS")

    print(
        df["optimization_action"]
        .value_counts()
    )


    print(
        f"\nResults saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()