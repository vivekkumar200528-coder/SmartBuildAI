import random

from building import create_rooms


# =========================================================
# OCCUPANCY
# =========================================================

def generate_occupancy(room, hour):

    room_type = room["room_type"]

    # Building closed
    if hour < 7 or hour >= 19:
        occupancy = 0

    # Morning arrival
    elif 7 <= hour < 9:

        if room_type == "office":
            occupancy = random.randint(2, 10)

        elif room_type == "meeting":
            occupancy = random.randint(0, 6)

        else:
            occupancy = random.randint(1, 8)

    # Morning working period
    elif 9 <= hour < 13:

        if room_type == "office":
            occupancy = random.randint(8, 18)

        elif room_type == "meeting":
            occupancy = random.randint(2, 12)

        else:
            occupancy = random.randint(4, 16)

    # Lunch period
    elif 13 <= hour < 14:

        if room_type == "office":
            occupancy = random.randint(2, 10)

        elif room_type == "meeting":
            occupancy = random.randint(0, 5)

        else:
            occupancy = random.randint(1, 8)

    # Afternoon working period
    elif 14 <= hour < 17:

        if room_type == "office":
            occupancy = random.randint(7, 18)

        elif room_type == "meeting":
            occupancy = random.randint(1, 10)

        else:
            occupancy = random.randint(4, 16)

    # Evening
    else:
        occupancy = random.randint(0, 3)

    return occupancy


# =========================================================
# TEMPERATURE
# =========================================================

def generate_temperature(occupancy, hour):

    # Base indoor temperature
    base_temperature = 23.0

    # Occupants generate heat
    occupancy_effect = occupancy * 0.035

    # Daytime heat gain
    if 10 <= hour <= 17:
        time_effect = 1.0

    elif 8 <= hour < 10:
        time_effect = 0.5

    else:
        time_effect = 0.2

    # Small environmental variation
    random_effect = random.uniform(
        -0.25,
        0.25
    )

    temperature = (
        base_temperature
        + occupancy_effect
        + time_effect
        + random_effect
    )

    return round(
        temperature,
        2
    )


# =========================================================
# HUMIDITY
# =========================================================

def generate_humidity(hour):

    if 10 <= hour <= 17:
        base_humidity = 50

    elif 7 <= hour < 10:
        base_humidity = 53

    else:
        base_humidity = 55

    variation = random.uniform(
        -3,
        3
    )

    humidity = (
        base_humidity
        + variation
    )

    return round(
        humidity,
        2
    )


# =========================================================
# CO2
# =========================================================

def generate_co2(occupancy):

    # Outdoor / background CO2
    base_co2 = 420

    # Each occupant contributes CO2
    co2_per_person = 28

    variation = random.uniform(
        -15,
        15
    )

    co2 = (
        base_co2
        + occupancy * co2_per_person
        + variation
    )

    return round(
        max(co2, 400),
        2
    )


# =========================================================
# LIGHTING POWER
# =========================================================

def generate_lighting_power(
    occupancy,
    hour
):

    # Daylight reduces artificial lighting demand
    if 9 <= hour <= 16:

        daylight_factor = 0.5

    elif 7 <= hour < 9:

        daylight_factor = 0.75

    else:

        daylight_factor = 1.0


    # Occupied room
    if occupancy > 0:

        lighting_power = (
            0.8 * daylight_factor
        )

    # Unoccupied room
    else:

        # Small standby/security lighting
        lighting_power = 0.05


    return round(
        lighting_power,
        2
    )


# =========================================================
# HVAC POWER
# =========================================================

def generate_hvac_power(
    occupancy,
    temperature
):

    # Minimum HVAC operation
    base_hvac = 0.5

    # Occupancy creates cooling load
    occupancy_load = (
        occupancy * 0.07
    )

    # HVAC responds when temperature rises
    temperature_load = max(
        temperature - 23.5,
        0
    ) * 0.8


    hvac_power = (
        base_hvac
        + occupancy_load
        + temperature_load
    )


    # If building is completely empty,
    # HVAC demand should be much lower.
    if occupancy == 0:

        hvac_power = 0.15


    return round(
        hvac_power,
        2
    )


# =========================================================
# EQUIPMENT POWER
# =========================================================

def generate_equipment_power(room):

    room_type = room["room_type"]


    if room_type == "lab":

        base_power = 1.5

    elif room_type == "office":

        base_power = 1.0

    else:

        base_power = 0.6


    variation = random.uniform(
        -0.15,
        0.15
    )


    power = max(
        base_power + variation,
        0.1
    )


    return round(
        power,
        2
    )


# =========================================================
# TOTAL POWER
# =========================================================

def calculate_total_power(
    hvac_power,
    lighting_power,
    equipment_power
):

    total_power = (
        hvac_power
        + lighting_power
        + equipment_power
    )

    return round(
        total_power,
        2
    )


# =========================================================
# COMPLETE SENSOR READING
# =========================================================

def generate_sensor_reading(
    room,
    hour
):

    # -----------------------------------------------------
    # 1. Occupancy
    # -----------------------------------------------------

    occupancy = generate_occupancy(
        room,
        hour
    )


    # -----------------------------------------------------
    # 2. Temperature
    # -----------------------------------------------------

    temperature = generate_temperature(
        occupancy,
        hour
    )


    # -----------------------------------------------------
    # 3. Humidity
    # -----------------------------------------------------

    humidity = generate_humidity(
        hour
    )


    # -----------------------------------------------------
    # 4. CO2
    # -----------------------------------------------------

    co2 = generate_co2(
        occupancy
    )


    # -----------------------------------------------------
    # 5. Lighting
    # -----------------------------------------------------

    lighting_power = generate_lighting_power(
        occupancy,
        hour
    )


    # -----------------------------------------------------
    # 6. HVAC
    # -----------------------------------------------------

    hvac_power = generate_hvac_power(
        occupancy,
        temperature
    )


    # -----------------------------------------------------
    # 7. Equipment
    # -----------------------------------------------------

    equipment_power = generate_equipment_power(
        room
    )


    # -----------------------------------------------------
    # 8. Total Power
    # -----------------------------------------------------

    total_power = calculate_total_power(
        hvac_power,
        lighting_power,
        equipment_power
    )


    # -----------------------------------------------------
    # RETURN SENSOR DATA
    # -----------------------------------------------------

    return {

        "room_id":
            room["room_id"],

        "floor":
            room["floor"],

        "room_type":
            room["room_type"],

        "occupancy":
            occupancy,

        "temperature_c":
            temperature,

        "humidity_percent":
            humidity,

        "co2_ppm":
            co2,

        "hvac_kw":
            hvac_power,

        "lighting_kw":
            lighting_power,

        "equipment_kw":
            equipment_power,

        "total_power_kw":
            total_power
    }


# =========================================================
# TEST SENSOR
# =========================================================

if __name__ == "__main__":

    rooms = create_rooms()

    room = rooms[0]

    reading = generate_sensor_reading(
        room,
        10
    )

    print(
        "Virtual Sensor Reading"
    )

    print(
        "----------------------"
    )

    for key, value in reading.items():

        print(
            f"{key}: {value}"
        )