from datetime import datetime, timedelta
from pathlib import Path
import sys
import pandas as pd

# ---------------------------------------------------------
# Allow this file to use building.py and sensors.py
# ---------------------------------------------------------

SIMULATOR_DIR = Path(__file__).resolve().parent

if str(SIMULATOR_DIR) not in sys.path:
    sys.path.insert(0, str(SIMULATOR_DIR))

from building import create_rooms
from sensors import generate_sensor_reading


# ---------------------------------------------------------
# Simulation configuration
# ---------------------------------------------------------

INTERVAL_MINUTES = 15

START_TIME = datetime(2026, 1, 5, 8, 0)


# ---------------------------------------------------------
# Live Simulator
# ---------------------------------------------------------

class LiveSimulator:

    def __init__(self):
        self.rooms = create_rooms()
        self.current_time = START_TIME

        # Store the latest generated records
        self.latest_records = []

    # -----------------------------------------------------
    # Generate one simulation step
    # -----------------------------------------------------

    def step(self):

        hour = (
            self.current_time.hour
            + self.current_time.minute / 60
        )

        records = []

        for room in self.rooms:

            reading = generate_sensor_reading(
                room,
                hour
            )

            reading["timestamp"] = self.current_time

            records.append(reading)

        self.latest_records = records

        # Move simulation time forward by 15 minutes
        self.current_time += timedelta(
            minutes=INTERVAL_MINUTES
        )

        return records

    # -----------------------------------------------------
    # Return latest records as DataFrame
    # -----------------------------------------------------

    def get_dataframe(self):

        return pd.DataFrame(
            self.latest_records
        )

    # -----------------------------------------------------
    # Return building-level summary
    # -----------------------------------------------------

    def get_building_summary(self):

        if not self.latest_records:
            self.step()

        df = self.get_dataframe()

        return {
            "timestamp": str(
                df["timestamp"].iloc[0]
            ),

            "occupancy": int(
                df["occupancy"].sum()
            ),

            "temperature_c": round(
                df["temperature_c"].mean(),
                2
            ),

            "humidity_percent": round(
                df["humidity_percent"].mean(),
                2
            ),

            "co2_ppm": round(
                df["co2_ppm"].mean(),
                2
            ),

            "current_power_kw": round(
                df["total_power_kw"].sum(),
                2
            )
        }

    # -----------------------------------------------------
    # Return room-level data
    # -----------------------------------------------------

    def get_rooms(self):

        if not self.latest_records:
            self.step()

        return self.latest_records


# ---------------------------------------------------------
# Standalone test
# ---------------------------------------------------------

if __name__ == "__main__":

    simulator = LiveSimulator()

    print()
    print("=" * 60)
    print("SMARTBUILD AI - LIVE VIRTUAL BUILDING SIMULATOR")
    print("=" * 60)

    for step_number in range(3):

        records = simulator.step()

        print()
        print(
            f"Simulation Step: {step_number + 1}"
        )

        print(
            f"Simulation Time: "
            f"{records[0]['timestamp']}"
        )

        print(
            f"Rooms Generated: "
            f"{len(records)}"
        )

        summary = simulator.get_building_summary()

        print(
            f"Occupancy: "
            f"{summary['occupancy']} people"
        )

        print(
            f"Temperature: "
            f"{summary['temperature_c']} °C"
        )

        print(
            f"CO2: "
            f"{summary['co2_ppm']} ppm"
        )

        print(
            f"Power: "
            f"{summary['current_power_kw']} kW"
        )

        print("-" * 60)