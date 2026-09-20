from scenario_time_step import run_scenario
from diagnosis_engine import diagnose_scenario
from intervention_engine import InterventionGenerator
from campus import create_campus


# ============================================================
# CONFIGURATION
# ============================================================

POPULATION_SIZE = 500
REGION = "global"
SEED = 42

BLOCKED_INFRASTRUCTURE = "staircase_a"
EMERGENCY_TIME = 5


# ============================================================
# PEAK OVERLOAD
# ============================================================

def calculate_peak_overload(
    result,
    campus,
):
    """
    Calculates the total simulated peak utilization
    above 100%.

    This is a simulation metric only.
    """

    peak_occupancy = result.get(
        "peak_occupancy",
        {},
    )

    overload = 0.0

    for location, occupancy in peak_occupancy.items():

        if location not in campus:
            continue

        capacity = campus.nodes[
            location
        ].get(
            "capacity",
            0,
        )

        if capacity <= 0:
            continue

        utilization = occupancy / capacity

        if utilization > 1.0:
            overload += utilization - 1.0

    return overload


# ============================================================
# PERFORMANCE INDEX
# ============================================================

def calculate_performance_index(
    result,
    intervention,
    campus,
):
    """
    Comparative metric used only to rank the configurations
    tested by AegisTwin.
    """

    completion_rate = result.get(
        "completion_rate",
        0.0,
    )

    failure_rate = result.get(
        "failure_rate",
        0.0,
    )

    average_time = result.get(
        "average_evacuation_time",
        9999,
    )

    maximum_time = result.get(
        "maximum_evacuation_time",
        9999,
    )

    reroutes = result.get(
        "reroutes",
        0,
    )

    overload = calculate_peak_overload(
        result,
        campus,
    )

    # --------------------------------------------------------
    # Approximate intervention complexity penalty
    # --------------------------------------------------------

    intervention_type = intervention.get(
        "type",
        "",
    )

    if intervention_type == "capacity_increase":

        intervention_cost = 5

    elif intervention_type == "flow_improvement":

        intervention_cost = 3

    elif intervention_type == "alternate_route":

        intervention_cost = 2

    else:

        intervention_cost = 1

    # --------------------------------------------------------
    # Comparative index
    # --------------------------------------------------------

    index = (
        completion_rate * 100
        - failure_rate * 100
        - average_time
        - maximum_time * 0.25
        - overload * 10
        - reroutes * 0.01
        - intervention_cost
    )

    return round(
        index,
        3,
    )


# ============================================================
# IMPROVEMENT ANALYSIS
# ============================================================

def calculate_improvement(
    emergency_result,
    candidate_result,
):
    """
    Compare an intervention against the emergency
    scenario without intervention.
    """

    emergency_avg = emergency_result[
        "average_evacuation_time"
    ]

    candidate_avg = candidate_result[
        "average_evacuation_time"
    ]

    emergency_max = emergency_result[
        "maximum_evacuation_time"
    ]

    candidate_max = candidate_result[
        "maximum_evacuation_time"
    ]

    emergency_completion = (
        emergency_result[
            "completion_rate"
        ]
    )

    candidate_completion = (
        candidate_result[
            "completion_rate"
        ]
    )

    emergency_failure = (
        emergency_result[
            "failure_rate"
        ]
    )

    candidate_failure = (
        candidate_result[
            "failure_rate"
        ]
    )

    return {
        "average_time_change":
            round(
                candidate_avg
                - emergency_avg,
                2,
            ),

        "average_time_improvement":
            round(
                emergency_avg
                - candidate_avg,
                2,
            ),

        "maximum_time_change":
            round(
                candidate_max
                - emergency_max,
                2,
            ),

        "maximum_time_improvement":
            round(
                emergency_max
                - candidate_max,
                2,
            ),

        "completion_change":
            round(
                candidate_completion
                - emergency_completion,
                4,
            ),

        "failure_change":
            round(
                candidate_failure
                - emergency_failure,
                4,
            ),
    }


