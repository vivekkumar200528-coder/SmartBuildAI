import pandas as pd


INPUT_FILE = "data/optimization_results.csv"

OUTPUT_FILE = "data/control_results.csv"


# ==========================================================
# CONTROL FUNCTION
# ==========================================================

def determine_control(row):

    occupancy = row["occupancy"]
    temperature = row["temperature_c"]
    co2 = row["co2_ppm"]

    optimized_hvac = row["optimized_hvac_kw"]
    optimized_lighting = row["optimized_lighting_kw"]

    # ------------------------------------------------------
    # PRIORITY 1: IAQ PROTECTION
    # ------------------------------------------------------

    if co2 > 1000:

        hvac_command = 100
        lighting_command = 100

        system_mode = "IAQ Protection"

        message = "Increase ventilation because CO2 is high"


    # ------------------------------------------------------
    # PRIORITY 2: HIGH TEMPERATURE
    # ------------------------------------------------------

    elif temperature > 26:

        hvac_command = 100
        lighting_command = 100

        system_mode = "Cooling"

        message = "Increase HVAC because temperature is high"


    # ------------------------------------------------------
    # PRIORITY 3: EMPTY ROOM
    # ------------------------------------------------------

    elif occupancy == 0:

        hvac_command = 40
        lighting_command = 10

        system_mode = "Energy Saving"

        message = "Room unoccupied"


    # ------------------------------------------------------
    # PRIORITY 4: NORMAL OCCUPIED ROOM
    # ------------------------------------------------------

    else:

        hvac_command = 80
        lighting_command = 100

        system_mode = "Normal"

        message = "Room operating normally"


    return (
        hvac_command,
        lighting_command,
        system_mode,
        message
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("Loading optimization results...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Records loaded: {len(df)}"
    )


    # ======================================================
    # GENERATE CONTROL COMMANDS
    # ======================================================

    hvac_commands = []

    lighting_commands = []

    modes = []

    messages = []


    for _, row in df.iterrows():

        (
            hvac,
            lighting,
            mode,
            message
        ) = determine_control(row)


        hvac_commands.append(hvac)

        lighting_commands.append(lighting)

        modes.append(mode)

        messages.append(message)


    # ======================================================
    # ADD CONTROL RESULTS
    # ======================================================

    df["hvac_command_percent"] = hvac_commands

    df["lighting_command_percent"] = lighting_commands

    df["control_mode"] = modes

    df["control_message"] = messages


    # ======================================================
    # SAVE RESULTS
    # ======================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    # ======================================================
    # DISPLAY SUMMARY
    # ======================================================

    print("\nCONTROL SUMMARY")
    print("---------------")

    print(
        df["control_mode"]
        .value_counts()
    )


    print(
        f"\nResults saved to: "
        f"{OUTPUT_FILE}"
    )


    # ======================================================
    # SHOW EXAMPLES
    # ======================================================

    print("\nSAMPLE CONTROL ACTIONS")
    print("----------------------")

    print(
        df[
            [
                "timestamp",
                "room_id",
                "occupancy",
                "temperature_c",
                "co2_ppm",
                "hvac_command_percent",
                "lighting_command_percent",
                "control_mode",
                "control_message"
            ]
        ].head(10)
    )


if __name__ == "__main__":
    main()