class LivePerformanceMetrics:
    """
    Calculates system-level performance metrics for one or more
    live SmartBuild AI simulation cycles.

    Metrics are derived from the actual current and optimized
    simulation values rather than fixed/demo percentages.
    """

    def __init__(self):
        self.current_power_history = []
        self.optimized_power_history = []
        self.energy_saved_kwh = 0.0
        self.cycles = 0

    def calculate(self, rooms, optimization, anomalies, control, verification):
        self.cycles += 1

        current_power = float(optimization.get("current_power_kw", 0))
        optimized_power = float(optimization.get("optimized_power_kw", 0))
        power_saved = max(current_power - optimized_power, 0)

        # Each live cycle represents 15 minutes.
        self.energy_saved_kwh += power_saved * 0.25

        self.current_power_history.append(current_power)
        self.optimized_power_history.append(optimized_power)

        if len(self.current_power_history) > 96:
            self.current_power_history.pop(0)
        if len(self.optimized_power_history) > 96:
            self.optimized_power_history.pop(0)

        total_rooms = len(rooms)

        comfort_ok = 0
        co2_ok = 0

        for room in rooms:
            temperature = float(room.get("temperature_c", 0))
            co2 = float(room.get("co2_ppm", 0))

            if 22.0 <= temperature <= 26.0:
                comfort_ok += 1

            if co2 <= 1000:
                co2_ok += 1

        comfort_compliance = (
            comfort_ok / total_rooms * 100
            if total_rooms else 0
        )
        co2_compliance = (
            co2_ok / total_rooms * 100
            if total_rooms else 0
        )

        overall_compliance = (
            sum(
                1
                for room in rooms
                if (
                    22.0 <= float(room.get("temperature_c", 0)) <= 26.0
                    and float(room.get("co2_ppm", 0)) <= 1000
                )
            )
            / total_rooms
            * 100
            if total_rooms else 0
        )

        optimized_rooms = sum(
            1
            for room in verification.get("rooms", [])
            if float(room.get("optimized_power_kw", 0))
            < float(room.get("current_power_kw", 0))
        )

        control_actions = sum(
            len(room.get("commands", []))
            for room in control.get("rooms", [])
        )

        peak_current = max(self.current_power_history, default=current_power)
        peak_optimized = max(
            self.optimized_power_history,
            default=optimized_power
        )

        return {
            "cycles_completed": self.cycles,
            "current_power_kw": round(current_power, 2),
            "optimized_power_kw": round(optimized_power, 2),
            "power_saved_kw": round(power_saved, 2),
            "saving_percentage": round(
                power_saved / current_power * 100
                if current_power > 0 else 0,
                2
            ),
            "peak_current_power_kw": round(peak_current, 2),
            "peak_optimized_power_kw": round(peak_optimized, 2),
            "peak_demand_reduction_kw": round(
                max(peak_current - peak_optimized, 0),
                2
            ),
            "cumulative_energy_saved_kwh": round(
                self.energy_saved_kwh,
                3
            ),
            "anomaly_count": int(
                anomalies.get("total_anomalies", 0)
            ),
            "optimized_rooms": optimized_rooms,
            "control_actions": control_actions,
            "comfort_compliance_percentage": round(
                comfort_compliance,
                2
            ),
            "co2_compliance_percentage": round(
                co2_compliance,
                2
            ),
            "overall_compliance_percentage": round(
                overall_compliance,
                2
            ),
            "total_rooms": total_rooms,
        }
