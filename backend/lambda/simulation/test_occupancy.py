from occupancy import count_edge_occupancy


def test_edge_occupancy():

    routes = [
        [
            "room_a",
            "corridor_a",
            "exit_a",
        ],

        [
            "room_b",
            "corridor_a",
            "exit_a",
        ],

        [
            "room_c",
            "corridor_b",
            "exit_b",
        ],
    ]

    occupancy = count_edge_occupancy(routes)

    assert occupancy[
        ("room_a", "corridor_a")
    ] == 1

    assert occupancy[
        ("room_b", "corridor_a")
    ] == 1

    assert occupancy[
        ("corridor_a", "exit_a")
    ] == 2

    assert occupancy[
        ("corridor_b", "exit_b")
    ] == 1


if __name__ == "__main__":

    test_edge_occupancy()

    print(
        "All occupancy tests passed."
    )