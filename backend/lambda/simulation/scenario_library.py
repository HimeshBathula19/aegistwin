from scenario_time_step import (
    run_scenario,
    compare_scenarios,
)


# ============================================================
# CONFIGURATION
# ============================================================

POPULATION_SIZE = 500

REGION = "global"

SEED = 42

EMERGENCY_TIME = 5


# ============================================================
# SCENARIO DEFINITIONS
# ============================================================

SCENARIOS = [
    {
        "id": "baseline",

        "name": "Normal Evacuation",

        "description": (
            "Normal evacuation with no "
            "infrastructure failure."
        ),

        "blocked_node": None,

        "block_time": None,
    },

    {
        "id": "staircase_a_failure",

        "name": "Staircase A Failure",

        "description": (
            "Staircase A becomes unavailable "
            "during evacuation."
        ),

        "blocked_node": "staircase_a",

        "block_time": EMERGENCY_TIME,
    },

    {
        "id": "staircase_b_failure",

        "name": "Staircase B Failure",

        "description": (
            "Staircase B becomes unavailable "
            "during evacuation."
        ),

        "blocked_node": "staircase_b",

        "block_time": EMERGENCY_TIME,
    },

    {
        "id": "corridor_a_failure",

        "name": "Corridor A Failure",

        "description": (
            "Corridor A becomes unavailable "
            "during evacuation."
        ),

        "blocked_node": "corridor_a",

        "block_time": EMERGENCY_TIME,
    },

    {
        "id": "corridor_b_failure",

        "name": "Corridor B Failure",

        "description": (
            "Corridor B becomes unavailable "
            "during evacuation."
        ),

        "blocked_node": "corridor_b",

        "block_time": EMERGENCY_TIME,
    },

    {
        "id": "corridor_c_failure",

        "name": "Corridor C Failure",

        "description": (
            "Corridor C becomes unavailable "
            "during evacuation."
        ),

        "blocked_node": "corridor_c",

        "block_time": EMERGENCY_TIME,
    },

    {
        "id": "exit_a_failure",

        "name": "Exit A Failure",

        "description": (
            "Exit A becomes unavailable "
            "during evacuation."
        ),

        "blocked_node": "exit_a",

        "block_time": EMERGENCY_TIME,
    },

    {
        "id": "exit_b_failure",

        "name": "Exit B Failure",

        "description": (
            "Exit B becomes unavailable "
            "during evacuation."
        ),

        "blocked_node": "exit_b",

        "block_time": EMERGENCY_TIME,
    },
]


# ============================================================
# RUN ONE SCENARIO
# ============================================================

def run_named_scenario(
    scenario,
):

    print()

    print("=" * 85)

    print(
        f"SCENARIO: {scenario['name']}"
    )

    print("=" * 85)

    print(
        f"Description : "
        f"{scenario['description']}"
    )

    result = run_scenario(
        population_size=POPULATION_SIZE,

        region=REGION,

        blocked_node=scenario[
            "blocked_node"
        ],

        block_time=scenario[
            "block_time"
        ],

        seed=SEED,
    )

    return result


# ============================================================
# RUN SCENARIO LIBRARY
# ============================================================

def run_all_scenarios():

    print()

    print("=" * 85)

    print(
        "AEGISTWIN SCENARIO LIBRARY"
    )

    print("=" * 85)

    print(
        f"Population : "
        f"{POPULATION_SIZE}"
    )

    print(
        f"Region     : "
        f"{REGION}"
    )

    print(
        f"Event time : "
        f"{EMERGENCY_TIME}"
    )

    print("=" * 85)

    results = {}

    baseline = None

    # --------------------------------------------------------
    # Run every scenario
    # --------------------------------------------------------

    for scenario in SCENARIOS:

        result = run_named_scenario(
            scenario
        )

        results[
            scenario["id"]
        ] = result

        if scenario["id"] == "baseline":

            baseline = result

    return (
        baseline,
        results,
    )


# ============================================================
# SCENARIO SUMMARY
# ============================================================

def print_summary(
    baseline,
    results,
):

    print()

    print("=" * 110)

    print(
        "AEGISTWIN SCENARIO COMPARISON"
    )

    print("=" * 110)

    print(
        f"{'SCENARIO':28}"
        f"{'COMPLETED':>12}"
        f"{'FAILED':>10}"
        f"{'AVG TIME':>14}"
        f"{'MAX TIME':>14}"
        f"{'REROUTES':>14}"
    )

    print("-" * 110)

    baseline_average = baseline[
        "average_evacuation_time"
    ]

    baseline_maximum = baseline[
        "maximum_evacuation_time"
    ]

    for scenario in SCENARIOS:

        result = results[
            scenario["id"]
        ]

        average_time = result[
            "average_evacuation_time"
        ]

        maximum_time = result[
            "maximum_evacuation_time"
        ]

        average_change = (
            average_time
            - baseline_average
        )

        maximum_change = (
            maximum_time
            - baseline_maximum
        )

        if scenario["id"] == "baseline":

            average_display = (
                f"{average_time:.2f}"
            )

            maximum_display = (
                f"{maximum_time:.2f}"
            )

        else:

            average_display = (
                f"{average_time:.2f} "
                f"({average_change:+.2f})"
            )

            maximum_display = (
                f"{maximum_time:.2f} "
                f"({maximum_change:+.2f})"
            )

        print(
            f"{scenario['name'][:27]:28}"
            f"{result['completed']:>12}"
            f"{result['failed']:>10}"
            f"{average_display:>14}"
            f"{maximum_display:>14}"
            f"{result['reroute_count']:>14}"
        )

    print("=" * 110)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    baseline, results = (
        run_all_scenarios()
    )

    print_summary(
        baseline,
        results,
    )