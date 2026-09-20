import networkx as nx

from campus import create_campus
from agents import Agent
from occupancy import count_edge_occupancy

def find_best_exit(campus, start, exits):
    """
    Find the lowest-cost reachable exit from an agent's location.
    """

    best_exit = None
    best_route = None
    best_cost = float("inf")

    for exit_node in exits:

        if exit_node not in campus:
            continue

        if not nx.has_path(campus, start, exit_node):
            continue

        route = nx.shortest_path(
            campus,
            start,
            exit_node,
            weight="weight",
        )

        cost = nx.path_weight(
            campus,
            route,
            weight="weight",
        )

        if cost < best_cost:
            best_exit = exit_node
            best_route = route
            best_cost = cost

    return best_exit, best_route, best_cost


def create_agents():
    """
    Create the initial synthetic population.
    """

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
            destination="exit_b",
            speed=1.3,
            reaction_time=4,
        ),

        Agent(
            agent_id=4,
            start_location="academic_lab_2",
            destination="exit_b",
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


def run_simulation():

    campus = create_campus()

    exits = [
        "exit_a",
        "exit_b",
    ]

    agents = create_agents()

    results = []
    routes = []

    for agent in agents:

        exit_node, route, cost = find_best_exit(
            campus,
            agent.start_location,
            exits,
        )

        if route is None:

            results.append({
                "agent_id": agent.agent_id,
                "status": "NO_REACHABLE_EXIT",
            })

            continue

        agent.destination = exit_node

        agent.assign_route(route)

        routes.append(route)

        agent.calculate_travel_time(cost)

        agent.complete()

        results.append(agent.summary())

    occupancy = count_edge_occupancy(routes)

    print()
    print("=" * 60)
    print("AUTOMATIC ROUTE OCCUPANCY")
    print("=" * 60)

    for edge, count in occupancy.items():

        print(
            f"{edge[0]:20} -> "
            f"{edge[1]:20} "
            f"{count:4} agents"
        )

    return results
def print_results(results):

    print()
    print("=" * 60)
    print("AEGISTWIN AGENT SIMULATION")
    print("=" * 60)

    for result in results:

        print()

        for key, value in result.items():
            print(f"{key:16}: {value}")

    print()
    print("=" * 60)


if __name__ == "__main__":

    results = run_simulation()

    print_results(results)