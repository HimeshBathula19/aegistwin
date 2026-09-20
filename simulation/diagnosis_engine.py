from collections import defaultdict

from scenario_time_step import run_scenario
from campus import create_campus


# ============================================================
# CONFIGURATION
# ============================================================

POPULATION_SIZE = 500
REGION = "global"
SEED = 42

EMERGENCY_TIME = 5
BLOCKED_INFRASTRUCTURE = "staircase_a"


# ============================================================
# DIAGNOSIS THRESHOLDS
# ============================================================

HIGH_DEPENDENCY_THRESHOLD = 0.50
CRITICAL_DEPENDENCY_THRESHOLD = 0.75

HIGH_UTILIZATION_THRESHOLD = 0.75
CRITICAL_UTILIZATION_THRESHOLD = 1.00

SIGNIFICANT_UTILIZATION_INCREASE = 0.15
CRITICAL_UTILIZATION_INCREASE = 0.30

HIGH_TIME_IMPACT = 5.0
CRITICAL_TIME_IMPACT = 10.0


# ============================================================
# ACTIONABLE INFRASTRUCTURE
# ============================================================

ACTIONABLE_TYPES = {
    "corridor",
    "staircase",
    "exit",
}


# ============================================================
# CAMPUS HELPERS
# ============================================================

def get_campus():

    return create_campus()


def get_node_type(
    campus,
    location,
):

    if location not in campus:

        return "unknown"

    return campus.nodes[
        location
    ].get(
        "type",
        "unknown",
    )


def get_capacity(
    campus,
    location,
):

    if location not in campus:

        return 0

    return campus.nodes[
        location
    ].get(
        "capacity",
        0,
    )


# ============================================================
# ROUTE DEPENDENCY
# ============================================================

def calculate_route_dependency(
    agents,
):
    """
    Measures how frequently each infrastructure
    location appears in successful evacuation routes.

    This is a simulation-derived route dependency
    indicator, not a physical safety measurement.
    """

    location_usage = defaultdict(int)

    successful_agents = 0

    for agent in agents:

        if not getattr(
            agent,
            "completed",
            False,
        ):

            continue

        route = getattr(
            agent,
            "route",
            [],
        )

        if not route:

            continue

        successful_agents += 1

        unique_locations = set(
            route
        )

        for location in unique_locations:

            location_usage[
                location
            ] += 1

    dependency = {}

    for location, count in (
        location_usage.items()
    ):

        if successful_agents == 0:

            dependency[
                location
            ] = 0.0

        else:

            dependency[
                location
            ] = count / successful_agents

    return dependency


# ============================================================
# PEAK UTILIZATION
# ============================================================

def calculate_peak_utilization(
    campus,
    peak_occupancy,
):
    """
    Calculates simulated peak utilization.

    utilization = peak occupancy / configured capacity
    """

    utilization = {}

    for location, occupancy in (
        peak_occupancy.items()
    ):

        capacity = get_capacity(
            campus,
            location,
        )

        if capacity <= 0:

            continue

        utilization[
            location
        ] = occupancy / capacity

    return utilization


# ============================================================
# SYSTEM IMPACT
# ============================================================

def analyze_failure_impact(
    baseline,
    scenario,
):

    average_change = (
        scenario[
            "average_evacuation_time"
        ]
        - baseline[
            "average_evacuation_time"
        ]
    )

    maximum_change = (
        scenario[
            "maximum_evacuation_time"
        ]
        - baseline[
            "maximum_evacuation_time"
        ]
    )

    completion_change = (
        scenario[
            "completion_rate"
        ]
        - baseline[
            "completion_rate"
        ]
    )

    failure_change = (
        scenario[
            "failure_rate"
        ]
        - baseline[
            "failure_rate"
        ]
    )

    reroutes = scenario.get(
        "reroutes",
        0,
    )

    return {
        "average_time_change":
            round(
                average_change,
                2,
            ),

        "maximum_time_change":
            round(
                maximum_change,
                2,
            ),

        "completion_change":
            round(
                completion_change,
                4,
            ),

        "failure_change":
            round(
                failure_change,
                4,
            ),

        "reroutes":
            reroutes,
    }


# ============================================================
# INFRASTRUCTURE DIAGNOSIS
# ============================================================

