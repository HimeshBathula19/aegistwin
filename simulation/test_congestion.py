from congestion import calculate_congestion


def test_low_congestion():

    result = calculate_congestion(
        location="corridor_c",
        occupancy=20,
        capacity=100,
    )

    assert result.level == "LOW"
    assert result.penalty == 1.0


def test_moderate_congestion():

    result = calculate_congestion(
        location="corridor_c",
        occupancy=60,
        capacity=100,
    )

    assert result.level == "MODERATE"
    assert result.penalty == 1.15


def test_high_congestion():

    result = calculate_congestion(
        location="corridor_c",
        occupancy=90,
        capacity=100,
    )

    assert result.level == "HIGH"
    assert result.penalty == 1.35


def test_critical_congestion():

    result = calculate_congestion(
        location="corridor_c",
        occupancy=150,
        capacity=100,
    )

    assert result.level == "CRITICAL"
    assert result.penalty == 1.75


if __name__ == "__main__":

    test_low_congestion()
    test_moderate_congestion()
    test_high_congestion()
    test_critical_congestion()

    print("All congestion tests passed.")