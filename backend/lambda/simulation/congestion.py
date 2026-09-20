from dataclasses import dataclass


@dataclass
class CongestionResult:
    """
    Describes congestion on one infrastructure segment.
    """

    location: str
    occupancy: int
    capacity: int
    utilization: float
    level: str
    penalty: float


def calculate_congestion(
    location: str,
    occupancy: int,
    capacity: int,
) -> CongestionResult:
    """
    Calculate congestion based on occupancy vs capacity.

    Utilization:
        occupancy / capacity

    Penalty:
        Additional travel-time multiplier caused by crowding.
    """

    if capacity <= 0:
        raise ValueError(
            "Capacity must be greater than zero."
        )

    utilization = occupancy / capacity

    if utilization < 0.50:
        level = "LOW"
        penalty = 1.0

    elif utilization < 0.80:
        level = "MODERATE"
        penalty = 1.15

    elif utilization < 1.00:
        level = "HIGH"
        penalty = 1.35

    else:
        level = "CRITICAL"
        penalty = 1.75

    return CongestionResult(
        location=location,
        occupancy=occupancy,
        capacity=capacity,
        utilization=round(utilization, 3),
        level=level,
        penalty=penalty,
    )


def print_congestion(result: CongestionResult):

    percentage = result.utilization * 100

    print(
        f"{result.location:18} "
        f"{result.occupancy:4}/{result.capacity:<4} "
        f"{percentage:6.1f}% "
        f"{result.level:10} "
        f"x{result.penalty:.2f}"
    )