def classify_infrastructure(
    dependency,
    scenario_utilization,
    baseline_utilization,
    node_type,
):
    """
    Classifies infrastructure using multiple indicators.

    Actionable infrastructure receives stronger weight
    than ordinary rooms.
    """

    utilization_change = (
        scenario_utilization
        - baseline_utilization
    )

    # --------------------------------------------------------
    # Critical route dependency
    # --------------------------------------------------------

    if (
        dependency
        >= CRITICAL_DEPENDENCY_THRESHOLD
        and node_type
        in ACTIONABLE_TYPES
    ):

        return "CRITICAL"

    # --------------------------------------------------------
    # Major scenario-induced overload
    # --------------------------------------------------------

    if (
        utilization_change
        >= CRITICAL_UTILIZATION_INCREASE
        and node_type
        in ACTIONABLE_TYPES
    ):

        return "CRITICAL"

    # --------------------------------------------------------
    # High route dependency
    # --------------------------------------------------------

    if (
        dependency
        >= HIGH_DEPENDENCY_THRESHOLD
        and node_type
        in ACTIONABLE_TYPES
    ):

        return "HIGH"

    # --------------------------------------------------------
    # High utilization in actionable infrastructure
    # --------------------------------------------------------

    if (
        scenario_utilization
        >= CRITICAL_UTILIZATION_THRESHOLD
        and node_type
        in ACTIONABLE_TYPES
    ):

        return "HIGH"

    if (
        scenario_utilization
        >= HIGH_UTILIZATION_THRESHOLD
        and node_type
        in ACTIONABLE_TYPES
    ):

        return "MODERATE"

    # --------------------------------------------------------
    # Rooms are diagnostic context, not primary
    # intervention targets.
    # --------------------------------------------------------

    if (
        scenario_utilization
        >= CRITICAL_UTILIZATION_THRESHOLD
    ):

        return "CONTEXT"

    if (
        scenario_utilization
        >= HIGH_UTILIZATION_THRESHOLD
    ):

        return "CONTEXT"

    return "LOW"


# ============================================================
# GENERATE FINDINGS
# ============================================================

def generate_findings(
    campus,
    baseline,
    scenario,
):

    baseline_dependency = (
        calculate_route_dependency(
            baseline["agents"]
        )
    )

    scenario_dependency = (
        calculate_route_dependency(
            scenario["agents"]
        )
    )

    baseline_utilization = (
        calculate_peak_utilization(
            campus,
            baseline[
                "peak_occupancy"
            ],
        )
    )

    scenario_utilization = (
        calculate_peak_utilization(
            campus,
            scenario[
                "peak_occupancy"
            ],
        )
    )

    locations = set(
        baseline_dependency.keys()
    )

    locations.update(
        scenario_dependency.keys()
    )

    locations.update(
        baseline_utilization.keys()
    )

    locations.update(
        scenario_utilization.keys()
    )

    findings = []

    for location in locations:

        node_type = get_node_type(
            campus,
            location,
        )

        baseline_dep = (
            baseline_dependency.get(
                location,
                0.0,
            )
        )

        scenario_dep = (
            scenario_dependency.get(
                location,
                0.0,
            )
        )

        baseline_util = (
            baseline_utilization.get(
                location,
                0.0,
            )
        )

        scenario_util = (
            scenario_utilization.get(
                location,
                0.0,
            )
        )

        dependency_change = (
            scenario_dep
            - baseline_dep
        )

        utilization_change = (
            scenario_util
            - baseline_util
        )

        risk_level = classify_infrastructure(
            scenario_dep,
            scenario_util,
            baseline_util,
            node_type,
        )

        if risk_level == "LOW":

            continue

        reasons = []

        if (
            scenario_dep
            >= HIGH_DEPENDENCY_THRESHOLD
        ):

            reasons.append(
                "high route dependency"
            )

        if (
            dependency_change
            >= HIGH_DEPENDENCY_THRESHOLD
        ):

            reasons.append(
                "dependency increased after disruption"
            )

        if (
            scenario_util
            >= HIGH_UTILIZATION_THRESHOLD
        ):

            reasons.append(
                "high simulated peak utilization"
            )

        if (
            utilization_change
            >= SIGNIFICANT_UTILIZATION_INCREASE
        ):

            reasons.append(
                "utilization increased after disruption"
            )

        if (
            location
            == BLOCKED_INFRASTRUCTURE
        ):

            reasons.append(
                "failed infrastructure"
            )

        findings.append(
            {
                "location":
                    location,

                "node_type":
                    node_type,

                "risk_level":
                    risk_level,

                "baseline_dependency":
                    round(
                        baseline_dep,
                        3,
                    ),

                "scenario_dependency":
                    round(
                        scenario_dep,
                        3,
                    ),

                "dependency_change":
                    round(
                        dependency_change,
                        3,
                    ),

                "baseline_utilization":
                    round(
                        baseline_util,
                        3,
                    ),

                "scenario_utilization":
                    round(
                        scenario_util,
                        3,
                    ),

                "utilization_change":
                    round(
                        utilization_change,
                        3,
                    ),

                "reasons":
                    reasons,
            }
        )

    priority = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MODERATE": 2,
        "CONTEXT": 3,
        "LOW": 4,
    }

    findings.sort(
        key=lambda item: (
            priority[
                item["risk_level"]
            ],
            -item[
                "scenario_dependency"
            ],
            -item[
                "utilization_change"
            ],
        )
    )

    return findings


