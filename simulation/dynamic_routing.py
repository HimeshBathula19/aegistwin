import networkx as nx


def edge_key(source, destination):
    """
    NetworkX uses an undirected graph, so always store
    an edge in a consistent order.
    """

    return tuple(
        sorted(
            (
                source,
                destination,
            )
        )
    )


def get_edge_capacity(
    campus,
    source,
    destination,
):
    """
    Determine the effective capacity of an edge.

    We use the lower capacity of the two connected
    locations.
    """

    source_capacity = campus.nodes[source].get(
        "capacity",
        100,
    )

    destination_capacity = campus.nodes[destination].get(
        "capacity",
        100,
    )

    return min(
        source_capacity,
        destination_capacity,
    )


def calculate_dynamic_edge_cost(
    campus,
    source,
    destination,
    edge_loads,
):
    """
    Calculate the effective cost of an edge.

    Base cost:
        Physical travel cost.

    Dynamic penalty:
        Additional cost caused by existing traffic.
    """

    base_cost = campus[source][destination]["weight"]

    capacity = get_edge_capacity(
        campus,
        source,
        destination,
    )

    load = edge_loads.get(
        edge_key(source, destination),
        0,
    )

    utilization = load / max(
        capacity,
        1,
    )

    # ---------------------------------------------------------
    # CONGESTION MODEL
    # ---------------------------------------------------------

    if utilization <= 0.25:

        multiplier = 1.0

    elif utilization <= 0.50:

        multiplier = 1.15

    elif utilization <= 0.75:

        multiplier = 1.50

    elif utilization <= 1.00:

        multiplier = 2.50

    else:

        # Strongly discourage already overloaded infrastructure.
        overload = utilization - 1.0

        multiplier = (
            4.0
            + overload * 8.0
        )

    return base_cost * multiplier


def find_dynamic_route(
    campus,
    start,
    exits,
    edge_loads,
):
    """
    Find the currently cheapest route while considering
    existing infrastructure load.
    """

    best_exit = None
    best_route = None
    best_cost = float("inf")

    for exit_node in exits:

        if exit_node not in campus:
            continue

        if not nx.has_path(
            campus,
            start,
            exit_node,
        ):
            continue

        def dynamic_weight(
            source,
            destination,
            data,
        ):

            return calculate_dynamic_edge_cost(
                campus,
                source,
                destination,
                edge_loads,
            )

        try:

            route = nx.shortest_path(
                campus,
                start,
                exit_node,
                weight=dynamic_weight,
            )

        except nx.NetworkXNoPath:

            continue

        total_cost = 0.0

        for source, destination in zip(
            route[:-1],
            route[1:],
        ):

            total_cost += (
                calculate_dynamic_edge_cost(
                    campus,
                    source,
                    destination,
                    edge_loads,
                )
            )

        if total_cost < best_cost:

            best_cost = total_cost
            best_exit = exit_node
            best_route = route

    return (
        best_exit,
        best_route,
        best_cost,
    )


def register_route(
    route,
    edge_loads,
):
    """
    Add one agent's route to the current
    infrastructure load.
    """

    for source, destination in zip(
        route[:-1],
        route[1:],
    ):

        edge = edge_key(
            source,
            destination,
        )

        edge_loads[edge] = (
            edge_loads.get(edge, 0)
            + 1
        )


def calculate_route_statistics(
    campus,
    edge_loads,
):
    """
    Calculate utilization for every used edge.
    """

    statistics = []

    for edge, load in edge_loads.items():

        source, destination = edge

        capacity = get_edge_capacity(
            campus,
            source,
            destination,
        )

        utilization = (
            load / max(capacity, 1)
        )

        if utilization > 1.0:

            level = "CRITICAL"

        elif utilization >= 0.80:

            level = "HIGH"

        elif utilization >= 0.50:

            level = "MODERATE"

        else:

            level = "LOW"

        statistics.append(
            {
                "source": source,
                "destination": destination,
                "load": load,
                "capacity": capacity,
                "utilization": utilization,
                "level": level,
            }
        )

    statistics.sort(
        key=lambda item: item["utilization"],
        reverse=True,
    )

    return statistics


def print_dynamic_statistics(
    campus,
    edge_loads,
):

    statistics = calculate_route_statistics(
        campus,
        edge_loads,
    )

    print()
    print("=" * 72)
    print("AEGISTWIN DYNAMIC ROUTING ANALYSIS")
    print("=" * 72)

    print(
        f"{'ROUTE':35}"
        f"{'LOAD':>8}"
        f"{'CAP':>8}"
        f"{'UTIL':>10}"
        f"{'LEVEL':>12}"
    )

    print("-" * 72)

    for item in statistics:

        route_name = (
            f"{item['source']} -> "
            f"{item['destination']}"
        )

        percentage = (
            item["utilization"] * 100
        )

        print(
            f"{route_name:35}"
            f"{item['load']:8}"
            f"{item['capacity']:8}"
            f"{percentage:9.1f}%"
            f"{item['level']:>12}"
        )

    print("=" * 72)