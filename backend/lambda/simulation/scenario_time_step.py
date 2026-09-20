import networkx as nx

from campus import create_campus
from population import generate_population


# ============================================================
# CONFIGURATION
# ============================================================

TIME_STEP = 1.0

MAX_SIMULATION_TIME = 300


# ============================================================
# BEHAVIOR
# ============================================================

def get_behavior_multiplier(agent):

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
# MOBILITY
# ============================================================

def get_mobility_multiplier(agent):

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

def find_best_route(
    campus,
    start,
    exits,
    blocked_nodes=None,
    edge_cost_multipliers=None,
):

    if blocked_nodes is None:
        blocked_nodes = set()

    if edge_cost_multipliers is None:
        edge_cost_multipliers = {}

    best_exit = None
    best_route = None
    best_cost = float("inf")

    for exit_node in exits:

        if exit_node in blocked_nodes:
            continue

        if exit_node not in campus:
            continue

        try:

            def dynamic_weight(
                source,
                destination,
                data,
            ):

                base_cost = data["weight"]

                key = tuple(
                    sorted(
                        (
                            source,
                            destination,
                        )
                    )
                )

                multiplier = (
                    edge_cost_multipliers.get(
                        key,
                        1.0,
                    )
                )

                return (
                    base_cost
                    * multiplier
                )

            route = nx.shortest_path(
                campus,
                start,
                exit_node,
                weight=dynamic_weight,
            )

            # Current location can be blocked
            # because an agent may already be there.
            #
            # Future locations cannot be blocked.

            future_route = route[1:]

            if any(
                node in blocked_nodes
                for node in future_route
            ):
                continue

            cost = 0.0

            for source, destination in zip(
                route[:-1],
                route[1:],
            ):

                cost += dynamic_weight(
                    source,
                    destination,
                    campus[
                        source
                    ][
                        destination
                    ],
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
# ROUTE ASSIGNMENT
# ============================================================

def assign_route(
    agent,
    campus,
    exits,
    blocked_nodes,
    edge_cost_multipliers,
):

    (
        exit_node,
        route,
        route_cost,
    ) = find_best_route(
        campus,
        agent.start_location,
        exits,
        blocked_nodes,
        edge_cost_multipliers,
    )

    if route is None:

        agent.route = []
        agent.destination = ""

        return False

    agent.destination = exit_node

    agent.assign_route(
        route
    )

    return True


# ============================================================
# CONGESTION
# ============================================================

def calculate_congestion_multiplier(
    utilization,
):

    if utilization <= 0.50:
        return 1.00

    if utilization <= 0.75:
        return 1.25

    if utilization <= 1.00:
        return 1.75

    overload = (
        utilization - 1.00
    )

    return (
        2.50
        + overload * 3.00
    )


# ============================================================
# RUN SCENARIO
# ============================================================

def run_scenario(
    population_size=500,
    region="global",
    blocked_node=None,
    block_time=None,
    seed=42,
    capacity_overrides=None,
    edge_cost_multipliers=None,
):

    if capacity_overrides is None:
        capacity_overrides = {}

    if edge_cost_multipliers is None:
        edge_cost_multipliers = {}

    campus = create_campus()

    exits = [
        node
        for node, data in campus.nodes(
            data=True
        )
        if data["type"] == "exit"
    ]

    # --------------------------------------------------------
    # Validate intervention nodes
    # --------------------------------------------------------

    for node in capacity_overrides:

        if node not in campus:

            raise ValueError(
                f"Unknown capacity node: {node}"
            )

    for edge in edge_cost_multipliers:

        if len(edge) != 2:

            raise ValueError(
                "Edge intervention must "
                "contain two nodes."
            )

        source, destination = edge

        if not campus.has_edge(
            source,
            destination,
        ):

            raise ValueError(
                f"Unknown edge: "
                f"{source} -> {destination}"
            )

    # --------------------------------------------------------
    # Generate population
    # --------------------------------------------------------

    agents = generate_population(
        campus,
        population_size,
        region=region,
        seed=seed,
    )

    blocked_nodes = set()

    active_agents = []

    failed_agents = []

    # --------------------------------------------------------
    # Initial routing
    # --------------------------------------------------------

    for agent in agents:

        success = assign_route(
            agent,
            campus,
            exits,
            blocked_nodes,
            edge_cost_multipliers,
        )

        if success:
            active_agents.append(
                agent
            )
        else:
            failed_agents.append(
                agent
            )

    # --------------------------------------------------------
    # Simulation state
    # --------------------------------------------------------

    completed_agents = []

    position_index = {
        agent.agent_id: 0
        for agent in active_agents
    }

    edge_progress = {
        agent.agent_id: 0.0
        for agent in active_agents
    }

    simulation_time = 0.0

    reroute_count = 0

    disruption_triggered = False

    disruption_time = None

    peak_occupancy = {}

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while (
        active_agents
        and simulation_time
        < MAX_SIMULATION_TIME
    ):

        # ====================================================
        # DYNAMIC FAILURE
        # ====================================================

        if (
            blocked_node is not None
            and block_time is not None
            and not disruption_triggered
            and simulation_time >= block_time
        ):

            disruption_triggered = True

            disruption_time = simulation_time

            blocked_nodes.add(
                blocked_node
            )

            print()
            print("=" * 80)
            print(
                "DYNAMIC EMERGENCY EVENT"
            )
            print("=" * 80)

            print(
                f"Time                  : "
                f"{simulation_time:.1f}"
            )

            print(
                f"Blocked infrastructure: "
                f"{blocked_node}"
            )

            print(
                "Agents are recalculating "
                "their evacuation routes."
            )

            print("=" * 80)

            # ------------------------------------------------
            # Reroute affected agents.
            # ------------------------------------------------

            for agent in list(
                active_agents
            ):

                agent_id = agent.agent_id

                index = position_index[
                    agent_id
                ]

                current_node = agent.route[
                    index
                ]

                future_route = agent.route[
                    index + 1:
                ]

                if blocked_node not in future_route:
                    continue

                (
                    new_exit,
                    new_route,
                    new_cost,
                ) = find_best_route(
                    campus,
                    current_node,
                    exits,
                    blocked_nodes,
                    edge_cost_multipliers,
                )

                if new_route is None:

                    active_agents.remove(
                        agent
                    )

                    failed_agents.append(
                        agent
                    )

                    continue

                agent.destination = new_exit

                agent.route = new_route

                position_index[
                    agent_id
                ] = 0

                edge_progress[
                    agent_id
                ] = 0.0

                reroute_count += 1

        # ====================================================
        # OCCUPANCY
        # ====================================================

        node_occupancy = {}

        for agent in active_agents:

            agent_id = agent.agent_id

            index = position_index[
                agent_id
            ]

            if index >= len(
                agent.route
            ):
                continue

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

        # ----------------------------------------------------
        # Peak occupancy
        # ----------------------------------------------------

        for node, occupancy in node_occupancy.items():

            previous = peak_occupancy.get(
                node,
                0,
            )

            peak_occupancy[node] = max(
                previous,
                occupancy,
            )

        # ====================================================
        # MOVE AGENTS
        # ====================================================

        finished_this_step = []

        for agent in list(
            active_agents
        ):

            agent_id = agent.agent_id

            index = position_index[
                agent_id
            ]

            # ------------------------------------------------
            # Destination
            # ------------------------------------------------

            if (
                index
                >= len(agent.route) - 1
            ):

                agent.complete()

                agent.travel_time = (
                    simulation_time
                )

                finished_this_step.append(
                    agent
                )

                continue

            current_node = agent.route[
                index
            ]

            next_node = agent.route[
                index + 1
            ]

            # =================================================
            # BLOCKED NEXT LOCATION
            # =================================================

            if next_node in blocked_nodes:

                (
                    new_exit,
                    new_route,
                    new_cost,
                ) = find_best_route(
                    campus,
                    current_node,
                    exits,
                    blocked_nodes,
                    edge_cost_multipliers,
                )

                if new_route is None:

                    active_agents.remove(
                        agent
                    )

                    failed_agents.append(
                        agent
                    )

                    continue

                agent.destination = new_exit

                agent.route = new_route

                position_index[
                    agent_id
                ] = 0

                edge_progress[
                    agent_id
                ] = 0.0

                reroute_count += 1

                continue

            # =================================================
            # EDGE COST
            # =================================================

            base_cost = campus[
                current_node
            ][
                next_node
            ]["weight"]

            edge_key = tuple(
                sorted(
                    (
                        current_node,
                        next_node,
                    )
                )
            )

            intervention_multiplier = (
                edge_cost_multipliers.get(
                    edge_key,
                    1.0,
                )
            )

            base_cost *= (
                intervention_multiplier
            )

            # ------------------------------------------------
            # Capacity
            # ------------------------------------------------

            current_capacity = (
                capacity_overrides.get(
                    current_node,
                    campus.nodes[
                        current_node
                    ].get(
                        "capacity",
                        100,
                    ),
                )
            )

            next_capacity = (
                capacity_overrides.get(
                    next_node,
                    campus.nodes[
                        next_node
                    ].get(
                        "capacity",
                        100,
                    ),
                )
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
                / max(
                    capacity,
                    1,
                )
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
            # Agent behavior
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
            # Effective movement cost
            # ------------------------------------------------

            effective_cost = (
                base_cost
                * congestion_multiplier
            )

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

            # =================================================
            # EDGE COMPLETION
            # =================================================

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

                if (
                    position_index[
                        agent_id
                    ]
                    >= len(
                        agent.route
                    ) - 1
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
        # REMOVE COMPLETED
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
        # ADVANCE TIME
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

    completed = len(
        completed_agents
    )

    failed = len(
        failed_agents
    )

    remaining = len(
        active_agents
    )

    completion_rate = (
        completed
        / population_size
        if population_size > 0
        else 0.0
    )

    failure_rate = (
        failed
        / population_size
        if population_size > 0
        else 0.0
    )

    return {
        "population": population_size,

        "region": region,

        "blocked_node": blocked_node,

        "block_time": block_time,

        "disruption_triggered":
            disruption_triggered,

        "disruption_time":
            disruption_time,

        "completed":
            completed,

        "failed":
            failed,

        "remaining":
            remaining,

        "completion_rate":
            round(
                completion_rate,
                4,
            ),

        "failure_rate":
            round(
                failure_rate,
                4,
            ),

        "simulation_time":
            round(
                simulation_time,
                2,
            ),

        "minimum_evacuation_time":
            round(
                minimum_time,
                2,
            ),

        "average_evacuation_time":
            round(
                average_time,
                2,
            ),

        "maximum_evacuation_time":
            round(
                maximum_time,
                2,
            ),

        "reroute_count":
            reroute_count,

        "peak_occupancy":
            peak_occupancy,

        "agents":
            agents,
    }


# ============================================================
# COMPARISON
# ============================================================

def compare_scenarios(
    baseline,
    scenario,
):

    return {
        "average_time_change": round(
            scenario[
                "average_evacuation_time"
            ]
            - baseline[
                "average_evacuation_time"
            ],
            2,
        ),

        "maximum_time_change": round(
            scenario[
                "maximum_evacuation_time"
            ]
            - baseline[
                "maximum_evacuation_time"
            ],
            2,
        ),

        "completion_change": round(
            scenario[
                "completion_rate"
            ]
            - baseline[
                "completion_rate"
            ],
            4,
        ),

        "failure_change": round(
            scenario[
                "failure_rate"
            ]
            - baseline[
                "failure_rate"
            ],
            4,
        ),

        "additional_reroutes":
            scenario[
                "reroute_count"
            ],
    }


# ============================================================
# REPORT
# ============================================================

def print_scenario_report(
    baseline,
    scenario,
    comparison,
):

    print()

    print("=" * 90)

    print(
        "AEGISTWIN DYNAMIC "
        "WHAT-IF ANALYSIS"
    )

    print("=" * 90)

    print()
    print("BASELINE")
    print("-" * 90)

    print(
        f"Population              : "
        f"{baseline['population']}"
    )

    print(
        f"Completed               : "
        f"{baseline['completed']}"
    )

    print(
        f"Failed                  : "
        f"{baseline['failed']}"
    )

    print(
        f"Average evacuation time : "
        f"{baseline['average_evacuation_time']:.2f}"
    )

    print(
        f"Maximum evacuation time : "
        f"{baseline['maximum_evacuation_time']:.2f}"
    )

    print()
    print("DYNAMIC EMERGENCY SCENARIO")
    print("-" * 90)

    print(
        f"Blocked infrastructure : "
        f"{scenario['blocked_node']}"
    )

    print(
        f"Block time             : "
        f"{scenario['block_time']:.1f}"
    )

    print(
        f"Event triggered         : "
        f"{scenario['disruption_triggered']}"
    )

    print(
        f"Completed               : "
        f"{scenario['completed']}"
    )

    print(
        f"Failed                  : "
        f"{scenario['failed']}"
    )

    print(
        f"Remaining               : "
        f"{scenario['remaining']}"
    )

    print(
        f"Average evacuation time : "
        f"{scenario['average_evacuation_time']:.2f}"
    )

    print(
        f"Maximum evacuation time : "
        f"{scenario['maximum_evacuation_time']:.2f}"
    )

    print(
        f"Completion rate         : "
        f"{scenario['completion_rate'] * 100:.1f}%"
    )

    print(
        f"Failure rate            : "
        f"{scenario['failure_rate'] * 100:.1f}%"
    )

    print(
        f"Reroutes                : "
        f"{scenario['reroute_count']}"
    )

    print()
    print("IMPACT")
    print("-" * 90)

    print(
        f"Average time change     : "
        f"{comparison['average_time_change']:+.2f}"
    )

    print(
        f"Maximum time change     : "
        f"{comparison['maximum_time_change']:+.2f}"
    )

    print(
        f"Completion change       : "
        f"{comparison['completion_change'] * 100:+.1f}%"
    )

    print(
        f"Failure-rate change     : "
        f"{comparison['failure_change'] * 100:+.1f}%"
    )

    print(
        f"Reroutes                : "
        f"{comparison['additional_reroutes']}"
    )

    print("=" * 90)


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    POPULATION_SIZE = 500

    REGION = "global"

    SEED = 42

    baseline = run_scenario(
        population_size=POPULATION_SIZE,
        region=REGION,
        blocked_node=None,
        block_time=None,
        seed=SEED,
    )

    scenario = run_scenario(
        population_size=POPULATION_SIZE,
        region=REGION,
        blocked_node="staircase_a",
        block_time=5,
        seed=SEED,
    )

    comparison = compare_scenarios(
        baseline,
        scenario,
    )

    print_scenario_report(
        baseline,
        scenario,
        comparison,
    )