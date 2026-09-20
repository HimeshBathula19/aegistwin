from campus import create_campus
from congestion import calculate_congestion, print_congestion


def analyze_bottlenecks(campus, occupancy):
    """
    Analyze infrastructure occupancy and identify
    congested locations.
    """

    results = []

    for location, people in occupancy.items():

        if location not in campus:
            continue

        capacity = campus.nodes[location].get(
            "capacity",
            0,
        )

        if capacity <= 0:
            continue

        result = calculate_congestion(
            location=location,
            occupancy=people,
            capacity=capacity,
        )

        results.append(result)

    return results


def print_report(results):

    print()
    print("=" * 75)
    print("AEGISTWIN BOTTLENECK ANALYSIS")
    print("=" * 75)

    print()

    print(
        f"{'LOCATION':18}"
        f"{'LOAD':10}"
        f"{'UTILIZATION':13}"
        f"{'LEVEL':12}"
        f"{'PENALTY'}"
    )

    print("-" * 75)

    for result in results:
        print_congestion(result)

    print()

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

    moderate = [
        result
        for result in results
        if result.level == "MODERATE"
    ]

    print(
        f"Critical bottlenecks : {len(critical)}"
    )

    print(
        f"High-risk locations  : {len(high)}"
    )

    print(
        f"Moderate locations   : {len(moderate)}"
    )


if __name__ == "__main__":

    campus = create_campus()

    # Temporary synthetic occupancy.
    # This will later be generated automatically
    # from the agent simulation.

    occupancy = {
        "corridor_a": 45,
        "corridor_b": 75,
        "corridor_c": 130,
        "staircase_a": 62,
        "staircase_b": 25,
    }

    results = analyze_bottlenecks(
        campus,
        occupancy,
    )

    print_report(results)