# ============================================================
# EVALUATE ONE INTERVENTION
# ============================================================

def evaluate_intervention(
    intervention,
    emergency_result,
    campus,
):
    """
    Run one generated intervention through the same
    emergency scenario.
    """

    changes = intervention.get(
        "changes",
        {},
    )

    capacity_overrides = changes.get(
        "capacity_overrides",
        None,
    )

    edge_cost_multipliers = changes.get(
        "edge_cost_multipliers",
        None,
    )

    result = run_scenario(
        population_size=POPULATION_SIZE,
        region=REGION,
        blocked_node=BLOCKED_INFRASTRUCTURE,
        block_time=EMERGENCY_TIME,
        seed=SEED,
        capacity_overrides=capacity_overrides,
        edge_cost_multipliers=edge_cost_multipliers,
    )

    improvement = calculate_improvement(
        emergency_result,
        result,
    )

    performance_index = (
        calculate_performance_index(
            result,
            intervention,
            campus,
        )
    )

    return {
        "intervention":
            intervention,

        "result":
            result,

        "improvement":
            improvement,

        "performance_index":
            performance_index,
    }


# ============================================================
# EVALUATE ALL INTERVENTIONS
# ============================================================

def evaluate_all(
    interventions,
    emergency_result,
    campus,
):
    """
    Test every generated intervention.
    """

    evaluations = []

    total = len(
        interventions
    )

    print()
    print("=" * 110)
    print(
        "AEGISTWIN INTERVENTION EVALUATION"
    )
    print("=" * 110)

    print(
        f"Testing {total} candidate interventions..."
    )

    print()

    for index, intervention in enumerate(
        interventions,
        start=1,
    ):

        print(
            f"[{index}/{total}] "
            f"Testing "
            f"{intervention['intervention_id']} "
            f"-> "
            f"{intervention['reason']}"
        )

        evaluation = evaluate_intervention(
            intervention,
            emergency_result,
            campus,
        )

        evaluations.append(
            evaluation
        )

    return evaluations


# ============================================================
# SORT RESULTS
# ============================================================

