import pandas as pd

from simulator.live_simulator import LiveSimulator
from model.energy_model import EnergyPredictionModel
from model.live_anomaly_detector import LiveAnomalyDetector
from model.live_optimizer import LiveOptimizer
from Control.live_controller import LiveController
from verification.live_verifier import LiveVerifier
from verification.live_metrics import LivePerformanceMetrics


class LiveBuildingLoop:
    """
    Complete SmartBuild AI live control loop:

    Sense -> Analyze -> Predict -> Optimize -> Control -> Verify -> Measure
    """

    def __init__(self):
        self.simulator = LiveSimulator()
        self.energy_model = EnergyPredictionModel()
        self.anomaly_detector = LiveAnomalyDetector()
        self.optimizer = LiveOptimizer()
        self.controller = LiveController()
        self.verifier = LiveVerifier()
        self.metrics = LivePerformanceMetrics()

    def step(self):
        # ---------------------------------------------------------
        # 1. SENSE
        # ---------------------------------------------------------
        rooms = self.simulator.step()
        summary = self.simulator.get_building_summary()

        total_occupancy = sum(
            float(room.get("occupancy", 0))
            for room in rooms
        )

        avg_temperature = (
            sum(float(room.get("temperature_c", 0)) for room in rooms)
            / len(rooms)
            if rooms else 0
        )

        avg_humidity = (
            sum(float(room.get("humidity_percent", 0)) for room in rooms)
            / len(rooms)
            if rooms else 0
        )

        avg_co2 = (
            sum(float(room.get("co2_ppm", 0)) for room in rooms)
            / len(rooms)
            if rooms else 0
        )

        hvac_power = sum(
            float(room.get("hvac_kw", 0))
            for room in rooms
        )

        lighting_power = sum(
            float(room.get("lighting_kw", 0))
            for room in rooms
        )

        equipment_power = sum(
            float(room.get("equipment_kw", 0))
            for room in rooms
        )

        current_power = sum(
            float(room.get("total_power_kw", 0))
            for room in rooms
        )

        # IMPORTANT:
        # LiveSimulator may return timestamp as a string.
        # Convert it to a real datetime before using .hour/.weekday().
        timestamp = pd.to_datetime(summary["timestamp"])

        # ---------------------------------------------------------
        # 2. PREDICT
        # ---------------------------------------------------------
        prediction_input = {
            "occupancy": total_occupancy,
            "temperature_c": avg_temperature,
            "humidity_percent": avg_humidity,
            "co2_ppm": avg_co2,
            "hvac_kw": hvac_power,
            "lighting_kw": lighting_power,
            "equipment_kw": equipment_power,
            "current_power_kw": current_power,
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
        }

        prediction = self.energy_model.predict(prediction_input)

        # ---------------------------------------------------------
        # 3. ANALYZE
        # ---------------------------------------------------------
        anomaly_result = (
            self.anomaly_detector
            .detect_building_anomalies(rooms)
        )

        # ---------------------------------------------------------
        # 4. OPTIMIZE
        # ---------------------------------------------------------
        optimization_result = (
            self.optimizer.optimize_building(rooms)
        )

        # ---------------------------------------------------------
        # 5. CONTROL
        # ---------------------------------------------------------
        control_result = self.controller.control_building(
            rooms,
            optimization_result["rooms"]
        )

        # ---------------------------------------------------------
        # 6. VERIFY
        # ---------------------------------------------------------
        verification_result = self.verifier.verify_building(
            rooms,
            control_result["rooms"]
        )

        # ---------------------------------------------------------
        # 7. SYSTEM PERFORMANCE METRICS
        # ---------------------------------------------------------
        performance_metrics = self.metrics.calculate(
            rooms=rooms,
            optimization=optimization_result,
            anomalies=anomaly_result,
            control=control_result,
            verification=verification_result,
        )

        return {
            "status": "success",
            "timestamp": str(timestamp),
            "summary": summary,
            "prediction": prediction,
            "anomalies": anomaly_result,
            "optimization": optimization_result,
            "control": control_result,
            "verification": verification_result,
            "metrics": performance_metrics,
            "rooms": rooms,
        }
