import pandas as pd
from sklearn.ensemble import RandomForestRegressor


class EnergyPredictionModel:

    def __init__(self):

        # Load historical building data
        self.input_file = "data/virtual_building_data.csv"

        df = pd.read_csv(self.input_file)

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Create building-level data
        building_data = (
            df.groupby("timestamp")
            .agg({
                "occupancy": "sum",
                "temperature_c": "mean",
                "humidity_percent": "mean",
                "co2_ppm": "mean",
                "hvac_kw": "sum",
                "lighting_kw": "sum",
                "equipment_kw": "sum",
                "total_power_kw": "sum"
            })
            .reset_index()
        )

        # Time features
        building_data["hour"] = (
            building_data["timestamp"].dt.hour
        )

        building_data["day_of_week"] = (
            building_data["timestamp"].dt.dayofweek
        )

        # Future power = next 15-minute power
        building_data["future_power_kw"] = (
            building_data["total_power_kw"].shift(-1)
        )

        building_data = building_data.dropna()

        # Same features as your existing model
        self.features = [
            "occupancy",
            "temperature_c",
            "humidity_percent",
            "co2_ppm",
            "hvac_kw",
            "lighting_kw",
            "equipment_kw",
            "total_power_kw",
            "hour",
            "day_of_week"
        ]

        X = building_data[self.features]

        y = building_data["future_power_kw"]

        # Same 80/20 time-based split
        split_index = int(len(building_data) * 0.8)

        X_train = X.iloc[:split_index]
        y_train = y.iloc[:split_index]

        # Create model
        self.model = RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        )

        # Train
        self.model.fit(
            X_train,
            y_train
        )

    def predict(self, live_features):

        input_data = pd.DataFrame(
            [live_features],
            columns=self.features
        )

        prediction = self.model.predict(
            input_data
        )

        return round(float(prediction[0]), 3)