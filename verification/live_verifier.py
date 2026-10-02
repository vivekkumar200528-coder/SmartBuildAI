class LiveVerifier:

    def verify_room(self, room, control):
        current_power = float(room.get("total_power_kw", 0))

        optimized_hvac = float(
            control.get("optimized_hvac_kw", room.get("hvac_kw", 0))
        )

        optimized_lighting = float(
            control.get("optimized_lighting_kw", room.get("lighting_kw", 0))
        )

        equipment = float(room.get("equipment_kw", 0))

        optimized_power = (
            optimized_hvac
            + optimized_lighting
            + equipment
        )

        power_saved = max(
            current_power - optimized_power,
            0
        )

        saving_percentage = (
            (power_saved / current_power) * 100
            if current_power > 0
            else 0
        )

        return {
            "room_id": room.get("room_id"),
            "current_power_kw": round(current_power, 2),
            "optimized_power_kw": round(optimized_power, 2),
            "power_saved_kw": round(power_saved, 2),
            "saving_percentage": round(saving_percentage, 2),
            "verification_status": (
                "Improved"
                if optimized_power < current_power
                else "No Improvement"
            )
        }

    def verify_building(self, rooms, controls):

        control_map = {
            control["room_id"]: control
            for control in controls
        }

        results = []

        for room in rooms:

            room_id = room.get("room_id")

            control = control_map.get(
                room_id,
                {}
            )

            result = self.verify_room(
                room,
                control
            )

            results.append(result)

        current_total = sum(
            result["current_power_kw"]
            for result in results
        )

        optimized_total = sum(
            result["optimized_power_kw"]
            for result in results
        )

        power_saved = max(
            current_total - optimized_total,
            0
        )

        saving_percentage = (
            (power_saved / current_total) * 100
            if current_total > 0
            else 0
        )

        improved_rooms = sum(
            1
            for result in results
            if result["verification_status"] == "Improved"
        )

        return {
            "total_rooms": len(results),
            "improved_rooms": improved_rooms,
            "current_power_kw": round(
                current_total,
                2
            ),
            "optimized_power_kw": round(
                optimized_total,
                2
            ),
            "power_saved_kw": round(
                power_saved,
                2
            ),
            "saving_percentage": round(
                saving_percentage,
                2
            ),
            "rooms": results
        }