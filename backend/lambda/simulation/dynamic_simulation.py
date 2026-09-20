from campus import create_campus
from agents import Agent
from dynamic_routing import (
    find_dynamic_route,
    register_route,
    print_dynamic_statistics,
)


def create_dynamic_agents():

    return [
        Agent(
            agent_id=1,
            start_location="north_classroom_1",
            destination="exit_a",
            speed=1.2,
            reaction_time=5,
        ),

        Agent(
            agent_id=2,
            start_location="north_classroom_2",
            destination="exit_a",
            speed=1.1,
            reaction_time=6,
        ),

        Agent(
            agent_id=3,
            start_location="academic_lab_1",
            destination="exit_a",
            speed=1.3,
            reaction_time=4,
        ),

        Agent(
            agent_id=4,
            start_location="academic_lab_2",
            destination="exit_a",
            speed=1.0,
            reaction_time=7,
        ),

        Agent(
            agent_id=5,
            start_location="cafeteria",
            destination="exit_a",
            speed=1.2,
            reaction_time=5,
        ),
    ]


def run_dynamic_simulation():

    print()
    print("=" * 72)
    print("AEGISTWIN DYNAMIC EVACUATION SIMULATION")
    print("=" * 72)

    campus = create_campus()

    exits = [
        "exit_a",
        "exit_b",
    ]

    agents = create_dynamic_agents()

    # Current simulated traffic.
    edge_loads = {}

    results = []

    for agent in agents:

        exit_node, route, dynamic_cost = find_dynamic_route(
            campus,
            agent.start_location,
            exits,
            edge_loads,
        )

        if route is None:

            results.append(
                {
                    "agent_id": agent.agent_id,
                    "status": "NO_REACHABLE_EXIT",
                }
            )

            continue

        agent.destination = exit_node

        agent.assign_route(route)

        register_route(
            route,
            edge_loads,
        )

        agent.calculate_travel_time(
            dynamic_cost
        )

        agent.complete()

        results.append(
            agent.summary()
        )

        print()
        print(
            f"Agent {agent.agent_id}"
        )

        print(
            f"  Start : "
            f"{agent.start_location}"
        )

        print(
            f"  Exit  : "
            f"{exit_node}"
        )

        print(
            f"  Route : "
            f"{route}"
        )

        print(
            f"  Cost  : "
            f"{dynamic_cost:.2f}"
        )

    print_dynamic_statistics(
        campus,
        edge_loads,
    )

    return results


if __name__ == "__main__":

    run_dynamic_simulation()