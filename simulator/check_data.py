import pandas as pd


# Load dataset
df = pd.read_csv("data/virtual_building_data.csv")


print("\nDATASET OVERVIEW")
print("----------------")

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print(f"Number of rooms: {df['room_id'].nunique()}")

print(
    f"Start time: {df['timestamp'].min()}"
)

print(
    f"End time: {df['timestamp'].max()}"
)


print("\nAVERAGE VALUES")
print("--------------")

print(
    f"Average occupancy: "
    f"{df['occupancy'].mean():.2f}"
)

print(
    f"Average temperature: "
    f"{df['temperature_c'].mean():.2f} °C"
)

print(
    f"Average humidity: "
    f"{df['humidity_percent'].mean():.2f} %"
)

print(
    f"Average CO2: "
    f"{df['co2_ppm'].mean():.2f} ppm"
)

print(
    f"Average total power: "
    f"{df['total_power_kw'].mean():.2f} kW"
)


print("\nMAXIMUM VALUES")
print("--------------")

print(
    f"Maximum occupancy: "
    f"{df['occupancy'].max()}"
)

print(
    f"Maximum temperature: "
    f"{df['temperature_c'].max():.2f} °C"
)

print(
    f"Maximum CO2: "
    f"{df['co2_ppm'].max():.2f} ppm"
)

print(
    f"Maximum total power: "
    f"{df['total_power_kw'].max():.2f} kW"
)


print("\nROOM TYPES")
print("----------")

print(
    df["room_type"].value_counts()
)


print("\nMISSING VALUES")
print("--------------")

print(
    df.isnull().sum()
)


print("\nFIRST 5 RECORDS")
print("----------------")

print(
    df.head()
)