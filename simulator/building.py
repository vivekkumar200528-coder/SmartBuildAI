BUILDING = {
    "name": "SmartBuild Office",
    "building_type": "Commercial Office",
    "floors": 3,
    "rooms_per_floor": 5,
    "area_per_room_m2": 200
}


ROOM_TYPES = {
    "office": {
        "max_occupancy": 18
    },

    "meeting": {
        "max_occupancy": 12
    },

    "lab": {
        "max_occupancy": 16
    }
}


def create_rooms():

    rooms = []

    room_types = [
        "office",
        "office",
        "meeting",
        "lab",
        "office"
    ]

    for floor in range(1, BUILDING["floors"] + 1):

        for room_number in range(
            1,
            BUILDING["rooms_per_floor"] + 1
        ):

            room = {
                "room_id": f"F{floor}-R{room_number}",
                "floor": floor,
                "room_number": room_number,
                "room_type": room_types[room_number - 1],
                "area_m2": BUILDING["area_per_room_m2"]
            }

            rooms.append(room)

    return rooms


if __name__ == "__main__":

    rooms = create_rooms()

    print("BUILDING")
    print("--------")

    print(f"Name: {BUILDING['name']}")
    print(f"Type: {BUILDING['building_type']}")
    print(f"Floors: {BUILDING['floors']}")
    print(f"Total rooms: {len(rooms)}")

    print("\nROOMS")
    print("-----")

    for room in rooms:
        print(room)