import pandas as pd
import random


INPUT_FILE = "data/virtual_building_data.csv"
OUTPUT_FILE = "data/virtual_building_data_with_anomalies.csv"


def inject_hvac_anomalies(df, percentage=0.01):
    """
    Increase HVAC power for a small number of records.
    """

    number_of_records = int(len(df) * percentage)

    indexes = random.sample(
        list(df.index),
        number_of_records
    )

    df.loc[indexes, "hvac_kw"] *= 2.5

    return df, indexes


def inject_occupancy_anomalies(df, percentage=0.005):
    """
    Create unusual occupancy during normally inactive hours.
    """

    number_of_records = int(len(df) * percentage)

    night_data = df[
        (pd.to_datetime(df["timestamp"]).dt.hour < 7) |
        (pd.to_datetime(df["timestamp"]).dt.hour >= 19)
    ]

    indexes = random.sample(
        list(night_data.index),
        min(number_of_records, len(night_data))
    )

    for index in indexes:
        df.loc[index, "occupancy"] = random.randint(10, 18)

    return df, indexes


def inject_equipment_anomalies(df, percentage=0.005):
    """
    Create unusually high equipment power.
    """

    number_of_records = int(len(df) * percentage)

    indexes = random.sample(
        list(df.index),
        number_of_records
    )

    df.loc[indexes, "equipment_kw"] *= 3

    return df, indexes


def recalculate_total_power(df):
    """
    Recalculate total power after injecting anomalies.
    """

    df["total_power_kw"] = (
        df["hvac_kw"]
        + df["lighting_kw"]
        + df["equipment_kw"]
    )

    return df


def main():

    print("Loading virtual building dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Original records: {len(df)}")

    # Inject HVAC anomalies
    df, hvac_indexes = inject_hvac_anomalies(df)

    # Inject occupancy anomalies
    df, occupancy_indexes = inject_occupancy_anomalies(df)

    # Inject equipment anomalies
    df, equipment_indexes = inject_equipment_anomalies(df)

    # Recalculate total power
    df = recalculate_total_power(df)

    # Save dataset
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nAnomalies injected successfully.")

    print(
        f"HVAC anomalies: "
        f"{len(hvac_indexes)}"
    )

    print(
        f"Occupancy anomalies: "
        f"{len(occupancy_indexes)}"
    )

    print(
        f"Equipment anomalies: "
        f"{len(equipment_indexes)}"
    )

    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()