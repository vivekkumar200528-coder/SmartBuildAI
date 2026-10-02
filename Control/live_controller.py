class LiveController:

    def __init__(self):
        self.min_temperature = 22.0
        self.max_temperature = 26.0
        self.max_co2 = 1000

    def control_room(self, room, optimized_room=None):

        room_id = room.get("room_id")

        occupancy = float(
            room.get("occupancy", 0)
        )

        temperature = float(
            room.get("temperature_c", 0)
        )

        co2 = float(
            room.get("co2_ppm", 0)
        )

        current_hvac = float(
            room.get("hvac_kw", 0)
        )

        current_lighting = float(
            room.get("lighting_kw", 0)
        )

        # -------------------------------------------------
        # Use optimizer output when available
        # -------------------------------------------------

        if optimized_room:

            optimized_hvac = float(
                optimized_room.get(
                    "optimized_hvac_kw",
                    current_hvac
                )
            )

            optimized_lighting = float(
                optimized_room.get(
                    "optimized_lighting_kw",
                    current_lighting
                )
            )

        else:

            optimized_hvac = current_hvac
            optimized_lighting = current_lighting

        commands = []

        # -------------------------------------------------
        # HVAC CONTROL
        # -------------------------------------------------

        if occupancy == 0:

            commands.append(
                "Set HVAC to standby"
            )

            hvac_command = "HVAC_STANDBY"

        elif temperature > self.max_temperature:

            commands.append(
                "Increase HVAC cooling"
            )

            hvac_command = "HVAC_COOLING"

        elif temperature < self.min_temperature:

            commands.append(
                "Reduce HVAC demand"
            )

            hvac_command = "HVAC_REDUCED"

        else:

            commands.append(
                "Apply optimized HVAC setting"
            )

            hvac_command = "HVAC_OPTIMIZED"

        # -------------------------------------------------
        # LIGHTING CONTROL
        # -------------------------------------------------

        if occupancy == 0:

            commands.append(
                "Turn lighting to standby"
            )

            lighting_command = "LIGHTING_STANDBY"

        elif optimized_lighting < current_lighting:

            commands.append(
                "Apply optimized lighting level"
            )

            lighting_command = "LIGHTING_OPTIMIZED"

        else:

            commands.append(
                "Maintain lighting"
            )

            lighting_command = "LIGHTING_ON"

        # -------------------------------------------------
        # VENTILATION CONTROL
        # -------------------------------------------------

        if co2 > self.max_co2:

            commands.append(
                "Increase ventilation"
            )

            ventilation_command = "VENTILATION_HIGH"

        else:

            commands.append(
                "Maintain ventilation"
            )

            ventilation_command = "VENTILATION_NORMAL"

        # -------------------------------------------------
        # CONTROL MODE
        # -------------------------------------------------

        if occupancy == 0:

            control_mode = "Energy Saving"

        elif temperature > self.max_temperature:

            control_mode = "Comfort Protection"

        elif co2 > self.max_co2:

            control_mode = "IAQ Protection"

        else:

            control_mode = "Optimized"

        return {

            "room_id": room_id,

            "control_mode": control_mode,

            "hvac_command": hvac_command,

            "lighting_command": lighting_command,

            "ventilation_command": ventilation_command,

            "optimized_hvac_kw": round(
                optimized_hvac,
                2
            ),

            "optimized_lighting_kw": round(
                optimized_lighting,
                2
            ),

            "commands": commands
        }

    def control_building(
        self,
        rooms,
        optimized_rooms=None
    ):

        optimized_map = {}

        if optimized_rooms:

            optimized_map = {
                room["room_id"]: room
                for room in optimized_rooms
            }

        results = []

        for room in rooms:

            room_id = room.get("room_id")

            optimized_room = optimized_map.get(
                room_id
            )

            result = self.control_room(
                room,
                optimized_room
            )

            results.append(result)

        return {

            "total_rooms": len(results),

            "controlled_rooms": len(results),

            "rooms": results
        }