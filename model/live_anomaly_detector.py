import pandas as pd


class LiveAnomalyDetector:

    def __init__(self):

        self.co2_limit = 1000

        self.high_temperature_limit = 26

        self.high_power_limit = 8

        self.empty_room_power_limit = 2.5


    def detect_room_anomaly(self, room):

        reasons = []


        occupancy = float(
            room.get("occupancy", 0)
        )

        temperature = float(
            room.get("temperature_c", 0)
        )

        co2 = float(
            room.get("co2_ppm", 0)
        )

        hvac = float(
            room.get("hvac_kw", 0)
        )

        total_power = float(
            room.get("total_power_kw", 0)
        )


        # =====================================================
        # RULE 1 — HIGH CO2
        # =====================================================

        if co2 > self.co2_limit:

            reasons.append(
                "High CO2 level"
            )


        # =====================================================
        # RULE 2 — HIGH TEMPERATURE
        # =====================================================

        if temperature > self.high_temperature_limit:

            reasons.append(
                "High temperature"
            )


        # =====================================================
        # RULE 3 — HIGH POWER
        # =====================================================

        if total_power > self.high_power_limit:

            reasons.append(
                "High energy consumption"
            )


        # =====================================================
        # RULE 4 — EMPTY ROOM BUT HIGH POWER
        # =====================================================

        if (
            occupancy == 0
            and total_power > self.empty_room_power_limit
        ):

            reasons.append(
                "Energy consumption in unoccupied room"
            )


        # =====================================================
        # RULE 5 — HIGH TEMPERATURE + HIGH HVAC
        # =====================================================

        if (
            temperature > self.high_temperature_limit
            and hvac > 2.0
        ):

            reasons.append(
                "High HVAC demand"
            )


        # =====================================================
        # FINAL STATUS
        # =====================================================

        if reasons:

            status = "Anomaly"

        else:

            status = "Normal"


        return {

            "room_id":
                room.get("room_id"),

            "floor":
                room.get("floor"),

            "room_type":
                room.get("room_type"),

            "occupancy":
                occupancy,

            "temperature_c":
                temperature,

            "co2_ppm":
                co2,

            "hvac_kw":
                hvac,

            "total_power_kw":
                total_power,

            "status":
                status,

            "reasons":
                reasons
        }


    def detect_building_anomalies(
        self,
        rooms
    ):

        results = []

        for room in rooms:

            result = self.detect_room_anomaly(
                room
            )

            results.append(
                result
            )


        anomalies = [
            room
            for room in results
            if room["status"] == "Anomaly"
        ]


        return {

            "total_rooms":
                len(results),

            "total_anomalies":
                len(anomalies),

            "normal_rooms":
                len(results) - len(anomalies),

            "anomalies":
                anomalies,

            "rooms":
                results
        }