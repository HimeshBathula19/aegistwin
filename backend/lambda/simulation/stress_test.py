from collections import Counter

from campus import create_campus
from population import generate_population
from simulation import find_best_exit
from dynamic_congestion import (
    calculate_congestion,
    print_congestion_report,
)


def run_stress_test(population_size):

    print()
    print("=" * 75)
    print(
        f"AEGISTWIN STRESS TEST — "
        f"{population_size:,} SIMULATED OCCUPANTS"
    )
    print("=" * 75)

    campus = create_campus()

    exits = [
        "exit_a",
        "exit_b",
    ]

    agents = generate_population(
        campus,
        population_size,
    )

    occupancy = Counter()

    completed = 0
    failed = 0

    for agent in agents:

        exit_node, route, cost = find_best_exit(
            campus,
            agent.start_location,
            exits,
        )

        if route is None:

            failed += 1
            continue

        completed += 1

        for location in route:

            if location.startswith("exit_"):
                continue

            occupancy[location] += 1

    capacities = {}

    for location, data in campus.nodes(
        data=True
    ):

        if data["type"] in {
            "room",
            "corridor",
            "staircase",
        }:

            capacities[
                location
            ] = data["capacity"]

    results = calculate_congestion(
        dict(occupancy),
        capacities,
    )

    print()
    print(
        f"Agents generated : {population_size:,}"
    )

    print(
        f"Routes completed : {completed:,}"
    )

    print(
        f"Routes failed    : {failed:,}"
    )

    print_congestion_report(results)

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
    print("=" * 75)
    print("STRESS TEST SUMMARY")
    print("=" * 75)

    print(
        f"Critical bottlenecks : {len(critical)}"
    )

    print(
        f"High-risk locations  : {len(high)}"
    )

    if critical:

        print()
        print("Critical locations:")

        for result in critical:

            print(
                f"  - {result.location}: "
                f"{result.utilization * 100:.1f}% utilization"
            )

    return results


if __name__ == "__main__":

    run_stress_test(100)