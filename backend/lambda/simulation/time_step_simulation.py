import networkx as nx

from campus import create_campus
from population import generate_population


# ============================================================
# CONFIGURATION
# ============================================================

TIME_STEP = 1.0
MAX_SIMULATION_TIME = 300


# ============================================================
# BEHAVIOR MODEL
# ============================================================

def get_behavior_multiplier(agent):
    """
    Modify movement speed according to the
    synthetic behavioral profile.
    """

    behavior = getattr(
        agent,
        "behavior",
        "normal",
    )

    if behavior == "fast_responder":
        return 1.10

    if behavior == "cautious":
        return 0.90

    if behavior == "hesitant":
        return 0.80

    return 1.00


# ============================================================
# MOBILITY MODEL
# ============================================================

def get_mobility_multiplier(agent):
    """
    Additional movement adjustment based on
    mobility profile.
    """

    mobility = getattr(
        agent,
        "mobility",
        "normal",
    )

    if mobility == "assisted":
        return 0.70

    if mobility == "reduced":
        return 0.82

    return 1.00


# ============================================================
# ROUTING
# ============================================================

def find_best_exit(campus, start, exits):
    """
    Find the lowest-cost reachable exit.
    """

    best_exit = None
    best_route = None
    best_cost = float("inf")

    for exit_node in exits:

        if exit_node not in campus:
            continue

        try:

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

                best_cost = cost
                best_exit = exit_node
                best_route = route

        except nx.NetworkXNoPath:

            continue

    return (
        best_exit,
        best_route,
        best_cost,
    )


# ============================================================
# CONGESTION MODEL
# ============================================================

def calculate_congestion_multiplier(
    utilization
):
    """
    Convert infrastructure utilization
    into a movement slowdown factor.
    """

    if utilization <= 0.50:

        return 1.00

    if utilization <= 0.75:

        return 1.25

    if utilization <= 1.00:

        return 1.75

    overload = utilization - 1.00

    return (
        2.50
        + overload * 3.00
    )


# ============================================================
# TIME-STEP SIMULATION
# ============================================================

