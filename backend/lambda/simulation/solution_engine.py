from scenario_time_step import run_scenario


# ============================================================
# CONFIGURATION
# ============================================================

POPULATION_SIZE = 500

REGION = "global"

SEED = 42

EMERGENCY_TIME = 5


# ============================================================
# INTERVENTION LIBRARY
# ============================================================

INTERVENTIONS = [
    {
        "id": "baseline_response",

        "name": "Baseline Response",

        "description": (
            "No additional intervention. "
            "Respond using the existing infrastructure."
        ),

        "capacity_overrides": {},

        "edge_cost_multipliers": {},
    },

    {
        "id": "increase_staircase_b_capacity",

        "name": "Increase Staircase B Capacity",

        "description": (
            "Increase the effective capacity of "
            "the alternate staircase."
        ),

        "capacity_overrides": {
            "staircase_b": 140,
        },

        "edge_cost_multipliers": {},
    },

    {
        "id": "increase_alternate_exit_capacity",

        "name": "Increase Alternate Exit Capacity",

        "description": (
            "Increase the effective capacity of "
            "the alternate staircase and exit."
        ),

        "capacity_overrides": {
            "staircase_b": 140,
            "exit_b": 140,
        },

        "edge_cost_multipliers": {},
    },

    {
        "id": "improve_staircase_b_flow",

        "name": "Improve Alternate Route Flow",

        "description": (
            "Reduce the effective travel cost through "
            "the alternate staircase and exit."
        ),

        "capacity_overrides": {
            "staircase_b": 140,
            "exit_b": 140,
        },

        "edge_cost_multipliers": {
            tuple(
                sorted(
                    (
                        "staircase_b",
                        "exit_b",
                    )
                )
            ): 0.75,
        },
    },

    {
        "id": "increase_staircase_and_exit_capacity",

        "name": "Expand Alternate Egress Capacity",

        "description": (
            "Increase alternate staircase and exit "
            "capacity together."
        ),

        "capacity_overrides": {
            "staircase_b": 180,
            "exit_b": 160,
        },

        "edge_cost_multipliers": {},
    },
]


# ============================================================
# RUN ONE INTERVENTION
# ============================================================

def run_intervention(
    intervention,
):

    print()

    print("=" * 90)

    print(
        f"INTERVENTION: "
        f"{intervention['name']}"
    )

    print("=" * 90)

    print(
        f"Description: "
        f"{intervention['description']}"
    )

    result = run_scenario(
        population_size=POPULATION_SIZE,

        region=REGION,

        blocked_node="staircase_a",

        block_time=EMERGENCY_TIME,

        seed=SEED,

        capacity_overrides=(
            intervention[
                "capacity_overrides"
            ]
        ),

        edge_cost_multipliers=(
            intervention[
                "edge_cost_multipliers"
            ]
        ),
    )

    return result


# ============================================================
# SCORE A SOLUTION
# ============================================================

def calculate_solution_score(
    result,
):
    """
    Calculate a transparent decision-support score.

    This is NOT a universal safety score.

    It is only used internally to compare the
    simulated configurations under the same
    test conditions.
    """

    completion = (
        result["completion_rate"]
    )

    average_time = (
        result["average_evacuation_time"]
    )

    maximum_time = (
        result["maximum_evacuation_time"]
    )

    failure_rate = (
        result["failure_rate"]
    )

    # --------------------------------------------------------
    # Higher completion is better.
    # Lower evacuation time is better.
    # Lower failure rate is better.
    #
    # This score is deliberately kept simple.
    # --------------------------------------------------------

    score = (
        completion * 100
        - average_time
        - maximum_time * 0.25
        - failure_rate * 100
    )

    return round(
        score,
        3,
    )


# ============================================================
# RUN SOLUTION SEARCH
# ============================================================

def search_solutions():

    print()

    print("=" * 90)

    print(
        "AEGISTWIN SOLUTION ENGINE"
    )

    print("=" * 90)

    print(
        f"Population       : "
        f"{POPULATION_SIZE}"
    )

    print(
        f"Region           : "
        f"{REGION}"
    )

    print(
        f"Failure event    : "
        f"staircase_a @ {EMERGENCY_TIME}s"
    )

    print("=" * 90)

    results = []

    # --------------------------------------------------------
    # Test every intervention
    # --------------------------------------------------------

    for intervention in INTERVENTIONS:

        result = run_intervention(
            intervention
        )

        score = calculate_solution_score(
            result
        )

        results.append(
            {
                "intervention": intervention,

                "result": result,

                "score": score,
            }
        )

    return results


