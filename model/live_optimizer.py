class LiveOptimizer:

    def __init__(self):

        # Comfort limits
        self.min_temperature = 22.0
        self.max_temperature = 26.0

        # CO2 comfort threshold
        self.max_co2 = 1000


    def optimize_room(self, room):

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

        lighting = float(
            room.get("lighting_kw", 0)
        )

        equipment = float(
            room.get("equipment_kw", 0)
        )

        current_power = float(
            room.get("total_power_kw", 0)
        )


        # Start with current values
        optimized_hvac = hvac
        optimized_lighting = lighting

        actions = []


        # =====================================================
        # RULE 1 — EMPTY ROOM
        # =====================================================

        if occupancy == 0:

            optimized_hvac = min(
                hvac,
                0.15
            )

            optimized_lighting = min(
                lighting,
                0.05
            )

            actions.append(
                "Reduce HVAC and lighting for unoccupied room"
            )


        # =====================================================
        # RULE 2 — HIGH TEMPERATURE
        # =====================================================

        elif temperature > self.max_temperature:

            optimized_hvac = hvac

            actions.append(
                "Maintain/increase HVAC for temperature control"
            )


        # =====================================================
        # RULE 3 — LOW TEMPERATURE
        # =====================================================

        elif temperature < self.min_temperature:

            optimized_hvac = max(
                hvac * 0.8,
                0.15
            )

            actions.append(
                "Reduce HVAC demand"
            )


        # =====================================================
        # RULE 4 — NORMAL TEMPERATURE
        # =====================================================

        else:

            optimized_hvac = max(
                hvac * 0.85,
                0.15
            )

            actions.append(
                "Optimize HVAC within comfort range"
            )


        # =====================================================
        # RULE 5 — HIGH CO2
        # =====================================================

        if co2 > self.max_co2:

            actions.append(
                "Maintain ventilation due to high CO2"
            )


        # =====================================================
        # LIGHTING OPTIMIZATION
        # =====================================================

        if occupancy == 0:

            optimized_lighting = 0.05

        else:

            optimized_lighting = lighting


        # =====================================================
        # CALCULATE OPTIMIZED POWER
        # =====================================================

        optimized_power = (
            optimized_hvac
            + optimized_lighting
            + equipment
        )

        optimized_power = round(
            optimized_power,
            2
        )


        power_saved = (
            current_power
            - optimized_power
        )

        power_saved = round(
            max(power_saved, 0),
            2
        )


        # =====================================================
        # CONTROL MODE
        # =====================================================

        if occupancy == 0:

            control_mode = "Energy Saving"

        elif temperature > self.max_temperature:

            control_mode = "Comfort Protection"

        elif co2 > self.max_co2:

            control_mode = "IAQ Protection"

        else:

            control_mode = "Optimized"


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

            "current_power_kw":
                round(
                    current_power,
                    2
                ),

            "optimized_hvac_kw":
                round(
                    optimized_hvac,
                    2
                ),

            "optimized_lighting_kw":
                round(
                    optimized_lighting,
                    2
                ),

            "equipment_kw":
                round(
                    equipment,
                    2
                ),

            "optimized_power_kw":
                optimized_power,

            "power_saved_kw":
                power_saved,

            "control_mode":
                control_mode,

            "actions":
                actions
        }


    def optimize_building(self, rooms):

        results = []

        for room in rooms:

            result = self.optimize_room(
                room
            )

            results.append(
                result
            )


        current_total = round(
            sum(
                room["current_power_kw"]
                for room in results
            ),
            2
        )


        optimized_total = round(
            sum(
                room["optimized_power_kw"]
                for room in results
            ),
            2
        )


        total_saved = round(
            max(
                current_total -
                optimized_total,
                0
            ),
            2
        )


        saving_percentage = (
            total_saved /
            current_total *
            100
            if current_total > 0
            else 0
        )


        return {

            "total_rooms":
                len(results),

            "current_power_kw":
                current_total,

            "optimized_power_kw":
                optimized_total,

            "power_saved_kw":
                total_saved,

            "saving_percentage":
                round(
                    saving_percentage,
                    2
                ),

            "rooms":
                results
        }