import pandas as pd
from datetime import datetime, timedelta

from building import create_rooms
from sensors import generate_sensor_reading


START_DATE = datetime(2026, 1, 5, 0, 0)

DAYS = 7

INTERVAL_MINUTES = 15


def generate_dataset():

    rooms = create_rooms()

    records = []

    current_time = START_DATE

    end_time = START_DATE + timedelta(
        days=DAYS
    )

    while current_time < end_time:

        hour = current_time.hour + (
            current_time.minute / 60
        )

        for room in rooms:

            reading = generate_sensor_reading(
                room,
                hour
            )

            reading["timestamp"] = current_time

            records.append(reading)

        current_time += timedelta(
            minutes=INTERVAL_MINUTES
        )

    return pd.DataFrame(records)


def main():

    print(
        "Generating virtual building data..."
    )

    df = generate_dataset()

    df = df.sort_values(
        ["timestamp", "room_id"]
    )

    output_file = (
        "data/virtual_building_data.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        "\nDataset generated successfully."
    )

    print(
        f"Total records: {len(df)}"
    )

    print(
        f"Number of rooms: "
        f"{df['room_id'].nunique()}"
    )

    print(
        f"Start time: "
        f"{df['timestamp'].min()}"
    )

    print(
        f"End time: "
        f"{df['timestamp'].max()}"
    )

    print(
        f"\nSaved to: {output_file}"
    )


if __name__ == "__main__":
    main()