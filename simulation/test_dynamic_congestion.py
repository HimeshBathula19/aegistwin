from dynamic_congestion import (
    calculate_congestion,
)


def test_congestion_levels():

    occupancy = {
        "corridor_a": 40,
        "corridor_b": 80,
        "corridor_c": 120,
    }

    capacities = {
        "corridor_a": 100,
        "corridor_b": 100,
        "corridor_c": 100,
    }

    results = calculate_congestion(
        occupancy,
        capacities,
    )

    levels = {
        result.location: result.level
        for result in results
    }

    assert levels["corridor_a"] == "LOW"

    assert levels["corridor_b"] == "HIGH"

    assert levels["corridor_c"] == "CRITICAL"


if __name__ == "__main__":

    test_congestion_levels()

    print(
        "All dynamic congestion tests passed."
    )