import json
import sys
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SIMULATION_DIR = PROJECT_ROOT / "simulation"

sys.path.insert(0, str(SIMULATION_DIR))


from scenario_time_step import run_scenario


# ============================================================
# REQUEST LOADING
# ============================================================

def load_request():

    request_path = (
        PROJECT_ROOT
        / "backend"
        / "models"
        / "simulation_request.json"
    )

    with open(
        request_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# INTERVENTION CONVERSION
# ============================================================

def build_capacity_overrides(interventions):

    overrides = {}

    for intervention in interventions:

        if intervention.get("type") != "capacity_increase":
            continue

        target = intervention.get("target")

        increase_percent = float(
            intervention.get(
                "increase_percent",
                0
            )
        )

        if not target:
            continue

        if increase_percent <= 0:
            continue

        overrides[target] = (
            1 + increase_percent / 100
        )

    return overrides


def build_edge_cost_multipliers(interventions):

    multipliers = {}

    for intervention in interventions:

        if intervention.get("type") != "flow_improvement":
            continue

        target = intervention.get("target")

        multiplier = intervention.get(
            "multiplier"
        )

        if not target:
            continue

        if multiplier is None:
            continue

        if "->" not in target:
            continue

        source, destination = target.split(
            "->",
            1
        )

        source = source.strip()
        destination = destination.strip()

        # scenario_time_step normalizes graph edges
        # using sorted tuples, so do the same here.

        edge = tuple(
            sorted(
                (
                    source,
                    destination
                )
            )
        )

        multipliers[edge] = float(
            multiplier
        )

    return multipliers


# ============================================================
# RUN SIMULATION
# ============================================================

def run_simulation(request):

    environment = request.get(
        "environment",
        {}
    )

    scenario = request.get(
        "scenario",
        {}
    )

    interventions = request.get(
        "interventions",
        []
    )

    population_size = int(
        environment.get(
            "population_size",
            500
        )
    )

    region = environment.get(
        "region",
        "global"
    )

    blocked_nodes = scenario.get(
        "blocked_nodes",
        []
    )

    blocked_node = (
        blocked_nodes[0]
        if blocked_nodes
        else None
    )

    block_time = scenario.get(
        "start_time"
    )

    if block_time is not None:
        block_time = float(
            block_time
        )

    capacity_overrides = (
        build_capacity_overrides(
            interventions
        )
    )

    edge_cost_multipliers = (
        build_edge_cost_multipliers(
            interventions
        )
    )

    print(
        f"Population size: {population_size}"
    )

    print(
        f"Region: {region}"
    )

    print(
        f"Blocked node: {blocked_node}"
    )

    print(
        f"Block time: {block_time}"
    )

    print(
        f"Capacity interventions: "
        f"{len(capacity_overrides)}"
    )

    print(
        f"Flow interventions: "
        f"{len(edge_cost_multipliers)}"
    )

    # ========================================================
    # EXISTING AEGISTWIN SIMULATION
    # ========================================================

    result = run_scenario(

        population_size=population_size,

        region=region,

        blocked_node=blocked_node,

        block_time=block_time,

        seed=42,

        capacity_overrides=capacity_overrides,

        edge_cost_multipliers=edge_cost_multipliers,
    )

    return result


# ============================================================
# API RESULT ADAPTER
# ============================================================

def build_result(
    request,
    simulation_result
):

    scenario = request.get(
        "scenario",
        {}
    )

    return {

        "run_id": "local_worker_run",

        "status": "completed",

        "scenario": {

            "name": scenario.get(
                "name",
                "Unnamed Scenario"
            ),

            "hazard": scenario.get(
                "hazard",
                "unknown"
            ),

            "blocked_nodes": scenario.get(
                "blocked_nodes",
                []
            ),

            "start_time": scenario.get(
                "start_time"
            )
        },

        "metrics": {

            "population": simulation_result.get(
                "population",
                0
            ),

            "completed": simulation_result.get(
                "completed",
                0
            ),

            "failed": simulation_result.get(
                "failed",
                0
            ),

            "remaining": simulation_result.get(
                "remaining",
                0
            ),

            "completion_rate": round(
                simulation_result.get(
                    "completion_rate",
                    0
                ) * 100,
                2
            ),

            "failure_rate": round(
                simulation_result.get(
                    "failure_rate",
                    0
                ) * 100,
                2
            ),

            "minimum_evacuation_time":
                simulation_result.get(
                    "minimum_evacuation_time",
                    0
                ),

            "average_evacuation_time":
                simulation_result.get(
                    "average_evacuation_time",
                    0
                ),

            "maximum_evacuation_time":
                simulation_result.get(
                    "maximum_evacuation_time",
                    0
                ),

            "reroutes":
                simulation_result.get(
                    "reroute_count",
                    0
                ),

            "simulation_duration":
                simulation_result.get(
                    "simulation_time",
                    0
                )
        },

        "interventions_tested": len(
            request.get(
                "interventions",
                []
            )
        )
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("AEGISTWIN SIMULATION WORKER")
    print("=" * 60)

    request = load_request()

    print("\nRequest loaded:")

    print(
        f"Population: "
        f"{request['environment']['population_size']}"
    )

    print(
        f"Scenario: "
        f"{request['scenario']['name']}"
    )

    print(
        f"Blocked infrastructure: "
        f"{request['scenario']['blocked_nodes']}"
    )

    print(
        f"Emergency start time: "
        f"{request['scenario']['start_time']}"
    )

    print(
        "\nRunning AegisTwin simulation...\n"
    )

    simulation_result = run_simulation(
        request
    )

    result = build_result(
        request,
        simulation_result
    )

    print("\n" + "=" * 60)
    print("SIMULATION COMPLETED")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    # ========================================================
    # SAVE RESULT
    # ========================================================

    output_path = (
        PROJECT_ROOT
        / "backend"
        / "models"
        / "latest_result.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=2
        )

    print(
        f"\nResult saved to:\n{output_path}"
    )


if __name__ == "__main__":
    main()