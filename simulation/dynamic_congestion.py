from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class CongestionResult:
    location: str
    occupancy: int
    capacity: int
    utilization: float
    level: str
    penalty: float


def classify_congestion(utilization: float) -> Tuple[str, float]:
    """
    Convert utilization into a congestion level.

    utilization:
        0.0 = empty
        1.0 = 100% utilized
        >1.0 = overloaded
    """

    if utilization < 0.50:
        return "LOW", 1.00

    if utilization < 0.75:
        return "MODERATE", 1.15

    if utilization < 1.00:
        return "HIGH", 1.40

    return "CRITICAL", 1.75


def calculate_congestion(
    occupancy: Dict[str, int],
    capacities: Dict[str, int],
):
    """
    Calculate congestion from simulated occupancy
    and infrastructure capacity.
    """

    results = []

    for location, capacity in capacities.items():

        current_occupancy = occupancy.get(
            location,
            0,
        )

        if capacity <= 0:
            utilization = 1.0

        else:
            utilization = (
                current_occupancy / capacity
            )

        level, penalty = classify_congestion(
            utilization
        )

        results.append(
            CongestionResult(
                location=location,
                occupancy=current_occupancy,
                capacity=capacity,
                utilization=utilization,
                level=level,
                penalty=penalty,
            )
        )

    return results


def print_congestion_report(results):

    print()
    print("=" * 75)
    print("AEGISTWIN AUTOMATIC CONGESTION ANALYSIS")
    print("=" * 75)

    print(
        f"{'LOCATION':20}"
        f"{'LOAD':>10}"
        f"{'CAPACITY':>12}"
        f"{'UTILIZATION':>15}"
        f"{'LEVEL':>12}"
    )

    print("-" * 75)

    for result in results:

        percentage = (
            result.utilization * 100
        )

        print(
            f"{result.location:20}"
            f"{result.occupancy:>10}"
            f"{result.capacity:>12}"
            f"{percentage:>14.1f}%"
            f"{result.level:>12}"
        )

    critical = [
        result
        for result in results
        if result.level == "CRITICAL"
    ]

    high = [
        result
        for result in results
        if result.level == "HIGH"
    ]

    print()
    print(
        f"Critical locations : {len(critical)}"
    )

    print(
        f"High-risk locations: {len(high)}"
    )