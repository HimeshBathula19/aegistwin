import networkx as nx


def create_campus():
    """
    Create the AegisTwin campus digital twin.

    The environment is represented as a weighted graph:

    Nodes:
        rooms, corridors, staircases, exits

    Edges:
        physical connections between locations

    Weight:
        approximate travel cost
    """

    campus = nx.Graph()

    # =========================================================
    # LOCATIONS
    # =========================================================

    nodes = [
        (
            "north_classroom_1",
            {
                "type": "room",
                "capacity": 40,
                "zone": "north_block",
            },
        ),
        (
            "north_classroom_2",
            {
                "type": "room",
                "capacity": 40,
                "zone": "north_block",
            },
        ),
        (
            "academic_lab_1",
            {
                "type": "room",
                "capacity": 60,
                "zone": "academic_block",
            },
        ),
        (
            "academic_lab_2",
            {
                "type": "room",
                "capacity": 60,
                "zone": "academic_block",
            },
        ),
        (
            "cafeteria",
            {
                "type": "room",
                "capacity": 180,
                "zone": "cafeteria",
            },
        ),
        (
            "corridor_a",
            {
                "type": "corridor",
                "capacity": 120,
                "zone": "north_block",
            },
        ),
        (
            "corridor_b",
            {
                "type": "corridor",
                "capacity": 150,
                "zone": "academic_block",
            },
        ),
        (
            "corridor_c",
            {
                "type": "corridor",
                "capacity": 100,
                "zone": "central",
            },
        ),
        (
            "staircase_a",
            {
                "type": "staircase",
                "capacity": 80,
                "zone": "central",
            },
        ),
        (
            "staircase_b",
            {
                "type": "staircase",
                "capacity": 70,
                "zone": "central",
            },
        ),
        (
            "exit_a",
            {
                "type": "exit",
                "capacity": 120,
                "zone": "south",
            },
        ),
        (
            "exit_b",
            {
                "type": "exit",
                "capacity": 100,
                "zone": "east",
            },
        ),
    ]

    campus.add_nodes_from(nodes)

    # =========================================================
    # CONNECTIONS
    # =========================================================

    connections = [
        # North block
        ("north_classroom_1", "corridor_a", 2),
        ("north_classroom_2", "corridor_a", 2),

        # Academic block
        ("academic_lab_1", "corridor_b", 2),
        ("academic_lab_2", "corridor_b", 2),

        # Cafeteria
        ("cafeteria", "corridor_c", 3),

        # North corridor → staircases
        ("corridor_a", "staircase_a", 3),
        ("corridor_a", "staircase_b", 4),

        # Academic corridor → staircases
        ("corridor_b", "staircase_a", 3),
        ("corridor_b", "staircase_b", 3),

        # Central corridor → staircases
        ("corridor_c", "staircase_a", 2),
        ("corridor_c", "staircase_b", 2),

        # Staircases → exits
        ("staircase_a", "exit_a", 4),
        ("staircase_b", "exit_b", 4),

        # Direct emergency route
        ("corridor_c", "exit_a", 5),
    ]

    for source, destination, travel_cost in connections:
        campus.add_edge(
            source,
            destination,
            weight=travel_cost,
        )

    return campus


# =============================================================
# TEST / INSPECTION
# =============================================================

if __name__ == "__main__":

    campus = create_campus()

    print("AegisTwin Digital Twin")
    print("----------------------")

    print(f"Locations: {campus.number_of_nodes()}")
    print(f"Connections: {campus.number_of_edges()}")

    print("\nLocations:")

    for node, data in campus.nodes(data=True):
        print(
            f"- {node:22} "
            f"type={data['type']:10} "
            f"capacity={data['capacity']}"
        )

    print("\nConnections:")

    for source, destination, data in campus.edges(data=True):
        print(
            f"- {source:22} -> "
            f"{destination:22} "
            f"cost={data['weight']}"
        )