def sort_evaluations(
    evaluations,
):

    return sorted(
        evaluations,
        key=lambda item:
            item[
                "performance_index"
            ],
        reverse=True,
    )


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    emergency_result,
    evaluations,
):

    ranked = sort_evaluations(
        evaluations
    )

    print()
    print("=" * 120)
    print(
        "AEGISTWIN DECISION SUPPORT"
    )
    print("=" * 120)

    # --------------------------------------------------------
    # Emergency baseline
    # --------------------------------------------------------

    print(
        "EMERGENCY BASELINE"
    )

    print("-" * 120)

    print(
        f"Completion       : "
        f"{emergency_result['completion_rate'] * 100:.1f}%"
    )

    print(
        f"Failure          : "
        f"{emergency_result['failure_rate'] * 100:.1f}%"
    )

    print(
        f"Average time     : "
        f"{emergency_result['average_evacuation_time']:.2f}"
    )

    print(
        f"Maximum time     : "
        f"{emergency_result['maximum_evacuation_time']:.2f}"
    )

    print()

    # --------------------------------------------------------
    # Ranked candidates
    # --------------------------------------------------------

    print(
        "TESTED CONFIGURATIONS"
    )

    print("-" * 120)

    print(
        f"{'ID':10}"
        f"{'TYPE':22}"
        f"{'AVG':10}"
        f"{'MAX':10}"
        f"{'COMP.':10}"
        f"{'FAIL.':10}"
        f"{'INDEX':10}"
    )

    print("-" * 120)

    for evaluation in ranked:

        intervention = evaluation[
            "intervention"
        ]

        result = evaluation[
            "result"
        ]

        print(
            f"{intervention['intervention_id']:10}"
            f"{intervention['type'][:20]:22}"
            f"{result['average_evacuation_time']:10.2f}"
            f"{result['maximum_evacuation_time']:10.2f}"
            f"{result['completion_rate'] * 100:9.1f}%"
            f"{result['failure_rate'] * 100:9.1f}%"
            f"{evaluation['performance_index']:10.2f}"
        )

    # --------------------------------------------------------
    # Best-performing tested configuration
    # --------------------------------------------------------

    if not ranked:
        print()
        print(
            "No interventions were evaluated."
        )
        return

    top = ranked[0]

    intervention = top[
        "intervention"
    ]

    improvement = top[
        "improvement"
    ]

    result = top[
        "result"
    ]

    print()
    print("=" * 120)
    print(
        "BEST-PERFORMING TESTED CONFIGURATION"
    )
    print("=" * 120)

    print(
        f"Intervention : "
        f"{intervention['intervention_id']}"
    )

    print(
        f"Type         : "
        f"{intervention['type']}"
    )

    print(
        f"Reason       : "
        f"{intervention['reason']}"
    )

    print()

    print(
        "SIMULATION RESULT"
    )

    print(
        f"Completion   : "
        f"{result['completion_rate'] * 100:.1f}%"
    )

    print(
        f"Failure      : "
        f"{result['failure_rate'] * 100:.1f}%"
    )

    print(
        f"Average time : "
        f"{result['average_evacuation_time']:.2f}"
    )

    print(
        f"Maximum time : "
        f"{result['maximum_evacuation_time']:.2f}"
    )

    print()

    print(
        "CHANGE VS EMERGENCY BASELINE"
    )

    print(
        f"Average time improvement : "
        f"{improvement['average_time_improvement']:+.2f}"
    )

    print(
        f"Maximum time improvement : "
        f"{improvement['maximum_time_improvement']:+.2f}"
    )

    print(
        f"Completion change        : "
        f"{improvement['completion_change'] * 100:+.1f}%"
    )

    print(
        f"Failure change           : "
        f"{improvement['failure_change'] * 100:+.1f}%"
    )

    print()

    print(
        "Performance index is only a comparative "
        "metric across the configurations tested "
        "by this simulation."
    )

    print("=" * 120)


# ============================================================
# MAIN PIPELINE
# ============================================================

if __name__ == "__main__":

    campus = create_campus()

    # --------------------------------------------------------
    # 1. Baseline
    # --------------------------------------------------------

    print(
        "Running baseline..."
    )

    baseline = run_scenario(
        population_size=POPULATION_SIZE,
        region=REGION,
        blocked_node=None,
        block_time=None,
        seed=SEED,
    )

    # --------------------------------------------------------
    # 2. Emergency scenario
    # --------------------------------------------------------

    print(
        "Running emergency scenario..."
    )

    emergency = run_scenario(
        population_size=POPULATION_SIZE,
        region=REGION,
        blocked_node=BLOCKED_INFRASTRUCTURE,
        block_time=EMERGENCY_TIME,
        seed=SEED,
    )

    # --------------------------------------------------------
    # 3. Diagnosis
    # --------------------------------------------------------

    print(
        "Running diagnosis..."
    )

    diagnosis = diagnose_scenario(
        baseline,
        emergency,
    )

    # --------------------------------------------------------
    # 4. Generate interventions
    # --------------------------------------------------------

    print(
        "Generating interventions..."
    )

    generator = InterventionGenerator(
        campus
    )

    interventions = generator.generate(
        diagnosis,
        max_findings=3,
    )

    print(
        f"Generated {len(interventions)} "
        f"candidate interventions."
    )

    # --------------------------------------------------------
    # 5. Evaluate all interventions
    # --------------------------------------------------------

    evaluations = evaluate_all(
        interventions,
        emergency,
        campus,
    )

    # --------------------------------------------------------
    # 6. Decision support
    # --------------------------------------------------------

    print_results(
        emergency,
        evaluations,
    )