from collections import Counter
from typing import List


def count_edge_occupancy(routes: List[List[str]]):
    """
    Count how many simulated agents use each
    connection in the campus graph.

    Example:

        Agent 1:
            A -> B -> C

        Agent 2:
            A -> B -> C

        Agent 3:
            A -> D

    Produces:

        A -> B : 2
        B -> C : 2
        A -> D : 1
    """

    occupancy = Counter()

    for route in routes:

        for index in range(len(route) - 1):

            source = route[index]
            destination = route[index + 1]

            edge = (
                source,
                destination
            )

            occupancy[edge] += 1

    return dict(occupancy)


def print_occupancy(occupancy):

    print()
    print("=" * 60)
    print("SIMULATED INFRASTRUCTURE OCCUPANCY")
    print("=" * 60)

    for (source, destination), count in occupancy.items():

        print(
            f"{source:20} -> "
            f"{destination:20} "
            f"{count:4} agents"
        )