# ============================================================
# FILTER FEASIBLE SOLUTIONS
# ============================================================

def get_feasible_solutions(
    results,
):
    """
    A configuration is considered feasible for this
    experiment when every simulated agent completes
    evacuation within the simulation horizon.
    """

    feasible = []

    for item in results:

        result = item["result"]

        if (
            result["completed"]
            == result["population"]
            and result["failed"] == 0
            and result["remaining"] == 0
        ):

            feasible.append(
                item
            )

    return feasible


# ============================================================
# SORT RESULTS
# ============================================================

def sort_solutions(
    results,
):

    return sorted(
        results,
        key=lambda item: item[
            "score"
        ],
        reverse=True,
    )


# ============================================================
# PRINT RESULTS
# ============================================================

def print_solution_report(
    results,
):

    print()

    print("=" * 115)

    print(
        "AEGISTWIN SOLUTION SEARCH RESULTS"
    )

    print("=" * 115)

    print(
        f"{'INTERVENTION':34}"
        f"{'COMP.':>10}"
        f"{'FAILED':>10}"
        f"{'AVG':>12}"
        f"{'MAX':>12}"
        f"{'REROUTES':>12}"
        f"{'SCORE':>14}"
    )

    print("-" * 115)

    for item in results:

        intervention = item[
            "intervention"
        ]

        result = item[
            "result"
        ]

        score = item[
            "score"
        ]

        print(
            f"{intervention['name'][:33]:34}"
            f"{result['completed']:>10}"
            f"{result['failed']:>10}"
            f"{result['average_evacuation_time']:>12.2f}"
            f"{result['maximum_evacuation_time']:>12.2f}"
            f"{result['reroute_count']:>12}"
            f"{score:>14.3f}"
        )

    print("=" * 115)


# ============================================================
# PRINT FEASIBILITY ANALYSIS
# ============================================================

def print_feasibility_report(
    results,
):

    feasible = get_feasible_solutions(
        results
    )

    print()

    print("=" * 90)

    print(
        "FEASIBILITY ANALYSIS"
    )

    print("=" * 90)

    print(
        f"Configurations tested : "
        f"{len(results)}"
    )

    print(
        f"Feasible simulations  : "
        f"{len(feasible)}"
    )

    print()

    for item in feasible:

        intervention = item[
            "intervention"
        ]

        result = item[
            "result"
        ]

        print(
            f"✓ {intervention['name']}"
        )

        print(
            f"  Completion : "
            f"{result['completion_rate'] * 100:.1f}%"
        )

        print(
            f"  Avg time   : "
            f"{result['average_evacuation_time']:.2f}"
        )

        print(
            f"  Max time   : "
            f"{result['maximum_evacuation_time']:.2f}"
        )

        print()

    print("=" * 90)


# ============================================================
# DECISION SUPPORT SUMMARY
# ============================================================

def print_decision_summary(
    results,
):

    feasible = get_feasible_solutions(
        results
    )

    if not feasible:

        print()

        print(
            "No fully feasible configuration "
            "was found under the tested conditions."
        )

        return

    ranked = sort_solutions(
        feasible
    )

    best = ranked[0]

    intervention = best[
        "intervention"
    ]

    result = best[
        "result"
    ]

    print()

    print("=" * 90)

    print(
        "AEGISTWIN DECISION SUPPORT"
    )

    print("=" * 90)

    print(
        "Best-performing tested "
        "configuration:"
    )

    print()

    print(
        f"Intervention : "
        f"{intervention['name']}"
    )

    print(
        f"Description  : "
        f"{intervention['description']}"
    )

    print()

    print(
        f"Completion   : "
        f"{result['completion_rate'] * 100:.1f}%"
    )

    print(
        f"Average time : "
        f"{result['average_evacuation_time']:.2f}"
    )

    print(
        f"Maximum time : "
        f"{result['maximum_evacuation_time']:.2f}"
    )

    print(
        f"Reroutes     : "
        f"{result['reroute_count']}"
    )

    print(
        f"Score        : "
        f"{best['score']:.3f}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "This result represents the "
        "best-performing configuration "
        "among the interventions tested "
        "under this simulation model."
    )

    print(
        "It is not a real-world guarantee "
        "or universal safety recommendation."
    )

    print("=" * 90)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    results = search_solutions()

    feasible = get_feasible_solutions(
        results
    )

    ranked = sort_solutions(
        feasible
    )

    print_solution_report(
        results
    )

    print_feasibility_report(
        results
    )

    print_decision_summary(
        ranked
    )