def run_time_step_simulation(
    population_size=100,
    region="global",
    seed=42,
):
    """
    Run a temporal evacuation simulation.

    Agents move through the digital twin
    one time step at a time.

    Population characteristics influence
    movement and evacuation behavior.
    """

    campus = create_campus()

    exits = [
        node
        for node, data in campus.nodes(
            data=True
        )
        if data["type"] == "exit"
    ]

    # --------------------------------------------------------
    # Generate synthetic population
    # --------------------------------------------------------

    agents = generate_population(
        campus,
        population_size,
        region=region,
        seed=seed,
    )

    # --------------------------------------------------------
    # Assign routes
    # --------------------------------------------------------

    for agent in agents:

        (
            exit_node,
            route,
            route_cost,
        ) = find_best_exit(
            campus,
            agent.start_location,
            exits,
        )

        if route is None:
            continue

        agent.destination = exit_node

        agent.assign_route(
            route
        )

    # --------------------------------------------------------
    # Active agents
    # --------------------------------------------------------

    active_agents = [
        agent
        for agent in agents
        if agent.route
    ]

    completed_agents = []

    # --------------------------------------------------------
    # Simulation clock
    # --------------------------------------------------------

    simulation_time = 0.0

    # --------------------------------------------------------
    # Current position of every agent
    #
    # Example:
    #
    # route:
    # A → B → C → D
    #
    # position_index = 0
    # means agent is at A
    # --------------------------------------------------------

    position_index = {
        agent.agent_id: 0
        for agent in active_agents
    }

    # --------------------------------------------------------
    # Progress through current edge
    # --------------------------------------------------------

    edge_progress = {
        agent.agent_id: 0.0
        for agent in active_agents
    }

    # --------------------------------------------------------
    # Main simulation loop
    # --------------------------------------------------------

    while (
        active_agents
        and simulation_time
        < MAX_SIMULATION_TIME
    ):

        # ====================================================
        # CURRENT NODE OCCUPANCY
        # ====================================================

        node_occupancy = {}

        for agent in active_agents:

            index = position_index[
                agent.agent_id
            ]

            current_node = agent.route[
                index
            ]

            node_occupancy[
                current_node
            ] = (
                node_occupancy.get(
                    current_node,
                    0,
                )
                + 1
            )

        # ====================================================
        # MOVE AGENTS
        # ====================================================

        finished_this_step = []

        for agent in active_agents:

            agent_id = agent.agent_id

            index = position_index[
                agent_id
            ]

            # ------------------------------------------------
            # Destination check
            # ------------------------------------------------

            if (
                index
                >= len(agent.route) - 1
            ):

                agent.complete()

                if agent.travel_time == 0:

                    agent.travel_time = (
                        simulation_time
                    )

                finished_this_step.append(
                    agent
                )

                continue

            # ------------------------------------------------
            # Current edge
            # ------------------------------------------------

            current_node = agent.route[
                index
            ]

            next_node = agent.route[
                index + 1
            ]

            base_cost = campus[
                current_node
            ][
                next_node
            ]["weight"]

            # ------------------------------------------------
            # Infrastructure capacity
            # ------------------------------------------------

            current_capacity = campus.nodes[
                current_node
            ].get(
                "capacity",
                100,
            )

            next_capacity = campus.nodes[
                next_node
            ].get(
                "capacity",
                100,
            )

            capacity = min(
                current_capacity,
                next_capacity,
            )

            # ------------------------------------------------
            # Occupancy
            # ------------------------------------------------

            occupancy = node_occupancy.get(
                current_node,
                0,
            )

            utilization = (
                occupancy
                / max(capacity, 1)
            )

            # ------------------------------------------------
            # Congestion
            # ------------------------------------------------

            congestion_multiplier = (
                calculate_congestion_multiplier(
                    utilization
                )
            )

            # ------------------------------------------------
            # Behavioral movement
            # ------------------------------------------------

            behavior_multiplier = (
                get_behavior_multiplier(
                    agent
                )
            )

            mobility_multiplier = (
                get_mobility_multiplier(
                    agent
                )
            )

            effective_speed = (
                agent.speed
                * behavior_multiplier
                * mobility_multiplier
            )

            effective_speed = max(
                effective_speed,
                0.1,
            )

            # ------------------------------------------------
            # Effective edge cost
            # ------------------------------------------------

            effective_cost = (
                base_cost
                * congestion_multiplier
            )

            # ------------------------------------------------
            # Movement this time step
            # ------------------------------------------------

            movement = (
                effective_speed
                * TIME_STEP
            )

            edge_progress[
                agent_id
            ] += (
                movement
                / effective_cost
            )

            # ------------------------------------------------
            # Edge completed
            # ------------------------------------------------

            if (
                edge_progress[
                    agent_id
                ] >= 1.0
            ):

                position_index[
                    agent_id
                ] += 1

                edge_progress[
                    agent_id
                ] = 0.0

                # --------------------------------------------
                # Destination reached
                # --------------------------------------------

                if (
                    position_index[
                        agent_id
                    ]
                    >= len(agent.route) - 1
                ):

                    agent.complete()

                    agent.travel_time = (
                        simulation_time
                        + TIME_STEP
                    )

                    finished_this_step.append(
                        agent
                    )

        # ====================================================
        # REMOVE COMPLETED AGENTS
        # ====================================================

        for agent in finished_this_step:

            if agent in active_agents:

                active_agents.remove(
                    agent
                )

                completed_agents.append(
                    agent
                )

        # ====================================================
        # ADVANCE CLOCK
        # ====================================================

        simulation_time += TIME_STEP

    # ========================================================
    # METRICS
    # ========================================================

    evacuation_times = [
        agent.travel_time
        for agent in completed_agents
    ]

    if evacuation_times:

        average_time = (
            sum(evacuation_times)
            / len(evacuation_times)
        )

        maximum_time = max(
            evacuation_times
        )

        minimum_time = min(
            evacuation_times
        )

    else:

        average_time = 0.0
        maximum_time = 0.0
        minimum_time = 0.0

    completion_rate = (
        len(completed_agents)
        / population_size
        if population_size > 0
        else 0.0
    )

    return {
        "population": population_size,
        "region": region,
        "completed": len(
            completed_agents
        ),
        "remaining": len(
            active_agents
        ),
        "completion_rate": round(
            completion_rate,
            4,
        ),
        "simulation_time": round(
            simulation_time,
            2,
        ),
        "average_evacuation_time": round(
            average_time,
            2,
        ),
        "minimum_evacuation_time": round(
            minimum_time,
            2,
        ),
        "maximum_evacuation_time": round(
            maximum_time,
            2,
        ),
        "agents": agents,
    }


# ============================================================
# REPORT
# ============================================================

def print_report(results):

    print()

    print("=" * 75)

    print(
        "AEGISTWIN TIME-STEP "
        "EVACUATION SIMULATION"
    )

    print("=" * 75)

    print(
        f"Population              : "
        f"{results['population']}"
    )

    print(
        f"Region                  : "
        f"{results['region']}"
    )

    print(
        f"Completed               : "
        f"{results['completed']}"
    )

    print(
        f"Remaining               : "
        f"{results['remaining']}"
    )

    print(
        f"Completion rate         : "
        f"{results['completion_rate'] * 100:.1f}%"
    )

    print(
        f"Simulation duration     : "
        f"{results['simulation_time']:.2f}"
    )

    print(
        f"Minimum evacuation time : "
        f"{results['minimum_evacuation_time']:.2f}"
    )

    print(
        f"Average evacuation time : "
        f"{results['average_evacuation_time']:.2f}"
    )

    print(
        f"Maximum evacuation time : "
        f"{results['maximum_evacuation_time']:.2f}"
    )

    print("=" * 75)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    results = run_time_step_simulation(
        population_size=100,
        region="global",
        seed=42,
    )

    print_report(
        results
    )