# ============================================================
# SCENARIO IMPACT CLASSIFICATION
# ============================================================

def classify_scenario_impact(
    impact,
):

    if (
        impact[
            "failure_change"
        ] > 0
    ):

        return "CRITICAL"

    if (
        impact[
            "average_time_change"
        ]
        >= CRITICAL_TIME_IMPACT
    ):

        return "CRITICAL"

    if (
        impact[
            "average_time_change"
        ]
        >= HIGH_TIME_IMPACT
    ):

        return "HIGH"

    if (
        impact[
            "average_time_change"
        ] > 0
    ):

        return "MODERATE"

    return "LOW"


# ============================================================
# COMPLETE DIAGNOSIS
# ============================================================

def diagnose_scenario(
    baseline,
    scenario,
):

    campus = get_campus()

    impact = analyze_failure_impact(
        baseline,
        scenario,
    )

    findings = generate_findings(
        campus,
        baseline,
        scenario,
    )

    scenario_impact = (
        classify_scenario_impact(
            impact
        )
    )

    actionable_findings = [
        finding
        for finding in findings
        if finding["node_type"]
        in ACTIONABLE_TYPES
    ]

    context_findings = [
        finding
        for finding in findings
        if finding["risk_level"]
        == "CONTEXT"
    ]

    return {
        "scenario_impact":
            scenario_impact,

        "impact":
            impact,

        "findings":
            findings,

        "actionable_findings":
            actionable_findings,

        "context_findings":
            context_findings,
    }


# ============================================================
# PRINT DIAGNOSIS
# ============================================================

def print_diagnosis(
    diagnosis,
):

    print()

    print("=" * 110)

    print(
        "AEGISTWIN DIAGNOSIS ENGINE v2"
    )

    print("=" * 110)

    print(
        f"Scenario impact : "
        f"{diagnosis['scenario_impact']}"
    )

    impact = diagnosis[
        "impact"
    ]

    print()

    print(
        "SYSTEM IMPACT"
    )

    print("-" * 110)

    print(
        f"Average evacuation change : "
        f"{impact['average_time_change']:+.2f}"
    )

    print(
        f"Maximum evacuation change : "
        f"{impact['maximum_time_change']:+.2f}"
    )

    print(
        f"Completion change          : "
        f"{impact['completion_change'] * 100:+.1f}%"
    )

    print(
        f"Failure-rate change        : "
        f"{impact['failure_change'] * 100:+.1f}%"
    )

    print(
        f"Rerouted agents            : "
        f"{impact['reroutes']}"
    )

    print()

    print(
        "ACTIONABLE INFRASTRUCTURE"
    )

    print("-" * 110)

    print(
        f"{'LOCATION':25}"
        f"{'TYPE':12}"
        f"{'RISK':12}"
        f"{'DEPENDENCY':15}"
        f"{'UTIL. Δ':12}"
        f"DIAGNOSIS"
    )

    print("-" * 110)

    if not diagnosis[
        "actionable_findings"
    ]:

        print(
            "No actionable infrastructure "
            "findings detected."
        )

    else:

        for finding in diagnosis[
            "actionable_findings"
        ]:

            reasons = ", ".join(
                finding["reasons"]
            )

            print(
                f"{finding['location'][:24]:25}"
                f"{finding['node_type'][:11]:12}"
                f"{finding['risk_level']:12}"
                f"{finding['scenario_dependency'] * 100:>12.1f}%"
                f"{finding['utilization_change'] * 100:>10.1f}%"
                f"  {reasons}"
            )

    print()

    print(
        "SIMULATION CONTEXT"
    )

    print("-" * 110)

    for finding in diagnosis[
        "context_findings"
    ]:

        print(
            f"{finding['location']}: "
            f"{finding['scenario_utilization'] * 100:.1f}% "
            f"simulated peak utilization "
            f"(context only)"
        )

    print()

    print("=" * 110)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

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

    print()

    print(
        "Running disruption scenario..."
    )

    scenario = run_scenario(
        population_size=POPULATION_SIZE,
        region=REGION,
        blocked_node=BLOCKED_INFRASTRUCTURE,
        block_time=EMERGENCY_TIME,
        seed=SEED,
    )

    diagnosis = diagnose_scenario(
        baseline,
        scenario,
    )

    print_diagnosis(
        diagnosis
    )