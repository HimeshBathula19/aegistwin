from collections import Counter

from campus import create_campus
from simulation import create_agents, find_best_exit
from dynamic_congestion import (
    calculate_congestion,
    print_congestion_report,
)


def run_integrated_analysis():

    campus = create_campus()

    exits = [
        "exit_a",
        "exit_b",
    ]

    agents = create_agents()

    routes = []

    for agent in agents:

        exit_node, route, cost = find_best_exit(
            campus,
            agent.start_location,
            exits,
        )

        if route is None:
            continue

        routes.append(route)

    # Count how many agents pass through
    # each location.
    occupancy = Counter()

    for route in routes:

        for location in route:

            # Exits are not treated as
            # congestion locations.
            if location.startswith("exit_"):
                continue

            occupancy[location] += 1

    # Capacities come from the digital twin.
    capacities = {}

    for location, data in campus.nodes(data=True):

        if data["type"] in {
            "room",
            "corridor",
            "staircase",
        }:

            capacities[location] = data["capacity"]

    results = calculate_congestion(
        dict(occupancy),
        capacities,
    )

    print_congestion_report(results)

    return results


if __name__ == "__main__":

    run_integrated_analysis()