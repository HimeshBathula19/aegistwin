from collections import Counter

from campus import create_campus
from population import generate_population
from simulation import find_best_exit
from dynamic_congestion import (
    calculate_congestion,
)


def run_scenario(
    population_size=500,
    blocked_nodes=None,
):

    blocked_nodes = blocked_nodes or []

    campus = create_campus()

    # Remove failed locations from the simulation.
    for node in blocked_nodes:

        if node in campus:
            campus.remove_node(node)

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

    evacuation_times = []

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

        # Estimated individual evacuation time.
        #
        # This is still a simplified model:
        # route cost / walking speed + reaction delay.

        if agent.speed > 0:

            travel_time = (
                cost / agent.speed
            )

        else:

            travel_time = 0

        evacuation_time = (
            agent.reaction_time
            + travel_time
        )

        evacuation_times.append(
            evacuation_time
        )

    capacities = {}

    for location, data in campus.nodes(
        data=True
    ):

        if data["type"] in {
            "room",
            "corridor",
            "staircase",
        }:

            capacities[location] = data[
                "capacity"
            ]

    congestion = calculate_congestion(
        dict(occupancy),
        capacities,
    )

    max_evacuation_time = (
        max(evacuation_times)
        if evacuation_times
        else 0
    )

    average_evacuation_time = (
        sum(evacuation_times)
        / len(evacuation_times)
        if evacuation_times
        else 0
    )

    critical = [
        result
        for result in congestion
        if result.level == "CRITICAL"
    ]

    high = [
        result
        for result in congestion
        if result.level == "HIGH"
    ]

    return {
        "population": population_size,
        "completed": completed,
        "failed": failed,
        "average_evacuation_time":
            round(
                average_evacuation_time,
                2,
            ),
        "maximum_evacuation_time":
            round(
                max_evacuation_time,
                2,
            ),
        "critical_locations":
            len(critical),
        "high_risk_locations":
            len(high),
        "congestion": congestion,
    }


def print_comparison(
    baseline,
    scenario,
    scenario_name,
):

    print()
    print("=" * 75)
    print("AEGISTWIN WHAT-IF ANALYSIS")
    print("=" * 75)

    print()
    print(
        f"SCENARIO: {scenario_name}"
    )

    print()
    print(
        f"{'METRIC':35}"
        f"{'BASELINE':15}"
        f"{'SCENARIO':15}"
    )

    print("-" * 65)

    print(
        f"{'Population':35}"
        f"{baseline['population']:<15}"
        f"{scenario['population']:<15}"
    )

    print(
        f"{'Completed evacuations':35}"
        f"{baseline['completed']:<15}"
        f"{scenario['completed']:<15}"
    )

    print(
        f"{'Failed evacuations':35}"
        f"{baseline['failed']:<15}"
        f"{scenario['failed']:<15}"
    )

    print(
        f"{'Average evacuation time':35}"
        f"{baseline['average_evacuation_time']:<15}"
        f"{scenario['average_evacuation_time']:<15}"
    )

    print(
        f"{'Maximum evacuation time':35}"
        f"{baseline['maximum_evacuation_time']:<15}"
        f"{scenario['maximum_evacuation_time']:<15}"
    )

    print(
        f"{'Critical locations':35}"
        f"{baseline['critical_locations']:<15}"
        f"{scenario['critical_locations']:<15}"
    )

    print(
        f"{'High-risk locations':35}"
        f"{baseline['high_risk_locations']:<15}"
        f"{scenario['high_risk_locations']:<15}"
    )

    print()
    print("=" * 75)
    print("SCENARIO BOTTLENECKS")
    print("=" * 75)

    for result in scenario["congestion"]:

        if result.level in {
            "CRITICAL",
            "HIGH",
        }:

            print(
                f"{result.location:25}"
                f"{result.utilization * 100:8.1f}%"
                f"  {result.level}"
            )


if __name__ == "__main__":

    population = 500

    baseline = run_scenario(
        population_size=population,
        blocked_nodes=[],
    )

    blocked_staircase = run_scenario(
        population_size=population,
        blocked_nodes=[
            "staircase_a",
        ],
    )

    print_comparison(
        baseline,
        blocked_staircase,
        "STAIRCASE A BLOCKED",
    )